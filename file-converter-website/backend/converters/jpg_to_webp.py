from pathlib import Path

from PIL import Image


def convert_jpg_to_webp(
    jpg_path: str,
    output_path: str
) -> str:
    """
    Convert a JPG or JPEG image into WEBP format.
    """

    jpg_path = Path(jpg_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with Image.open(jpg_path) as image:

        # JPG does not support transparency.
        # RGB is the correct color mode for JPG → WEBP.
        image.convert("RGB").save(
            output_path,
            "WEBP",
            quality=90
        )

    if not output_path.exists():
        raise RuntimeError(
            "WEBP file was not created."
        )

    return str(output_path)