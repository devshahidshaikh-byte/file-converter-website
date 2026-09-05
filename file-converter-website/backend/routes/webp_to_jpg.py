from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from converters.webp_to_jpg import convert_webp_to_jpg
from utils.file_handler import create_job_directories
from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/image",
    tags=["Image"],
)


@router.post("/webp-to-jpg")
async def webp_to_jpg(
    file: UploadFile = File(...)
):
    """
    Convert one WEBP image into a JPG image.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a WEBP file."
        )

    extension = Path(file.filename).suffix.lower()

    if extension != ".webp":
        raise HTTPException(
            status_code=400,
            detail="Only WEBP files are supported."
        )

    job_id, upload_dir, output_dir = create_job_directories()

    try:
        input_path = upload_dir / "input.webp"
        output_path = output_dir / "converted.jpg"

        # Save uploaded WEBP
        with open(input_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                buffer.write(chunk)

        # Convert WEBP to JPG
        jpg_path = convert_webp_to_jpg(
            str(input_path),
            str(output_path)
        )

        return FileResponse(
            path=jpg_path,
            media_type="image/jpeg",
            filename=f"{Path(file.filename).stem}.jpg",
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