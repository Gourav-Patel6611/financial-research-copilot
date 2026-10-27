
from document_pipeline import process_document


if __name__ == "__main__":
    result = process_document(
        pdf_path="data/raw/report.pdf",
        document_id="reliance_test",
    )

    print("\nDocument processed successfully:")
    for key, value in result.items():
        print(f"{key}: {value}")
