import pymupdf
from pathlib import Path


def convert_pdf_to_jpg(
    pdf_path: str,
    output_directory: str
) -> list[str]:

    pdf_file = Path(pdf_path)
    output_dir = Path(output_directory)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    generated_files = []

    document = pymupdf.open(pdf_file)

    try:

        for page_number in range(len(document)):

            page = document.load_page(
                page_number
            )

            matrix = pymupdf.Matrix(
                2,
                2
            )

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            output_file = (
                output_dir
                / f"{pdf_file.stem}_page_{page_number + 1}.jpg"
            )

            pixmap.save(
                str(output_file)
            )

            generated_files.append(
                str(output_file)
            )

    finally:

        document.close()

    return generated_files