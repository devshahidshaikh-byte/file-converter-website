from pathlib import Path

import fitz
from PIL import Image
from pptx import Presentation
from pptx.util import Inches


def convert_pdf_to_ppt(pdf_path: str, output_path: str) -> str:
    """
    Convert each PDF page into an image on a PowerPoint slide.
    The resulting PPTX preserves the page appearance.
    """

    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    document = fitz.open(str(pdf_path))
    presentation = Presentation()

    # Remove the default blank slide
    if presentation.slides:
        first_slide = presentation.slides[0]
        relationship = first_slide.part.rels.get(
            first_slide.part.slide_id
        )
        if relationship:
            presentation.part.drop_rel(relationship.rId)

    # Use widescreen presentation size
    presentation.slide_width = Inches(13.333333)
    presentation.slide_height = Inches(7.5)

    blank_layout = presentation.slide_layouts[6]

    try:
        for page_number, page in enumerate(document):
            # Render PDF page as an image
            matrix = fitz.Matrix(2, 2)
            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            image_path = output_path.parent / (
                f"page_{page_number + 1}.png"
            )

            pixmap.save(str(image_path))

            # Add a blank slide
            slide = presentation.slides.add_slide(blank_layout)

            # Add the page image to fill the slide
            slide.shapes.add_picture(
                str(image_path),
                0,
                0,
                width=presentation.slide_width,
                height=presentation.slide_height,
            )

            # Remove temporary page image
            image_path.unlink(missing_ok=True)

        presentation.save(str(output_path))

    finally:
        document.close()

    if not output_path.exists():
        raise RuntimeError("PowerPoint file was not created.")

    return str(output_path)