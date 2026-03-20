import json
import os
import re
from pathlib import Path

import pandas as pd
import streamlit as st
from llama_index.core import QueryBundle
from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)

from app_core.resources import setup_requirement_extractor, setup_retriever
from src.module.constants import DATA_DIR, RAW_DOC_DIR

MAX_REQUIREMENTS = 100


@st.cache_data
def get_filenames():
    """Return all PDF filenames under the raw documents directory."""
    return [
        pdf_file.name
        for pdf_file in Path(os.path.join(DATA_DIR, RAW_DOC_DIR)).rglob("*.pdf")
    ]


def extract_requirements(fname):
    """Extract requirements from a single file."""

    # Build metadata filter for the file
    filters = MetadataFilters(
        filters=[
            MetadataFilter(key="file_name", value=fname, operator=FilterOperator.EQ)
        ]
    )

    # Retrieve all relevant nodes. Set high top K to ensure all the relevant nodes for the document is extracted
    text_nodes = retriever.retrieve(QueryBundle(""), top_k=1000, filters=filters)

    # Sort nodes in original document order
    text_nodes.sort(
        key=lambda x: (
            x.node.metadata.get("section_start_idx"),
            x.node.start_char_idx,
        ),
        reverse=False,
    )

    # Process 5 nodes at a time in case there are many nodes
    step_size = 5
    reqs = []

    for i in range(0, len(text_nodes), step_size):
        req = requirement_extractor.generate_response(
            question=None, context=text_nodes[i : i + step_size], citation=False
        )
        processed_req = re.sub(r"```json|```", "", req).strip()
        reqs += json.loads(processed_req)

    return reqs


retriever = setup_retriever()
requirement_extractor = setup_requirement_extractor()
files = get_filenames()

st.title("Tender Requirement Extractor")
st.caption(
    "Click the button to extract requirements from the tender documents. "
    f"Extraction stops after at least {MAX_REQUIREMENTS} requirements is extracted in order to limit API usage and time"
)


if st.button("Extract Requirements"):
    log_container = st.container()
    req = []

    for file in files:
        log_container.write(f"Processing {file}...")

        req += extract_requirements(file)

        log_container.write(f"Finished processing {file}")
        log_container.write(f"Total of {len(req)} requirement(s) extracted so far")

        if len(req) > MAX_REQUIREMENTS:
            break

    st.session_state["df_req"] = pd.DataFrame(req)
    st.session_state["csv_req"] = pd.DataFrame(req).to_csv(index=False).encode("utf-8")
    st.success("Done!")
    st.table(st.session_state["df_req"])


if "csv_req" in st.session_state:
    st.download_button(
        "Download Results", st.session_state["csv_req"], "requirements.csv", "text/csv"
    )
