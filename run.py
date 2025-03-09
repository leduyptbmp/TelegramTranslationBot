#!/usr/bin/env python3
"""
Script để chạy Bot Dịch Thuật Telegram trực tiếp từ thư mục gốc.
"""

import os
import sys
import logging

# Thêm thư mục hiện tại vào đường dẫn để có thể import các module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import module main từ src
from src.main import main

if __name__ == "__main__":
    try:
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