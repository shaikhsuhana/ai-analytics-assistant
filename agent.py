# agent.py — AI Analytics Agent using LangGraph + SQLite + Groq (free)

import os
import sqlite3
import pandas as pd
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from setup_db import create_db, DB_PATH

# ── Ensure DB exists ──────────────────────────────────────────────────────────
if not os.path.exists(DB_PATH):
    create_db()


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_schema() -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    schema_parts = []
    for table in tables:
        c.execute(f"PRAGMA table_info({table})")
        cols = c.fetchall()
        col_defs = ", ".join(f"{col[1]} ({col[2]})" for col in cols)
        schema_parts.append(f"Table `{table}`: {col_defs}")
    conn.close()
    return "\n".join(schema_parts)


def run_sql(query: str) -> tuple[str, pd.DataFrame | None]:
    """Returns (text_result, dataframe_or_None)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            return "Query returned no results.", None
        return df.to_string(index=False), df
    except Exception as e:
        return f"SQL Error: {e}", None


# ── LangGraph State ───────────────────────────────────────────────────────────
class AnalyticsState(TypedDict):
    question: str
    schema: str
    sql_query: str
    raw_result: str
    final_answer: str
    dataframe: object
    chart_hint: str


# ── Agent Nodes ───────────────────────────────────────────────────────────────
def build_agent():
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        groq_api_key=os.environ.get("GROQ_API_KEY", "")
    )

    schema = get_schema()

    def fetch_schema(state: AnalyticsState) -> AnalyticsState:
        return {**state, "schema": schema}

    def generate_sql(state: AnalyticsState) -> AnalyticsState:
        prompt = f"""You are an expert data analyst and SQL developer.
Database schema (SQLite):
{state['schema']}

Rules:
- Write only a valid SQLite SELECT query.
- Never use UPDATE, DELETE, DROP, INSERT.
- Return ONLY the raw SQL, no explanation, no markdown, no backticks.
- Limit results to 50 rows max unless the question asks for totals/aggregates.

User question: {state['question']}"""
        sql = llm.invoke(prompt).content.strip()
        sql = sql.replace("```sql", "").replace("```", "").strip()
        return {**state, "sql_query": sql}

    def execute_query(state: AnalyticsState) -> AnalyticsState:
        text, df = run_sql(state["sql_query"])
        return {**state, "raw_result": text, "dataframe": df}

    def generate_answer(state: AnalyticsState) -> AnalyticsState:
        prompt = f"""You are a senior data analyst presenting findings to a business stakeholder.

User asked: {state['question']}
SQL used: {state['sql_query']}
Data returned:
{state['raw_result']}

Write a clear, concise answer in 2-4 sentences. Include the key numbers.
Then on a new line write: CHART: bar | line | pie | none
Choose the chart type that best visualises this data. Use "none" for single-value answers."""
        response = llm.invoke(prompt).content.strip()

        chart_hint = "none"
        answer = response
        if "CHART:" in response:
            parts = response.rsplit("CHART:", 1)
            answer = parts[0].strip()
            chart_hint = parts[1].strip().split()[0].lower()

        return {**state, "final_answer": answer, "chart_hint": chart_hint}

    graph = StateGraph(AnalyticsState)
    graph.add_node("fetch_schema",    fetch_schema)
    graph.add_node("generate_sql",    generate_sql)
    graph.add_node("execute_query",   execute_query)
    graph.add_node("generate_answer", generate_answer)

    graph.set_entry_point("fetch_schema")
    graph.add_edge("fetch_schema",    "generate_sql")
    graph.add_edge("generate_sql",    "execute_query")
    graph.add_edge("execute_query",   "generate_answer")
    graph.add_edge("generate_answer", END)

    return graph.compile()


def ask_analytics(question: str) -> dict:
    agent = build_agent()
    result = agent.invoke({
        "question": question,
        "schema": "",
        "sql_query": "",
        "raw_result": "",
        "final_answer": "",
        "dataframe": None,
        "chart_hint": "none",
    })
    return result
