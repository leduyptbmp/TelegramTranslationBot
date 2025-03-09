from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

from src.database import db
from src.utils.translator import translate_text
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
    
    # Lấy nội dung tin nhắn
    text = update.message.text
    
    if not text:
        await update.message.reply_text(
            "Tôi chỉ có thể dịch tin nhắn văn bản. Vui lòng gửi tin nhắn văn bản hoặc forward tin nhắn văn bản từ kênh/bot khác."
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
    
    # Lấy nội dung tin nhắn
    text = update.message.text
    
    if not text:
        await update.message.reply_text(
            "Tôi chỉ có thể dịch tin nhắn văn bản. Vui lòng forward tin nhắn văn bản từ kênh/bot khác."
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