import ollama

from tos.db import DB


class RAG:
    """
    Retrieval-Augmented Generation pipeline using ChromaDB + Ollama.

    Supports:
    - Document retrieval based on semantic similarity
    - Contextual prompt generation
    - LLM completion (single-turn or multi-turn)

    Attributes:
        db (DB): Initialized ChromaDB wrapper.
        llm_model (str): The LLM model to use via Ollama (default: "llama3").
        top_k (int): Number of top matching documents to retrieve.
    """

    def __init__(self, llm_model: str = "llama3.2", top_k: int = 5):
        self.db = DB()
        self.llm_model = llm_model
        self.top_k = top_k

    def retrieve_chunks(self, query: str) -> list[str]:
        """
        Retrieve relevant document chunks from the vector store.
        """
        results = self.db.query_documents(query, n_results=self.top_k)
        if results and results["documents"]:
            return results["documents"][0]
        return []

    def build_prompt(self, query: str, context_chunks: list[str]) -> str:
        """
        Format context and user query into a single prompt for the LLM.
        """
        context = "\n\n".join(context_chunks)
        prompt = f"""You are TOS, a Support Assistant for Technical Operation Services at Solution-Tek.

                Your job is to help users by answering questions **strictly based on the APR user help documentation** which has already been saved to DB.

                If you are unsure of an answer or it is not covered in the documentation, politely say so and encourage the user to reach out to support at akulkarni@solution-tek.com

                Respond in a helpful, clear, and professional tone.

                ---

                Context:
                {context}

                Question:
                {query}

                Answer:"""

        return prompt

    def answer(self, query: str) -> str:
        """
        Retrieve, build prompt, and generate a response from the LLM.
        """
        chunks = self.retrieve_chunks(query)
        prompt = self.build_prompt(query, chunks)

        response = ollama.chat(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"]

    def chat(self, messages: list[dict[str, str]]) -> str:
        """
        Direct multi-turn conversation with LLM, bypassing retrieval.

        Format:
        [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."},
            ...
        ]
        """
        response = ollama.chat(model=self.llm_model, messages=messages)
        return response["message"]["content"]

    def retrieve_with_sources(self, query: str) -> dict:
        """
        Retrieve chunks with metadata for showing sources.
        """
        results = self.db.query_documents(query, n_results=self.top_k)
        chunks = results["documents"][0] if results else []
        sources = results["metadatas"][0] if results else []

        prompt = self.build_prompt(query, chunks)
        response = ollama.chat(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return {
            "answer": response["message"]["content"],
            "sources": sources,
        }
