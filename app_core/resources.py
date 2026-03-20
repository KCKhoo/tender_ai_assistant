import chromadb
import streamlit as st
from llama_index.core import VectorStoreIndex
from llama_index.postprocessor.jinaai_rerank import JinaRerank
from llama_index.vector_stores.chroma import ChromaVectorStore

from src.module.constants import (
    JINAAI_API_KEY,
    VECTOR_DB_COLLECTION_NAME,
    VECTOR_DB_DIR,
)
from src.module.generation import ResponseGenerator
from src.module.retrieval import Retriever
from src.prompt_template import (
    ANSWERING_PROMPT_TEMPLATE,
    BOM_BOQ_PROMPT,
    REQUIRMENT_EXTRACTOR_PROMPT,
)
from src.rag_pipeline import RAGPipeline


@st.cache_resource
def set_reranker():
    return JinaRerank(api_key=JINAAI_API_KEY)


@st.cache_resource
def load_vector_store():

    db = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    chroma_collection = db.get_or_create_collection(VECTOR_DB_COLLECTION_NAME)
    return VectorStoreIndex.from_vector_store(
        ChromaVectorStore(chroma_collection=chroma_collection)
    )


@st.cache_resource
def setup_retriever():

    vector_store = load_vector_store()
    reranker = set_reranker()

    return Retriever(vector_store.as_retriever(), reranker)


@st.cache_resource(show_spinner="Initializing RAG Pipeline...")
def setup_rag_pipeline():
    """Initializes and caches the RAG pipeline. Only run once when the app starts"""
    try:
        retriever = setup_retriever()
        generator = ResponseGenerator(ANSWERING_PROMPT_TEMPLATE)

        return RAGPipeline(retriever, generator)

    except Exception as e:
        st.error(f"Failed to initialize RAG pipeline: {e}")
        return None


@st.cache_resource
def setup_requirement_extractor():
    return ResponseGenerator(REQUIRMENT_EXTRACTOR_PROMPT)


@st.cache_resource
def setup_bom_boq_generator():
    return ResponseGenerator(BOM_BOQ_PROMPT)
