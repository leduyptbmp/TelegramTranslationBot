#!/usr/bin/env python3
"""
Script để chạy Bot Dịch Thuật Telegram trực tiếp từ thư mục gốc.
"""

import os
import sys
import logging
import shutil

# Thêm thư mục hiện tại vào đường dẫn để có thể import các module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Kiểm tra Tesseract OCR
def check_tesseract():
    """Kiểm tra xem Tesseract OCR đã được cài đặt chưa"""
    if shutil.which('tesseract') is None:
        print("⚠️  Cảnh báo: Tesseract OCR chưa được cài đặt hoặc không có trong PATH.")
        print("   Tính năng OCR sẽ không hoạt động.")
        print("   Hướng dẫn cài đặt Tesseract OCR:")
        print("   - Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-vie")
        print("   - Windows: Tải từ https://github.com/UB-Mannheim/tesseract/wiki")
        print("   - macOS: brew install tesseract tesseract-lang")
        print("")

# Import module main từ src
try:
    from src.main import main
except ImportError as e:
    print(f"Lỗi khi import module: {e}")
    print("Vui lòng đảm bảo bạn đã cài đặt đầy đủ các thư viện cần thiết:")
    print("pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    try:
        # Kiểm tra Tesseract OCR
        check_tesseract()
        
        # Cấu hình logging
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )
        
        # Chạy bot
        print("Đang khởi động Bot Dịch Thuật Telegram...")
        main()
    except KeyboardInterrupt:
        print("\nĐã dừng bot.")
    except Exception as e:
        print(f"Lỗi khi chạy bot: {e}")
        logging.exception("Lỗi không xử lý được:")
        sys.exit(1) 