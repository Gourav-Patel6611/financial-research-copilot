from pathlib import Path

from src.ingest import extract_text
from src.chunking import process_text_file
from src.embeddings import load_chunks, build_index


def process_document(pdf_path, document_id, storage_dir="data/uploads"):
    """Extract, chunk, and index one PDF."""

    pdf_path = Path(pdf_path)
    document_dir = Path(storage_dir) / document_id
    document_dir.mkdir(parents=True, exist_ok=True)

    extracted_text_path = document_dir / "extracted_text.txt"
    chunks_path = document_dir / "chunks.txt"
    index_path = document_dir / "faiss.index"
    metadata_path = document_dir / "chunk_metadata.json"

    # 1. Extract text while preserving page numbers.
    extract_text(pdf_path, extracted_text_path)

    # 2. Split the extracted text into chunks.
    process_text_file(extracted_text_path, chunks_path)

    # 3. Load the chunks and build a document-specific index.
    chunks = load_chunks(chunks_path)

    if not chunks:
        raise ValueError(
            "No extractable text was found in this PDF."
        )

    build_index(chunks, index_path, metadata_path)

    return {
        "document_id": document_id,
        "filename": pdf_path.name,
        "chunk_count": len(chunks),
        "index_path": str(index_path),
        "metadata_path": str(metadata_path),
    }
