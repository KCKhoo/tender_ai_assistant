import os

from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
JINAAI_API_KEY = os.getenv("JINAAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

VECTOR_DB_DIR = "chroma_db"
VECTOR_DB_COLLECTION_NAME = "tender_documents"

EMBED_MODEL = "Qwen/Qwen3-Embedding-0.6B"
GEMINI_MODEL = "gemma-3-27b-it"  # "gemini-3-flash-preview"
