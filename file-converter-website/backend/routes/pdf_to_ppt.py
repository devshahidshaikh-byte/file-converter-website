from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from converters.pdf_to_ppt import convert_pdf_to_ppt
from utils.file_handler import create_job_directories
from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/pdf",
    tags=["PDF"],
)


@router.post("/to-ppt")
async def pdf_to_ppt(
    file: UploadFile = File(...)
):
    """
    Convert one PDF file into a PowerPoint presentation.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file."
        )

    extension = Path(file.filename).suffix.lower()

    if extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    job_id, upload_dir, output_dir = create_job_directories()

    try:
        input_path = upload_dir / "input.pdf"
        output_path = output_dir / "converted.pptx"

        # Save uploaded PDF
        with open(input_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                buffer.write(chunk)

        # Convert PDF to PPTX
        ppt_path = convert_pdf_to_ppt(
            str(input_path),
            str(output_path)
        )

        return FileResponse(
            path=ppt_path,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "presentationml.presentation"
            ),
            filename=f"{Path(file.filename).stem}.pptx",
            background=BackgroundTask(
                cleanup_job,
                job_id
            )
        )

    except HTTPException:
        cleanup_job(job_id)
        raise

    except Exception as e:
        cleanup_job(job_id)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )