import json
import re

import pandas as pd
import streamlit as st
from llama_index.core import QueryBundle
from llama_index.core.vector_stores import (
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)

from app_core.resources import setup_bom_boq_generator, setup_retriever


def generate_bom_boq(fname="1. Bid Price Schedule.pdf"):
    """Generate BoM and BoQ."""

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

    resp = bom_boq_generator.generate_response(
        question=None, context=text_nodes, citation=False
    )
    processed_resp = re.sub(r"```json|```", "", resp).strip()

    return json.loads(processed_resp)


retriever = setup_retriever()
bom_boq_generator = setup_bom_boq_generator()

st.title("Bill of Materials & Bill of Quantities Generator")
st.caption("Click the button to generate BoM & BoQ")

if st.button("Generate BoM & BoQ"):
    log_container = st.container()
    req = []

    log_container.write("Generating...")

    req += generate_bom_boq()

    log_container.write("Finished processing.")

    st.session_state["df_bom_boq"] = pd.DataFrame(req)
    st.session_state["csv_bom_boq"] = (
        pd.DataFrame(req).to_csv(index=False).encode("utf-8")
    )
    st.success("Done!")
    st.table(st.session_state["df_bom_boq"])


if "csv_bom_boq" in st.session_state:
    st.download_button(
        "Download Results",
        st.session_state["csv_bom_boq"],
        "requirements.csv",
        "text/csv",
    )
