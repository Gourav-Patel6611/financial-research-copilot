
from generate_answer import generate_answer

answer = generate_answer(
    question=(
        "What was Reliance Industries' consolidated "
        "revenue from operations in FY 2024-25?"
    ),
    index_path="data/uploads/reliance_test/faiss.index",
    metadata_path="data/uploads/reliance_test/chunk_metadata.json",
)

print("\n===== DOCUMENT-SPECIFIC ANSWER =====\n")
print(answer)
