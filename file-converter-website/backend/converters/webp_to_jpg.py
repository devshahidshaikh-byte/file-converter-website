from pathlib import Path

from PIL import Image


def convert_webp_to_jpg(
    webp_path: str,
    output_path: str
) -> str:
    """
    Convert a WEBP image into a JPG image.
    """

    webp_path = Path(webp_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(webp_path) as image:
        # JPG does not support transparency.
        # Use a white background when the WEBP has transparency.
        if image.mode in ("RGBA", "LA") or (
            image.mode == "P" and "transparency" in image.info
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