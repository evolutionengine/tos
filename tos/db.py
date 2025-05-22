import chromadb
from chromadb import Collection, QueryResult
from chromadb.utils import embedding_functions

from tos.chunk import Chunk
from tos.utils import BASE_PATH

DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DB_PATH = BASE_PATH / "db"


class DB:
    """
    DB manages interaction with ChromaDB using Ollama-based embedding functions.

    It supports:
    - Persistent local storage of embeddings via chromadb.PersistentClient
    - Automatic setup of collections based on the embedding model name
    - Adding single or batch document chunks
    - Querying top-N related documents for a given query text

    Attributes:
        embedding_model (str): Name of the Ollama embedding model to use.
        client (chromadb.PersistentClient): Persistent client instance.
        collection (chromadb.Collection): Active vector collection with embedding function.
        embedding_fn (embedding_functions.OllamaEmbeddingFunction): Embedding wrapper for automatic queries.

    Methods:
        add_document(chunk: Chunk) -> bool:
            Add a single chunk (document) to the collection.

        add_documents(chunks: list[Chunk]) -> bool:
            Add a list of chunks (documents) to the collection.

        query_documents(query: str, n_results: int = 3) -> QueryResult | None:
            Perform semantic search over the vector database using the embedding model.

    Example:
        ```python
        db = DB()
        db.add_document(Chunk(...))
        matches = db.query_documents("What is rayleigh scattering?")
        ```
    """

    def __init__(self) -> None:
        self.embedding_model = DEFAULT_EMBEDDING_MODEL
        self.client = chromadb.PersistentClient(str(DB_PATH))

        try:
            self.embedding_fn = embedding_functions.OllamaEmbeddingFunction(
                url="http://localhost:11434",
                model_name=self.embedding_model,
            )
        except Exception as e:
            print(f"Error setting up embedding function: {str(e)}")
            raise e

        self.collection = self.setup_collection()

    def setup_collection(self) -> Collection:
        """Setup collection with proper dimension handling"""

        collection_name = f"documents_{self.embedding_model}"

        try:
            # Try to get existing collection first
            try:
                collection = self.client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_fn,  # type: ignore
                )
                print(
                    f"Using existing collection for {self.embedding_model} embeddings"
                )
            except Exception as _:
                # If collection doesn't exist, create new one
                collection = self.client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_fn,  # type: ignore
                    metadata={"model": self.embedding_model},
                )
                print(f"Created new collection for {self.embedding_model} embeddings")

            return collection

        except Exception as e:
            print(f"Error setting up collection: {str(e)}")
            raise e

    def add_document(self, chunk: Chunk) -> bool:
        """Add document to ChromaDB"""

        try:
            # Add documents
            self.collection.add(
                ids=[chunk.id],
                documents=[chunk.text],
                metadatas=[chunk.meta],
            )
            return True
        except Exception as e:
            print(f"Error adding documents: {str(e)}")
            return False

    def add_documents(self, chunks: list[Chunk]) -> bool:
        """Add documents to ChromaDB"""

        try:
            # Add documents
            self.collection.add(
                ids=[chunk.id for chunk in chunks],
                documents=[chunk.text for chunk in chunks],
                metadatas=[chunk.meta for chunk in chunks],
            )
            return True
        except Exception as e:
            print(f"Error adding documents: {str(e)}")
            return False

    def query_documents(self, query: str, n_results=3) -> QueryResult | None:
        """Query documents and return relevant chunks"""

        try:
            results = self.collection.query(query_texts=[query], n_results=n_results)
            return results
        except Exception as e:
            print(f"Error querying documents: {str(e)}")
            return None

    def reset_collection(self):
        """Delete and recreate the current collection"""

        try:
            self.client.delete_collection(name=self.collection.name)
            self.collection = self.setup_collection()
            print("✅ Collection reset")
        except Exception as e:
            print(f"Error resetting collection: {str(e)}")
