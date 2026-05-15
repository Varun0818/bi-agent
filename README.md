# Autonomous Business Intelligence Agent

> Ask business questions in plain English. Get SQL, insights, and charts instantly.

[![Backend](https://img.shields.io/badge/backend-FastAPI-009688)](https://fastapi.tiangolo.com)
[![Orchestration](https://img.shields.io/badge/orchestration-LangGraph-1D9E75)](https://langchain-ai.github.io/langgraph)
[![LLM](https://img.shields.io/badge/LLM-Groq%20Llama--3.3-orange)](https://groq.com)
[![Frontend](https://img.shields.io/badge/frontend-React%2018-61DAFB)](https://react.dev)

## What It Does

The BI Agent accepts natural language business questions and autonomously writes,
validates, and — if necessary — self-corrects SQL queries against a retail analytics
database. It generates business insights, renders interactive charts, and exposes
every reasoning step through a trace viewer.

**Example:** _"Show monthly revenue by region for the last 12 months"_
→ Schema retrieval → SQL generation → Validation → Execution → Insights + Chart

## Live Demo

- Frontend: [your-app.vercel.app](https://your-app.vercel.app)
- Backend API: [your-backend.onrender.com/docs](https://your-backend.onrender.com/docs)

## Architecture
