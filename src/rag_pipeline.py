from llama_index.core import QueryBundle


class RAGPipeline:
    """End-to-end Retrieval-Augmented Generation (RAG) pipeline."""

    def __init__(
        self,
        retriever,
        generator,
    ):
        """
        Initialize the RAG pipeline.

        :param retriever: Component responsible for retrieving and reranking context.
        :param generator: Component responsible for generating responses from context.
        """
        self.retriever = retriever
        self.generator = generator

    def answer(
        self,
        question,
        top_k_retrieve=10,
        retriever_filter=None,
        top_k_rerank=5,
        callback=None,
    ):
        """Generate an answer for a given question using the RAG pipeline."""

        try:
            query_bundle = QueryBundle(query_str=question)

            if callback:
                callback("Retrieving contexts...")

            retrieved_context = self.retriever.retrieve(
                query_bundle, top_k_retrieve, retriever_filter
            )

            if callback:
                callback("Re-ranking contexts...")

            ranked_context = self.retriever.rerank(
                query_bundle, retrieved_context, top_k_rerank
            )

            if callback:
                callback("Generating answer...")

            answer = self.generator.generate_response(question, ranked_context)

            return {
                "status": "success",
                "error_message": None,
                "question": question,
                "answer": answer,
                "retrieved_context": retrieved_context,
                "ranked_context": ranked_context,
                # Future Improvement: Output latency, token usage for model monitoring
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e),
                "question": question,
            }
