import os
import json
import logging
from groq import Groq
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Initialize Groq client
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY environment variable is not set. Groq features will fail.")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Initialize local SentenceTransformer embedding model (lazy loading)
embedding_model = None

def get_embedding_model():
    """Helper to lazily load and return the SentenceTransformer model."""
    global embedding_model
    if embedding_model is None:
        logger.info(f"Lazily loading embedding model: {EMBEDDING_MODEL_NAME}...")
        try:
            embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise e
    return embedding_model

def get_embedding(text: str) -> list[float]:
    """Generates a 384-dimensional vector embedding for the input text."""
    model = get_embedding_model()
    # Standardize string formatting
    cleaned_text = text.strip().replace("\n", " ")
    embedding = model.encode(cleaned_text)
    return embedding.tolist()

def generate_tags(question: str, answer: str) -> str:
    """
    Analyzes the Question-Answer pair and generates a comma-separated list
    of 4 to 8 relevant tags.
    """
    if not groq_client:
        logger.warning("Groq client not initialized. Returning default tags.")
        return "feedback, support, user"
        
    prompt = f"""You are a content tagging expert.

Analyze Question and Answer submissions and generate relevant descriptive tags.

Rules:
* Generate 4 to 8 tags.
* Tags should represent:
  * Topic
  * Key Concepts
  * Technical Terms
  * User Intent
* Keep tags short.
* Use lowercase.
* Return only comma-separated tags.

Question:
{question}

Answer:
{answer}

Output:"""

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=GROQ_MODEL,
            temperature=0.1,
            max_tokens=50
        )
        tags_str = response.choices[0].message.content.strip()
        # Clean response (remove prefixes if LLM hallucinated them, force lowercase)
        if ":" in tags_str:
            tags_str = tags_str.split(":")[-1]
        tags_list = [t.strip().lower() for t in tags_str.split(",") if t.strip()]
        # Truncate to between 4 and 8 tags if necessary
        if len(tags_list) > 8:
            tags_list = tags_list[:8]
        return ", ".join(tags_list)
    except Exception as e:
        logger.error(f"Error generating tags: {e}")
        # Return fallback tags based on basic word matching
        words = list(set([w.lower() for w in (question + " " + answer).split() if len(w) > 4 and w.isalnum()]))
        return ", ".join(words[:5]) if words else "general, support"

def extract_search_terms(query: str) -> str:
    """
    Extracts important keywords, intent, and short search terms from the user query.
    Returns a comma-separated string of search terms.
    """
    if not groq_client:
        # Fallback keyword extraction
        words = [w.strip(",?.!").lower() for w in query.split() if len(w) > 3]
        return ", ".join(words[:4]) if words else query
        
    prompt = f"""You are a query analysis expert.
Extract key search terms, technical concepts, and topic keywords from the user's question for a search database.
Return ONLY a comma-separated list of 2 to 5 search terms. No explanation. No sentences.

User Question: {query}

Search Terms:"""

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=GROQ_MODEL,
            temperature=0.1,
            max_tokens=40
        )
        search_terms = response.choices[0].message.content.strip()
        if ":" in search_terms:
            search_terms = search_terms.split(":")[-1]
        terms = [t.strip().lower() for t in search_terms.split(",") if t.strip()]
        return ", ".join(terms)
    except Exception as e:
        logger.error(f"Error extracting search terms: {e}")
        words = [w.strip(",?.!").lower() for w in query.split() if len(w) > 3]
        return ", ".join(words[:4]) if words else query

def synthesize_answer(question: str, retrieved_records: list[dict]) -> str:
    """
    Synthesizes a final coherent response based on retrieved QA records.
    Abides by strict context rules.
    """
    if not retrieved_records:
        return "I couldn't find relevant information in the feedback database."
        
    # If exactly one highly relevant record is found, return its answer directly
    if len(retrieved_records) == 1:
        return retrieved_records[0]["answer"]
        
    # If multiple records, format context for synthesis
    context_str = ""
    for idx, rec in enumerate(retrieved_records):
        context_str += f"Record #{idx+1} (ID: {rec['id']})\nQuestion: {rec['question']}\nAnswer: {rec['answer']}\nTags: {rec['tags']}\n\n"
        
    prompt = f"""You are a Domain-Specific Feedback RAG Chatbot.
Your primary responsibility is to answer user questions using only the information available in the retrieved records.

STRICT RULES:
1. Only answer using the retrieved records provided below.
2. Do NOT use external knowledge, guess answers, or hallucinate facts.
3. If the information is not present in the database, clearly state that the information could not be found.
4. Combine the information from the records, remove duplicate information, and produce a concise, coherent final answer.

User Question:
{question}

Retrieved Records:
{context_str}

Final Answer:"""

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=GROQ_MODEL,
            temperature=0.1,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error synthesizing answer: {e}")
        # Simple fallback combining responses
        combined = []
        for rec in retrieved_records:
            if rec["answer"] not in combined:
                combined.append(rec["answer"])
        return " ".join(combined)

def evaluate_answer_quality(question: str, generated_answer: str, ground_truth: str) -> dict:
    """
    Evaluates generated answer against the ground truth and question using Groq as LLM Judge.
    Returns relevance, correctness, and completeness scores (1-5).
    """
    default_scores = {"relevance": 1, "correctness": 1, "completeness": 1}
    
    if not groq_client:
        logger.warning("Groq client not initialized for LLM Judge. Returning default scores.")
        return default_scores
        
    prompt = f"""You are an objective LLM Judge evaluating a Feedback RAG chatbot.
Evaluate the generated answer against the user's question and the ground truth answer.
Assign integer scores from 1 to 5 for the following metrics:
1. Relevance: Is the generated answer directly relevant to the user question, without unnecessary fluff? (1 = Irrelevant, 5 = Highly Relevant)
2. Correctness: Does the generated answer accurately match the facts in the ground truth answer? (1 = Completely Incorrect/Contradictory, 5 = Completely Correct)
3. Completeness: Does the generated answer address all aspects of the user's question as described in the ground truth? (1 = Extremely Incomplete, 5 = Fully Complete)

Respond strictly in JSON format with the keys "relevance", "correctness", and "completeness" (integer values 1-5). Do not include any explanation or markdown formatting block except the JSON.

User Question: {question}
Ground Truth Answer: {ground_truth}
Generated Answer: {generated_answer}

JSON Output:"""

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model=GROQ_MODEL,
            temperature=0.1,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        # Ensure scores are between 1 and 5
        scores = {
            "relevance": max(1, min(5, int(data.get("relevance", 1)))),
            "correctness": max(1, min(5, int(data.get("correctness", 1)))),
            "completeness": max(1, min(5, int(data.get("completeness", 1))))
        }
        return scores
    except Exception as e:
        logger.error(f"Error in LLM Judge evaluation: {e}")
        return default_scores

if __name__ == "__main__":
    # Test embeddings
    logger.info("Testing embedding generation...")
    emb = get_embedding("Test question")
    logger.info(f"Generated test embedding with length: {len(emb)}")
    
    # Test tags
    logger.info("Testing tag generation...")
    tags = generate_tags("How do I update my profile photo?", "Go to settings, click avatar, upload photo.")
    logger.info(f"Generated tags: {tags}")
