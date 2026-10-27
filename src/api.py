
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.document_pipeline import process_document
from src.generate_answer import generate_answer

app = FastAPI(title="Financial Research Copilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


class QuestionRequest(BaseModel):
    question: str


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/documents")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    document_id = uuid.uuid4().hex
    document_dir = UPLOAD_DIR / document_id
    document_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = document_dir / "original.pdf"

    try:
        size = 0

        with pdf_path.open("wb") as destination:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break

                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF exceeds the 25 MB upload limit.",
                    )

                destination.write(chunk)

        if size == 0:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        result = process_document(
            pdf_path=pdf_path,
            document_id=document_id,
            storage_dir=str(UPLOAD_DIR),
        )

        return {
            "document_id": document_id,
            "filename": file.filename,
            "chunk_count": result["chunk_count"],
            "message": "PDF processed and indexed successfully.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not process PDF: {exc}",
        ) from exc
    finally:
        await file.close()


@app.post("/api/documents/{document_id}/questions")
def ask_question(document_id: str, request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if not document_id or any(
        char not in "0123456789abcdef" for char in document_id.lower()
    ):
        raise HTTPException(status_code=400, detail="Invalid document ID.")

    document_dir = UPLOAD_DIR / document_id
    index_path = document_dir / "faiss.index"
    metadata_path = document_dir / "chunk_metadata.json"

    if not index_path.is_file() or not metadata_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Document not found. Please upload the PDF again.",
        )

    try:
        answer = generate_answer(
            question=question,
            index_path=str(index_path),
            metadata_path=str(metadata_path),
        )
        return {"document_id": document_id, "question": question, "answer": answer}

    
    except Exception as exc:
        # Log the actual error in the backend terminal for debugging.
        print(
            f"Question endpoint error: {type(exc).__name__}: {exc}",
            flush=True,
        )

        # Keep the error message shown to the frontend user generic.
        raise HTTPException(
            status_code=503,
            detail=(
                "Answer generation is temporarily unavailable. "
                "Please try again shortly."
            ),
        ) from exc

    