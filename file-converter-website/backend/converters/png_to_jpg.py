from pathlib import Path

from PIL import Image


def convert_png_to_jpg(
    png_path: str,
    output_path: str
) -> str:
    """
    Convert a PNG image into a JPG image.
    Transparent areas are replaced with a white background.
    """

    png_path = Path(png_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(png_path) as image:

        if image.mode in ("RGBA", "LA") or (
            image.mode == "P"
            and "transparency" in image.info
        ):
            image = image.convert("RGBA")

            background = Image.new(
                "RGB",
                image.size,
                "white"
            )

            background.paste(
                image,
                mask=image.getchannel("A")
            )

            background.save(
                output_path,
                "JPEG",
                quality=95
            )

        else:
            image.convert("RGB").save(
                output_path,
                "JPEG",
                quality=95
            )

    if not output_path.exists():
        raise RuntimeError("JPG file was not created.")

    return str(output_path)