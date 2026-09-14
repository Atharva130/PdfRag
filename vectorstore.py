import chromadb
from sentence_transformers import SentenceTransformer

# Loaded once at import time — reused across requests
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
COLLECTION_NAME = "current_document"


def get_collection():
    """Get or create the single collection we use for the MVP (one doc at a time)."""
    return chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def reset_collection():
    """Wipe any previously stored document before storing a new upload."""
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass  # collection may not exist yet on first run
    return chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def store_chunks(chunks):
    """
    chunks: list of {"chunk_id": int, "page": int, "text": str}
    Embeds each chunk and stores it in Chroma.
    """
    collection = reset_collection()

    texts = [c["text"] for c in chunks]
    embeddings = embedding_model.encode(texts).tolist()

    collection.add(
        ids=[str(c["chunk_id"]) for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"page": c["page"]} for c in chunks],
    )
    return len(chunks)


def query_chunks(query: str, n_results: int = 5):
    """
    Embeds the query and retrieves the most similar stored chunks.
    Returns list of {"text": str, "page": int, "distance": float}
    """
    collection = get_collection()
    query_embedding = embedding_model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
    )

    retrieved = []
    for text, meta, dist in zip(
        results["documents"][0], #type:ignore
        results["metadatas"][0], #type:ignore
        results["distances"][0], #type:ignore
    ):
        retrieved.append({"text": text, "page": meta["page"], "distance": dist})
    return retrieved