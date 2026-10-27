
from pathlib import Path
import json

import faiss
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def get_model():
    """Load the embedding model once per process."""
    global _model

    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def load_chunks(chunks_path):
    """Load chunks and preserve their source page numbers."""
    chunks_path = Path(chunks_path)
    text = chunks_path.read_text(encoding="utf-8")

    chunks = []
    current_page = None
    current_text = []

    for line in text.splitlines():
        if line.startswith("--- Chunk "):
            if current_text and current_page is not None:
                chunk_text = "\n".join(current_text).strip()
                if chunk_text:
                    chunks.append({
                        "page": current_page,
                        "text": chunk_text,
                    })

            current_text = []

            page_part = line.split("| Page ")
            current_page = int(page_part[1].split(" ")[0].rstrip("-"))

        else:
            current_text.append(line)

    if current_text and current_page is not None:
        chunk_text = "\n".join(current_text).strip()
        if chunk_text:
            chunks.append({
                "page": current_page,
                "text": chunk_text,
            })

    return chunks


def build_index(chunks, index_path, metadata_path):
    """Build and save a FAISS index for one document."""
    if not chunks:
        raise ValueError("No text chunks were provided.")

    index_path = Path(index_path)
    metadata_path = Path(metadata_path)

    index_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    model = get_model()
    texts = [chunk["text"] for chunk in chunks]

    print(f"Generating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype("float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, str(index_path))

    metadata_path.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Embeddings created: {len(chunks)}")
    print(f"Vector dimensions: {embeddings.shape[1]}")
    print(f"Saved index: {index_path}")
    print(f"Saved metadata: {metadata_path}")


def main():
    chunks = load_chunks("data/processed/chunks.txt")
    print(f"Loaded {len(chunks)} chunks.")

    build_index(
        chunks,
        "data/processed/faiss.index",
        "data/processed/chunk_metadata.json",
    )


if __name__ == "__main__":
    main()
