from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from converters.ppt_to_pdf import convert_ppt_to_pdf
from utils.file_handler import create_job_directories
from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/ppt",
    tags=["PowerPoint"],
)


@router.post("/to-pdf")
async def ppt_to_pdf(
    files: List[UploadFile] = File(...)
):
    """
    Convert one or more PowerPoint files to PDF.
    """

    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one PowerPoint file."
        )

    # Create a separate temporary job folder
    job_id, upload_dir, output_dir = create_job_directories()

    try:
        # Currently this endpoint converts one PPT file at a time.
        if len(files) > 1:
            raise HTTPException(
                status_code=400,
                detail="Please upload one PowerPoint file at a time."
            )

        uploaded_file = files[0]

        if not uploaded_file.filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename."
            )

        extension = Path(uploaded_file.filename).suffix.lower()

        if extension not in [".ppt", ".pptx"]:
            raise HTTPException(
                status_code=400,
                detail="Only PPT and PPTX files are supported."
            )

        # Save uploaded PowerPoint
        input_path = upload_dir / f"input{extension}"

        with open(input_path, "wb") as buffer:
            while True:
                chunk = await uploaded_file.read(1024 * 1024)

                if not chunk:
                    break

                buffer.write(chunk)

        # Convert to PDF
        pdf_path = convert_ppt_to_pdf(
            str(input_path),
            str(output_dir)
        )

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"{Path(uploaded_file.filename).stem}.pdf",
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