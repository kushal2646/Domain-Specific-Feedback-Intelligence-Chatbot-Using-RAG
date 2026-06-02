import os
import io
import csv
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Import our backend services
from backend.database import init_db, get_db_connection
from backend.llm import generate_tags, get_embedding, synthesize_answer
from backend.retrieval import hybrid_search
from backend.evaluator import run_evaluation_batch, get_historical_evaluation_stats
from backend.seed_data import SEED_RECORDS

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize database
logger.info("Initializing database...")
try:
    init_db()
except Exception as e:
    logger.error(f"Database initialization failed: {e}")

app = FastAPI(
    title="Domain-Specific Feedback Intelligence RAG Chatbot",
    description="RAG Chatbot using Groq Llama 3, Neon PostgreSQL, and Semantic Search"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    semantic_weight: Optional[float] = 0.5
    text_weight: Optional[float] = 0.3
    tag_weight: Optional[float] = 0.2
    score_threshold: Optional[float] = 0.25

class IngestRequest(BaseModel):
    question: str
    answer: str
    tags: Optional[str] = None # If None, will auto-generate

class EditRequest(BaseModel):
    question: str
    answer: str
    tags: Optional[str] = None # If None, will auto-generate

# API Routes

@app.get("/health")
async def health_check():
    """Health check endpoint used by Railway for service status monitoring."""
    return {"status": "healthy"}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """
    Executes the RAG chatbot workflow:
    1. Extracts search terms and keywords
    2. Performs hybrid search
    3. Merges and ranks documents
    4. Synthesizes the final answer using Groq
    """
    try:
        retrieved, search_terms = hybrid_search(
            req.question,
            top_k=req.top_k,
            semantic_weight=req.semantic_weight,
            text_weight=req.text_weight,
            tag_weight=req.tag_weight,
            score_threshold=req.score_threshold
        )
        
        answer = synthesize_answer(req.question, retrieved)
        
        return {
            "question": req.question,
            "search_terms": search_terms,
            "retrieved_context": retrieved,
            "answer": answer
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest")
async def ingest(req: IngestRequest):
    """Ingests a single QA record, generating tags and embeddings automatically."""
    try:
        # 1. Generate tags if not provided
        tags = req.tags
        if not tags or not tags.strip():
            tags = generate_tags(req.question, req.answer)
        
        # Bug fix: PostgreSQL TEXT[] requires a list, not a comma-separated string
        tags_list = [t.strip() for t in tags.split(',') if t.strip()]
            
        # 2. Generate embedding
        embedding = get_embedding(req.question)
        
        # 3. Save to database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO feedback_records (question, answer, tags, embedding)
            VALUES (%s, %s, %s, %s)
            RETURNING id, question, answer, tags, created_at;
        """, (req.question, req.answer, tags_list, embedding))
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        # Normalize tags list -> comma-string for consistent JSON response
        resp_tags = ', '.join(row[3]) if isinstance(row[3], list) else (row[3] or '')
        return {
            "message": "Record ingested successfully.",
            "record": {
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "tags": resp_tags,
                "created_at": row[4]
            }
        }
    except Exception as e:
        logger.error(f"Error in ingest endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/kb/{rec_id}")
async def edit_record(rec_id: int, req: EditRequest):
    """Edits an existing QA record, regenerating tags and embeddings."""
    try:
        # 1. Generate tags if not provided
        tags = req.tags
        if not tags or not tags.strip():
            tags = generate_tags(req.question, req.answer)
        
        # Bug fix: PostgreSQL TEXT[] requires a list, not a comma-separated string
        tags_list = [t.strip() for t in tags.split(',') if t.strip()]
            
        # 2. Generate embedding
        embedding = get_embedding(req.question)
        
        # 3. Update database
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if record exists
        cur.execute("SELECT id FROM feedback_records WHERE id = %s;", (rec_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Record not found")
            
        cur.execute("""
            UPDATE feedback_records
            SET question = %s, answer = %s, tags = %s, embedding = %s
            WHERE id = %s
            RETURNING id, question, answer, tags, created_at;
        """, (req.question, req.answer, tags_list, embedding, rec_id))
        row = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        # Normalize tags list -> comma-string for consistent JSON response
        resp_tags = ', '.join(row[3]) if isinstance(row[3], list) else (row[3] or '')
        return {
            "message": "Record updated successfully.",
            "record": {
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "tags": resp_tags,
                "created_at": row[4]
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in edit endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/kb/{rec_id}")
async def delete_record(rec_id: int):
    """Deletes a record from the database."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if record exists
        cur.execute("SELECT id FROM feedback_records WHERE id = %s;", (rec_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            # Bug fix: was incorrectly returning 444 (non-standard). Correct code is 404.
            raise HTTPException(status_code=404, detail="Record not found")
            
        cur.execute("DELETE FROM feedback_records WHERE id = %s;", (rec_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        return {"message": f"Record {rec_id} deleted successfully."}
    except HTTPException as he:
        # Re-raise HTTP exceptions (e.g. 404) directly — conn/cur already closed above
        raise he
    except Exception as e:
        logger.error(f"Error in delete endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/kb")
async def list_records(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None
):
    """Lists knowledge base records with search filter and pagination."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        offset = (page - 1) * limit
        
        if search and search.strip():
            # Bug fix: tags is TEXT[] -- use array_to_string() for ILIKE compatibility
            search_param = f"%{search.strip()}%"
            cur.execute("""
                SELECT COUNT(*) FROM feedback_records
                WHERE question ILIKE %s OR array_to_string(tags, ', ') ILIKE %s;
            """, (search_param, search_param))
            total_records = cur.fetchone()[0]
            
            cur.execute("""
                SELECT id, question, answer, tags, created_at 
                FROM feedback_records
                WHERE question ILIKE %s OR array_to_string(tags, ', ') ILIKE %s
                ORDER BY id DESC
                LIMIT %s OFFSET %s;
            """, (search_param, search_param, limit, offset))
        else:
            cur.execute("SELECT COUNT(*) FROM feedback_records;")
            total_records = cur.fetchone()[0]
            
            cur.execute("""
                SELECT id, question, answer, tags, created_at 
                FROM feedback_records
                ORDER BY id DESC
                LIMIT %s OFFSET %s;
            """, (limit, offset))
            
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        records = []
        for r in rows:
            # Normalize tags: psycopg2 returns TEXT[] as list; convert to string for frontend
            tags_val = ', '.join(r[3]) if isinstance(r[3], list) else (r[3] or '')
            records.append({
                "id": r[0],
                "question": r[1],
                "answer": r[2],
                "tags": tags_val,
                "created_at": r[4]
            })
            
        return {
            "total_records": total_records,
            "page": page,
            "limit": limit,
            "total_pages": (total_records + limit - 1) // limit,
            "records": records
        }
    except Exception as e:
        logger.error(f"Error listing records: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/seed")
async def seed_database():
    """Seeds the database with 100+ default Question-Answer records."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check current count
        cur.execute("SELECT COUNT(*) FROM feedback_records;")
        count = cur.fetchone()[0]
        
        # We will seed records that do not already exist (based on question text match)
        cur.execute("SELECT question FROM feedback_records;")
        existing_questions = set([r[0] for r in cur.fetchall()])
        
        seeded_count = 0
        skipped_count = 0
        
        for idx, rec in enumerate(SEED_RECORDS):
            question = rec["question"]
            answer = rec["answer"]
            
            if question in existing_questions:
                skipped_count += 1
                continue
                
            # 1. Generate tags (fallback to local tags if Groq fails or rate-limits)
            try:
                tags = generate_tags(question, answer)
            except Exception as tags_err:
                logger.warning(f"Failed to generate tags for row {idx}: {tags_err}")
                tags = "seeding, feedback, support"
            
            # Bug fix: convert comma-string to list for TEXT[] column
            tags_list = [t.strip() for t in tags.split(',') if t.strip()]
                
            # 2. Generate embedding
            try:
                embedding = get_embedding(question)
            except Exception as emb_err:
                logger.error(f"Failed to generate embedding for row {idx}: {emb_err}")
                embedding = None
                
            # 3. Insert record
            cur.execute("""
                INSERT INTO feedback_records (question, answer, tags, embedding)
                VALUES (%s, %s, %s, %s);
            """, (question, answer, tags_list, embedding))
            seeded_count += 1
            
            # Commit periodically
            if seeded_count % 10 == 0:
                conn.commit()
                logger.info(f"Seeded {seeded_count} records so far...")
                
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "message": "Seeding operation complete.",
            "seeded_count": seeded_count,
            "skipped_count": skipped_count,
            "total_count": count + seeded_count
        }
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Uploads a CSV of QA pairs, generates tags and embeddings, and stores them."""
    try:
        content = await file.read()
        csv_file = io.StringIO(content.decode("utf-8"))
        reader = csv.DictReader(csv_file)
        
        # Verify columns
        if not reader.fieldnames or "question" not in reader.fieldnames or "answer" not in reader.fieldnames:
            raise HTTPException(
                status_code=400, 
                detail="CSV must contain 'question' and 'answer' headers."
            )
            
        conn = get_db_connection()
        cur = conn.cursor()
        
        inserted_count = 0
        for row in reader:
            question = row.get("question")
            answer = row.get("answer")
            
            if not question or not answer:
                continue
                
            # Generate or extract tags
            tags = row.get("tags")
            if not tags or not tags.strip():
                tags = generate_tags(question, answer)
            # Bug fix: convert comma-string to list for TEXT[] column
            tags_list = [t.strip() for t in tags.split(',') if t.strip()]
            # Generate embedding
            embedding = get_embedding(question)
            
            cur.execute("""
                INSERT INTO feedback_records (question, answer, tags, embedding)
                VALUES (%s, %s, %s, %s);
            """, (question, answer, tags_list, embedding))
            inserted_count += 1
            
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "message": "CSV upload complete.",
            "records_inserted": inserted_count
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error uploading CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluation/run")
async def run_evaluation(top_k: int = Query(3, ge=1, le=10)):
    """Triggers a batch evaluation session and returns the metrics."""
    try:
        eval_results = run_evaluation_batch(top_k=top_k)
        return eval_results
    except Exception as e:
        logger.error(f"Error running evaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evaluation/stats")
async def evaluation_stats():
    """Gets historical evaluation statistics."""
    try:
        stats = get_historical_evaluation_stats()
        return stats
    except Exception as e:
        logger.error(f"Error fetching evaluation stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evaluation")
async def evaluation_stats_alias():
    """Alias for getting historical evaluation stats to satisfy GET /api/evaluation."""
    try:
        stats = get_historical_evaluation_stats()
        return stats
    except Exception as e:
        logger.error(f"Error fetching evaluation stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset")
async def reset_database():
    """Wipes all knowledge base records and evaluation logs."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE feedback_records RESTART IDENTITY CASCADE;")
        cur.execute("TRUNCATE TABLE evaluation_logs RESTART IDENTITY CASCADE;")
        conn.commit()
        cur.close()
        conn.close()
        return {"message": "Database wiped successfully. Ready for fresh seeding."}
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve static frontend files
# Create static directory structures if they don't exist
os.makedirs("frontend/static", exist_ok=True)

# Mount the static files directory
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/")
async def get_index():
    return FileResponse("frontend/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
