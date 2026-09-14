import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using ONLY the provided document context.

Rules:
- Answer strictly based on the given context. Do not use outside knowledge.
- If the answer isn't in the context, say "I couldn't find this in the document" — do not guess or make things up.
- Be concise and direct.
- When useful, mention which page the information came from.
"""


def build_prompt(query: str, retrieved_chunks: list) -> str:
    context_blocks = []
    for chunk in retrieved_chunks:
        context_blocks.append(f"[Page {chunk['page']}]\n{chunk['text']}")
    context = "\n\n---\n\n".join(context_blocks)

    return f"""Context from the document:

{context}

---

Question: {query}

Answer using only the context above."""


def generate_answer(query: str, retrieved_chunks: list) -> str:
    prompt = build_prompt(query, retrieved_chunks)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_tokens=500,
    )

    return response.choices[0].message.content #type:ignore

def split_query(query: str) -> list:
    """Use the LLM to split a compound question into sub-questions."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Split the user's question into a list of separate, self-contained sub-questions if it contains multiple distinct asks. If it's already a single question, return it as a one-item list. Return ONLY a JSON array of strings, nothing else."},
            {"role": "user", "content": query},
        ],
        temperature=0,
        max_tokens=200,
    )
    import json
    try:
        return json.loads(response.choices[0].message.content) #type:ignore
    except Exception:
        return [query]  # fallback: treat as single question if parsing fails