from pathlib import Path
import shutil
import uuid


BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"


UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def create_job_directories() -> tuple[str, Path, Path]:
    """
    Create a unique directory for one conversion job.

    Returns:
        job_id
        upload directory
        output directory
    """

    job_id = uuid.uuid4().hex

    upload_directory = UPLOAD_DIR / job_id
    output_directory = OUTPUT_DIR / job_id

    upload_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return (
        job_id,
        upload_directory,
        output_directory
    )


def save_uploaded_file(
    source_file,
    destination: Path
) -> Path:
    """
    Save an uploaded file to the specified location.
    """

    with destination.open("wb") as buffer:
        shutil.copyfileobj(
            source_file,
            buffer
        )

    return destination


def safe_filename(filename: str) -> str:
    """
    Create a simple safe filename.

    We don't use the original filename directly
    as the server-side filename.
    """

    original = Path(filename)

    extension = original.suffix.lower()

    return f"file{extension}"