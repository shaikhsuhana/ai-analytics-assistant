# app.py — AI-Powered Analytics Assistant

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from agent import ask_analytics, get_schema, DB_PATH
from setup_db import create_db

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Analytics Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Font & base ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* ── Background ── */
  .stApp { background: #0f1117; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: #161b27 !important;
    border-right: 1px solid #1e2533;
  }

  /* ── Chat bubbles ── */
  .user-bubble {
    background: #1a2744;
    border: 1px solid #2a3a5c;
    border-radius: 12px 12px 4px 12px;
    padding: 14px 18px;
    margin: 8px 0;
    color: #e2e8f0;
    font-size: 0.95rem;
  }
  .assistant-bubble {
    background: #111827;
    border: 1px solid #1e2d40;
    border-left: 3px solid #3b82f6;
    border-radius: 4px 12px 12px 12px;
    padding: 14px 18px;
    margin: 8px 0;
    color: #cbd5e1;
    font-size: 0.95rem;
    line-height: 1.6;
  }

  /* ── SQL block ── */
  .sql-block {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #58a6ff;
    margin-top: 8px;
    overflow-x: auto;
  }

  /* ── Metric cards ── */
  .metric-card {
    background: #161b27;
    border: 1px solid #1e2533;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
  }
  .metric-value { font-size: 1.6rem; font-weight: 700; color: #3b82f6; }
  .metric-label { font-size: 0.78rem; color: #64748b; margin-top: 2px; letter-spacing: 0.05em; text-transform: uppercase; }

  /* ── Suggestion chips ── */
  .chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
  .chip {
    background: #1a2236;
    border: 1px solid #2a3a5c;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.8rem;
    color: #93c5fd;
    cursor: pointer;
  }

  /* ── Header ── */
  .main-header {
    padding: 24px 0 8px 0;
    border-bottom: 1px solid #1e2533;
    margin-bottom: 24px;
  }
  .main-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.02em;
  }
  .main-subtitle { font-size: 0.85rem; color: #475569; margin-top: 4px; }

  /* ── Schema table ── */
  .schema-table { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #64748b; }

  /* Hide Streamlit branding ── */
  #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Ensure DB ─────────────────────────────────────────────────────────────────
if not os.path.exists(DB_PATH):
    create_db()

# ── API key from secrets or env ───────────────────────────────────────────────
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Analytics Assistant")
    st.markdown("<div style='color:#475569;font-size:0.8rem;margin-bottom:20px'>Ask anything about the e-commerce dataset in plain English.</div>", unsafe_allow_html=True)

    # API key input if not set
    if not os.environ.get("OPENAI_API_KEY"):
        st.markdown("**OpenAI API Key**")
        api_key = st.text_input("", type="password", placeholder="sk-...", label_visibility="collapsed")
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

    st.divider()

    # DB stats
    st.markdown("**📁 Dataset**")
    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        orders_count  = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        customers_count = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        revenue_total = conn.execute("SELECT SUM(revenue) FROM orders WHERE status='Completed'").fetchone()[0]
        conn.close()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Orders",    f"{orders_count:,}")
            st.metric("Revenue",   f"${revenue_total:,.0f}")
        with col2:
            st.metric("Customers", f"{customers_count:,}")
            st.metric("Products",  "10")
    except Exception:
        st.info("Dataset loading...")

    st.divider()

    # Schema viewer
    with st.expander("🗂 View Schema"):
        schema = get_schema()
        for line in schema.split("\n"):
            st.markdown(f"<div class='schema-table'>{line}</div>", unsafe_allow_html=True)

    st.divider()

    if st.button("🗑 Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class='main-header'>
  <div class='main-title'>📊 AI Analytics Assistant</div>
  <div class='main-subtitle'>E-commerce Intelligence · Powered by GPT-4o + LangGraph</div>
</div>
""", unsafe_allow_html=True)

# ── Suggested questions ───────────────────────────────────────────────────────
SUGGESTIONS = [
    "What are the top 5 products by revenue?",
    "Which region has the highest sales?",
    "Show monthly revenue trend",
    "What is the refund rate by channel?",
    "Which category sells the most units?",
    "Who are the top 10 customers by spend?",
]

if not st.session_state.messages:
    st.markdown("<div style='color:#475569;font-size:0.85rem;margin-bottom:8px'>✨ Try asking:</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i % 3]:
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_question = suggestion
                st.rerun()

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-bubble'>🧑 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-bubble'>🤖 {msg['content']}</div>", unsafe_allow_html=True)
        if msg.get("sql"):
            with st.expander("View SQL query"):
                st.markdown(f"<div class='sql-block'>{msg['sql']}</div>", unsafe_allow_html=True)
        if msg.get("dataframe") is not None:
            df = msg["dataframe"]
            chart_hint = msg.get("chart_hint", "none")
            col_data, col_chart = st.columns([1, 1]) if chart_hint != "none" else (st.container(), None)

            with col_data if chart_hint != "none" else col_data:
                st.dataframe(df, use_container_width=True, hide_index=True)

            if chart_hint != "none" and col_chart:
                with col_chart:
                    try:
                        num_cols = df.select_dtypes(include="number").columns.tolist()
                        cat_cols = df.select_dtypes(exclude="number").columns.tolist()
                        if num_cols and cat_cols:
                            x, y = cat_cols[0], num_cols[0]
                            if chart_hint == "bar":
                                fig = px.bar(df, x=x, y=y, color_discrete_sequence=["#3b82f6"])
                            elif chart_hint == "line":
                                fig = px.line(df, x=x, y=y, color_discrete_sequence=["#3b82f6"], markers=True)
                            elif chart_hint == "pie":
                                fig = px.pie(df, names=x, values=y, color_discrete_sequence=px.colors.sequential.Blues_r)
                            else:
                                fig = px.bar(df, x=x, y=y, color_discrete_sequence=["#3b82f6"])

                            fig.update_layout(
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                font_color="#94a3b8",
                                margin=dict(t=20, b=20, l=20, r=20),
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass

# ── Handle pending question (from suggestion chips) ───────────────────────────
question = st.session_state.pop("pending_question", None)

# ── Chat input ────────────────────────────────────────────────────────────────
typed = st.chat_input("Ask a question about your data...")
if typed:
    question = typed

if question:
    if not os.environ.get("OPENAI_API_KEY"):
        st.warning("Please enter your OpenAI API key in the sidebar to continue.")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        st.markdown(f"<div class='user-bubble'>🧑 {question}</div>", unsafe_allow_html=True)

        with st.spinner("Analysing your data..."):
            try:
                result = ask_analytics(question)
                answer     = result["final_answer"]
                sql        = result["sql_query"]
                df         = result["dataframe"]
                chart_hint = result.get("chart_hint", "none")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sql": sql,
                    "dataframe": df,
                    "chart_hint": chart_hint,
                })
                st.rerun()
            except Exception as e:
                st.error(f"Something went wrong: {e}")
