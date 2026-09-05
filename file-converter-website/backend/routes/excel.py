from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from converters.excel_to_pdf import convert_excel_to_pdf

from utils.file_handler import create_job_directories
from utils.validator import MAX_FILE_SIZE, validate_file_extension
from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/excel",
    tags=["Excel"]
)


# ---------------------------------------
# EXCEL → PDF
# ---------------------------------------

@router.post("/to-pdf")
async def excel_to_pdf(
    file: UploadFile = File(
        ...,
        description="Select an Excel XLSX file"
    )
):

    # -----------------------------------
    # CHECK FILE NAME
    # -----------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Please select an Excel file."
        )

    # -----------------------------------
    # CHECK FILE EXTENSION
    # -----------------------------------

    try:

        validate_file_extension(
            file.filename,
            [".xlsx"]
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # -----------------------------------
    # CREATE TEMPORARY DIRECTORIES
    # -----------------------------------

    (
        job_id,
        upload_directory,
        output_directory
    ) = create_job_directories()

    input_path = (
        upload_directory / "input.xlsx"
    )

    try:

        # -----------------------------------
        # SAVE UPLOADED FILE
        # -----------------------------------

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
                        detail=(
                            "The Excel file is "
                            "larger than the allowed "
                            "file size."
                        )
                    )

                buffer.write(chunk)

        # -----------------------------------
        # CONVERT EXCEL → PDF
        # -----------------------------------

        output_pdf = convert_excel_to_pdf(
            str(input_path),
            str(output_directory)
        )

        # -----------------------------------
        # CHECK OUTPUT
        # -----------------------------------

        if not Path(output_pdf).exists():

            raise HTTPException(
                status_code=500,
                detail="PDF was not created."
            )

        # -----------------------------------
        # RETURN PDF
        # -----------------------------------

        return FileResponse(
            path=output_pdf,
            media_type="application/pdf",
            filename="converted.pdf",

            background=BackgroundTask(
                cleanup_job,
                upload_directory,
                output_directory
            )
        )

    # -----------------------------------
    # HTTP ERROR
    # -----------------------------------

    except HTTPException:

        cleanup_job(
            upload_directory,
            output_directory
        )

        raise

    # -----------------------------------
    # CONVERSION ERROR
    # -----------------------------------

    except Exception as error:

        print(
            f"Excel to PDF error: {error}"
        )

        cleanup_job(
            upload_directory,
            output_directory
        )

        raise HTTPException(
            status_code=500,
            detail="Excel to PDF conversion failed."
        )