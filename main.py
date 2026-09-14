from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from document_parser import parse_document
from chunker import chunk_pages
from vectorstore import store_chunks, query_chunks
from rag import generate_answer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        pages_text = parse_document(file.filename, contents) #type:ignore
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    chunks = chunk_pages(pages_text)

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in this file. It may be a scanned/image-only document, which isn't supported yet."
        )

    num_stored = store_chunks(chunks)

    return {
        "filename": file.filename,
        "num_pages": len(pages_text),
        "num_chunks": num_stored,
    }

@app.post("/chat")
def chat(request: ChatRequest): #type:ignore
    # in main.py /chat endpoint
    retrieved_chunks = query_chunks(request.query, n_results=8) 

    if not retrieved_chunks:
        return {"answer": "No document has been uploaded yet.", "sources": []}

    answer = generate_answer(request.query, retrieved_chunks)

    return {
        "answer": answer,
        "sources": [{"page": c["page"]} for c in retrieved_chunks],
    }

from rag import generate_answer, split_query

@app.post("/chat")
def chat(request: ChatRequest):
    sub_questions = split_query(request.query)

    all_chunks = []
    seen_texts = set()
    for sq in sub_questions:
        for chunk in query_chunks(sq, n_results=5):
            if chunk["text"] not in seen_texts:
                all_chunks.append(chunk)
                seen_texts.add(chunk["text"])

    if not all_chunks:
        return {"answer": "No document has been uploaded yet.", "sources": []}

    answer = generate_answer(request.query, all_chunks)

    return {
        "answer": answer,
        "sources": [{"page": c["page"]} for c in all_chunks],
    }