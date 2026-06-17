# 📊 AI-Powered Analytics Assistant

An intelligent data analytics assistant that lets you query an e-commerce database using plain English — no SQL required. Built with GPT-4o, LangGraph, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red) ![LangGraph](https://img.shields.io/badge/LangGraph-0.1-green) ![OpenAI](https://img.shields.io/badge/GPT--4o-OpenAI-black)

---

## 🎯 What it does

Ask business questions in plain English. The agent:
1. **Understands** your question using GPT-4o
2. **Generates** the correct SQL query automatically
3. **Executes** it against the database
4. **Explains** the results in clear business language
5. **Visualises** the data with the right chart type

**Example questions you can ask:**
- *"What are the top 5 products by revenue?"*
- *"Which region has the highest refund rate?"*
- *"Show me monthly revenue trend for the last 6 months"*
- *"Who are the top 10 customers by total spend?"*
- *"Which sales channel drives the most orders?"*

---

## 🏗 Architecture

```
User Question
     │
     ▼
┌─────────────────────────────────────────┐
│           LangGraph Agent               │
│                                         │
│  fetch_schema → generate_sql →          │
│  execute_query → generate_answer        │
└─────────────────────────────────────────┘
     │
     ▼
Streamlit UI (chat + table + chart)
```

**Tech Stack:**
- **LangGraph** — multi-step agent orchestration
- **GPT-4o** — natural language → SQL + answer generation
- **SQLite** — bundled e-commerce database (no setup needed)
- **Streamlit** — interactive chat UI
- **Plotly** — dynamic charts (bar, line, pie — auto-selected)

---

## 🗄 Dataset

Bundled sample e-commerce database with:
- **1,000 orders** across 365 days
- **200 customers** across 5 regions
- **10 products** in 5 categories
- **3 sales channels** (Online, In-Store, Mobile App)

Tables: `orders`, `products`, `customers`

---

## 🚀 Run locally

```bash
git clone https://github.com/shaikhsuhana/ai-analytics-assistant
cd ai-analytics-assistant

pip install -r requirements.txt

cp .env.example .env
# Add your OpenAI API key to .env

streamlit run app.py
```

---

## ☁️ Deploy on Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select this repo, set `app.py` as the main file
4. Under **Advanced settings → Secrets**, add:
   ```
   OPENAI_API_KEY = "sk-..."
   ```
5. Click **Deploy**

---

## 💡 Key skills demonstrated

| Skill | Implementation |
|---|---|
| AI Agent Design | LangGraph multi-node pipeline |
| Prompt Engineering | Schema-aware SQL generation, structured output parsing |
| Data Analytics | SQL aggregations, trend analysis, business insights |
| Data Visualisation | Auto-selected Plotly charts based on query type |
| Full-Stack | End-to-end from DB to UI |

---

## 👩‍💻 Author

**Suhana Shaikh** · [GitHub](https://github.com/shaikhsuhana) · [Portfolio](https://shaikhsuhana.github.io/suhana-portfolio)
