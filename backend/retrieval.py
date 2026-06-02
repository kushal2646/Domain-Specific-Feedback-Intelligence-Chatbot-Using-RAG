import logging
from backend.database import get_db_connection
from backend.llm import get_embedding, extract_search_terms

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def hybrid_search(query: str, top_k: int = 5, semantic_weight: float = 0.5, text_weight: float = 0.3, tag_weight: float = 0.2, score_threshold: float = 0.25) -> list[dict]:
    """
    Performs hybrid search combining:
    1. Question Search (keyword match on question)
    2. Tag Search (keyword match on tags)
    3. Semantic Vector Search (pgvector cosine similarity)
    
    Ranks the combined results by a weighted relevance score.
    """
    logger.info(f"Starting hybrid search for query: '{query}'")
    
    # 1. Extract search terms from query
    search_terms_str = extract_search_terms(query)
    search_terms = [t.strip().lower() for t in search_terms_str.split(",") if t.strip()]
    logger.info(f"Extracted search terms: {search_terms}")
    
    # 2. Generate embedding for query
    try:
        query_vector = get_embedding(query)
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        query_vector = None
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Dictionary to hold merged results: { record_id: record_dict }
    merged_results = {}
    
    try:
        # A. Semantic Search (pgvector)
        semantic_matches = []
        if query_vector:
            # Cosine similarity is 1 - (v1 <=> v2)
            cur.execute("""
                SELECT id, question, answer, tags, (1.0 - (embedding <=> %s::vector)) AS similarity
                FROM feedback_records
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """, (query_vector, query_vector, top_k * 2))
            
            rows = cur.fetchall()
            for r in rows:
                rec_id, question, answer, tags, similarity = r
                # PostgreSQL might return similarity as None if vector is null
                sim_val = float(similarity) if similarity is not None else 0.0
                semantic_matches.append({
                    "id": rec_id,
                    "question": question,
                    "answer": answer,
                    "tags": tags,
                    "semantic_score": sim_val
                })
                
        # B. Text & Tag Search (using search terms)
        keyword_matches = []
        if search_terms:
            # Construct ILIKE conditions
            q_conditions = []
            t_conditions = []
            params = []
            
            for term in search_terms:
                q_conditions.append("question ILIKE %s")
                # Bug fix: tags is TEXT[] -- must cast to text for ILIKE
                t_conditions.append("array_to_string(tags, ', ') ILIKE %s")
                # Wrap with wildcards
                params.append(f"%{term}%")
                
            # We fetch records matching any of the terms
            where_clause = " OR ".join(q_conditions + t_conditions)
            query_sql = f"""
                SELECT id, question, answer, tags
                FROM feedback_records
                WHERE {where_clause}
                LIMIT {top_k * 2};
            """
            cur.execute(query_sql, params + params)
            rows = cur.fetchall()
            for r in rows:
                rec_id, question, answer, tags = r
                keyword_matches.append({
                    "id": rec_id,
                    "question": question,
                    "answer": answer,
                    "tags": tags
                })
                
        # Merge results and calculate scores
        # We process all records found in either search
        all_record_ids = set([r["id"] for r in semantic_matches] + [r["id"] for r in keyword_matches])
        
        # Build map for fast lookup
        semantic_map = {r["id"]: r for r in semantic_matches}
        keyword_map = {r["id"]: r for r in keyword_matches}
        
        for rec_id in all_record_ids:
            # Get base info
            ref_rec = semantic_map.get(rec_id) or keyword_map.get(rec_id)
            question = ref_rec["question"]
            answer = ref_rec["answer"]
            tags = ref_rec["tags"]
            
            # 1. Semantic score (defaults to 0.0 if not in top vector matches)
            semantic_score = semantic_map.get(rec_id, {}).get("semantic_score", 0.0)
            
            # 2. Text score (percentage of search terms found in question)
            text_matches = 0
            for term in search_terms:
                if term in question.lower():
                    text_matches += 1
            text_score = text_matches / len(search_terms) if search_terms else 0.0
            
            # 3. Tag score (percentage of search terms found in tags)
            # Bug fix: psycopg2 returns TEXT[] as a Python list; handle both list and str
            if isinstance(tags, list):
                tags_text = ", ".join(tags).lower()
            else:
                tags_text = str(tags).lower()
            tag_matches = 0
            for term in search_terms:
                if term in tags_text:
                    tag_matches += 1
            tag_score = tag_matches / len(search_terms) if search_terms else 0.0
            
            # Combined Relevance Score
            relevance_score = (
                semantic_weight * semantic_score +
                text_weight * text_score +
                tag_weight * tag_score
            )
            
            merged_results[rec_id] = {
                "id": rec_id,
                "question": question,
                "answer": answer,
                # Normalize tags: always return as comma-separated string for JSON
                "tags": ', '.join(tags) if isinstance(tags, list) else (tags or ''),
                "semantic_score": round(semantic_score, 4),
                "text_score": round(text_score, 4),
                "tag_score": round(tag_score, 4),
                "relevance_score": round(relevance_score, 4)
            }
            
    except Exception as e:
        logger.error(f"Error executing hybrid search query: {e}")
    finally:
        cur.close()
        conn.close()
        
    # Sort merged results by relevance score descending
    sorted_results = sorted(merged_results.values(), key=lambda x: x["relevance_score"], reverse=True)
    
    # Filter by threshold to eliminate completely irrelevant documents
    filtered_results = [r for r in sorted_results if r["relevance_score"] >= score_threshold]
    
    # Slice to top_k
    top_results = filtered_results[:top_k]
    
    logger.info(f"Hybrid search returned {len(top_results)} records matching threshold {score_threshold}")
    for idx, r in enumerate(top_results):
        logger.info(f" Rank {idx+1}: ID={r['id']}, Score={r['relevance_score']} (Sem={r['semantic_score']}, Txt={r['text_score']}, Tag={r['tag_score']})")
        
    return top_results, search_terms_str
