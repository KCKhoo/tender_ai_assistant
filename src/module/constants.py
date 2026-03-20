import os

import streamlit as st
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
JINAAI_API_KEY = os.getenv("JINAAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DATA_DIR = "data"
RAW_DOC_DIR = "raw_documents"
PARSED_DOC_DIR = "parsed_documents"
VECTOR_DB_DIR = "chroma_db"
VECTOR_DB_COLLECTION_NAME = "tender_documents"

EMBED_MODEL = "Qwen/Qwen3-Embedding-0.6B"
GEMINI_MODEL = "gemma-3-27b-it"  # "gemini-3-flash-preview"


# Define embedding model globally
@st.cache_resource
def get_embed_model():
    return HuggingFaceEmbedding(
        model_name=EMBED_MODEL,
        token=HF_TOKEN,
    )


Settings.embed_model = get_embed_model()
