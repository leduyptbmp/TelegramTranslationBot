from deep_translator import GoogleTranslator
import logging

def translate_text(text, dest_language='vi', src_language=None):
    """
    Dịch văn bản sang ngôn ngữ đích
    
    Args:
        text (str): Văn bản cần dịch
        dest_language (str): Mã ngôn ngữ đích (mặc định: 'vi')
        src_language (str, optional): Mã ngôn ngữ nguồn (tự động phát hiện nếu không cung cấp)
    
    Returns:
        dict: Kết quả dịch với các thông tin: văn bản gốc, văn bản đã dịch, ngôn ngữ nguồn
    """
    if not text or text.strip() == "":
        return {
            "original_text": text,
            "translated_text": text,
            "source_language": None
        }
    
    try:
        # Dịch văn bản
        if src_language:
            translator = GoogleTranslator(source=src_language, target=dest_language)
        else:
            # Phát hiện ngôn ngữ nguồn
            detected_lang = detect_language(text)
            if detected_lang == dest_language:
                return {
                    "original_text": text,
                    "translated_text": text,
                    "source_language": detected_lang
                }
            translator = GoogleTranslator(source='auto', target=dest_language)
        
        translated_text = translator.translate(text)
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "source_language": src_language or detect_language(text)
        }
    except Exception as e:
        logging.error(f"Lỗi khi dịch văn bản: {e}")
        return {
            "original_text": text,
            "translated_text": text,
            "source_language": None,
            "error": str(e)
        }

def detect_language(text):
    """
    Phát hiện ngôn ngữ của văn bản
    
    Args:
        text (str): Văn bản cần phát hiện ngôn ngữ
    
    Returns:
        str: Mã ngôn ngữ đã phát hiện
    """
    if not text or text.strip() == "":
        return None
    
    try:
        # Sử dụng GoogleTranslator để phát hiện ngôn ngữ
        translator = GoogleTranslator(source='auto', target='en')
        detected_lang = translator.detect_language(text)
        return detected_lang
    except Exception as e:
        logging.error(f"Lỗi khi phát hiện ngôn ngữ: {e}")
        return None 