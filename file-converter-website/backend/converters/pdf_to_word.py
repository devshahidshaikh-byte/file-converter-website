from pathlib import Path

import fitz
from docx import Document


def convert_pdf_to_word(pdf_path: str, output_path: str) -> str:
    """
    Convert selectable text from a PDF into a Word document.
    """

    pdf_path = Path(pdf_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    document = fitz.open(str(pdf_path))
    word_document = Document()

    try:
        for page_number, page in enumerate(document):
            text = page.get_text("text")

            if text.strip():
                word_document.add_paragraph(text)

            # Add a page break between PDF pages
            if page_number < len(document) - 1:
                word_document.add_page_break()

        word_document.save(str(output_path))

    finally:
        document.close()

    if not output_path.exists():
        raise RuntimeError("Word file was not created.")

    return str(output_path)