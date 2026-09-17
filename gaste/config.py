import os

class Settings:
    SESSION_TTL_SECONDS: int = int(os.getenv("SESSION_TTL_SECONDS", 1800))
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    DB_PATH: str = os.getenv("DB_PATH", "gaste_catalog.db")
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    INDEX_DIR: str = os.getenv("INDEX_DIR", "indexes")
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "indexes/faiss.index")

settings = Settings()
