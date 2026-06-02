# 🧠 Domain-Specific Feedback Intelligence RAG Chatbot

A **production-ready, enterprise-grade** Retrieval-Augmented Generation (RAG) chatbot that automates customer support feedback analysis using a verified Feedback Knowledge Base. Built with Groq Llama 3, Neon PostgreSQL, pgvector, and deployed on Railway.

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    User([User Question]) --> ChatRoute[FastAPI /api/chat]
    ChatRoute --> ExtTerms[Extract Search Terms <br> Groq Llama 3]
    ChatRoute --> Embed[Generate Embedding <br> MiniLM-L6-v2]
    
    ExtTerms --> TextSearch[Question Text Search <br> ILIKE]
    ExtTerms --> TagSearch[Tag Array Search <br> array_to_string ILIKE]
    Embed --> SemanticSearch[Semantic Vector Search <br> pgvector Cosine]
    
    TextSearch --> Merge[Merge & Rerank <br> Weighted Score]
    TagSearch --> Merge
    SemanticSearch --> Merge
    
    Merge --> Filter[Relevance Threshold Filter]
    Filter --> Synth[Answer Synthesis <br> Groq Llama 3]
    Synth --> Response([Final Synthesized Answer])
```

---

## 🔧 Tech Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend** | HTML5, Vanilla CSS, JavaScript SPA | Dark glassmorphism, responsive interface. |
| **Backend** | FastAPI (Python) | High-performance asynchronous API framework. |
| **Database** | Neon PostgreSQL | Serverless cloud PostgreSQL database. |
| **Vector Search** | pgvector extension | Custom indices for multidimensional vector search. |
| **Embeddings** | `all-MiniLM-L6-v2` | local 384-dimensional vector embedding model. |
| **LLM Inference** | Groq Cloud API | Llama 3.3-70b-versatile for fast synthesis. |
| **Deployment** | Railway | Continuous deployment using NIXPACKS build system. |

---

## 📁 Project Structure

```
├── backend/
│   ├── __init__.py          # Python package marker
│   ├── main.py              # FastAPI app & all API routes
│   ├── database.py          # PostgreSQL init & connection
│   ├── llm.py               # Groq tag generation, embeddings, synthesis
│   ├── retrieval.py         # Hybrid search logic
│   ├── evaluator.py         # Batch evaluation + LLM Judge
│   └── seed_data.py         # 100 Q&A seed records
├── frontend/
│   └── static/
│       ├── index.html       # Single-page app (4 views)
│       ├── style.css        # Dark glassmorphism theme with media queries
│       └── app.js           # All frontend logic
├── .env                     # Local env vars (not committed)
├── .gitignore
├── railway.json             # Railway deployment config
├── requirements.txt
└── README.md
```

---

## 🗄️ Database Schema

```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Main knowledge base table
CREATE TABLE feedback_records (
    id          SERIAL PRIMARY KEY,
    question    TEXT NOT NULL,
    answer      TEXT NOT NULL,
    tags        TEXT[],                      -- Array of auto-generated tags
    embedding   VECTOR(384),                 -- all-MiniLM-L6-v2 embedding
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Evaluation logs
CREATE TABLE evaluation_logs (
    id                   SERIAL PRIMARY KEY,
    question             TEXT NOT NULL,
    generated_answer     TEXT NOT NULL,
    ground_truth_answer  TEXT,
    retrieved_record_ids INTEGER[],
    retrieved_accuracy   FLOAT DEFAULT 0.0,
    precision_k          FLOAT DEFAULT 0.0,
    recall_k             FLOAT DEFAULT 0.0,
    average_similarity   FLOAT DEFAULT 0.0,
    relevance_score      FLOAT DEFAULT 0.0,
    correctness_score    FLOAT DEFAULT 0.0,
    completeness_score   FLOAT DEFAULT 0.0,
    evaluation_type      VARCHAR(50) DEFAULT 'automated',
    feedback_rating      INTEGER DEFAULT 0,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 Setup Instructions

### 1. Prerequisites

* Python 3.10+
* Git
* A serverless PostgreSQL instance (Neon)
* A Groq developer account

### 2. Clone & Install

```bash
git clone <your-repo-url>
cd "Domain-Specific Feedback Intelligence Chatbot Using RAG"

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python -m uvicorn backend.main:app --port 8000 --reload
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_groq_key_here
NEON_DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## ⚡ Neon PostgreSQL Setup

1. Go to [Neon console](https://console.neon.tech/) and create a new project.
2. Select your preferred AWS region and configure database sizing.
3. Retrieve your connection string `postgresql://...` from the Neon dashboard. Ensure `sslmode=require` is appended.
4. Run `init_db()` locally or trigger `/api/seed` to automatically enable `pgvector` and construct all tables and schema indices.

---

## 🤖 Groq Setup

1. Sign up on [Groq Console](https://console.groq.com/).
2. Create an API Key in the **API Keys** section.
3. Copy the key to your `.env` as `GROQ_API_KEY`.
4. The system is preset to use `llama-3.3-70b-versatile` for synthesis and query parsing, which offers high speed and context understanding.

---

## 🚂 Railway Deployment

1. Create a **New Project** on [Railway](https://railway.app/).
2. Click **Deploy from GitHub repo** and connect your repository.
3. Add the following **Variables** in your project settings:
   * `GROQ_API_KEY`
   * `NEON_DATABASE_URL`
   * `GROQ_MODEL` (e.g., `llama-3.3-70b-versatile`)
   * `EMBEDDING_MODEL` (`sentence-transformers/all-MiniLM-L6-v2`)
4. Railway automatically detects the `railway.json` file and builds the Nixpacks container:
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": { "builder": "NIXPACKS" },
     "deploy": {
       "startCommand": "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
     }
   }
   ```
5. Deployments trigger automatically on every branch push.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check - returns `{"status": "healthy"}` |
| `POST` | `/api/chat` | RAG chat - hybrid retrieval + answer synthesis |
| `GET` | `/api/kb` | List knowledge base (paginated, searchable) |
| `POST` | `/api/ingest` | Add a single Q&A record |
| `PUT` | `/api/kb/{id}` | Edit a record |
| `DELETE` | `/api/kb/{id}` | Delete a record |
| `POST` | `/api/seed` | Seed 100+ default records |
| `POST` | `/api/upload` | Upload CSV of Q&A pairs |
| `POST` | `/api/reset` | Wipe all tables |
| `POST` | `/api/evaluation/run` | Run batch evaluation (LLM Judge) |
| `GET` | `/api/evaluation/stats` | Get historical evaluation stats |
| `GET` | `/api/evaluation` | Alias for getting historical evaluation stats |

---

## 📊 Evaluation Metrics

| Metric | Code Key | Description |
|---|---|---|
| **Retrieval Accuracy** | `retrieval_accuracy` | % of queries where the target document was retrieved. |
| **Precision @ K** | `precision_at_k` | Fraction of retrieved documents that are relevant. |
| **Recall @ K** | `recall_at_k` | Fraction of relevant documents successfully retrieved. |
| **Avg Similarity** | `average_similarity` | Mean cosine similarity of context documents. |
| **Answer Relevance** | `relevance` | LLM Judge score 1–5: evaluates if answer is on-topic. |
| **Answer Correctness** | `correctness` | LLM Judge score 1–5: checks factual alignment with database. |
| **Answer Completeness** | `completeness` | LLM Judge score 1–5: check details covered. |

---

## 📸 Screenshots Section

### 1. Intelligence Chat Screen
Offers custom parameters (Top K, Similarity threshold, semantic/text/tag weights) with interactive chat logs and an accordion trace panel detailing the RAG pipeline execution (search terms generated, matched records with scores and tags).

### 2. Feedback Knowledge Base Screen
A clean paginated tabular representation of all customer QA records in the database. Supports inline tag badges, text searching on tags/questions, and quick editing or deletion.

### 3. Administration & Ingestion Screen
Provides interfaces to add QA records individually, import files via drag-and-drop CSV uploads, seed default dataset, or wipe the PostgreSQL database.

### 4. Evaluation Dashboard Screen
Consolidates system performance metrics with radar and bar charts powered by Chart.js, rendering retrieval success and LLM Judge quality scores along with tabular details of evaluation runs.
