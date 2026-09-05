from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from pathlib import Path
import zipfile

from converters.pdf_to_jpg import convert_pdf_to_jpg

from utils.file_handler import create_job_directories

from utils.validator import (
    ALLOWED_PDF_EXTENSIONS,
    MAX_FILE_SIZE,
    validate_file_extension
)

from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/pdf",
    tags=["PDF"]
)


@router.post("/to-jpg")
async def pdf_to_jpg(
    file: UploadFile = File(
        ...,
        description="Select a PDF file"
    )
):
    """
    Convert a PDF into JPG images.
    """

    # -----------------------------------
    # CHECK FILE
    # -----------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Please select a PDF file."
        )

    try:

        validate_file_extension(
            file.filename,
            ALLOWED_PDF_EXTENSIONS
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # -----------------------------------
    # CREATE JOB
    # -----------------------------------

    (
        job_id,
        upload_directory,
        output_directory
    ) = create_job_directories()

    pdf_path = (
        upload_directory / "input.pdf"
    )

    try:

        # -----------------------------------
        # SAVE PDF
        # -----------------------------------

        total_size = 0

        with pdf_path.open("wb") as buffer:

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
                        detail=(
                            "The PDF is larger than "
                            "the allowed file size."
                        )
                    )

                buffer.write(chunk)

        # -----------------------------------
        # CONVERT PDF
        # -----------------------------------

        generated_files = convert_pdf_to_jpg(
            str(pdf_path),
            str(output_directory)
        )

        if not generated_files:

            raise HTTPException(
                status_code=500,
                detail="No pages were found in the PDF."
            )

        # -----------------------------------
        # ONE PAGE → JPG
        # -----------------------------------

        if len(generated_files) == 1:

            return FileResponse(
                path=generated_files[0],
                media_type="image/jpeg",
                filename=Path(
                    generated_files[0]
                ).name,

                background=BackgroundTask(
                    cleanup_job,
                    upload_directory,
                    output_directory
                )
            )

        # -----------------------------------
        # MULTIPLE PAGES → ZIP
        # -----------------------------------

        zip_path = (
            output_directory
            / "converted_images.zip"
        )

        with zipfile.ZipFile(
            zip_path,
            "w",
            compression=zipfile.ZIP_DEFLATED
        ) as zip_file:

            for image_file in generated_files:

                image_path = Path(
                    image_file
                )

                zip_file.write(
                    image_path,
                    arcname=image_path.name
                )

        return FileResponse(
            path=str(zip_path),
            media_type="application/zip",
            filename="converted_images.zip",

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
            f"PDF to JPG error: {error}"
        )

        cleanup_job(
            upload_directory,
            output_directory
        )

        raise HTTPException(
            status_code=500,
            detail="PDF conversion failed."
        )