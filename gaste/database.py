import sqlite3
import json
import os
from config import settings

def init_db():
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deeplinks (
            id TEXT PRIMARY KEY,
            metadata TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS siis_responses (
            id TEXT PRIMARY KEY,
            content TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id TEXT PRIMARY KEY,
            query TEXT,
            canonical TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS semantic_cache (
            query_hash TEXT PRIMARY KEY,
            response_payload TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    
    # Load deeplinks.json
    deeplinks_path = os.path.join(settings.DATA_DIR, "deeplinks.json")
    if os.path.exists(deeplinks_path):
        with open(deeplinks_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                cursor.execute("INSERT OR IGNORE INTO deeplinks (id, metadata) VALUES (?, ?)", (k, json.dumps(v)))
                
    # Load siis_responses.json
    siis_path = os.path.join(settings.DATA_DIR, "siis_responses.json")
    if os.path.exists(siis_path):
        with open(siis_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                cursor.execute("INSERT OR IGNORE INTO siis_responses (id, content) VALUES (?, ?)", (k, json.dumps(v)))
                
    # Load queries.json
    queries_path = os.path.join(settings.DATA_DIR, "queries.json")
    if os.path.exists(queries_path):
        with open(queries_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                cursor.execute("INSERT OR IGNORE INTO queries (id, query, canonical) VALUES (?, ?, ?)", 
                               (k, v.get("query", ""), v.get("canonical", "")))
                               
    conn.commit()
    conn.close()

def get_deeplink(deeplink_id: str):
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT metadata FROM deeplinks WHERE id = ?", (deeplink_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def get_siis_response(siis_id: str):
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM siis_responses WHERE id = ?", (siis_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def setup_database():
    init_db()
    load_data()
