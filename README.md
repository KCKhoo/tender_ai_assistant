# Tender AI Assistant

A Retrieval-Augmented Generation (RAG) powered assistant designed to:
1. Answer user queries regarding tender documents
2. Extract requirements from tender documents
3. Extract Bill of Quantities (BoQ) and Bill of Material (BoM) from tender documents

Link for (1): https://tender-ai-assistant.streamlit.app/
Link for (2): https://tender-ai-assistant.streamlit.app/Tender_Requirement_Extractor
Link for (3): https://tender-ai-assistant.streamlit.app/BoM_and_BoQ_Generator

## System Architecture
- PDF Parser
- Chnking and Generting embedding
- 3 different pipeline With vector store different purpose

## Tech Stack & Models

### Dependency and Environment Management
- `uv`
- `pyproject.toml`

### Framework
- PDF Parser: LlamaParse
- Data Ingestion and Indexing: LlamaIndex
- RAG: LlamaIndex

### Storage
- Vector Database: Chroma

### Models
- Embedding Model: `Qwen/Qwen3-Embedding-0.6B`
- Reranker: `jina-reranker-v3`
- LLM: Google Gemini

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-org/rag-chatbot.git
cd tender_ai_assistant
```

### 2. Install uv for managing environment

If UV is not installed yet:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Create and activate the virtual environment
```bash
uv venv
source .venv/bin/activate
```

### 4. Install dependencies
```bash
uv sync
```

### 5. Edit `.env` and add your API keys:
```bash
LLAMA_CLOUD_API_KEY=your_api_key_here
HF_TOKEN=your_api_key_here
JINAAI_API_KEY=your_api_key_here
GEMINI_API_KEY=your_api_key_here
```
#### Note
`LLAMA_CLOUD_API_KEY` is only required if you plan to parse PDFs using LlamaParse. It is not needed when using a precomputed vector database or running the Streamlit app.

#### Getting API keys
- LLAMA Cloud: https://cloud.llamaindex.ai
- HF: https://huggingface.co
- JinaAI: https://jina.ai/reranker
    - Ensure the select model is `jina-reranker-v3`
- Gemini: https://aistudio.google.com

## Running the Project

### Launch Tender AI Assistant User Interface (Streamlit)
In `tender_ai_assistant` directory,
```bash
uv run streamlit run Home.py
```

After the server starts, open the link shown in the terminal to access the UI.

## Running the Notebook

Before running the notebooks, make sure the correct kernal/environment is selected

### Parse PDFs
Follow the steps in `notebooks/parsing.ipynb`.

### Generate Vector Store
\*Prerequisite: Parsed PDFs

Follow the steps in `notebooks/generating_vector_db.ipynb`.

