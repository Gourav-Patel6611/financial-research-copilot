
from search import search_report

results = search_report(
    question=(
        "What was Reliance Industries' consolidated "
        "revenue from operations in FY 2024-25?"
    ),
    top_k=3,
    index_path="data/uploads/reliance_test/faiss.index",
    metadata_path="data/uploads/reliance_test/chunk_metadata.json",
)

for result in results:
    print(f"\nPage: {result['page']}")
    print(result["text"][:500])
