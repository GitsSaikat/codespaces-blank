# src/utils/helpers.py

import pandas as pd
import logging
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def read_excel(file_path: str) -> pd.DataFrame:
    """
    Reads an Excel file and returns a pandas DataFrame.

    :param file_path: Path to the Excel file.
    :return: pandas DataFrame.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
        logger.info(f"Excel file '{file_path}' read successfully.")
        return df
    except Exception as e:
        logger.error(f"Error reading Excel file '{file_path}': {e}")
        raise IOError(f"Error reading Excel file: {e}")


def save_pdf(file_path: str, content: str):
    """
    Saves content to a PDF file using ReportLab.

    :param file_path: Path to save the PDF.
    :param content: Content to write into the PDF.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        textobject = c.beginText(50, height - 50)
        textobject.setFont("Helvetica", 12)

        for line in content.split('\n'):
            textobject.textLine(line)
        c.drawText(textobject)
        c.showPage()
        c.save()
        logger.info(f"PDF saved successfully at {file_path}.")
    except ImportError:
        logger.error("ReportLab library is not installed.")
        raise
    except Exception as e:
        logger.error(f"Failed to save PDF: {e}")
        raise
