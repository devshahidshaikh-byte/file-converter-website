from pathlib import Path

from PIL import Image


def convert_gif_to_jpg(gif_path: str, output_path: str) -> str:
    """
    Convert the first frame of a GIF into a JPG image.
    """

    gif_path = Path(gif_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(gif_path) as image:
        # Select the first frame
        image.seek(0)

        # Convert transparency into a white background
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

    if not output_path.exists():
        raise RuntimeError("JPG file was not created.")

    return str(output_path)