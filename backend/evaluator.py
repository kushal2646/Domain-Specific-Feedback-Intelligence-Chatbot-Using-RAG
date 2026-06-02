import logging
from backend.database import get_db_connection
from backend.retrieval import hybrid_search
from backend.llm import synthesize_answer, evaluate_answer_quality

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Representative test suite for evaluation.
# We will match the test questions to the seeded records by their text to find their real database IDs.
TEST_SUITE = [
    {
        "test_query": "How do I reset my user account password?",
        "ground_truth_question": "How can I reset my account password?",
        "ground_truth_answer": "Click 'Forgot Password' on the login screen, enter your email address, and follow the instructions sent to your inbox to set a new password."
    },
    {
        "test_query": "What is your refund policy for annual subscriptions?",
        "ground_truth_question": "What is your subscription refund policy?",
        "ground_truth_answer": "We offer a full refund within 14 days of purchase for both monthly and annual subscriptions. To request a refund, please contact billing support."
    },
    {
        "test_query": "Does the system support MFA or two-factor auth?",
        "ground_truth_question": "Does the app support Multi-Factor Authentication (MFA)?",
        "ground_truth_answer": "Yes, you can enable Multi-Factor Authentication (MFA) in your Account Settings under the Security tab. We support Google Authenticator, Authy, and SMS."
    },
    {
        "test_query": "I am getting a 429 rate limit exceeded error on the API",
        "ground_truth_question": "What are the API rate limits?",
        "ground_truth_answer": "Our standard API rate limit is 100 requests per minute per API key. If you exceed this limit, you will receive a HTTP 429 Too Many Requests response."
    },
    {
        "test_query": "Where can I configure a webhook url?",
        "ground_truth_question": "How do I set up webhooks?",
        "ground_truth_answer": "Go to the Developer Console, click on 'Webhooks', select 'Add Webhook', and enter your payload URL and the events you want to listen to."
    },
    {
        "test_query": "How do I invite team members to my workspace?",
        "ground_truth_question": "How do I invite team members to my organization?",
        "ground_truth_answer": "Go to Organization Settings, click on the 'Members' tab, select 'Invite Member', enter their email address, select their role, and click 'Send Invite'."
    },
    {
        "test_query": "Can I export data as CSV?",
        "ground_truth_question": "How can I export my account data?",
        "ground_truth_answer": "You can export all workspace data as a CSV or JSON file from the Workspace settings page under the 'Export Data' section."
    },
    {
        "test_query": "Is there a dark mode in the dashboard?",
        "ground_truth_question": "How do I enable dark mode?",
        "ground_truth_answer": "Click on your profile avatar in the top right corner, select 'Theme Preferences', and toggle the setting to 'Dark Mode'."
    },
    {
        "test_query": "My billing page is showing a blank screen",
        "ground_truth_question": "Why is the billing dashboard showing a blank screen?",
        "ground_truth_answer": "This is typically caused by active ad-blockers blocking our payment gateway scripts (Stripe). Please temporarily disable ad-blockers and refresh the page."
    },
    {
        "test_query": "Is my data encrypted?",
        "ground_truth_question": "How is customer data secured?",
        "ground_truth_answer": "All customer data is encrypted in transit using TLS 1.3 and at rest using AES-256 encryption. We also maintain SOC 2 Type II compliance."
    }
]

def find_ground_truth_ids(conn) -> dict:
    """Finds and maps ground truth questions in TEST_SUITE to their actual database IDs."""
    mapping = {}
    cur = conn.cursor()
    try:
        for item in TEST_SUITE:
            q_text = item["ground_truth_question"]
            cur.execute("SELECT id FROM feedback_records WHERE question = %s LIMIT 1;", (q_text,))
            row = cur.fetchone()
            if row:
                mapping[q_text] = row[0]
            else:
                # Fallback to loose matching if exact match not found
                cur.execute("SELECT id FROM feedback_records WHERE question ILIKE %s LIMIT 1;", (f"%{q_text[:30]}%",))
                fallback_row = cur.fetchone()
                if fallback_row:
                    mapping[q_text] = fallback_row[0]
    except Exception as e:
        logger.error(f"Error mapping ground truth IDs: {e}")
    finally:
        cur.close()
    return mapping

def run_evaluation_batch(top_k: int = 3) -> dict:
    """
    Runs a batch evaluation of the test suite.
    Computes retrieval and generation metrics and saves logs to the database.
    """
    logger.info("Starting batch evaluation...")
    conn = get_db_connection()
    
    # 1. Map questions to actual database IDs
    gt_id_map = find_ground_truth_ids(conn)
    logger.info(f"Mapped {len(gt_id_map)} ground truth IDs: {gt_id_map}")
    
    results = []
    
    # Track totals for averages
    total_relevance = 0.0
    total_correctness = 0.0
    total_completeness = 0.0
    total_accuracy = 0.0
    total_precision = 0.0
    total_recall = 0.0
    total_similarity = 0.0
    
    valid_evals = 0
    
    for item in TEST_SUITE:
        test_query = item["test_query"]
        gt_question = item["ground_truth_question"]
        gt_answer = item["ground_truth_answer"]
        gt_id = gt_id_map.get(gt_question)
        
        if not gt_id:
            logger.warning(f"Could not find database record for ground truth: '{gt_question}'. Skipping from metric computation.")
            continue
            
        # Run hybrid retrieval
        retrieved, search_terms = hybrid_search(test_query, top_k=top_k)
        retrieved_ids = [r["id"] for r in retrieved]
        
        # Calculate retrieval metrics
        # Retrieval Accuracy: Is ground truth document in the retrieved set?
        retrieved_accuracy = 1.0 if gt_id in retrieved_ids else 0.0
        
        # Precision@K: Relevant retrieved / K. In our single document case:
        precision_k = (1.0 if gt_id in retrieved_ids else 0.0) / top_k
        
        # Recall@K: Relevant retrieved / Total relevant. In our case:
        recall_k = 1.0 if gt_id in retrieved_ids else 0.0
        
        # Average similarity score of retrieved items
        avg_sim = sum([r["semantic_score"] for r in retrieved]) / len(retrieved) if retrieved else 0.0
        
        # Run synthesis
        generated_ans = synthesize_answer(test_query, retrieved)
        
        # Run LLM-as-a-judge if matching records were found, otherwise generation will output the fallback
        if retrieved:
            scores = evaluate_answer_quality(test_query, generated_ans, gt_answer)
        else:
            scores = {"relevance": 1.0, "correctness": 1.0, "completeness": 1.0}
            
        relevance = float(scores["relevance"])
        correctness = float(scores["correctness"])
        completeness = float(scores["completeness"])
        
        # Save to database log
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO evaluation_logs 
                (question, generated_answer, ground_truth_answer, retrieved_record_ids, 
                 retrieved_accuracy, precision_k, recall_k, average_similarity, relevance_score, 
                 correctness_score, completeness_score, evaluation_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'automated')
                RETURNING id;
            """, (test_query, generated_ans, gt_answer, retrieved_ids, 
                  retrieved_accuracy, precision_k, recall_k, avg_sim, relevance, 
                  correctness, completeness))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save evaluation log: {e}")
        finally:
            cur.close()
            
        # Accumulate metrics
        total_accuracy += retrieved_accuracy
        total_precision += precision_k
        total_recall += recall_k
        total_similarity += avg_sim
        total_relevance += relevance
        total_correctness += correctness
        total_completeness += completeness
        valid_evals += 1
        
        results.append({
            "question": test_query,
            "generated_answer": generated_ans,
            "ground_truth_answer": gt_answer,
            "retrieved_ids": retrieved_ids,
            "retrieved_accuracy": retrieved_accuracy,
            "precision_k": precision_k,
            "precision_at_k": precision_k,
            "recall_k": recall_k,
            "recall_at_k": recall_k,
            "relevance": relevance,
            "correctness": correctness,
            "completeness": completeness,
            "average_similarity": round(avg_sim, 4),
            "avg_similarity": round(avg_sim, 4)
        })
        
    conn.close()
    
    # Calculate averages
    avg_metrics = {
        "retrieved_count": valid_evals,
        "retrieval_accuracy": round(total_accuracy / valid_evals, 4) if valid_evals else 0.0,
        "precision_k": round(total_precision / valid_evals, 4) if valid_evals else 0.0,
        "precision_at_k": round(total_precision / valid_evals, 4) if valid_evals else 0.0,
        "recall_k": round(total_recall / valid_evals, 4) if valid_evals else 0.0,
        "recall_at_k": round(total_recall / valid_evals, 4) if valid_evals else 0.0,
        "average_similarity": round(total_similarity / valid_evals, 4) if valid_evals else 0.0,
        "relevance": round(total_relevance / valid_evals, 4) if valid_evals else 0.0,
        "correctness": round(total_correctness / valid_evals, 4) if valid_evals else 0.0,
        "completeness": round(total_completeness / valid_evals, 4) if valid_evals else 0.0,
        # Retain old keys for compatibility
        "answer_relevance": round(total_relevance / valid_evals, 4) if valid_evals else 0.0,
        "answer_correctness": round(total_correctness / valid_evals, 4) if valid_evals else 0.0,
        "answer_completeness": round(total_completeness / valid_evals, 4) if valid_evals else 0.0
    }
    
    logger.info(f"Evaluation complete. Summary metrics: {avg_metrics}")
    return {
        "summary": avg_metrics,
        "details": results
    }
 
def get_historical_evaluation_stats() -> dict:
    """Retrieves aggregated evaluation logs stats from database."""
    conn = get_db_connection()
    cur = conn.cursor()
    stats = {}
    try:
        cur.execute("""
            SELECT 
                COUNT(*) as total_runs,
                AVG(retrieved_accuracy) as avg_accuracy,
                AVG(precision_k) as avg_precision,
                AVG(recall_k) as avg_recall,
                AVG(average_similarity) as avg_similarity,
                AVG(relevance_score) as avg_relevance,
                AVG(correctness_score) as avg_correctness,
                AVG(completeness_score) as avg_completeness
            FROM evaluation_logs;
        """)
        row = cur.fetchone()
        if row and row[0] > 0:
            stats = {
                "total_runs": row[0],
                "retrieval_accuracy": round(float(row[1]), 4) if row[1] is not None else 0.0,
                "precision_at_k": round(float(row[2]), 4) if row[2] is not None else 0.0,
                "recall_at_k": round(float(row[3]), 4) if row[3] is not None else 0.0,
                "average_similarity": round(float(row[4]), 4) if row[4] is not None else 0.0,
                "relevance": round(float(row[5]), 4) if row[5] is not None else 0.0,
                "correctness": round(float(row[6]), 4) if row[6] is not None else 0.0,
                "completeness": round(float(row[7]), 4) if row[7] is not None else 0.0,
                # Retain old keys for safety
                "precision_k": round(float(row[2]), 4) if row[2] is not None else 0.0,
                "recall_k": round(float(row[3]), 4) if row[3] is not None else 0.0,
                "answer_relevance": round(float(row[5]), 4) if row[5] is not None else 0.0,
                "answer_correctness": round(float(row[6]), 4) if row[6] is not None else 0.0,
                "answer_completeness": round(float(row[7]), 4) if row[7] is not None else 0.0
            }
        else:
            stats = {
                "total_runs": 0,
                "retrieval_accuracy": 0.0,
                "precision_at_k": 0.0,
                "recall_at_k": 0.0,
                "average_similarity": 0.0,
                "relevance": 0.0,
                "correctness": 0.0,
                "completeness": 0.0,
                # Retain old keys for safety
                "precision_k": 0.0,
                "recall_k": 0.0,
                "answer_relevance": 0.0,
                "answer_correctness": 0.0,
                "answer_completeness": 0.0
            }
    except Exception as e:
        logger.error(f"Error fetching historical stats: {e}")
    finally:
        cur.close()
        conn.close()
    return stats
