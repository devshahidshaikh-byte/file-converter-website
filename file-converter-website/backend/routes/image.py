from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from converters.ico_to_jpg import convert_ico_to_jpg

from utils.file_handler import create_job_directories

from utils.validator import MAX_FILE_SIZE

from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/image",
    tags=["Image"]
)


# =========================================================
# ICO → JPG
# =========================================================

@router.post("/ico-to-jpg")
async def ico_to_jpg(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select an ICO image."
        )

    if not file.filename.lower().endswith(".ico"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an ICO image."
        )

    (
        job_id,
        upload_directory,
        output_directory
    ) = create_job_directories()

    ico_path = upload_directory / "input.ico"
    output_jpg = output_directory / "converted.jpg"

    try:

        total_size = 0

        with ico_path.open("wb") as buffer:

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

        convert_ico_to_jpg(
            str(ico_path),
            str(output_jpg)
        )

        if not output_jpg.exists():
            raise HTTPException(
                status_code=500,
                detail="JPG was not created."
            )

        return FileResponse(
            path=str(output_jpg),
            media_type="image/jpeg",
            filename="converted.jpg",

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
            f"ICO to JPG error: {error}"
        )

        cleanup_job(
            upload_directory,
            output_directory
        )

        raise HTTPException(
            status_code=500,
            detail="ICO to JPG conversion failed."
        )