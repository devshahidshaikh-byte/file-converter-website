import shutil
import subprocess
from pathlib import Path


def convert_excel_to_pdf(
    input_path: str,
    output_directory: str
):
    """
    Convert an Excel workbook (.xlsx) to PDF
    using LibreOffice.

    Parameters:
        input_path:
            Path to the Excel file.

        output_directory:
            Directory where the PDF will be created.

    Returns:
        Path to the generated PDF.
    """

    input_file = Path(input_path)
    output_dir = Path(output_directory)

    # ---------------------------------------
    # CHECK INPUT
    # ---------------------------------------

    if not input_file.exists():
        raise FileNotFoundError(
            "Excel file was not found."
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

    libreoffice = shutil.which(
        "libreoffice"
    )

    if libreoffice is None:
        libreoffice = shutil.which(
            "soffice"
        )

    # Windows installation locations
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
            "LibreOffice is not installed. "
            "Excel to PDF conversion requires "
            "LibreOffice."
        )

    # ---------------------------------------
    # CONVERT EXCEL → PDF
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
    # CHECK CONVERSION RESULT
    # ---------------------------------------

    if result.returncode != 0:

        raise RuntimeError(
            result.stderr
            or "Excel to PDF conversion failed."
        )

    # ---------------------------------------
    # FIND GENERATED PDF
    # ---------------------------------------

    expected_pdf = (
        output_dir
        / f"{input_file.stem}.pdf"
    )

    if not expected_pdf.exists():

        raise RuntimeError(
            "LibreOffice did not create "
            "the expected PDF file."
        )

    return str(expected_pdf)