
from search import load_chunks, tokenize, MODEL_NAME, INDEX_PATH
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import faiss

question = input("Enter your search question: ")
chunks = load_chunks()

# Check keyword retrieval.
tokenized_chunks = [tokenize(c["text"]) for c in chunks]
bm25 = BM25Okapi(tokenized_chunks)
bm25_scores = bm25.get_scores(tokenize(question))

keyword_ranking = sorted(
    range(len(chunks)),
    key=lambda i: bm25_scores[i],
    reverse=True
)[:10]

print("\n===== BM25 KEYWORD RESULTS =====")
for rank, i in enumerate(keyword_ranking, start=1):
    print(f"\nRank {rank} | Page {chunks[i]['page']} | "
          f"Score {bm25_scores[i]:.4f}")
    print(chunks[i]["text"][:350].replace("\n", " "))

# Check semantic retrieval.
index = faiss.read_index(str(INDEX_PATH))
model = SentenceTransformer(MODEL_NAME)
query_vector = model.encode(
    [question],
    normalize_embeddings=True
).astype("float32")

scores, indices = index.search(query_vector, 10)

print("\n===== FAISS SEMANTIC RESULTS =====")
for rank, (score, i) in enumerate(
    zip(scores[0], indices[0]), start=1
):
    if i < 0:
        continue

    print(f"\nRank {rank} | Page {chunks[i]['page']} | "
          f"Score {score:.4f}")
    print(chunks[i]["text"][:350].replace("\n", " "))
