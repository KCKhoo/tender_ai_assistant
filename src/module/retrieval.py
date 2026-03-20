class Retriever:
    """Retrieve and rerank vector embeddings"""

    def __init__(self, retriever, reranker):
        """
        Initialize the Retriever.

        :param retriever: Retriever used to retrieve relevant contexts (i.e. embeddings) from the vector store
        :param reranker: Reranker used to reorder retrieved embeddings
        """

        self.retriever = retriever
        self.reranker = reranker

    def retrieve(self, query_bundle, top_k=10, filters=None):
        """Retrieve the relevant context for a given query."""

        self.retriever.similarity_top_k = top_k

        if filters:
            self.retriever._filters = filters

        try:
            output = self.retriever.retrieve(query_bundle)
        except Exception as e:
            raise Exception(f"Error in retrieving context: {e}") from e

        return output

    def rerank(self, query_bundle, retrieved_nodes, top_k=5):
        """Rerank retrieved nodes for a given query."""

        self.reranker.top_n = top_k

        try:
            output = self.reranker.postprocess_nodes(retrieved_nodes, query_bundle)
        except Exception as e:
            raise Exception(f"Error in reranking: {e}") from e

        return output
