
import pymupdf
from pathlib import Path


def extract_text(pdf_path, output_path):
    """Extract text from a PDF and preserve page numbers."""

    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Please provide a PDF file.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pymupdf.open(pdf_path) as document:
        with open(output_path, "w", encoding="utf-8") as file:
            for page_number, page in enumerate(document, start=1):
                text = page.get_text()

                file.write(f"\n--- Page {page_number} ---\n")
                file.write(text)
                file.write("\n")

    print(f"Extraction complete. Saved to: {output_path}")


if __name__ == "__main__":
    extract_text(
        "data/raw/report.pdf",
        "data/processed/extracted_text.txt",
    )
