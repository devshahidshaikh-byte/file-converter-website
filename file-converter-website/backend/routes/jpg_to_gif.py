from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from converters.jpg_to_gif import convert_jpg_to_gif
from utils.file_handler import create_job_directories
from utils.cleanup import cleanup_job


router = APIRouter(
    prefix="/api/image",
    tags=["Image"],
)


@router.post("/jpg-to-gif")
async def jpg_to_gif(
    file: UploadFile = File(...)
):
    """
    Convert one JPG or JPEG file into a GIF image.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a JPG file."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in [".jpg", ".jpeg"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and JPEG files are supported."
        )

    job_id, upload_dir, output_dir = create_job_directories()

    try:
        input_path = upload_dir / f"input{extension}"
        output_path = output_dir / "converted.gif"

        # Save uploaded JPG
        with open(input_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                buffer.write(chunk)

        # Convert JPG to GIF
        gif_path = convert_jpg_to_gif(
            str(input_path),
            str(output_path)
        )

        return FileResponse(
            path=gif_path,
            media_type="image/gif",
            filename=f"{Path(file.filename).stem}.gif",
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