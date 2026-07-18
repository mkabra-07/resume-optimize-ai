import subprocess
from config import settings
import os

def export_pdf(docx_path: str, output_dir: str) -> str:
    try:
        subprocess.run([settings.LIBREOFFICE_PATH, '--headless', '--convert-to', 'pdf', docx_path, '--outdir', output_dir], check=True)
        pdf_filename = os.path.basename(docx_path).replace(".docx", ".pdf")
        return os.path.join(output_dir, pdf_filename)
    except Exception as e:
        # Fallback or log if libreoffice is missing
        return None
