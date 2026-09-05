import os
import subprocess
from pathlib import Path


def convert_ppt_to_pdf(ppt_path: str, output_dir: str) -> str:
    """
    Convert a PowerPoint file (.ppt or .pptx) to PDF
    using LibreOffice.
    """

    ppt_path = Path(ppt_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # LibreOffice executable location
    libreoffice_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]

    soffice = None

    for path in libreoffice_paths:
        if os.path.exists(path):
            soffice = path
            break

    if soffice is None:
        raise FileNotFoundError(
            "LibreOffice is not installed or its executable was not found."
        )

    # Convert PPT/PPTX to PDF
    command = [
        soffice,
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output_dir),
        str(ppt_path),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice conversion failed: {result.stderr}"
        )

    # LibreOffice creates a PDF with the same filename
    generated_pdf = output_dir / f"{ppt_path.stem}.pdf"

    if not generated_pdf.exists():
        raise RuntimeError("PDF was not created.")

    return str(generated_pdf)