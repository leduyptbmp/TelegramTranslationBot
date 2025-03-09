from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
import tempfile
import os
from PIL import Image
import pytesseract

from src.database import db
from src.utils.translator import translate_text
from src.utils.ocr import extract_text_from_image
from src.config import DEFAULT_LANGUAGE

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn thông thường"""
    # Nếu tin nhắn là từ kênh hoặc được forward, xử lý riêng
    if update.message.forward_from_chat or update.message.forward_from:
        await handle_forwarded_message(update, context)
        return
    
    # Lấy thông tin người dùng
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    # Nếu người dùng chưa tồn tại, tạo mới
    if not user:
        user = db.create_user(
            user_id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            language_code=update.effective_user.language_code or DEFAULT_LANGUAGE
        )
    
    # Lấy ngôn ngữ dịch của người dùng
    target_language = user.get("language_code", DEFAULT_LANGUAGE)
    
    # Kiểm tra loại tin nhắn
    if update.message.photo:
        # Xử lý tin nhắn hình ảnh
        await handle_photo_message(update, context, target_language)
        return
    
    # Lấy nội dung tin nhắn
    text = update.message.text
    
    if not text:
        await update.message.reply_text(
            "Tôi có thể dịch tin nhắn văn bản hoặc hình ảnh. Vui lòng gửi tin nhắn văn bản, hình ảnh hoặc forward tin nhắn từ kênh/bot khác."
        )
        return
    
    # Dịch tin nhắn
    translation = translate_text(text, dest_language=target_language)
    
    # Nếu có lỗi khi dịch
    if "error" in translation:
        await update.message.reply_text(
            f"❌ Có lỗi xảy ra khi dịch tin nhắn: {translation['error']}"
        )
        return
    
    # Nếu ngôn ngữ nguồn giống ngôn ngữ đích
    if translation["source_language"] == target_language:
        await update.message.reply_text(
            f"Tin nhắn đã ở ngôn ngữ đích ({target_language})."
        )
        return
    
    # Gửi kết quả dịch
    await update.message.reply_text(
        f"🔄 *Bản dịch:*\n\n{translation['translated_text']}",
        parse_mode="Markdown"
    )

async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE, target_language):
    """Xử lý tin nhắn hình ảnh"""
    # Gửi tin nhắn đang xử lý
    processing_message = await update.message.reply_text(
        "⏳ Đang trích xuất văn bản từ hình ảnh..."
    )
    
    # Trích xuất văn bản từ hình ảnh
    text = await extract_text_from_image(update, context)
    
    # Nếu không thể trích xuất văn bản
    if text.startswith("Không thể trích xuất") or text.startswith("Có lỗi xảy ra"):
        await processing_message.edit_text(text)
        return
    
    # Cập nhật tin nhắn đang xử lý
    await processing_message.edit_text(
        f"📝 *Văn bản trích xuất:*\n\n{text}\n\n⏳ Đang dịch..."
    )
    
    # Dịch văn bản
    translation = translate_text(text, dest_language=target_language)
    
    # Nếu có lỗi khi dịch
    if "error" in translation:
        await processing_message.edit_text(
            f"📝 *Văn bản trích xuất:*\n\n{text}\n\n❌ Có lỗi xảy ra khi dịch: {translation['error']}"
        )
        return
    
    # Nếu ngôn ngữ nguồn giống ngôn ngữ đích
    if translation["source_language"] == target_language:
        await processing_message.edit_text(
            f"📝 *Văn bản trích xuất:*\n\n{text}\n\nVăn bản đã ở ngôn ngữ đích ({target_language})."
        )
        return
    
    # Gửi kết quả dịch
    await processing_message.edit_text(
        f"📝 *Văn bản trích xuất:*\n\n{text}\n\n"
        f"🔄 *Bản dịch ({translation['source_language']} → {target_language}):*\n\n{translation['translated_text']}",
        parse_mode="Markdown"
    )

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn được forward"""
    # Lấy thông tin người dùng
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    # Nếu người dùng chưa tồn tại, tạo mới
    if not user:
        user = db.create_user(
            user_id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            language_code=update.effective_user.language_code or DEFAULT_LANGUAGE
        )
    
    # Lấy ngôn ngữ dịch của người dùng
    target_language = user.get("language_code", DEFAULT_LANGUAGE)
    
    # Lấy thông tin kênh/người dùng gốc
    forward_from_chat = update.message.forward_from_chat
    forward_from = update.message.forward_from
    
    # Xác định ID và tiêu đề của kênh/người dùng gốc
    if forward_from_chat:
        # Tin nhắn được forward từ kênh/nhóm
        source_id = str(forward_from_chat.id)
        source_title = forward_from_chat.title or source_id
    elif forward_from:
        # Tin nhắn được forward từ người dùng
        source_id = str(forward_from.id)
        source_title = forward_from.first_name or source_id
    else:
        # Không xác định được nguồn
        await update.message.reply_text(
            "Không thể xác định nguồn của tin nhắn được forward."
        )
        return
    
    # Kiểm tra xem kênh đã được đăng ký chưa
    channel = db.get_channel(source_id)
    is_registered = channel and user_id in channel.get("subscribers", [])
    
    # Kiểm tra loại tin nhắn
    if update.message.photo:
        # Xử lý tin nhắn hình ảnh được forward
        await handle_forwarded_photo(update, context, target_language, source_id, source_title, is_registered)
        return
    
    # Lấy nội dung tin nhắn
    text = update.message.text
    
    if not text:
        await update.message.reply_text(
            "Tôi chỉ có thể dịch tin nhắn văn bản hoặc hình ảnh. Vui lòng forward tin nhắn văn bản hoặc hình ảnh từ kênh/bot khác."
        )
        return
    
    # Dịch tin nhắn
    translation = translate_text(text, dest_language=target_language)
    
    # Nếu có lỗi khi dịch
    if "error" in translation:
        await update.message.reply_text(
            f"❌ Có lỗi xảy ra khi dịch tin nhắn: {translation['error']}",
            reply_to_message_id=update.message.message_id
        )
        return
    
    # Nếu ngôn ngữ nguồn giống ngôn ngữ đích
    if translation["source_language"] == target_language:
        if not is_registered:
            # Hiển thị nút đăng ký nếu kênh chưa được đăng ký
            keyboard = [[
                InlineKeyboardButton("📌 Đăng ký kênh này", callback_data=f"register_{source_id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"Tin nhắn đã ở ngôn ngữ đích ({target_language}).\n\n"
                f"Bạn có muốn đăng ký kênh {source_title} để tự động dịch tin nhắn mới?",
                reply_markup=reply_markup,
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.message.reply_text(
                f"Tin nhắn đã ở ngôn ngữ đích ({target_language}).",
                reply_to_message_id=update.message.message_id
            )
        return
    
    # Gửi kết quả dịch
    if not is_registered:
        # Hiển thị nút đăng ký nếu kênh chưa được đăng ký
        keyboard = [[
            InlineKeyboardButton("📌 Đăng ký kênh này", callback_data=f"register_{source_id}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🔄 *Bản dịch từ {source_title}:*\n\n{translation['translated_text']}\n\n"
            f"Bạn có muốn đăng ký kênh này để tự động dịch tin nhắn mới?",
            parse_mode="Markdown",
            reply_markup=reply_markup,
            reply_to_message_id=update.message.message_id
        )
    else:
        await update.message.reply_text(
            f"🔄 *Bản dịch từ {source_title}:*\n\n{translation['translated_text']}",
            parse_mode="Markdown",
            reply_to_message_id=update.message.message_id
        )

async def handle_forwarded_photo(update, context, target_language, source_id, source_title, is_registered):
    """Xử lý tin nhắn hình ảnh được forward"""
    # Gửi tin nhắn đang xử lý
    processing_message = await update.message.reply_text(
        "⏳ Đang trích xuất văn bản từ hình ảnh...",
        reply_to_message_id=update.message.message_id
    )
    
    # Kiểm tra xem tin nhắn có caption không
    caption = update.message.caption
    
    # Trích xuất văn bản từ hình ảnh
    text = await extract_text_from_image(update, context)
    
    # Nếu không thể trích xuất văn bản và không có caption
    if (text.startswith("Không thể trích xuất") or text.startswith("Có lỗi xảy ra")) and not caption:
        await processing_message.edit_text(text)
        return
    
    # Nếu không thể trích xuất văn bản nhưng có caption
    if (text.startswith("Không thể trích xuất") or text.startswith("Có lỗi xảy ra")) and caption:
        text = ""  # Đặt text thành chuỗi rỗng để chỉ dịch caption
    
    # Chuẩn bị nội dung để dịch
    content_to_translate = ""
    
    # Nếu có văn bản trích xuất từ hình ảnh
    if text and not text.startswith("Không thể trích xuất") and not text.startswith("Có lỗi xảy ra"):
        content_to_translate += f"📝 *Văn bản trích xuất từ hình ảnh của {source_title}:*\n\n{text}\n\n"
    
    # Nếu có caption
    if caption:
        content_to_translate += f"📝 *Caption từ {source_title}:*\n\n{caption}\n\n"
    
    # Cập nhật tin nhắn đang xử lý
    await processing_message.edit_text(
        f"{content_to_translate}⏳ Đang dịch..."
    )
    
    # Dịch văn bản từ hình ảnh (nếu có)
    image_translation = None
    if text and not text.startswith("Không thể trích xuất") and not text.startswith("Có lỗi xảy ra"):
        image_translation = translate_text(text, dest_language=target_language)
    
    # Dịch caption (nếu có)
    caption_translation = None
    if caption:
        caption_translation = translate_text(caption, dest_language=target_language)
    
    # Chuẩn bị kết quả dịch
    translation_result = ""
    
    # Thêm kết quả dịch văn bản từ hình ảnh (nếu có)
    if image_translation and "error" not in image_translation:
        if image_translation["source_language"] != target_language:
            translation_result += f"🔄 *Bản dịch văn bản từ hình ảnh ({image_translation['source_language']} → {target_language}):*\n\n{image_translation['translated_text']}\n\n"
        else:
            translation_result += f"📝 *Văn bản trích xuất từ hình ảnh đã ở ngôn ngữ đích ({target_language})*\n\n"
    elif image_translation and "error" in image_translation:
        translation_result += f"❌ Có lỗi xảy ra khi dịch văn bản từ hình ảnh: {image_translation['error']}\n\n"
    
    # Thêm kết quả dịch caption (nếu có)
    if caption_translation and "error" not in caption_translation:
        if caption_translation["source_language"] != target_language:
            translation_result += f"🔄 *Bản dịch caption ({caption_translation['source_language']} → {target_language}):*\n\n{caption_translation['translated_text']}"
        else:
            translation_result += f"📝 *Caption đã ở ngôn ngữ đích ({target_language})*"
    elif caption_translation and "error" in caption_translation:
        translation_result += f"❌ Có lỗi xảy ra khi dịch caption: {caption_translation['error']}"
    
    # Nếu không có kết quả dịch nào
    if not translation_result:
        await processing_message.edit_text(
            "❌ Không thể dịch nội dung. Vui lòng thử lại với hình ảnh khác hoặc thêm caption."
        )
        return
    
    # Gửi kết quả dịch
    if not is_registered:
        # Hiển thị nút đăng ký nếu kênh chưa được đăng ký
        keyboard = [[
            InlineKeyboardButton("📌 Đăng ký kênh này", callback_data=f"register_{source_id}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await processing_message.edit_text(
            f"{content_to_translate}{translation_result}\n\n"
            f"Bạn có muốn đăng ký kênh này để tự động dịch tin nhắn mới?",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await processing_message.edit_text(
            f"{content_to_translate}{translation_result}",
            parse_mode="Markdown"
        )

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn mới từ kênh"""
    # Lấy thông tin kênh
    channel_id = str(update.channel_post.chat.id)
    channel = db.get_channel(channel_id)
    
    # Nếu kênh không được đăng ký, bỏ qua
    if not channel:
        return
    
    # Lấy danh sách người dùng đã đăng ký kênh
    subscribers = channel.get("subscribers", [])
    
    # Nếu không có người dùng nào đăng ký, bỏ qua
    if not subscribers:
        return
    
    # Kiểm tra loại tin nhắn
    if update.channel_post.photo:
        # Xử lý tin nhắn hình ảnh từ kênh
        await handle_channel_photo(update, context, channel)
        return
    
    # Lấy nội dung tin nhắn
    text = update.channel_post.text
    
    if not text:
        return
    
    # Dịch tin nhắn cho từng người dùng
    for user_id in subscribers:
        # Lấy thông tin người dùng
        user = db.get_user(user_id)
        
        if not user:
            continue
        
        # Lấy ngôn ngữ dịch của người dùng
        target_language = user.get("language_code", DEFAULT_LANGUAGE)
        
        # Dịch tin nhắn
        translation = translate_text(text, dest_language=target_language)
        
        # Nếu có lỗi khi dịch hoặc ngôn ngữ nguồn giống ngôn ngữ đích, bỏ qua
        if "error" in translation or translation["source_language"] == target_language:
            continue
        
        # Gửi kết quả dịch cho người dùng
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🔄 *Bản dịch từ {channel.get('title', channel_id)}:*\n\n{translation['translated_text']}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Lỗi khi gửi tin nhắn đến người dùng {user_id}: {e}")

async def handle_channel_photo(update, context, channel):
    """Xử lý tin nhắn hình ảnh từ kênh"""
    channel_id = str(update.channel_post.chat.id)
    
    # Lấy danh sách người dùng đã đăng ký kênh
    subscribers = channel.get("subscribers", [])
    
    # Kiểm tra xem tin nhắn có caption không
    caption = update.channel_post.caption
    
    # Trích xuất văn bản từ hình ảnh
    try:
        # Lấy file ảnh với kích thước lớn nhất
        photo = update.channel_post.photo[-1]
        
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
            
            # Nếu không có văn bản trích xuất và không có caption, bỏ qua
            if not text and not caption:
                return
            
            # Dịch tin nhắn cho từng người dùng
            for user_id in subscribers:
                # Lấy thông tin người dùng
                user = db.get_user(user_id)
                
                if not user:
                    continue
                
                # Lấy ngôn ngữ dịch của người dùng
                target_language = user.get("language_code", DEFAULT_LANGUAGE)
                
                # Chuẩn bị nội dung để hiển thị
                content_to_display = ""
                translation_result = ""
                
                # Dịch văn bản từ hình ảnh (nếu có)
                if text:
                    content_to_display += f"📝 *Văn bản trích xuất từ hình ảnh:*\n\n{text}\n\n"
                    image_translation = translate_text(text, dest_language=target_language)
                    
                    # Nếu dịch thành công và ngôn ngữ nguồn khác ngôn ngữ đích
                    if "error" not in image_translation and image_translation["source_language"] != target_language:
                        translation_result += f"🔄 *Bản dịch văn bản từ hình ảnh ({image_translation['source_language']} → {target_language}):*\n\n{image_translation['translated_text']}\n\n"
                
                # Dịch caption (nếu có)
                if caption:
                    content_to_display += f"📝 *Caption:*\n\n{caption}\n\n"
                    caption_translation = translate_text(caption, dest_language=target_language)
                    
                    # Nếu dịch thành công và ngôn ngữ nguồn khác ngôn ngữ đích
                    if "error" not in caption_translation and caption_translation["source_language"] != target_language:
                        translation_result += f"🔄 *Bản dịch caption ({caption_translation['source_language']} → {target_language}):*\n\n{caption_translation['translated_text']}"
                
                # Nếu không có kết quả dịch nào, bỏ qua
                if not translation_result:
                    continue
                
                # Gửi kết quả dịch cho người dùng
                try:
                    # Gửi hình ảnh gốc
                    sent_photo = await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo.file_id,
                        caption=f"📝 *Hình ảnh từ {channel.get('title', channel_id)}*",
                        parse_mode="Markdown"
                    )
                    
                    # Gửi văn bản trích xuất và bản dịch
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"{content_to_display}{translation_result}",
                        parse_mode="Markdown",
                        reply_to_message_id=sent_photo.message_id
                    )
                except Exception as e:
                    logging.error(f"Lỗi khi gửi tin nhắn đến người dùng {user_id}: {e}")
    except Exception as e:
        logging.error(f"Lỗi khi xử lý hình ảnh từ kênh: {e}")
        return 