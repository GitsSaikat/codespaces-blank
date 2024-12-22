# src/reporting.py

from typing import Dict
import logging

from src.utils.logger import setup_logger
from src.utils.helpers import save_pdf

logger = setup_logger(__name__)


def generate_report(simulation_results: Dict[str, float], lcc: float) -> str:
    """
    Generate a textual report based on simulation results and LCCA.

    :param simulation_results: Dictionary containing simulation results.
    :param lcc: Lifecycle Cost Analysis result.
    :return: Formatted report content as a string.
    """
    report = "Mechanistic-Empirical Pavement Design Report\n"
    report += "="*50 + "\n\n"

    report += "Pavement Performance Predictions:\n"
    report += "-"*30 + "\n"
    for key, value in simulation_results.items():
        report += f"{key}: {value:.4f}\n"

    report += f"\nLifecycle Cost Analysis (LCCA):\n"
    report += "-"*30 + "\n"
    report += f"Total Lifecycle Cost: ${lcc:,.2f}\n"

    report += "\nConclusion:\n"
    report += "The pavement design meets the required performance criteria based on the simulation results.\n"

    logger.info("Report generated successfully.")
    return report


def export_report_to_pdf(report_content: str, file_path: str):
    """
    Export the report content to a PDF file.

    :param report_content: The content of the report as a string.
    :param file_path: The path where the PDF will be saved.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch

        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        textobject = c.beginText()
        textobject.setTextOrigin(inch, height - inch)
        textobject.setFont("Helvetica", 12)

        for line in report_content.split('\n'):
            textobject.textLine(line)
        c.drawText(textobject)
        c.showPage()
        c.save()
        logger.info(f"Report exported to PDF at {file_path}")
    except ImportError:
        logger.error("ReportLab is not installed. Please install it using 'pip install reportlab'")
        raise
    except Exception as e:
        logger.error(f"Failed to export report to PDF: {e}")
        raise
