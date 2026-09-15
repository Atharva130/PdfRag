# 📄 DocuChat — AI-Powered Document Q&A Chatbot

A full-stack **Retrieval-Augmented Generation (RAG)** application that allows users to upload PDF or DOCX documents and ask natural-language questions about their content.

DocuChat retrieves the most relevant sections from the uploaded document and uses an LLM to generate answers **strictly grounded in the retrieved content**, with source page citations. When the requested information cannot be found in the document, the system explicitly declines to answer instead of relying on outside knowledge.

🔗 **Live Demo:** https://pdfrag-pgks.onrender.com
🔗 **Repository:** https://github.com/Atharva130/PdfRag

---

## ✨ Features

* 📑 **PDF & DOCX Support** — Extracts text from both PDF and Word documents.
* 🔍 **Semantic Search** — Retrieves relevant document sections using dense vector embeddings.
* 🧠 **Query Decomposition** — Automatically splits compound questions into independent sub-questions before retrieval.
* 🎯 **Grounded Generation** — Answers are generated strictly from retrieved document context.
* 🚫 **Hallucination Prevention** — Explicitly refuses to answer when relevant information is not present.
* 📚 **Source Citations** — Returns the document page numbers associated with the retrieved context.
* 📝 **Markdown Rendering** — Supports formatted answers including tables, lists, bold text, and structured responses.
* 💬 **Interactive Chat UI** — Provides a custom chat interface with file upload, typing indicators, and source chips.
* 🖱️ **Drag & Drop Upload** — Upload documents directly through the frontend.
* 📊 **Document Statistics** — Displays useful ingestion information such as page and chunk counts.
* ⚡ **Fast Inference** — Uses Groq-hosted LLM inference for low-latency responses.
* 🖥️ **CPU-Based Embeddings** — Local embeddings avoid external embedding API costs.
* 🐳 **Dockerized Deployment** — Containerized and deployed as a single service.

---

# 🏗️ Architecture

DocuChat follows a complete **document ingestion → retrieval → generation** RAG pipeline.

```text
                         DOCUMENT INGESTION
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   PDF / DOCX Upload                                          │
│          │                                                   │
│          ▼                                                   │
│   Document Parser                                            │
│   ┌───────────────────┬────────────────────┐                 │
│   │ PDF → pypdf       │ DOCX → python-docx │                 │
│   └───────────────────┴────────────────────┘                 │
│          │                                                   │
│          ▼                                                   │
│   Extracted Text + Metadata                                  │
│          │                                                   │
│          ▼                                                   │
│   RecursiveCharacterTextSplitter                             │
│          │                                                   │
│          ▼                                                   │
│   Overlapping Document Chunks                                 │
│          │                                                   │
│          ▼                                                   │
│   all-MiniLM-L6-v2 Embeddings                                │
│          │                                                   │
│          ▼                                                   │
│   ChromaDB                                                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘


                            QUERY PIPELINE
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   User Question                                              │
│        │                                                     │
│        ▼                                                     │
│   LLM Query Decomposition                                    │
│        │                                                     │
│        ├───────────────┬───────────────┐                     │
│        ▼               ▼               ▼                     │
│   Sub-question 1  Sub-question 2  Sub-question N            │
│        │               │               │                     │
│        ▼               ▼               ▼                     │
│      Embed           Embed           Embed                   │
│        │               │               │                     │
│        ▼               ▼               ▼                     │
│   ChromaDB Vector Search                                     │
│        │                                                     │
│        ▼                                                     │
│   Merge + Deduplicate Retrieved Chunks                       │
│        │                                                     │
│        ▼                                                     │
│   Context Construction                                       │
│        │                                                     │
│        ▼                                                     │
│   Groq — openai/gpt-oss-20b                                 │
│        │                                                     │
│        ▼                                                     │
│   Grounded Answer + Source Pages                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

# 🔄 End-to-End Workflow

## 1. Document Ingestion

The user uploads a `.pdf` or `.docx` document through the frontend.

The backend identifies the file type and routes it to the appropriate parser:

### PDF

PDFs are processed using `pypdf`.

Text is extracted **page by page**, allowing page numbers to be preserved as metadata for later source citations.

### DOCX

DOCX files are processed using `python-docx`.

Paragraph text is extracted and treated as a single logical document unit because DOCX does not provide a reliable native page structure.

---

## 2. Chunking

The extracted text is split into smaller overlapping chunks using LangChain's:

```text
RecursiveCharacterTextSplitter
```

The splitter attempts to preserve semantic structure by prioritizing:

```text
Paragraphs
   ↓
Sentences
   ↓
Words
   ↓
Characters
```

This prevents unnecessary mid-sentence cuts while keeping chunks small enough for effective retrieval.

Each chunk stores metadata such as:

```text
chunk_id
page_number
document content
```

The overlap between chunks also helps preserve context across chunk boundaries.

---

## 3. Embedding & Vector Storage

Every document chunk is converted into a dense vector representation using:

```text
sentence-transformers
        ↓
all-MiniLM-L6-v2
```

The embedding model runs locally on CPU, avoiding an external embedding API.

The resulting embeddings, chunk text, and metadata are stored in:

```text
ChromaDB
```

The current application follows a **single-document MVP architecture**.

When a new document is uploaded, the previous vector collection is reset and replaced with the new document.

---

# 🔎 4. Query Decomposition & Retrieval

A major part of the system is how it handles **compound questions**.

For example:

```text
"What are the main features of Project A
and how does it differ from Project B?"
```

Instead of embedding the entire question as one vector, the system first uses an LLM-based query decomposition step:

```text
Original Question
       │
       ▼
"What are the main features of Project A
 and how does it differ from Project B?"
       │
       ▼
 ┌─────────────────────────────────┐
 │ Sub-question 1                  │
 │ What are the main features of   │
 │ Project A?                      │
 └─────────────────────────────────┘

 ┌─────────────────────────────────┐
 │ Sub-question 2                  │
 │ How does Project A differ from  │
 │ Project B?                      │
 └─────────────────────────────────┘
```

Each sub-question is independently embedded and searched against ChromaDB.

The retrieved results are then:

```text
Retrieved Chunks
      ↓
Merge
      ↓
Deduplicate
      ↓
Final Context
```

### Why Query Decomposition?

During development, a single embedding for a multi-part question caused a real retrieval failure.

The semantic similarity search could become dominated by one part of the question, causing relevant chunks for the other part to be pushed out of the top-k results.

Query decomposition solves this by giving each sub-question its own retrieval opportunity.

This significantly improves retrieval coverage for multi-part questions.

---

# 🤖 5. Answer Generation

The retrieved chunks are assembled into a context block and passed to the LLM together with the original user question.

The application uses:

```text
Groq API
    ↓
openai/gpt-oss-20b
```

The generation prompt enforces several grounding rules:

### Strict Context Grounding

The model is instructed to use only the provided document context.

It should not introduce information from its general knowledge.

### Explicit Refusal

If the retrieved context does not contain relevant information, the system responds with an explicit refusal such as:

```text
I couldn't find this information in the document.
```

### Evidence Without Fabrication

The system also handles questions that require interpretation.

For example:

```text
"What is the best project mentioned in the document?"
```

The document may describe several projects without explicitly ranking them.

Instead of incorrectly refusing because the word "best" does not literally appear in the document, the prompt allows the model to present the relevant evidence while avoiding an invented ranking.

This distinction helps balance:

```text
Grounding
     +
Useful answers
     +
No fabricated conclusions
```

---

# 📚 6. Source Citations

Every retrieved chunk retains its original document metadata.

For PDFs, this includes the page number.

The final API response therefore contains:

```text
Answer
+
Source Pages
```

The frontend displays these sources as clickable page chips, making it easier for users to trace an answer back to the original document.

---

# 🎨 Frontend

DocuChat uses a custom-built frontend without a JavaScript framework.

### Technologies

```text
HTML
CSS
Vanilla JavaScript
marked.js
```

### Interface Features

* Drag-and-drop document upload
* PDF/DOCX file selection
* Upload progress/status
* Document statistics
* Page and chunk counts
* Interactive chat interface
* Typing indicator
* Formatted Markdown responses
* Tables and bullet lists
* Source page chips
* Responsive layout

LLM responses are rendered using `marked.js`, allowing Markdown generated by the model to be displayed correctly instead of appearing as raw text.

The frontend is served directly by FastAPI, keeping the application as a **single deployable unit**.

---

# 🧩 Backend Architecture

The backend is intentionally separated into focused modules rather than placing the complete RAG pipeline inside a single file.

```text
PdfRag/
│
├── main.py
│   └── FastAPI routes & request orchestration
│
├── document_parser.py
│   └── PDF / DOCX text extraction
│
├── chunker.py
│   └── Text chunking & metadata handling
│
├── vectorstore.py
│   └── Embeddings + ChromaDB operations
│
├── rag.py
│   └── Query decomposition
│   └── Retrieval logic
│   └── Prompt construction
│   └── LLM generation
│
├── static/
│   └── index.html
│       └── Frontend chat interface
│
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

---

# 🔌 API Endpoints

| Endpoint  | Method | Description                                       |
| --------- | ------ | ------------------------------------------------- |
| `/`       | GET    | Serves the frontend                               |
| `/health` | GET    | Application health check                          |
| `/upload` | POST   | Uploads and processes a PDF/DOCX                  |
| `/chat`   | POST   | Retrieves context and generates a grounded answer |
| `/docs`   | GET    | FastAPI Swagger API documentation                 |

---

# 🛠️ Tech Stack

| Layer                  | Technology                                 |
| ---------------------- | ------------------------------------------ |
| **Backend**            | Python, FastAPI, Uvicorn                   |
| **PDF Parsing**        | pypdf                                      |
| **DOCX Parsing**       | python-docx                                |
| **Chunking**           | LangChain `RecursiveCharacterTextSplitter` |
| **Embeddings**         | sentence-transformers `all-MiniLM-L6-v2`   |
| **Vector Database**    | ChromaDB                                   |
| **LLM**                | Groq API — `openai/gpt-oss-20b`            |
| **Frontend**           | HTML, CSS, Vanilla JavaScript              |
| **Markdown Rendering** | marked.js                                  |
| **Containerization**   | Docker                                     |
| **Deployment**         | Render                                     |
| **Version Control**    | Git, GitHub                                |

---

# 🧠 Key Engineering Challenges

## 1. Compound Query Retrieval Failure

### Problem

Embedding an entire multi-part question into a single vector could cause one topic to dominate semantic similarity results.

### Solution

Implemented LLM-based query decomposition.

```text
Compound Query
      ↓
Independent Sub-queries
      ↓
Individual Vector Searches
      ↓
Merge + Deduplicate
      ↓
Improved Retrieval Coverage
```

---

## 2. Overly Strict Grounding

### Problem

The initial grounding prompt could cause the LLM to refuse questions where the document contained relevant evidence but did not explicitly state the requested conclusion.

### Solution

Refined the prompt to distinguish between:

```text
Information is absent
        vs.
Information exists but requires interpretation
```

This preserves hallucination prevention without unnecessarily refusing answerable questions.

---

## 3. Long-Context Answer Truncation

### Problem

Longer document questions occasionally produced responses that ended abruptly.

### Cause

The configured generation token limit was too restrictive for longer summary-style responses.

### Solution

Increased the maximum generation token allowance so longer grounded responses could complete successfully.

---

## 4. Free-Tier Memory Constraints

### Problem

The deployment environment has limited memory, making heavyweight ML dependencies expensive.

### Solution

Used the CPU-only PyTorch build instead of installing GPU-related dependencies.

This significantly reduces unnecessary dependency overhead while still allowing:

```text
all-MiniLM-L6-v2
```

to run locally for document embeddings.

---

## 5. Markdown Rendering

### Problem

The LLM frequently generated useful Markdown such as tables and bullet lists, but the frontend initially displayed the Markdown syntax as plain text.

### Solution

Integrated:

```text
marked.js
```

to parse and render Markdown on the client side.

This made structured LLM responses substantially easier to read.

---

# 🐳 Deployment

The application is containerized using Docker.

### Base Image

```text
Python 3.12-slim
```

### Deployment Platform

```text
Render
```

The application is deployed as a Docker web service with automatic deployment from the GitHub `main` branch.

The architecture keeps the frontend and backend together:

```text
Browser
   │
   ▼
Render
   │
   ├── FastAPI Backend
   ├── Static Frontend
   ├── RAG Pipeline
   └── ChromaDB
```

The Groq API key is stored using Render's environment-variable/secret configuration and is never committed to source control.

The `.gitignore` excludes:

```text
venv/
chroma_db/
__pycache__/
.env
```

---

# 🚀 Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/Atharva130/PdfRag.git
cd PdfRag
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## 5. Start the application

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# ⚠️ Current Limitations

* **Single-document MVP** — uploading a new document replaces the currently indexed document.
* **No OCR** — scanned/image-only PDFs without an embedded text layer are not currently supported.
* **DOCX page citations** — DOCX documents do not have reliable native page metadata, so PDF-style page citations are not available for them.
* **Local vector storage** — ChromaDB is currently configured for the application's single-document workflow rather than a multi-user production vector database.
* **No authentication** — the current deployment is intended as a project/demo application rather than a multi-user SaaS platform.

---

# 🔮 Possible Future Improvements

* Multi-document knowledge bases
* User/session-based document collections
* OCR support for scanned PDFs
* Hybrid keyword + semantic retrieval
* Reranking retrieved chunks
* Conversation memory
* Streaming LLM responses
* Authentication and user accounts
* Cloud-hosted vector database
* Document deletion and management
* Improved DOCX structural/page metadata
* Retrieval evaluation and automated RAG benchmarks

---

# 📸 Project Highlights

### Upload

Upload a PDF or DOCX document using the drag-and-drop interface.

### Ask

Ask natural-language questions about the document.

### Retrieve

The system decomposes complex questions and retrieves relevant document chunks using semantic search.

### Answer

The LLM generates a grounded response using only the retrieved document context.

### Verify

Source page citations allow users to trace answers back to the original document.

---

# 👤 Author

**Atharva Rahate**

* GitHub: https://github.com/Atharva130
* LinkedIn: https://linkedin.com/in/atharva-rahate

---

## ⭐ Project Summary

DocuChat demonstrates a complete production-oriented RAG workflow:

```text
Document Upload
      ↓
Multi-format Parsing
      ↓
Semantic Chunking
      ↓
Local Embeddings
      ↓
ChromaDB Vector Storage
      ↓
LLM Query Decomposition
      ↓
Semantic Retrieval
      ↓
Context Merging & Deduplication
      ↓
Grounded LLM Generation
      ↓
Source-Cited Answer
```

The project focuses not only on implementing a basic RAG pipeline, but also on solving practical retrieval and generation problems encountered during development, including **compound-query retrieval failures, grounding/refusal behavior, long-context truncation, deployment memory constraints, and structured response rendering**.
