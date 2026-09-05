from PIL import Image


def load_images(image_paths):
    """
    Load images and convert them to RGB.
    Invalid images are skipped.
    """

    images = []

    for image_path in image_paths:
        try:
            image = Image.open(image_path)
            image = image.convert("RGB")
            images.append(image)

        except Exception as error:
            print(
                f"Skipping '{image_path}': {error}"
            )

    return images


def make_uniform_pages(images):
    """
    Creates PDF pages with the same dimensions.

    The largest image determines the page size.
    Smaller images are resized while keeping
    their original aspect ratio and centered
    on a white background.
    """

    if not images:
        return []

    # Find the largest width and height.
    max_width = max(
        image.width
        for image in images
    )

    max_height = max(
        image.height
        for image in images
    )

    pages = []

    for image in images:

        # Calculate the scaling ratio.
        ratio = min(
            max_width / image.width,
            max_height / image.height
        )

        # Calculate new dimensions.
        new_width = max(
            1,
            int(image.width * ratio)
        )

        new_height = max(
            1,
            int(image.height * ratio)
        )

        # Resize while keeping aspect ratio.
        resized_image = image.resize(
            (
                new_width,
                new_height
            ),
            Image.Resampling.LANCZOS
        )

        # Create a white page.
        page = Image.new(
            "RGB",
            (
                max_width,
                max_height
            ),
            (255, 255, 255)
        )

        # Center the image.
        x = (
            max_width - new_width
        ) // 2

        y = (
            max_height - new_height
        ) // 2

        page.paste(
            resized_image,
            (x, y)
        )

        pages.append(page)

    return pages


def convert_images_to_pdf(
    image_paths,
    output_path
):
    """
    Convert multiple JPG/JPEG/PNG images
    into a single PDF.

    Parameters:
        image_paths: List of image file paths
        output_path: Destination PDF path

    Returns:
        output_path
    """

    # Load images.
    images = load_images(
        image_paths
    )

    if not images:
        raise ValueError(
            "No valid images were found."
        )

    # Create uniform PDF pages.
    pages = make_uniform_pages(
        images
    )

    if not pages:
        raise ValueError(
            "Could not create PDF pages."
        )

    # First page.
    first_page = pages[0]

    # Remaining pages.
    remaining_pages = pages[1:]

    # Save PDF.
    first_page.save(
        output_path,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=remaining_pages
    )

    # Close images to release resources.
    for image in images:
        image.close()

    for page in pages:
        page.close()

    return output_path