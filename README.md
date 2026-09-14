# 📄 PdfRag — Document Q&A Chatbot 🤖

A lightweight, local Retrieval-Augmented Generation (RAG) chatbot MVP. This application allows users to upload a PDF file and ask context-aware questions about its content using FastAPI, ChromaDB, and Groq LLMs. The bot retrieves relevant sections from the document and generates grounded, source-cited answers—explicitly declining to answer when the information isn't actually in the document.

---

## 🚀 Features
* **PDF Processing:** Text extraction with page number tracking.
* **Semantic Vector Search:** Local text embedding generation and storage using ChromaDB.
* **Fast LLM Responses:** Blazing fast inference powered by the Groq API.
* **Grounded Answers:** Instructed to prevent hallucinations and return source page numbers.
* **Clean UI:** Simple, interactive vanilla HTML/CSS/JS frontend for effortless file uploads and chatting.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **Backend** | FastAPI, Uvicorn |
| **PDF Parsing** | pypdf |
| **Chunking** | LangChain `RecursiveCharacterTextSplitter` |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| **Vector Store** | ChromaDB (persistent, local) |
| **LLM Engine** | Groq API |
| **Frontend** | Vanilla HTML / CSS / JS |

---

## 🏗️ Architecture & Project Structure

### System Data Flow
```text
Upload (PDF) -> Parse text (page-aware) -> Chunk (overlapping) -> Embed Chunks -> Store in ChromaDB
                                                                                         |
User Query ----> Embed Query ------------> Retrieve top-k chunks ------------------------+
                                                 |
                                                 v
                                    Generate Answer (Groq) -> Return answer + source pages
```

### Folder Layout
```text
PdfRag/
├── main.py            # FastAPI app & routing endpoints
├── document_parser.py # PDF text extraction logic
├── chunker.py         # Text chunking and splitting configuration
├── vectorstore.py     # Embeddings implementation + ChromaDB storage
├── rag.py             # Prompt building and Groq LLM generation
├── static/
│   └── index.html     # Chat UI interface
├── requirements.txt   # Python project dependencies
└── .env               # Secrets configuration (Not committed to source control)
```

---

## 📋 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Atharva130/PdfRag.git
   cd PdfRag
   ```

2. **Create a virtual environment & activate it:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   *Get a free API key at [console.groq.com](https://console.groq.com)*

5. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```
   Open your browser and navigate to `http://127.0.0.1:8000`.

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the static chat web UI |
| `/health` | GET | Basic application API health check |
| `/upload` | POST | Accepts a PDF, executes parse → chunk → embed → store |
| `/chat` | POST | Submits a query; returns a grounded answer + source pages |

*Interactive API documentation is accessible via Swagger UI at `/docs`.*

---

## ⚠️ Known Limitations
* **Single-document MVP:** Uploading a new file overwrites the current collection (no persistent multi-doc or session tracking yet).
* **No OCR:** Scanned or image-only PDFs lacking a native text layer are unsupported.

---

## 👤 Author
**Atharva Rahate**  
[GitHub](https://github.com/Atharva130) · [LinkedIn](https://linkedin.com/in/atharva-rahate)
