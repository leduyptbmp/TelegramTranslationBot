import os
import logging
import tempfile
from PIL import Image
import pytesseract
from telegram import Update
import shutil

async def extract_text_from_image(update: Update, context):
    """
    Trích xuất văn bản từ hình ảnh sử dụng OCR
    
    Args:
        update (Update): Update từ Telegram
        context: Context từ Telegram
    
    Returns:
        str: Văn bản được trích xuất từ hình ảnh
    """
    try:
        # Kiểm tra xem Tesseract OCR đã được cài đặt chưa
        if not is_tesseract_installed():
            return (
                "⚠️ Tesseract OCR chưa được cài đặt. Vui lòng cài đặt Tesseract OCR để sử dụng tính năng này.\n\n"
                "Hướng dẫn cài đặt:\n"
                "- Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-vie\n"
                "- Windows: Tải từ https://github.com/UB-Mannheim/tesseract/wiki\n"
                "- macOS: brew install tesseract tesseract-lang"
            )
        
        # Xác định loại tin nhắn (từ người dùng hoặc từ kênh)
        if update.message:
            # Tin nhắn từ người dùng
            photo = update.message.photo[-1]
        elif update.channel_post:
            # Tin nhắn từ kênh
            photo = update.channel_post.photo[-1]
        else:
            return "Không thể xác định loại tin nhắn."
        
        # Tạo thư mục tạm để lưu ảnh
        with tempfile.TemporaryDirectory() as temp_dir:
            # Tạo đường dẫn đến file ảnh
            photo_path = os.path.join(temp_dir, f"{photo.file_id}.jpg")
            
            # Tải file ảnh
            photo_file = await context.bot.get_file(photo.file_id)
            await photo_file.download_to_drive(photo_path)
            
            # Mở ảnh bằng Pillow
            image = Image.open(photo_path)
            
            # Sử dụng pytesseract để trích xuất văn bản
            text = pytesseract.image_to_string(image)
            
            # Xóa khoảng trắng thừa và kiểm tra nếu văn bản rỗng
            text = text.strip()
            if not text:
                return "Không thể trích xuất văn bản từ hình ảnh này. Vui lòng thử lại với hình ảnh khác có văn bản rõ ràng hơn."
            
            return text
    except pytesseract.TesseractNotFoundError:
        logging.error("Tesseract OCR không được cài đặt hoặc không tìm thấy")
        return (
            "⚠️ Tesseract OCR không được cài đặt hoặc không tìm thấy. Vui lòng cài đặt Tesseract OCR để sử dụng tính năng này.\n\n"
            "Hướng dẫn cài đặt:\n"
            "- Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-vie\n"
            "- Windows: Tải từ https://github.com/UB-Mannheim/tesseract/wiki\n"
            "- macOS: brew install tesseract tesseract-lang"
        )
    except Exception as e:
        logging.error(f"Lỗi khi trích xuất văn bản từ hình ảnh: {e}")
        return f"Có lỗi xảy ra khi trích xuất văn bản: {str(e)}"

def is_tesseract_installed():
    """Kiểm tra xem Tesseract OCR đã được cài đặt chưa"""
    try:
        # Kiểm tra xem lệnh tesseract có tồn tại không
        if shutil.which('tesseract') is not None:
            return True
        
        # Thử truy cập trực tiếp vào Tesseract OCR
        pytesseract.get_tesseract_version()
        return True
    except:
        return False 