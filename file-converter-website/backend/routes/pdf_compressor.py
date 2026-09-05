from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from converters.pdf_compressor import compress_pdf

from utils.file_handler import create_job_directories

from utils.validator import MAX_FILE_SIZE

from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/pdf",
    tags=["PDF"]
)


# =========================================================
# PDF COMPRESSOR
# =========================================================

@router.post(
    "/compress",
    summary="PDF Compressor",
    description="Compress a PDF file while keeping it as a PDF."
)
async def pdf_compressor(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a PDF file."
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    (
        job_id,
        upload_directory,
        output_directory
    ) = create_job_directories()

    input_path = upload_directory / "input.pdf"
    output_path = output_directory / "compressed.pdf"

    try:

        total_size = 0

        with input_path.open("wb") as buffer:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="File is too large."
                    )

                buffer.write(chunk)

        compress_pdf(
            str(input_path),
            str(output_path)
        )

        if not output_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Compressed PDF was not created."
            )

        return FileResponse(
            path=str(output_path),
            media_type="application/pdf",
            filename="compressed.pdf",

            background=BackgroundTask(
                cleanup_job,
                upload_directory,
                output_directory
            )
        )

    except HTTPException:

        cleanup_job(
            upload_directory,
            output_directory
        )

        raise

    except Exception as error:

        print(
            f"PDF compression error: {error}"
        )

        cleanup_job(
            upload_directory,
            output_directory
        )

        raise HTTPException(
            status_code=500,
            detail="PDF compression failed."
        )   