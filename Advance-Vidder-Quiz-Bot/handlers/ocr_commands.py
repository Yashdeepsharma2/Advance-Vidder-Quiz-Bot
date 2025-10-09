# Powered by Viddertech

import logging
import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

from integrations.ocr_processor import OcrProcessor

logger = logging.getLogger(__name__)

# Conversation states
AWAIT_FILE = range(1)
TEMP_FILE_DIR = "temp_files"

async def ocr_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the OCR process by asking for a file."""
    await update.message.reply_text(
        "Please send an image (JPG, PNG) or a PDF file to extract text from.\n\n"
        "Note: For this to work, the bot must be running on a system with Tesseract OCR and Poppler utilities installed."
    )
    return AWAIT_FILE

async def process_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives a file, processes it with OCR, and sends back the text."""
    is_photo = bool(update.message.photo)
    is_document = bool(update.message.document)

    if not is_photo and not is_document:
        await update.message.reply_text("That doesn't look like an image or a document. Please send a supported file.")
        return AWAIT_FILE

    await update.message.reply_text("📥 File received. Processing with OCR... this may take a moment.")

    try:
        if is_photo:
            file = await update.message.photo[-1].get_file() # Get the highest resolution photo
            file_extension = ".jpg"
        else: # Is document
            if update.message.document.mime_type not in ["image/jpeg", "image/png", "application/pdf"]:
                await update.message.reply_text("Unsupported document type. Please send a JPG, PNG, or PDF.")
                return AWAIT_FILE
            file = await update.message.document.get_file()
            file_extension = ".pdf" if update.message.document.mime_type == "application/pdf" else ".png"

        # Ensure temp directory exists
        os.makedirs(TEMP_FILE_DIR, exist_ok=True)

        # Download the file locally
        local_file_path = os.path.join(TEMP_FILE_DIR, f"{file.file_unique_id}{file_extension}")
        await file.download_to_drive(local_file_path)

        # Process with the OCR engine
        ocr_processor = OcrProcessor()
        extracted_text = ""
        if file_extension == ".pdf":
            extracted_text = ocr_processor.process_pdf(local_file_path)
        else:
            extracted_text = ocr_processor.process_image(local_file_path)

        if not extracted_text.strip():
            await update.message.reply_text("OCR finished, but no text could be extracted. The image might be empty or of low quality.")
        else:
            # Send the extracted text back to the user.
            # If the text is too long, it needs to be split into multiple messages.
            for i in range(0, len(extracted_text), 4096):
                await update.message.reply_text(
                    text=extracted_text[i:i+4096],
                    parse_mode=None # Send as plain text
                )
            await update.message.reply_text("✅ OCR processing complete.")

    except Exception as e:
        logger.error(f"OCR processing failed: {e}")
        await update.message.reply_text(f"An error occurred during OCR processing: {e}")
    finally:
        # Clean up the downloaded file
        if 'local_file_path' in locals() and os.path.exists(local_file_path):
            os.remove(local_file_path)

    return ConversationHandler.END

async def ocr_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the OCR process."""
    await update.message.reply_text("OCR process cancelled.")
    return ConversationHandler.END

ocr_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("ocr", ocr_start)],
    states={
        AWAIT_FILE: [MessageHandler(filters.PHOTO | filters.Document.ALL, process_file)]
    },
    fallbacks=[CommandHandler("cancel", ocr_cancel)],
    conversation_timeout=300 # 5 minutes to upload a file
)