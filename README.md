---
title: EmailAgentwithMemory
emoji: 🦀
colorFrom: green
colorTo: indigo
sdk: docker
pinned: false
license: apache-2.0
short_description: Email  ai agent project with memory.
---

# 📧 AI-Driven Email Agent 🧠

A production-grade, multi-agent system built with LangGraph and FastAPI that automates email triage, context retrieval, and drafting. This project demonstrates advanced implementation of **Long-term Memory**, **State Persistence**, and **Human-in-the-Loop Interrupts** using LangGraph's Functional API Command pattern.

---

## 🚀 Key Features

- **Advanced Learning Implementation**  
  Implemented **Semantic Memory**, **Checkpointer Persistence**, and **Functional Interrupts**, enabling the agent to maintain state and handle user feedback reliably.

- **Multi-Agent Workflow**  
  Specialized agents for:
  - Triage
  - Context Synthesis
  - Email Drafting

- **Intelligent Triage**  
  Automatically classifies emails, assigns priority, and determines if a reply is required.

- **Semantic Memory**  
  Uses `langmem` and `PostgresStore` to retrieve past interactions, allowing the agent to remember previous project details.

- **Resource Management**  
  A dedicated **Token Count Node** ensures large emails (e.g., deployment logs) are summarized before processing to optimize costs.

- **Human-in-the-Loop**  
  The graph pauses using `interrupt()` to allow users to:
  - Review drafts  
  - Approve responses  
  - Provide feedback via `Command(resume=...)`

- **Scalable Architecture**  
  Built with **FastAPI**, **Docker**, and a modular structure for enterprise-grade deployment.

---

## 🛠️ Tech Stack

- **Orchestration:** `langgraph` (Functional API), `langchain`  
- **LLM Interface:** `langchain-groq`  
- **Memory & Persistence:**  
  - `langmem`  
  - `PostgresCheckpoint`  
  - `PostgresStore` (Neon/PostgreSQL)  
- **Database ORM:** SQLAlchemy 2.0  
- **Embeddings:** `langchain_huggingface` (DistilBERT)  
- **Backend:** FastAPI + Uvicorn  
- **Configuration:** `pydantic-settings` (.env management)  
- **Authentication:** `google-auth` (Gmail API Integration)  

---

## 📂 Project Structure

```bash
app/
├── agents/             # Brains: Specialized LLM logic (Triage, Writer, Context)
├── database/           # Data: SQLAlchemy models and Connection Pooling
├── nodes/              # Workflow: Functional steps of the graph (Safety, Tokens)
├── persistance/        # Persistence: Postgres Checkpointer & Memory Store config
├── state/              # Schema: Pydantic & TypedDict state definitions
├── utils/              # Toolbox: Token counters, Embeddings, and Auth helpers
├── graph.py            # Logic: StateGraph construction and compilation
└── main.py             # Entry: FastAPI app and Controller logic



