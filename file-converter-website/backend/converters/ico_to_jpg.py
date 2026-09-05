from pathlib import Path
from PIL import Image


def convert_ico_to_jpg(ico_path: str, output_path: str) -> str:
    ico_path = Path(ico_path)
    output_path = Path(output_path)

    with Image.open(ico_path) as image:
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

    return str(output_path)