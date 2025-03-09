import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# MongoDB URI
MONGODB_URI = os.getenv("MONGODB_URI")

# Danh sách ngôn ngữ hỗ trợ
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

# Ngôn ngữ mặc định
DEFAULT_LANGUAGE = 'vi' 