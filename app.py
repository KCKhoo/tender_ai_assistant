import chromadb
import streamlit as st
from llama_index.core import Settings, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.postprocessor.jinaai_rerank import JinaRerank
from llama_index.vector_stores.chroma import ChromaVectorStore

from src.module.constants import EMBED_MODEL, HF_TOKEN, JINAAI_API_KEY, VECTOR_DB_DIR
from src.module.generation import ResponseGenerator
from src.module.retrieval import Retriever
from src.prompt_template import ANSWERING_PROMPT_TEMPLATE
from src.rag_pipeline import RAGPipeline


@st.cache_resource
def set_embed_model():
    return HuggingFaceEmbedding(
        model_name=EMBED_MODEL,
        token=HF_TOKEN,
    )


@st.cache_resource
def set_reranker():
    return JinaRerank(api_key=JINAAI_API_KEY)


st.set_page_config(page_title="AI Tender Assistant", page_icon="💬")


@st.cache_resource(show_spinner="Initializing RAG Pipeline...")
def init_rag_pipeline():
    """Initializes and caches the RAG pipeline. Only run once when the app starts"""
    try:
        # Set embedding model and reranker
        Settings.embed_model = set_embed_model()
        reranker = set_reranker()

        # Load vector stores
        db = chromadb.PersistentClient(path=VECTOR_DB_DIR)
        chroma_collection = db.get_or_create_collection("tender_documents")
        vector_store = VectorStoreIndex.from_vector_store(
            ChromaVectorStore(chroma_collection=chroma_collection)
        )

        # Setup retriever and generator
        retriever = Retriever(vector_store.as_retriever(), reranker)
        generator = ResponseGenerator(ANSWERING_PROMPT_TEMPLATE)

        return RAGPipeline(retriever, generator)

    except Exception as e:
        st.error(f"Failed to initialize RAG pipeline: {e}")
        return None


rag_pipeline = init_rag_pipeline()

st.title("Tender AI Assistant")
st.caption("Hi! Ask me anything about the tender documents.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_ques := st.chat_input("Enter your question"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_ques})

    with st.chat_message("user"):
        st.markdown(user_ques)

    # Answer user query
    if rag_pipeline:
        spinner = st.empty()

        with st.chat_message("assistant"):
            output = rag_pipeline.answer(
                user_ques,
                20,
                retriever_filter=None,
                top_k_rerank=10,
                callback=lambda msg: spinner.markdown(f"⏳ *{msg}*"),
            )

            if output.get("status") == "error":
                error_msg = output["error_message"]
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"Error: {error_msg}"}
                )

            else:
                answer = output["answer"]
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

        spinner.empty()

    else:
        st.error("Oops, there is an error")
