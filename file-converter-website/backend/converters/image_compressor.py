from pathlib import Path

from PIL import Image


def compress_image(
    input_path: str,
    output_path: str,
    quality: int = 75
) -> str:
    """
    Compress a JPG, PNG, or WEBP image.
    The output format is the same as the input format.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    extension = input_path.suffix.lower()

    with Image.open(input_path) as image:

        if extension in [".jpg", ".jpeg"]:

            image.convert("RGB").save(
                output_path,
                "JPEG",
                quality=quality,
                optimize=True
            )

        elif extension == ".png":

            image.save(
                output_path,
                "PNG",
                optimize=True
            )

        elif extension == ".webp":

            image.save(
                output_path,
                "WEBP",
                quality=quality,
                method=6
            )

        else:

            raise ValueError(
                "Only JPG, JPEG, PNG, and WEBP images are supported."
            )

    if not output_path.exists():
        raise RuntimeError(
            "Compressed image was not created."
        )

    return str(output_path)