from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from converters.jpg_to_webp import convert_jpg_to_webp

from utils.file_handler import create_job_directories

from utils.validator import MAX_FILE_SIZE

from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/image",
    tags=["Image"]
)


# =========================================================
# JPG → WEBP
# =========================================================

@router.post(
    "/jpg-to-webp",
    summary="JPG To Webp",
    description="Convert one JPG or JPEG image into WEBP format."
)
async def jpg_to_webp(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a JPG image."
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in [".jpg", ".jpeg"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and JPEG files are supported."
        )

    (
        job_id,
        upload_directory,
        output_directory
    ) = create_job_directories()

    jpg_path = upload_directory / f"input{extension}"
    output_webp = output_directory / "converted.webp"

    try:

        total_size = 0

        with jpg_path.open("wb") as buffer:

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

        convert_jpg_to_webp(
            str(jpg_path),
            str(output_webp)
        )

        if not output_webp.exists():
            raise HTTPException(
                status_code=500,
                detail="WEBP was not created."
            )

        return FileResponse(
            path=str(output_webp),
            media_type="image/webp",
            filename="converted.webp",

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
            f"JPG to WEBP error: {error}"
        )

        cleanup_job(
            upload_directory,
            output_directory
        )

        raise HTTPException(
            status_code=500,
            detail="JPG to WEBP conversion failed."
        )