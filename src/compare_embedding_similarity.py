
import json
import numpy as np
from sentence_transformers import SentenceTransformer

METADATA_PATH = "data/processed/chunk_metadata.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

QUESTION = (
    "List the four segments reported by Reliance Industries "
    "for FY2024-25."
)

with open(METADATA_PATH, "r", encoding="utf-8") as file:
    chunks = json.load(file)

# Find the passage that explicitly identifies the four segments.
relevant = [
    chunk for chunk in chunks
    if "four principal operating and reporting segments" in chunk["text"].lower()
]

if not relevant:
    raise ValueError("Could not find the known relevant passage.")

# Find a previously irrelevant result from page 28.
irrelevant = [
    chunk for chunk in chunks
    if chunk["page"] == 28
    and "committee" in chunk["text"].lower()
]

if not irrelevant:
    raise ValueError(
        "Could not find the comparison passage on page 28. "
        "Check the previous search output."
    )

relevant_chunk = relevant[0]
irrelevant_chunk = irrelevant[0]

print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

texts = [
    QUESTION,
    relevant_chunk["text"],
    irrelevant_chunk["text"],
]

vectors = model.encode(
    texts,
    normalize_embeddings=True,
    convert_to_numpy=True,
).astype("float32")

query_vector = vectors[0]

relevant_score = float(np.dot(query_vector, vectors[1]))
irrelevant_score = float(np.dot(query_vector, vectors[2]))

print("\n--- Comparison ---")
print(f"Question: {QUESTION}")

print(
    f"\nRelevant passage | Page {relevant_chunk['page']} "
    f"| Similarity: {relevant_score:.4f}"
)
print(relevant_chunk["text"].replace("\n", " "))

print(
    f"\nComparison passage | Page {irrelevant_chunk['page']} "
    f"| Similarity: {irrelevant_score:.4f}"
)
print(irrelevant_chunk["text"][:350].replace("\n", " "))

print("\n--- Interpretation ---")
if relevant_score > irrelevant_score:
    print("The model prefers the relevant passage in this comparison.")
elif relevant_score < irrelevant_score:
    print("The model prefers the irrelevant passage in this comparison.")
else:
    print("Both passages have equal similarity in this comparison.")
