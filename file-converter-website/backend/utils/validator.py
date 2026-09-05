from pathlib import Path


# Maximum size for one uploaded file.
# Change this later if you want.
from config import MAX_FILE_SIZE


ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}

ALLOWED_PDF_EXTENSIONS = {
    ".pdf",
}

ALLOWED_DOCUMENT_EXTENSIONS = {
    ".doc",
    ".docx",
}

ALLOWED_EXCEL_EXTENSIONS = {
    ".xls",
    ".xlsx",
}

ALLOWED_POWERPOINT_EXTENSIONS = {
    ".ppt",
    ".pptx",
}


def get_extension(filename: str) -> str:
    """
    Get a file's extension in lowercase.
    """

    return Path(filename).suffix.lower()


def is_allowed_extension(
    filename: str,
    allowed_extensions: set[str]
) -> bool:
    """
    Check whether a filename has an allowed extension.
    """

    extension = get_extension(filename)

    return extension in allowed_extensions


def validate_file_extension(
    filename: str,
    allowed_extensions: set[str]
) -> None:
    """
    Raise an error if the file extension isn't allowed.
    """

    if not filename:
        raise ValueError("Filename is missing.")

    extension = get_extension(filename)

    if extension not in allowed_extensions:
        allowed = ", ".join(
            sorted(allowed_extensions)
        )

        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Allowed types: {allowed}"
        )


def validate_file_size(file_size: int) -> None:
    """
    Validate uploaded file size.
    """

    if file_size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE / (1024 * 1024)

        raise ValueError(
            f"File is too large. "
            f"Maximum size is {max_mb:.0f} MB."
        )