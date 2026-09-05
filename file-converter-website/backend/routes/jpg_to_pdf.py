from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from converters.jpg_to_pdf import convert_images_to_pdf

from utils.file_handler import create_job_directories

from utils.validator import (
    MAX_FILE_SIZE,
    validate_file_extension
)

from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/image",
    tags=["Image"]
)


# =========================================================
# JPG → PDF
# =========================================================

@router.post(
    "/to-pdf",
    summary="JPG To PDF",
    description="Convert one or more JPG or JPEG images into one PDF."
)
async def jpg_to_pdf(
    files: list[UploadFile] = File(...)
):

    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please select at least one JPG image."
        )

    (
        job_id,
        upload_directory,
        output_directory
    ) = create_job_directories()

    saved_files = []

    try:

        for index, file in enumerate(files):

            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file."
                )

            extension = Path(
                file.filename
            ).suffix.lower()

            if extension not in [".jpg", ".jpeg"]:
                raise HTTPException(
                    status_code=400,
                    detail="Only JPG and JPEG files are supported."
                )

            destination = (
                upload_directory
                / f"image_{index + 1}{extension}"
            )

            total_size = 0

            with destination.open("wb") as buffer:

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
                            detail=f"{file.filename} is too large."
                        )

                    buffer.write(chunk)

            saved_files.append(destination)

        output_pdf = (
            output_directory
            / "converted_images.pdf"
        )

        convert_images_to_pdf(
            [
                str(path)
                for path in saved_files
            ],
            str(output_pdf)
        )

        if not output_pdf.exists():
            raise HTTPException(
                status_code=500,
                detail="PDF was not created."
            )

        return FileResponse(
            path=str(output_pdf),
            media_type="application/pdf",
            filename="converted_images.pdf",

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
            f"JPG to PDF error: {error}"
        )

        cleanup_job(
            upload_directory,
            output_directory
        )

        raise HTTPException(
            status_code=500,
            detail="JPG to PDF conversion failed."
        )