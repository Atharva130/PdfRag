import threading
import chromadb
from chromadb.utils import embedding_functions

chroma_client = chromadb.PersistentClient(path="./chroma_db")
COLLECTION_NAME = "current_document"

embedding_lock = threading.Lock()

# Lightweight ONNX runtime model — replaces sentence-transformers + torch,
# cuts baseline memory footprint significantly
embedding_fn = embedding_functions.ONNXMiniLM_L6_V2()


def get_collection():
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )


def reset_collection():
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )


def store_chunks(chunks):
    with embedding_lock:
        collection = reset_collection()
        collection.add(
            ids=[str(c["chunk_id"]) for c in chunks],
            documents=[c["text"] for c in chunks],
            metadatas=[{"page": c["page"]} for c in chunks],
        )
    return len(chunks)


def query_chunks(query: str, n_results: int = 5):
    with embedding_lock:
        collection = get_collection()
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        retrieved = []
        for text, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            retrieved.append({"text": text, "page": meta["page"], "distance": dist})
    return retrieved