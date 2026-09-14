from pypdf import PdfReader
from docx import Document
import io

def parse_pdf(contents: bytes):
    reader = PdfReader(io.BytesIO(contents))
    pages_text = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages_text.append({"page": page_num, "text": text})
    return pages_text

def parse_docx(contents: bytes):
    doc = Document(io.BytesIO(contents))
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return [{"page": 1, "text": full_text}]

def parse_document(filename: str, contents: bytes):
    filename = filename.lower()
    if filename.endswith(".pdf"):
        return parse_pdf(contents)
    elif filename.endswith(".docx"):
        return parse_docx(contents)
    else:
        raise ValueError("Only .pdf and .docx files are supported")