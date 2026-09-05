import fitz
from pathlib import Path


def convert_pdf_to_text(pdf_path: str, output_path: str) -> str:
    """
    Extract text from a PDF and save it as a TXT file.
    """

    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    document = fitz.open(pdf_path)

    try:
        text = "\n\n".join(
            page.get_text("text")
            for page in document
        )

        output_path.write_text(text, encoding="utf-8")

        return str(output_path)

    finally:
        document.close()