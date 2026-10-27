
import json
import faiss
from sentence_transformers import SentenceTransformer

INDEX_PATH = "data/processed/faiss.index"
METADATA_PATH = "data/processed/chunk_metadata.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
question = (
    "The Group has four principal operating and reporting "
    "segments; viz. Oil To Chemicals (O2C), Oil and Gas, "
    "Retail and Digital Services."
)

with open(METADATA_PATH, "r", encoding="utf-8") as file:
    chunks = json.load(file)

index = faiss.read_index(INDEX_PATH)
model = SentenceTransformer(MODEL_NAME)

query_vector = model.encode(
    [question],
    normalize_embeddings=True,
).astype("float32")

scores, indices = index.search(query_vector, 10)

for rank, (score, index_id) in enumerate(
    zip(scores[0], indices[0]), start=1
):
    if index_id < 0:
        continue

    chunk = chunks[int(index_id)]

    print(
        f"\nRank {rank} | Score {score:.4f} "
        f"| Chunk {index_id + 1} | Page {chunk['page']}"
    )
    print(chunk["text"][:350].replace("\n", " "))
