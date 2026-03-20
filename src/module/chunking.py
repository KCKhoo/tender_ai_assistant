from pathlib import Path

from llama_index.core import Document

from src.module.utils import char_idx_to_page_num, combine_markdown_files


class Chunker:
    """Chunk text"""

    def __init__(self, markdown_chunker, text_chunker):
        """Initialize the Chunker.

        :param markdown_chunker: Component used to split documents by markdown structure.
        :param text_chunker: Component used to split text into chunks
        """

        self.markdown_chunker = markdown_chunker
        self.text_chunker = text_chunker

    def _chunk_markdown(self, docs):
        """Split documents into sections based on markdown headers"""

        section_nodes = self.markdown_chunker.get_nodes_from_documents(docs)

        return [
            Document(
                text=n.text,
                metadata={**n.metadata, "section_start_idx": n.start_char_idx},
            )
            for n in section_nodes
        ]

    def _chunk_text(self, section_nodes):
        """Split section-level texts into smaller text chunks."""

        text_nodes = self.text_chunker.get_nodes_from_documents(section_nodes)

        for n in text_nodes:
            page_offsets = n.metadata.get("page_offsets", [])

            start_page = (
                char_idx_to_page_num(
                    n.metadata["section_start_idx"] + n.start_char_idx, page_offsets
                )
                + 1
            )
            end_page = (
                char_idx_to_page_num(
                    n.metadata["section_start_idx"] + n.end_char_idx - 1, page_offsets
                )
                + 1
            )

            # Store list as string as LlamaIndex does not support list
            n.metadata["page_offsets"] = str(page_offsets)
            n.metadata["page_span"] = str([start_page, end_page])

        return text_nodes

    def _postprocess(self, text_nodes):
        """Postprocess nodes by excluding metadata fields from embedding and LLM inputs."""

        for n in text_nodes:
            metadata_keys = n.metadata.keys()
            n.excluded_embed_metadata_keys = list(metadata_keys)
            n.excluded_llm_metadata_keys = list(metadata_keys)

        return text_nodes

    def chunk_docs(self, docs):
        """Perform chunking on a list of documents"""

        sections_nodes = self._chunk_markdown(docs)
        text_nodes = self._chunk_text(sections_nodes)
        text_nodes = self._postprocess(text_nodes)

        return text_nodes

    def chunk_docs_from_dir(self, dir):
        """Perform chunking on a directory containing a list of documents"""

        parsed_docs = [
            combine_markdown_files(pkl_file)
            for pkl_file in list(Path(dir).rglob("*.pkl"))
        ]
        return self.chunk_docs(parsed_docs)
