# Powered by Viddertech

import logging
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)

# Note: This implementation requires Tesseract OCR engine to be installed on the system
# where the bot is running. For Debian/Ubuntu: `sudo apt install tesseract-ocr`
# It also requires poppler-utils for pdf2image: `sudo apt install poppler-utils`

class OcrProcessor:
    """
    A class to handle Optical Character Recognition (OCR) for images and PDFs.
    """

    @staticmethod
    def process_image(image_path: str) -> str:
        """
        Extracts text from a single image file.

        :param image_path: The local path to the image file.
        :return: The extracted text as a string.
        """
        try:
            text = pytesseract.image_to_string(Image.open(image_path))
            logger.info(f"Successfully extracted text from image: {image_path}")
            return text
        except Exception as e:
            logger.error(f"OCR failed for image {image_path}: {e}")
            raise  # Re-raise the exception to be handled by the command handler

    @staticmethod
    def process_pdf(pdf_path: str) -> str:
        """
        Extracts text from all pages of a PDF file.

        :param pdf_path: The local path to the PDF file.
        :return: The concatenated extracted text from all pages.
        """
        full_text = ""
        try:
            # Convert PDF to a list of PIL images
            images = convert_from_path(pdf_path)

            for i, image in enumerate(images):
                # Extract text from each page image
                page_text = pytesseract.image_to_string(image)
                full_text += f"\n\n--- Page {i + 1} ---\n\n{page_text}"

            logger.info(f"Successfully extracted text from PDF: {pdf_path}")
            return full_text
        except Exception as e:
            logger.error(f"OCR failed for PDF {pdf_path}: {e}")
            raise  # Re-raise the exception to be handled by the command handler