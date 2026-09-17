import os
import json
import numpy as np
from config import settings
from schema import Goal, Action, StepGroup, actionCategory, ContextDeeplinkResponse, Deeplink
from database import get_deeplink, get_siis_response

model = None
index = None
siis_ids = []

def init_engine():
    global model, index, siis_ids
    import faiss
    from sentence_transformers import SentenceTransformer
    
    # Load model
    print("Loading embedding model...")
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    
    # Load or build index
    if os.path.exists(settings.FAISS_INDEX_PATH):
        print("Loading FAISS index...")
        index = faiss.read_index(settings.FAISS_INDEX_PATH)
        # We need to map FAISS indices to SIIS IDs. 
        # In a real system, we'd store the mapping alongside the index.
        mapping_path = settings.FAISS_INDEX_PATH + ".map"
        if os.path.exists(mapping_path):
            with open(mapping_path, "r") as f:
                siis_ids = json.load(f)
    else:
        print("Building FAISS index...")
        # Get all SIIS responses to build the index
        import sqlite3
        conn = sqlite3.connect(settings.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, content FROM siis_responses")
        rows = cursor.fetchall()
        conn.close()
        
        texts = []
        for r in rows:
            siis_ids.append(r[0])
            content = json.loads(r[1])
            texts.append(content.get("text", ""))
        
        if texts:
            embeddings = model.encode(texts, convert_to_numpy=True)
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
            
            # Save index
            os.makedirs(settings.INDEX_DIR, exist_ok=True)
            faiss.write_index(index, settings.FAISS_INDEX_PATH)
            with open(settings.FAISS_INDEX_PATH + ".map", "w") as f:
                json.dump(siis_ids, f)

def retrieve_siis(query: str, k: int = 1):
    if not model or not index or not siis_ids:
        return None
    
    query_emb = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_emb, k)
    
    if len(indices) > 0 and len(indices[0]) > 0:
        best_idx = indices[0][0]
        if best_idx < len(siis_ids):
            siis_id = siis_ids[best_idx]
            return get_siis_response(siis_id)
    return None

from guardrails import format_goal, format_title, format_description, scrub_urls
from safety_engine import sort_actions

def synthesize_response(query: str, siis_context: dict = None) -> ContextDeeplinkResponse:
    # Dummy synthesizer for now based on context
    topic = "General"
    if siis_context:
        topic = siis_context.get("topic", "General")
        
    goal_str = format_goal(topic)
    title_str = format_title(f"{topic} issue")
    desc_str = format_description(f"It will check {topic.lower()} settings")
    
    # We should match deeplinks. For simplicity, we hardcode the match logic for demo
    dl_meta = None
    if "battery" in query.lower():
        dl_meta = get_deeplink("dl_battery")
    elif "swipe" in query.lower() or "navigation" in query.lower():
        dl_meta = get_deeplink("dl_nav_bar")
        
    actionable_dl = None
    if dl_meta:
        actionable_dl = Deeplink(
            deeplink=dl_meta.get("deeplink"),
            description=dl_meta.get("description"),
            message=dl_meta.get("message")
        )
        
    action = Action(
        actionName=f"Configure {topic} Settings",
        description=scrub_urls(desc_str),
        category=actionCategory.auto,
        stepGroups=[
            StepGroup(
                steps=["Navigate to settings", f"Tap on {topic}"],
                actionableDeeplink=actionable_dl
            )
        ]
    )
    
    # Apply safety sorting
    actions = sort_actions([action])
    
    goal = Goal(
        goal=goal_str,
        title=title_str,
        actions=actions,
        score=0.95
    )
    
    return ContextDeeplinkResponse(contexts=[goal])

import cache

def process_troubleshoot_request(query: str, siis_response_text: str = None) -> ContextDeeplinkResponse:
    # Normalize query (lowercase etc)
    normalized_query = query.lower().strip()
    
    # Check cache
    cached = cache.get_cached_response(normalized_query)
    if cached and not siis_response_text:
        return cached
    
    # Semantic Retrieval
    context = None
    if not siis_response_text:
        context = retrieve_siis(normalized_query)
    else:
        context = {"text": siis_response_text, "topic": "Custom"}
        
    # Extractive Synthesizer
    response = synthesize_response(normalized_query, context)
    
    if not siis_response_text:
        cache.set_cached_response(normalized_query, response)
        
    return response
