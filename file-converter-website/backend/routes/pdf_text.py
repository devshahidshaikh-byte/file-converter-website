from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse
from fastapi import HTTPException

from converters.pdf_to_text import convert_pdf_to_text

router = APIRouter()

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@router.post("/to-text")
async def pdf_to_text(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    file_id = uuid4().hex

    pdf_path = UPLOAD_DIR / f"{file_id}.pdf"
    text_path = OUTPUT_DIR / f"{file_id}.txt"

    try:
        pdf_path.write_bytes(await file.read())

        convert_pdf_to_text(
            str(pdf_path),
            str(text_path)
        )

        return FileResponse(
            path=str(text_path),
            media_type="text/plain",
            filename="converted.txt"
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"PDF to text conversion failed: {error}"
        )

    finally:
        if pdf_path.exists():
            pdf_path.unlink()