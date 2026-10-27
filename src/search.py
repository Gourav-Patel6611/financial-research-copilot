
from pathlib import Path
from functools import lru_cache
import json
import re

import faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

RRF_K = 60
CANDIDATE_COUNT = 30
RERANK_CANDIDATE_COUNT = 40

DEFAULT_INDEX_PATH = Path("data/processed/faiss.index")
DEFAULT_METADATA_PATH = Path("data/processed/chunk_metadata.json")

_embedding_model = None
_reranker = None
@lru_cache(maxsize=8)
def load_chunks_cached(metadata_path):
    """Cache document chunks by metadata path."""
    return load_chunks(metadata_path)


@lru_cache(maxsize=8)
def load_faiss_index_cached(index_path):
    """Cache FAISS indexes by index path."""
    return faiss.read_index(index_path)


@lru_cache(maxsize=8)
def build_bm25_cached(metadata_path):
    """Build and cache BM25 for a document."""
    chunks = load_chunks_cached(metadata_path)
    tokenized_chunks = [
        tokenize(chunk["text"]) for chunk in chunks
    ]
    return BM25Okapi(tokenized_chunks)


def get_embedding_model():
    global _embedding_model

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME
        )

    return _embedding_model


def get_reranker():
    global _reranker

    if _reranker is None:
        _reranker = CrossEncoder(RERANKER_MODEL_NAME)

    return _reranker


def tokenize(text):
    """Tokenize words, financial terms, and numeric values."""
    return re.findall(r"[a-z0-9]+", text.lower())


def load_chunks(metadata_path=DEFAULT_METADATA_PATH):
    """Load metadata for the selected document."""
    metadata_path = Path(metadata_path)

    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Chunk metadata not found: {metadata_path}"
        )

    return json.loads(
        metadata_path.read_text(encoding="utf-8")
    )


def reciprocal_rank_fusion(rankings, k=RRF_K):
    """Combine ranked lists using Reciprocal Rank Fusion."""
    fused_scores = {}

    for ranking in rankings:
        for rank, chunk_index in enumerate(ranking, start=1):
            fused_scores[chunk_index] = (
                fused_scores.get(chunk_index, 0.0)
                + 1.0 / (k + rank)
            )

    ranked_indices = sorted(
        fused_scores,
        key=fused_scores.get,
        reverse=True,
    )

    return ranked_indices, fused_scores


def search_report(
    question,
    top_k=5,
    index_path=DEFAULT_INDEX_PATH,
    metadata_path=DEFAULT_METADATA_PATH,
):

    """
    Search one document using BM25, FAISS, RRF, and reranking.

    Pass document-specific paths to search an uploaded PDF.
    """
    
    if not question or not question.strip():
        return []

    if top_k <= 0:
        return []

    index_path = Path(index_path)

    if not index_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found: {index_path}"
        )

    metadata_path = str(Path(metadata_path).resolve())
    index_path = str(Path(index_path).resolve())

    chunks = load_chunks_cached(metadata_path)


    if not chunks:
        return []

    index = load_faiss_index_cached(index_path)

    if index.ntotal != len(chunks):
        raise ValueError(
            f"Index contains {index.ntotal} vectors, "
            f"but metadata contains {len(chunks)} chunks. "
            "Rebuild embeddings before searching."
        )

    candidate_count = min(CANDIDATE_COUNT, len(chunks))

    # 1. Keyword retrieval with BM25.


    bm25 = build_bm25_cached(metadata_path)
    bm25_scores = bm25.get_scores(tokenize(question))



    bm25_ranking = sorted(
        range(len(chunks)),
        key=lambda i: bm25_scores[i],
        reverse=True,
    )[:candidate_count]

    # 2. Semantic retrieval with FAISS.
    model = get_embedding_model()

    query_embedding = model.encode(
        [question],
        normalize_embeddings=True,
    ).astype("float32")

    _, semantic_indices = index.search(
        query_embedding,
        candidate_count,
    )

    semantic_ranking = [
        int(i)
        for i in semantic_indices[0]
        if i >= 0
    ]

    # 3. Combine rankings.
    fused_ranking, fused_scores = reciprocal_rank_fusion(
        [bm25_ranking, semantic_ranking]
    )

    # 4. Rerank the strongest hybrid candidates.
    rerank_count = min(
        RERANK_CANDIDATE_COUNT,
        len(fused_ranking),
    )

    candidate_indices = fused_ranking[:rerank_count]

    pairs = [
        (question, chunks[i]["text"])
        for i in candidate_indices
    ]

    reranker = get_reranker()

    rerank_scores = reranker.predict(
        pairs,
        show_progress_bar=False,
    )

    reranked = sorted(
        zip(candidate_indices, rerank_scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )

    # 5. Return ranked passages with page citations.
    results = []

    for chunk_index, rerank_score in reranked[:top_k]:
        chunk = chunks[chunk_index]

        results.append({
            "page": chunk["page"],
            "text": chunk["text"],
            "rerank_score": float(rerank_score),
            "rrf_score": fused_scores[chunk_index],
        })

    return results


if __name__ == "__main__":
    question = input(
        "Ask a question about the indexed report: "
    ).strip()

    results = search_report(question)

    for number, result in enumerate(results, start=1):
        print(f"\n--- Result {number} ---")
        print(f"Page: {result['page']}")
        print(f"Reranker score: {result['rerank_score']:.4f}")
        print(f"RRF score: {result['rrf_score']:.4f}")
        print(result["text"][:900])
