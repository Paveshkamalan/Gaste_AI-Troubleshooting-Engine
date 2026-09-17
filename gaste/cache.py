import sqlite3
import hashlib
import json
from config import settings
from schema import ContextDeeplinkResponse

def get_cache_key(query: str) -> str:
    return hashlib.sha256(query.encode('utf-8')).hexdigest()

def get_cached_response(query: str) -> ContextDeeplinkResponse:
    key = get_cache_key(query)
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT response_payload FROM semantic_cache WHERE query_hash = ?", (key,))
        row = cursor.fetchone()
    except sqlite3.OperationalError:
        row = None
    finally:
        conn.close()
        
    if row:
        payload = json.loads(row[0])
        return ContextDeeplinkResponse(**payload)
    return None

def set_cached_response(query: str, response: ContextDeeplinkResponse):
    key = get_cache_key(query)
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO semantic_cache (query_hash, response_payload) VALUES (?, ?)", 
                   (key, response.model_dump_json()))
    conn.commit()
    conn.close()
