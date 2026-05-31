import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("NEON_DATABASE_URL")

def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise e

def init_db():
    """Initializes the database by creating the required extensions and tables."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Enable pgvector extension
        logger.info("Ensuring pgvector extension is enabled...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create feedback_records table
        logger.info("Creating feedback_records table if it doesn't exist...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback_records (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                tags TEXT NOT NULL,
                embedding VECTOR(384),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes for faster search
        logger.info("Creating GIN indexes for full-text search on question and tags...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_question_fts 
            ON feedback_records USING gin(to_tsvector('english', question));
            
            CREATE INDEX IF NOT EXISTS idx_feedback_tags_fts 
            ON feedback_records USING gin(to_tsvector('english', tags));
        """)
        
        # Create evaluation_logs table
        logger.info("Creating evaluation_logs table if it doesn't exist...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS evaluation_logs (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                generated_answer TEXT NOT NULL,
                ground_truth_answer TEXT,
                retrieved_record_ids INTEGER[],
                retrieved_accuracy FLOAT DEFAULT 0.0,
                precision_k FLOAT DEFAULT 0.0,
                recall_k FLOAT DEFAULT 0.0,
                relevance_score FLOAT DEFAULT 0.0,
                correctness_score FLOAT DEFAULT 0.0,
                completeness_score FLOAT DEFAULT 0.0,
                evaluation_type VARCHAR(50) DEFAULT 'automated',
                feedback_rating INTEGER DEFAULT 0, -- 1 for helpful, -1 for unhelpful, 0 for unrated
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        logger.info("Database initialized successfully.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to initialize database: {e}")
        raise e
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_db()
