# PdfRag Chatbot 🤖📄

A lightweight, local Retrieval-Augmented Generation (RAG) chatbot MVP. This application allows users to upload a PDF file and ask context-aware questions about its content using FastAPI, ChromaDB, and Groq LLMs.

## 🚀 Features
* **PDF Processing:** Text extraction with page number tracking.
* **Semantic Vector Search:** Local text embedding generation and storage using ChromaDB.
* **Fast LLM Responses:** Blazing fast inference powered by the Groq API.
* **Clean UI:** Simple, interactive frontend for effortless file uploads and chatting.

## 🛠️ Tech Stack
* **Backend:** FastAPI, Uvicorn
* **PDF Parser:** PyPDF
* **Vector Database:** ChromaDB
* **Embeddings:** Sentence-Transformers (`all-MiniLM-L6-v2`)
* **LLM Engine:** Groq API

## 📋 Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com
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

5. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```
   Open your browser and navigate to `http://127.0.0.1:8000`.
