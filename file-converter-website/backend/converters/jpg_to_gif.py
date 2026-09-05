from pathlib import Path

from PIL import Image


def convert_jpg_to_gif(jpg_path: str, output_path: str) -> str:
    """
    Convert a JPG image into a single-frame GIF.
    """

    jpg_path = Path(jpg_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(jpg_path) as image:
        image.convert("RGB").save(
            output_path,
            "GIF"
        )

    if not output_path.exists():
        raise RuntimeError("GIF file was not created.")

    return str(output_path)