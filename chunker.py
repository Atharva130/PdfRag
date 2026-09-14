from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=900,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""]
)

def chunk_pages(pages_text):
    chunks = []
    chunk_id = 0
    for page_data in pages_text:
        page_num = page_data["page"]
        splits = text_splitter.split_text(page_data["text"])
        for split in splits:
            if split.strip():
                chunks.append({
                    "chunk_id": chunk_id,
                    "page": page_num,
                    "text": split
                })
                chunk_id += 1
    return chunks