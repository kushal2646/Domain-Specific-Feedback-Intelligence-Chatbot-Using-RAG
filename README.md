# Design and Development of a Domain-Specific Feedback Intelligence RAG Chatbot Using Groq LLM, Neon PostgreSQL, and Semantic Search

An advanced, production-ready, domain-specific RAG (Retrieval-Augmented Generation) Chatbot designed to process, search, and analyze customer feedback records. Powered by Groq's Llama 3 LLM, Neon PostgreSQL (with `pgvector` for semantic search), and a local Sentence-Transformers embedding model.

---

## 🚀 Key Features

* **Hybrid Retrieval System**: Combines pgvector Cosine Distance semantic similarity (50% weight), question keyword index search (30% weight), and tag keyword search (20% weight) with customizable parameter tuning.
* **Automatic Content Tagging**: Analyzes question-answer inputs upon ingestion and uses Groq Llama 3 to generate 4-8 lowercase descriptive tags representing topics, intents, and technical terms.
* **LLM-as-a-Judge Evaluation Dashboard**: Automatically benchmarks RAG response quality (Relevance, Correctness, Completeness) on a scale of 1-5 using Llama 3 as an objective judge, side-by-side with standard search metrics (Retrieval Accuracy, Precision@K, Recall@K).
* **SPA Dashboard Interface**: Built with raw HTML5, CSS3, and JavaScript, featuring a premium glassmorphic dark theme, active RAG trace inspectors, knowledge base editor grid, and interactive Chart.js analytics.
* **Streamlit Dashboard**: Includes a complete `streamlit_app.py` for direct deployment compatibility with Streamlit Cloud.

---

## 🛠️ Technology Stack

* **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism, Dark Theme, HSL Color System), Vanilla JavaScript, Chart.js
* **Backend**: FastAPI (Python), Uvicorn Server
* **Database**: Neon PostgreSQL (Serverless)
* **Vector Engine**: `pgvector` (384-dimensional cosine metrics)
* **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (Local generation)
* **LLM**: Groq Cloud API (`llama-3.3-70b-versatile`)

---

## 📂 Project Architecture

```text
├── backend/
│   ├── database.py      # PostgreSQL connections & DDL tables init
│   ├── llm.py           # Groq client integration & embedding generation
│   ├── retrieval.py     # Hybrid search fusion ranking algorithm
│   ├── evaluator.py     # Batch evaluation & LLM-as-a-judge scoring
│   ├── seed_data.py     # 100+ default QA feedback records list
│   └── main.py          # FastAPI application server & routing
├── frontend/
│   └── static/
│       ├── index.html   # Main Dashboard SPA UI
│       ├── style.css    # Premium glassmorphic stylesheets
│       └── app.js       # Client state, event bindings & charts
├── requirements.txt     # Python package dependencies
├── render.yaml          # Render blueprint for one-click web deploy
├── streamlit_app.py     # Streamlit app script for Streamlit Cloud
└── .gitignore           # Ignored folders and local secrets (.env)
```

---

## ⚙️ Local Setup Instructions

### 1. Prerequisite Installations
Ensure you have **Python 3.10+** and **Pip** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/kushal2646/Domain-Specific-Feedback-Intelligence-Chatbot-Using-RAG.git
cd Domain-Specific-Feedback-Intelligence-Chatbot-Using-RAG
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Secrets
Create a `.env` file in the root directory and input your credentials:
```env
GROQ_API_KEY=your_groq_api_key_here
NEON_DATABASE_URL=postgresql://your_neon_db_connection_url_here?sslmode=require
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
```

### 5. Launch the Server
Start the FastAPI server:
```bash
python -m backend.main
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser to interact with the dashboard.

*To run the Streamlit version instead:*
```bash
streamlit run streamlit_app.py
```

---

## 🚀 Deployment Instructions

### Option A: Render (FastAPI Server + Frontend)
This project includes a **[render.yaml](render.yaml)** Blueprint. 
1. Log in to [Render](https://dashboard.render.com/) and connect your GitHub account.
2. Select **Blueprint** (Infrastructure as Code).
3. Connect your repository and supply the required secrets (`GROQ_API_KEY`, `NEON_DATABASE_URL`).
4. Click **Approve**. Render will deploy your service automatically.

### Option B: Streamlit Cloud (Streamlit Dashboard)
1. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Create a new app linked to your GitHub repo, pointing the main file path to `streamlit_app.py`.
3. Open **Advanced Settings** and add your environment secrets under the **Secrets** textarea in TOML format:
   ```toml
   GROQ_API_KEY = "gsk_..."
   NEON_DATABASE_URL = "postgresql://..."
   GROQ_MODEL = "llama-3.3-70b-versatile"
   EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
   EMBEDDING_DIMENSION = 384
   ```
4. Click **Deploy**.
