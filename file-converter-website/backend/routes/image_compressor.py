from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from converters.image_compressor import compress_image

from utils.file_handler import create_job_directories

from utils.validator import MAX_FILE_SIZE

from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/image",
    tags=["Image"]
)


# =========================================================
# IMAGE COMPRESSOR
# =========================================================

@router.post(
    "/compress",
    summary="Image Compressor",
    description="Compress a JPG, PNG, or WEBP image."
)
async def image_compressor(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select an image."
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG, and WEBP images are supported."
        )

    (
        job_id,
        upload_directory,
        output_directory
    ) = create_job_directories()

    input_path = upload_directory / f"input{extension}"
    output_path = output_directory / f"compressed{extension}"

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

        compress_image(
            str(input_path),
            str(output_path)
        )

        if not output_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Compressed image was not created."
            )

        return FileResponse(
            path=str(output_path),
            media_type=file.content_type or "application/octet-stream",
            filename=f"compressed{extension}",

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
            f"Image compression error: {error}"
        )

        cleanup_job(
            upload_directory,
            output_directory
        )

        raise HTTPException(
            status_code=500,
            detail="Image compression failed."
        )