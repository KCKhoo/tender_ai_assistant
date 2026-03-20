import pickle
import re
from bisect import bisect_right

import pandas as pd
from llama_index.core import Document


def normalize_whitespace(text):

    # Strip leading and trailing whitespace
    text = text.strip()

    # Suppress multiple horizontal spaces or tabs into a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Suppress 3+ consecutive newlines into 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


def load_pickle(fpath):

    with open(fpath, "rb") as f:
        return pickle.load(f)


def view_parsed_doc(fpath):

    parsed_doc = load_pickle(fpath)

    for page in parsed_doc.markdown.pages:
        print(f"{page.page_number}\n\n")
        print(f"{page.markdown}")


def view_text_nodes(nodes):

    node_data = [
        {"id": node.node_id, "text": node.get_content(), **node.metadata}
        for node in nodes
    ]

    return pd.DataFrame(node_data)


def combine_markdown_files(fpath):
    """Combine all the markdown files for a single PDF into a single Document with page offsets"""

    md_objects = load_pickle(fpath)

    fname = md_objects.job.name
    full_content = ""
    page_offsets = []

    for page in md_objects.markdown.pages:
        preprocessed_content = normalize_whitespace(page.markdown)
        full_content += preprocessed_content + "\n\n"
        page_offsets.append(len(full_content))

    doc = Document(
        text=full_content, metadata={"file_name": fname, "page_offsets": page_offsets}
    )

    return doc


def char_idx_to_page_num(char_idx, page_start_offsets):
    """Map character index to page number"""

    return bisect_right(page_start_offsets, char_idx)
