from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from converters.png_to_jpg import convert_png_to_jpg
from utils.file_handler import create_job_directories
from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/image",
    tags=["Image"],
)


@router.post("/png-to-jpg")
async def png_to_jpg(
    file: UploadFile = File(...)
):
    """
    Convert one PNG image into a JPG image.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PNG file."
        )

    extension = Path(file.filename).suffix.lower()

    if extension != ".png":
        raise HTTPException(
            status_code=400,
            detail="Only PNG files are supported."
        )

    job_id, upload_dir, output_dir = create_job_directories()

    try:
        input_path = upload_dir / "input.png"
        output_path = output_dir / "converted.jpg"

        # Save uploaded PNG
        with open(input_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                buffer.write(chunk)

        # Convert PNG to JPG
        jpg_path = convert_png_to_jpg(
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