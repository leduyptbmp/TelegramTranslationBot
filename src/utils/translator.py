from deep_translator import GoogleTranslator
import logging
from langdetect import detect
from src.config import SUPPORTED_LANGUAGES

def translate_text(text, dest_language='vi', src_language=None):
    """
    Dịch văn bản sử dụng Google Translate
    
    Args:
        text (str): Văn bản cần dịch
        dest_language (str): Ngôn ngữ đích (mặc định: 'vi')
        src_language (str, optional): Ngôn ngữ nguồn (mặc định: None - tự động phát hiện)
    
    Returns:
        dict: Kết quả dịch bao gồm văn bản đã dịch và ngôn ngữ nguồn
    """
    if not text or text.strip() == "":
        return {"error": "Văn bản trống"}
    
    try:
        # Nếu không có ngôn ngữ nguồn, tự động phát hiện
        if not src_language:
            src_language = detect_language(text)
            
            # Nếu không phát hiện được ngôn ngữ
            if not src_language:
                return {"error": "Không thể phát hiện ngôn ngữ nguồn"}
        
        # Nếu ngôn ngữ nguồn giống ngôn ngữ đích, không cần dịch
        if src_language == dest_language:
            return {
                "translated_text": text,
                "source_language": src_language
            }
        
        # Dịch văn bản
        translator = GoogleTranslator(source=src_language, target=dest_language)
        translated_text = translator.translate(text)
        
        # Trả về kết quả
        return {
            "translated_text": translated_text,
            "source_language": src_language
        }
    except Exception as e:
        logging.error(f"Lỗi khi dịch văn bản: {e}")
        return {"error": str(e)}

def detect_language(text):
    """
    Phát hiện ngôn ngữ của văn bản sử dụng thư viện langdetect
    
    Args:
        text (str): Văn bản cần phát hiện ngôn ngữ
    
    Returns:
        str: Mã ngôn ngữ đã phát hiện
    """
    if not text or text.strip() == "":
        return None
    
    try:
        # Sử dụng langdetect để phát hiện ngôn ngữ
        detected_lang = detect(text)
        
        # Xử lý một số trường hợp đặc biệt
        if detected_lang == 'nl' and any(word in text.lower() for word in ['de', 'het', 'een', 'en', 'of', 'dat']):
            return 'nl'  # Xác nhận tiếng Hà Lan
        elif detected_lang == 'af' and any(word in text.lower() for word in ['die', 'en', 'het', 'is', 'nie']):
            return 'af'  # Xác nhận tiếng Afrikaans
        elif detected_lang == 'no' and any(word in text.lower() for word in ['og', 'er', 'det', 'i', 'på']):
            return 'no'  # Xác nhận tiếng Na Uy
        elif detected_lang == 'da' and any(word in text.lower() for word in ['og', 'er', 'det', 'at', 'en']):
            return 'da'  # Xác nhận tiếng Đan Mạch
        
        # Kiểm tra nếu văn bản có nhiều ký tự tiếng Việt
        if has_vietnamese_chars(text) and detected_lang != 'vi':
            return 'vi'  # Ưu tiên tiếng Việt nếu có dấu tiếng Việt
        
        return detected_lang
    except Exception as e:
        logging.error(f"Lỗi khi phát hiện ngôn ngữ: {e}")
        return None

def has_vietnamese_chars(text):
    """Kiểm tra xem văn bản có chứa ký tự tiếng Việt không"""
    vietnamese_chars = set('áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ')
    text_lower = text.lower()
    return any(char in vietnamese_chars for char in text_lower)

def get_language_name(lang_code):
    """Lấy tên đầy đủ của ngôn ngữ từ mã ngôn ngữ"""
    # Danh sách tên ngôn ngữ phổ biến
    language_names = {
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
        'nl': 'Tiếng Hà Lan',
        'af': 'Tiếng Afrikaans',
        'no': 'Tiếng Na Uy',
        'da': 'Tiếng Đan Mạch',
        'sv': 'Tiếng Thụy Điển',
        'fi': 'Tiếng Phần Lan',
        'pt': 'Tiếng Bồ Đào Nha',
        'pl': 'Tiếng Ba Lan',
        'tr': 'Tiếng Thổ Nhĩ Kỳ',
        'ar': 'Tiếng Ả Rập',
        'hi': 'Tiếng Hindi',
        'bn': 'Tiếng Bengali',
        'fa': 'Tiếng Ba Tư',
        'he': 'Tiếng Do Thái',
        'uk': 'Tiếng Ukraine',
        'cs': 'Tiếng Séc',
        'hu': 'Tiếng Hungary',
        'el': 'Tiếng Hy Lạp',
        'ro': 'Tiếng Romania',
        'sk': 'Tiếng Slovakia',
        'bg': 'Tiếng Bulgaria',
        'hr': 'Tiếng Croatia',
        'sr': 'Tiếng Serbia',
        'sl': 'Tiếng Slovenia',
        'lt': 'Tiếng Lithuania',
        'lv': 'Tiếng Latvia',
        'et': 'Tiếng Estonia',
    }
    
    # Trả về tên ngôn ngữ nếu có trong danh sách, nếu không trả về mã ngôn ngữ
    return language_names.get(lang_code, f"Ngôn ngữ mã '{lang_code}'") 