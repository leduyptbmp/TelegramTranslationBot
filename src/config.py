import os
from dotenv import load_dotenv
import logging

# Thiết lập logger
logger = logging.getLogger(__name__)

# Tải biến môi trường từ file .env
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# MongoDB URI
MONGODB_URI = os.getenv("MONGODB_URI")

# Danh sách ngôn ngữ hỗ trợ cho dịch thuật
SUPPORTED_LANGUAGES = {
    'vi': 'Tiếng Việt',
    'en': 'Tiếng Anh',
    'zh-cn': 'Tiếng Trung',
    'ja': 'Tiếng Nhật',
    'ko': 'Tiếng Hàn',
    'fr': 'Tiếng Pháp',
    'de': 'Tiếng Đức',
    'ru': 'Tiếng Nga',
    'es': 'Tiếng Tây Ban Nha',
    'it': 'Tiếng Ý',
    'th': 'Tiếng Thái',
    'id': 'Tiếng Indonesia',
    'ms': 'Tiếng Malaysia',
}

# Danh sách ngôn ngữ giao tiếp của bot
BOT_INTERFACE_LANGUAGES = {
    'vi': 'Tiếng Việt',
    'en': 'English',
}

# Ngôn ngữ mặc định cho dịch thuật
DEFAULT_LANGUAGE = 'vi'

# Ngôn ngữ giao tiếp mặc định của bot
DEFAULT_INTERFACE_LANGUAGE = 'vi' 