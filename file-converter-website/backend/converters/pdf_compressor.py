from pathlib import Path

import fitz


def compress_pdf(
    input_path: str,
    output_path: str
) -> str:
    """
    Compress a PDF without changing its format.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    document = fitz.open(str(input_path))

    try:
        document.save(
            str(output_path),
            garbage=4,
            deflate=True,
            clean=True
        )

    finally:
        document.close()

    if not output_path.exists():
        raise RuntimeError(
            "Compressed PDF was not created."
        )

    return str(output_path)