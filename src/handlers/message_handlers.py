from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging
import tempfile
import os
from PIL import Image
import pytesseract

from src.database import db
from src.utils.translator import translate_text, get_language_name
from src.utils.ocr import extract_text_from_image
from src.config import DEFAULT_LANGUAGE, DEFAULT_INTERFACE_LANGUAGE, SUPPORTED_LANGUAGES, BOT_INTERFACE_LANGUAGES

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
        # Xác định ngôn ngữ giao tiếp từ ngôn ngữ của người dùng nếu được hỗ trợ
        user_lang = update.effective_user.language_code
        interface_lang = user_lang if user_lang in BOT_INTERFACE_LANGUAGES else DEFAULT_INTERFACE_LANGUAGE
        
        user = db.create_user(
            user_id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            language_code=DEFAULT_LANGUAGE,
            interface_language=interface_lang
        )
    
    # Lấy ngôn ngữ dịch và giao tiếp của người dùng
    target_language = user.get("language_code", DEFAULT_LANGUAGE)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE)
    
    # Kiểm tra xem người dùng đã cài đặt ngôn ngữ đích chưa
    if not target_language:
        # Tạo nút cài đặt ngôn ngữ
        keyboard = [[
            InlineKeyboardButton("Cài đặt ngôn ngữ / Set language", callback_data="setlang_prompt")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Hiển thị thông báo theo ngôn ngữ giao tiếp
        if interface_language == "en":
            await update.message.reply_text(
                "⚠️ You haven't set your target translation language yet.\n\n"
                "Please use the /setlang command to set your preferred translation language.",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "⚠️ Bạn chưa cài đặt ngôn ngữ dịch mục tiêu.\n\n"
                "Vui lòng sử dụng lệnh /setlang để cài đặt ngôn ngữ dịch ưa thích của bạn.",
                reply_markup=reply_markup
            )
        return
    
    # Kiểm tra loại tin nhắn
    if update.message.photo:
        # Xử lý tin nhắn hình ảnh
        await handle_photo_message(update, context, target_language)
        return
    elif update.message.video:
        # Xử lý tin nhắn video (chỉ dịch caption)
        await handle_video_message(update, context, target_language, interface_language)
        return
    
    # Lấy nội dung tin nhắn
    text = update.message.text
    
    if not text:
        # Hiển thị thông báo theo ngôn ngữ giao tiếp
        if interface_language == "en":
            await update.message.reply_text(
                "I can translate text messages, images, or videos with captions. Please send a text message, image, video, or forward a message from another channel/bot."
            )
        else:
            await update.message.reply_text(
                "Tôi có thể dịch tin nhắn văn bản, hình ảnh, hoặc video có caption. Vui lòng gửi tin nhắn văn bản, hình ảnh, video hoặc forward tin nhắn từ kênh/bot khác."
            )
        return
    
    # Dịch tin nhắn
    translation = translate_text(text, dest_language=target_language)
    
    # Nếu có lỗi khi dịch
    if "error" in translation:
        # Hiển thị thông báo lỗi theo ngôn ngữ giao tiếp
        if interface_language == "en":
            await update.message.reply_text(
                f"❌ An error occurred while translating the message: {translation['error']}"
            )
        else:
            await update.message.reply_text(
                f"❌ Có lỗi xảy ra khi dịch tin nhắn: {translation['error']}"
            )
        return
    
    # Nếu ngôn ngữ nguồn giống ngôn ngữ đích
    if translation["source_language"] == target_language:
        # Hiển thị thông báo theo ngôn ngữ giao tiếp
        target_lang_name = get_language_name(target_language)
        if interface_language == "en":
            await update.message.reply_text(
                f"The message is already in your target language ({target_lang_name})."
            )
        else:
            await update.message.reply_text(
                f"Tin nhắn đã ở ngôn ngữ đích của bạn ({target_lang_name})."
            )
        return
    
    # Lấy tên ngôn ngữ đầy đủ
    source_lang_name = get_language_name(translation["source_language"])
    target_lang_name = get_language_name(target_language)
    
    # Gửi kết quả dịch
    if interface_language == "en":
        await update.message.reply_text(
            f"🔄 *Translation from {source_lang_name} to {target_lang_name}:*\n\n{translation['translated_text']}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"🔄 *Bản dịch từ {source_lang_name} sang {target_lang_name}:*\n\n{translation['translated_text']}",
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

async def handle_video_message(update: Update, context: ContextTypes.DEFAULT_TYPE, target_language, interface_language):
    """Xử lý tin nhắn video (chỉ dịch caption)"""
    # Lấy caption của video
    caption = update.message.caption
    
    # Nếu không có caption
    if not caption:
        # Hiển thị thông báo theo ngôn ngữ giao tiếp
        if interface_language == "en":
            await update.message.reply_text(
                "The video doesn't have any caption to translate. I can only translate captions of videos."
            )
        else:
            await update.message.reply_text(
                "Video không có caption để dịch. Tôi chỉ có thể dịch caption của video."
            )
        return
    
    # Dịch caption
    translation = translate_text(caption, dest_language=target_language)
    
    # Nếu có lỗi khi dịch
    if "error" in translation:
        # Hiển thị thông báo lỗi theo ngôn ngữ giao tiếp
        if interface_language == "en":
            await update.message.reply_text(
                f"❌ An error occurred while translating the caption: {translation['error']}"
            )
        else:
            await update.message.reply_text(
                f"❌ Có lỗi xảy ra khi dịch caption: {translation['error']}"
            )
        return
    
    # Nếu ngôn ngữ nguồn giống ngôn ngữ đích
    if translation["source_language"] == target_language:
        # Hiển thị thông báo theo ngôn ngữ giao tiếp
        if interface_language == "en":
            await update.message.reply_text(
                f"The caption is already in your target language ({get_language_name(target_language)})."
            )
        else:
            await update.message.reply_text(
                f"Caption đã ở ngôn ngữ đích của bạn ({get_language_name(target_language)})."
            )
        return
    
    # Lấy tên ngôn ngữ
    source_lang_name = get_language_name(translation["source_language"])
    target_lang_name = get_language_name(target_language)
    
    # Gửi kết quả dịch
    if interface_language == "en":
        await update.message.reply_text(
            f"📝 *Original Caption:*\n\n{caption}\n\n"
            f"🔄 *Translation from {source_lang_name} to {target_lang_name}:*\n\n{translation['translated_text']}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"📝 *Caption gốc:*\n\n{caption}\n\n"
            f"🔄 *Bản dịch từ {source_lang_name} sang {target_lang_name}:*\n\n{translation['translated_text']}",
            parse_mode="Markdown"
        )

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn được forward"""
    # Lấy thông tin người dùng
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    # Nếu người dùng chưa tồn tại, tạo mới
    if not user:
        # Xác định ngôn ngữ giao tiếp từ ngôn ngữ của người dùng nếu được hỗ trợ
        user_lang = update.effective_user.language_code
        interface_lang = user_lang if user_lang in BOT_INTERFACE_LANGUAGES else DEFAULT_INTERFACE_LANGUAGE
        
        user = db.create_user(
            user_id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            language_code=DEFAULT_LANGUAGE,
            interface_language=interface_lang
        )
    
    # Lấy ngôn ngữ dịch và giao tiếp của người dùng
    target_language = user.get("language_code", DEFAULT_LANGUAGE)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE)
    
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
        if interface_language == "en":
            await update.message.reply_text(
                "Unable to identify the source of the forwarded message."
            )
        else:
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
    elif update.message.video:
        # Xử lý tin nhắn video được forward
        await handle_forwarded_video(update, context, target_language, interface_language, source_id, source_title, is_registered)
        return
    
    # Lấy nội dung tin nhắn
    text = update.message.text
    
    if not text:
        if interface_language == "en":
            await update.message.reply_text(
                "I can only translate text messages, images, or videos with captions. Please forward a text message, image, or video with caption from another channel/bot."
            )
        else:
            await update.message.reply_text(
                "Tôi chỉ có thể dịch tin nhắn văn bản, hình ảnh, hoặc video có caption. Vui lòng forward tin nhắn văn bản, hình ảnh, hoặc video có caption từ kênh/bot khác."
            )
        return
    
    # Dịch tin nhắn
    translation = translate_text(text, dest_language=target_language)
    
    # Nếu có lỗi khi dịch
    if "error" in translation:
        if interface_language == "en":
            await update.message.reply_text(
                f"❌ An error occurred while translating the message: {translation['error']}",
                reply_to_message_id=update.message.message_id
            )
        else:
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
            
            if interface_language == "en":
                await update.message.reply_text(
                    f"The message is already in the target language ({get_language_name(target_language)}).\n\n"
                    f"Do you want to register the channel {source_title} to automatically translate new messages?",
                    reply_markup=reply_markup,
                    reply_to_message_id=update.message.message_id
                )
            else:
                await update.message.reply_text(
                    f"Tin nhắn đã ở ngôn ngữ đích ({get_language_name(target_language)}).\n\n"
                    f"Bạn có muốn đăng ký kênh {source_title} để tự động dịch tin nhắn mới?",
                    reply_markup=reply_markup,
                    reply_to_message_id=update.message.message_id
                )
        else:
            if interface_language == "en":
                await update.message.reply_text(
                    f"The message is already in the target language ({get_language_name(target_language)}).",
                    reply_to_message_id=update.message.message_id
                )
            else:
                await update.message.reply_text(
                    f"Tin nhắn đã ở ngôn ngữ đích ({get_language_name(target_language)}).",
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
        
        if interface_language == "en":
            await update.message.reply_text(
                f"🔄 *Translation from {source_title}:*\n\n"
                f"From {get_language_name(translation['source_language'])} to {get_language_name(target_language)}:\n\n"
                f"{translation['translated_text']}",
                parse_mode="Markdown",
                reply_markup=reply_markup,
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.message.reply_text(
                f"🔄 *Bản dịch từ {source_title}:*\n\n"
                f"Từ {get_language_name(translation['source_language'])} sang {get_language_name(target_language)}:\n\n"
                f"{translation['translated_text']}",
                parse_mode="Markdown",
                reply_markup=reply_markup,
                reply_to_message_id=update.message.message_id
            )
    else:
        if interface_language == "en":
            await update.message.reply_text(
                f"🔄 *Translation from {source_title}:*\n\n"
                f"From {get_language_name(translation['source_language'])} to {get_language_name(target_language)}:\n\n"
                f"{translation['translated_text']}",
                parse_mode="Markdown",
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.message.reply_text(
                f"🔄 *Bản dịch từ {source_title}:*\n\n"
                f"Từ {get_language_name(translation['source_language'])} sang {get_language_name(target_language)}:\n\n"
                f"{translation['translated_text']}",
                parse_mode="Markdown",
                reply_to_message_id=update.message.message_id
            )

async def handle_forwarded_video(update, context, target_language, interface_language, source_id, source_title, is_registered):
    """Xử lý tin nhắn video được forward"""
    # Lấy caption của video
    caption = update.message.caption
    
    # Nếu không có caption
    if not caption:
        if interface_language == "en":
            await update.message.reply_text(
                "The forwarded video doesn't have any caption to translate.",
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.message.reply_text(
                "Video được forward không có caption để dịch.",
                reply_to_message_id=update.message.message_id
            )
        return
    
    # Dịch caption
    translation = translate_text(caption, dest_language=target_language)
    
    # Nếu có lỗi khi dịch
    if "error" in translation:
        if interface_language == "en":
            await update.message.reply_text(
                f"❌ An error occurred while translating the caption: {translation['error']}",
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.message.reply_text(
                f"❌ Có lỗi xảy ra khi dịch caption: {translation['error']}",
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
            
            if interface_language == "en":
                await update.message.reply_text(
                    f"The caption is already in the target language ({get_language_name(target_language)}).\n\n"
                    f"Do you want to register the channel {source_title} to automatically translate new messages?",
                    reply_markup=reply_markup,
                    reply_to_message_id=update.message.message_id
                )
            else:
                await update.message.reply_text(
                    f"Caption đã ở ngôn ngữ đích ({get_language_name(target_language)}).\n\n"
                    f"Bạn có muốn đăng ký kênh {source_title} để tự động dịch tin nhắn mới?",
                    reply_markup=reply_markup,
                    reply_to_message_id=update.message.message_id
                )
        else:
            if interface_language == "en":
                await update.message.reply_text(
                    f"The caption is already in the target language ({get_language_name(target_language)}).",
                    reply_to_message_id=update.message.message_id
                )
            else:
                await update.message.reply_text(
                    f"Caption đã ở ngôn ngữ đích ({get_language_name(target_language)}).",
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
        
        if interface_language == "en":
            await update.message.reply_text(
                f"📝 *Original Caption from {source_title}:*\n\n{caption}\n\n"
                f"🔄 *Translation ({translation['source_language']} → {target_language}):*\n\n{translation['translated_text']}\n\n"
                f"Do you want to register this channel to automatically translate new messages?",
                parse_mode="Markdown",
                reply_markup=reply_markup,
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.message.reply_text(
                f"📝 *Caption gốc từ {source_title}:*\n\n{caption}\n\n"
                f"🔄 *Bản dịch ({translation['source_language']} → {target_language}):*\n\n{translation['translated_text']}\n\n"
                f"Bạn có muốn đăng ký kênh này để tự động dịch tin nhắn mới?",
                parse_mode="Markdown",
                reply_markup=reply_markup,
                reply_to_message_id=update.message.message_id
            )
    else:
        if interface_language == "en":
            await update.message.reply_text(
                f"📝 *Original Caption from {source_title}:*\n\n{caption}\n\n"
                f"🔄 *Translation ({translation['source_language']} → {target_language}):*\n\n{translation['translated_text']}",
                parse_mode="Markdown",
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.message.reply_text(
                f"📝 *Caption gốc từ {source_title}:*\n\n{caption}\n\n"
                f"🔄 *Bản dịch ({translation['source_language']} → {target_language}):*\n\n{translation['translated_text']}",
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
    try:
        # Lấy thông tin kênh
        channel_id = str(update.channel_post.chat.id)
        channel_title = update.channel_post.chat.title
        
        logging.info(f"Received new message from channel {channel_title} ({channel_id})")
        logging.info(f"Message type: {update.channel_post.type}")
        logging.info(f"Message ID: {update.channel_post.message_id}")
        
        # Lấy danh sách người dùng đã đăng ký kênh này
        registered_users = db.get_channel_users(channel_id)
        
        if not registered_users:
            logging.info(f"No registered users for channel {channel_title} ({channel_id})")
            return
        
        logging.info(f"Found {len(registered_users)} registered users for channel {channel_title} ({channel_id})")
        
        # Lấy nội dung tin nhắn
        message = update.channel_post
        
        # Xử lý tin nhắn văn bản
        if message.text:
            text = message.text
            logging.info(f"Processing text message from channel {channel_title} ({channel_id})")
        # Xử lý tin nhắn hình ảnh có caption
        elif message.caption:
            text = message.caption
            logging.info(f"Processing image caption from channel {channel_title} ({channel_id})")
        else:
            logging.info(f"No text content to translate from channel {channel_title} ({channel_id})")
            return
        
        # Nhóm người dùng theo ngôn ngữ đích
        users_by_language = {}
        for user in registered_users:
            target_language = user.get("language_code", DEFAULT_LANGUAGE)
            if target_language not in users_by_language:
                users_by_language[target_language] = []
            users_by_language[target_language].append(user)
        
        logging.info(f"Grouped users by target language: {list(users_by_language.keys())}")
        
        # Dịch và gửi tin nhắn cho từng nhóm ngôn ngữ
        for target_language, users in users_by_language.items():
            try:
                # Dịch nội dung một lần cho mỗi ngôn ngữ đích
                translation = translate_text(text, dest_language=target_language)
                logging.info(f"Translated text to {target_language}")
                
                # Gửi tin nhắn cho tất cả người dùng trong nhóm ngôn ngữ
                for user in users:
                    try:
                        user_id = user.get("user_id")
                        interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE)
                        
                        logging.info(f"Sending message to user {user_id} in {interface_language}")
                        
                        # Tạo tin nhắn phản hồi
                        if interface_language == "en":
                            response = f"📢 *New message from {channel_title}*\n\n"
                            response += f"*Original:*\n{text}\n\n"
                            response += f"*Translation:*\n{translation['translated_text']}"
                        else:
                            response = f"📢 *Tin nhắn mới từ {channel_title}*\n\n"
                            response += f"*Nội dung gốc:*\n{text}\n\n"
                            response += f"*Bản dịch:*\n{translation['translated_text']}"
                        
                        # Gửi tin nhắn đã dịch trực tiếp cho người dùng trong chat riêng
                        await context.bot.send_message(
                            chat_id=user_id,  # Gửi đến user_id thay vì channel_id
                            text=response,
                            parse_mode="Markdown"
                        )
                        logging.info(f"Successfully sent translated message to user {user_id}")
                        
                    except Exception as e:
                        logging.error(f"Error sending message to user {user_id}: {e}")
                        continue
                        
            except Exception as e:
                logging.error(f"Error processing translation for language {target_language}: {e}")
                continue
                
    except Exception as e:
        logging.error(f"Error handling channel post: {e}")

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
                
                # Lấy ngôn ngữ dịch và giao tiếp của người dùng
                target_language = user.get("language_code", DEFAULT_LANGUAGE)
                interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE)
                
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

async def handle_channel_video(update, context, channel):
    """Xử lý tin nhắn video từ kênh"""
    channel_id = str(update.channel_post.chat.id)
    
    # Lấy danh sách người dùng đã đăng ký kênh
    subscribers = channel.get("subscribers", [])
    
    # Lấy caption của video
    caption = update.channel_post.caption
    
    # Nếu không có caption, bỏ qua
    if not caption:
        return
    
    # Dịch tin nhắn cho từng người dùng
    for user_id in subscribers:
        # Lấy thông tin người dùng
        user = db.get_user(user_id)
        
        if not user:
            continue
        
        # Lấy ngôn ngữ dịch và giao tiếp của người dùng
        target_language = user.get("language_code", DEFAULT_LANGUAGE)
        interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE)
        
        # Dịch caption
        translation = translate_text(caption, dest_language=target_language)
        
        # Nếu có lỗi khi dịch hoặc ngôn ngữ nguồn giống ngôn ngữ đích, bỏ qua
        if "error" in translation or translation["source_language"] == target_language:
            continue
        
        # Gửi kết quả dịch cho người dùng
        try:
            # Gửi video gốc
            sent_video = await context.bot.send_video(
                chat_id=user_id,
                video=update.channel_post.video.file_id,
                caption=f"📝 *Video từ {channel.get('title', channel_id)}*",
                parse_mode="Markdown"
            )
            
            # Gửi caption và bản dịch
            if interface_language == "en":
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📝 *Original Caption:*\n\n{caption}\n\n"
                    f"🔄 *Translation ({translation['source_language']} → {target_language}):*\n\n{translation['translated_text']}",
                    parse_mode="Markdown",
                    reply_to_message_id=sent_video.message_id
                )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📝 *Caption gốc:*\n\n{caption}\n\n"
                    f"🔄 *Bản dịch ({translation['source_language']} → {target_language}):*\n\n{translation['translated_text']}",
                    parse_mode="Markdown",
                    reply_to_message_id=sent_video.message_id
                )
        except Exception as e:
            logging.error(f"Lỗi khi gửi tin nhắn đến người dùng {user_id}: {e}")

async def register_channel_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý nhập lệnh đăng ký kênh"""
    # Lấy thông tin người dùng
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    if not user:
        # Nếu người dùng chưa tồn tại, tạo mới
        user_lang = update.effective_user.language_code
        interface_lang = user_lang if user_lang in BOT_INTERFACE_LANGUAGES else DEFAULT_INTERFACE_LANGUAGE
        
        user = db.create_user(
            user_id=user_id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            language_code=DEFAULT_LANGUAGE,
            interface_language=interface_lang
        )
    
    # Lấy ngôn ngữ dịch và giao tiếp của người dùng
    target_language = user.get("language_code", DEFAULT_LANGUAGE)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE)
    
    # Kiểm tra nếu người dùng nhập lệnh khác
    if channel_id.startswith('/'):
        # Nếu là lệnh, thoát khỏi chế độ đăng ký
        if interface_language == "en":
            await update.message.reply_text(
                "Registration canceled. Processing your command..."
            )
        else:
            await update.message.reply_text(
                "Đã hủy đăng ký. Đang xử lý lệnh của bạn..."
            )
        
        # Xóa trạng thái đăng ký kênh
        context.user_data.pop('register_command', None)
        return ConversationHandler.END

    # Kiểm tra xem kênh đã được đăng ký chưa
    channel = db.get_channel(channel_id)
    is_registered = channel and user_id in channel.get("subscribers", [])
    
    # Kiểm tra loại tin nhắn
    if update.message.photo:
        # Xử lý tin nhắn hình ảnh được forward
        await handle_forwarded_photo(update, context, target_language, channel_id, channel.get('title', channel_id), is_registered)
        return
    elif update.message.video:
        # Xử lý tin nhắn video được forward
        await handle_forwarded_video(update, context, target_language, interface_language, channel_id, channel.get('title', channel_id), is_registered)
        return
    
    # Lấy nội dung tin nhắn
    text = update.message.text
    
    if not text:
        if interface_language == "en":
            await update.message.reply_text(
                "I can only translate text messages, images, or videos with captions. Please forward a text message, image, or video with caption from another channel/bot."
            )
        else:
            await update.message.reply_text(
                "Tôi chỉ có thể dịch tin nhắn văn bản, hình ảnh, hoặc video có caption. Vui lòng forward tin nhắn văn bản, hình ảnh, hoặc video có caption từ kênh/bot khác."
            )
        return
    
    # Dịch tin nhắn
    translation = translate_text(text, dest_language=target_language)
    
    # Nếu có lỗi khi dịch
    if "error" in translation:
        if interface_language == "en":
            await update.message.reply_text(
                f"❌ An error occurred while translating the message: {translation['error']}",
                reply_to_message_id=update.message.message_id
            )
        else:
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
                InlineKeyboardButton("📌 Đăng ký kênh này", callback_data=f"register_{channel_id}")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if interface_language == "en":
                await update.message.reply_text(
                    f"The message is already in the target language ({get_language_name(target_language)}).\n\n"
                    f"Do you want to register the channel {channel.get('title', channel_id)} to automatically translate new messages?",
                    reply_markup=reply_markup,
                    reply_to_message_id=update.message.message_id
                )
            else:
                await update.message.reply_text(
                    f"Tin nhắn đã ở ngôn ngữ đích ({get_language_name(target_language)}).\n\n"
                    f"Bạn có muốn đăng ký kênh {channel.get('title', channel_id)} để tự động dịch tin nhắn mới?",
                    reply_markup=reply_markup,
                    reply_to_message_id=update.message.message_id
                )
        else:
            if interface_language == "en":
                await update.message.reply_text(
                    f"The message is already in the target language ({get_language_name(target_language)}).",
                    reply_to_message_id=update.message.message_id
                )
            else:
                await update.message.reply_text(
                    f"Tin nhắn đã ở ngôn ngữ đích ({get_language_name(target_language)}).",
                    reply_to_message_id=update.message.message_id
                )
        return
    
    # Gửi kết quả dịch
    if not is_registered:
        # Hiển thị nút đăng ký nếu kênh chưa được đăng ký
        keyboard = [[
            InlineKeyboardButton("📌 Đăng ký kênh này", callback_data=f"register_{channel_id}")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if interface_language == "en":
            await update.message.reply_text(
                f"🔄 *Translation from {channel.get('title', channel_id)}:*\n\n"
                f"From {get_language_name(translation['source_language'])} to {get_language_name(target_language)}:\n\n"
                f"{translation['translated_text']}",
                parse_mode="Markdown",
                reply_markup=reply_markup,
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.message.reply_text(
                f"🔄 *Bản dịch từ {channel.get('title', channel_id)}:*\n\n"
                f"Từ {get_language_name(translation['source_language'])} sang {get_language_name(target_language)}:\n\n"
                f"{translation['translated_text']}",
                parse_mode="Markdown",
                reply_markup=reply_markup,
                reply_to_message_id=update.message.message_id
            )
    else:
        if interface_language == "en":
            await update.message.reply_text(
                f"🔄 *Translation from {channel.get('title', channel_id)}:*\n\n"
                f"From {get_language_name(translation['source_language'])} to {get_language_name(target_language)}:\n\n"
                f"{translation['translated_text']}",
                parse_mode="Markdown",
                reply_to_message_id=update.message.message_id
            )
        else:
            await update.message.reply_text(
                f"🔄 *Bản dịch từ {channel.get('title', channel_id)}:*\n\n"
                f"Từ {get_language_name(translation['source_language'])} sang {get_language_name(target_language)}:\n\n"
                f"{translation['translated_text']}",
                parse_mode="Markdown",
                reply_to_message_id=update.message.message_id
            )

    # Xóa trạng thái đăng ký kênh
    context.user_data.pop('register_command', None)
    return ConversationHandler.END 