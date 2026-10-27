
from pathlib import Path
import re

CHUNK_SIZE = 1200


def split_into_pages(text):
    """Split extracted text into page-numbered sections."""
    pages = re.split(r"--- Page (\d+) ---", text)
    page_data = []

    for i in range(1, len(pages), 2):
        page_number = int(pages[i])
        page_text = pages[i + 1].strip()

        if page_text:
            page_data.append((page_number, page_text))

    return page_data


def split_into_blocks(page_text):
    """Split page text into non-empty paragraphs."""
    blocks = re.split(r"\n\s*\n", page_text.strip())
    return [block.strip() for block in blocks if block.strip()]


def create_chunks(page_data, chunk_size=CHUNK_SIZE):
    """Create text chunks while preserving their source page numbers."""
    chunks = []

    for page_number, page_text in page_data:
        blocks = split_into_blocks(page_text)
        current_blocks = []
        current_length = 0

        for block in blocks:
            if len(block) > chunk_size:
                if current_blocks:
                    chunks.append({
                        "page": page_number,
                        "text": "\n\n".join(current_blocks).strip()
                    })
                    current_blocks = []
                    current_length = 0

                start = 0
                while start < len(block):
                    piece = block[start:start + chunk_size].strip()

                    if piece:
                        chunks.append({
                            "page": page_number,
                            "text": piece
                        })

                    start += chunk_size

                continue

            block_length = len(block) + 2

            if (
                current_blocks
                and current_length + block_length > chunk_size
            ):
                chunks.append({
                    "page": page_number,
                    "text": "\n\n".join(current_blocks).strip()
                })
                current_blocks = []
                current_length = 0

            current_blocks.append(block)
            current_length += block_length

        if current_blocks:
            chunks.append({
                "page": page_number,
                "text": "\n\n".join(current_blocks).strip()
            })

    return chunks


def save_chunks(chunks, output_path):
    """Save chunks in a readable format."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for number, chunk in enumerate(chunks, start=1):
            file.write(
                f"--- Chunk {number} | Page {chunk['page']} ---\n"
            )
            file.write(chunk["text"])
            file.write("\n\n")

    print(f"Chunks created: {len(chunks)}")
    print(f"Saved to: {output_path}")


def process_text_file(input_path, output_path):
    """Process an extracted-text file from any PDF."""
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Extracted text not found: {input_path}")

    text = input_path.read_text(encoding="utf-8")
    pages = split_into_pages(text)
    chunks = create_chunks(pages)

    save_chunks(chunks, output_path)

    print(f"Pages processed: {len(pages)}")


def main():
    process_text_file(
        "data/processed/extracted_text.txt",
        "data/processed/chunks.txt",
    )


if __name__ == "__main__":
    main()
