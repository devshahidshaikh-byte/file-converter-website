import shutil
import subprocess
from pathlib import Path


def convert_word_to_pdf(
    input_path: str,
    output_directory: str
):
    """
    Convert a DOCX Word document to PDF
    using LibreOffice.
    """

    input_file = Path(input_path)
    output_dir = Path(output_directory)

    # ---------------------------------------
    # CHECK INPUT
    # ---------------------------------------

    if not input_file.exists():
        raise FileNotFoundError(
            "Word document was not found."
        )

    # ---------------------------------------
    # CREATE OUTPUT DIRECTORY
    # ---------------------------------------

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # ---------------------------------------
    # FIND LIBREOFFICE
    # ---------------------------------------

    libreoffice = shutil.which("soffice")

    if libreoffice is None:
        libreoffice = shutil.which("libreoffice")

    # Windows fallback
    if libreoffice is None:

        possible_paths = [
            Path(
                r"C:\Program Files\LibreOffice\program\soffice.exe"
            ),
            Path(
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
            )
        ]

        for path in possible_paths:

            if path.exists():
                libreoffice = str(path)
                break

    # ---------------------------------------
    # CHECK LIBREOFFICE
    # ---------------------------------------

    if libreoffice is None:

        raise RuntimeError(
            "LibreOffice was not found."
        )

    # ---------------------------------------
    # CONVERT DOCX → PDF
    # ---------------------------------------

    command = [
        libreoffice,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_dir),
        str(input_file)
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    # ---------------------------------------
    # CHECK PROCESS
    # ---------------------------------------

    if result.returncode != 0:

        raise RuntimeError(
            result.stderr
            or "Word to PDF conversion failed."
        )

    # ---------------------------------------
    # FIND GENERATED PDF
    # ---------------------------------------

    output_pdf = (
        output_dir
        / f"{input_file.stem}.pdf"
    )

    if not output_pdf.exists():

        raise RuntimeError(
            "LibreOffice did not create "
            "the PDF file."
        )

    return str(output_pdf)