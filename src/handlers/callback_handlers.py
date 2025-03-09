from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import logging

from src.database import db
from src.config import SUPPORTED_LANGUAGES

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý các callback từ nút inline"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Lấy dữ liệu callback
    callback_data = query.data
    
    # Xử lý callback dựa trên loại
    if callback_data.startswith("setlang_"):
        # Xử lý callback cài đặt ngôn ngữ
        await handle_setlang_callback(query, user_id, callback_data)
    elif callback_data.startswith("unregister_"):
        # Xử lý callback hủy đăng ký kênh
        await handle_unregister_callback(query, user_id, callback_data)
    elif callback_data.startswith("register_"):
        # Xử lý callback đăng ký kênh
        await handle_register_callback(query, user_id, callback_data)
    elif callback_data == "cancel_register":
        # Xử lý callback hủy đăng ký kênh
        await handle_cancel_register_callback(query, context)
    else:
        # Callback không xác định
        await query.answer("Không thể xử lý yêu cầu này.")

async def handle_setlang_callback(query, user_id, callback_data):
    """Xử lý callback cài đặt ngôn ngữ"""
    # Lấy mã ngôn ngữ từ callback data
    lang_code = callback_data.replace("setlang_", "")
    
    # Kiểm tra xem ngôn ngữ có được hỗ trợ không
    if lang_code not in SUPPORTED_LANGUAGES:
        await query.answer("Ngôn ngữ không được hỗ trợ.")
        return
    
    # Cập nhật ngôn ngữ cho người dùng
    db.update_user_language(user_id, lang_code)
    
    # Thông báo cho người dùng
    lang_name = SUPPORTED_LANGUAGES[lang_code]
    await query.answer(f"Đã cài đặt ngôn ngữ dịch sang {lang_name}.")
    
    # Cập nhật tin nhắn
    await query.edit_message_text(
        f"✅ Đã cài đặt ngôn ngữ dịch sang {lang_name}.\n\n"
        f"Bây giờ bạn có thể đăng ký kênh/bot bằng cách forward tin nhắn từ kênh đó hoặc sử dụng lệnh /register."
    )

async def handle_unregister_callback(query, user_id, callback_data):
    """Xử lý callback hủy đăng ký kênh"""
    # Lấy ID kênh từ callback data
    channel_id = callback_data.replace("unregister_", "")
    
    # Hủy đăng ký kênh cho người dùng
    db.unregister_channel(user_id, channel_id)
    
    # Thông báo cho người dùng
    await query.answer("Đã hủy đăng ký kênh thành công.")
    
    # Lấy danh sách kênh đã đăng ký mới
    channels = db.get_user_channels(user_id)
    
    if not channels:
        # Nếu không còn kênh nào, cập nhật tin nhắn
        await query.edit_message_text(
            "Bạn chưa đăng ký kênh/bot nào.\n\n"
            "Sử dụng lệnh /register hoặc forward tin nhắn từ kênh/bot để đăng ký."
        )
    else:
        # Cập nhật tin nhắn với danh sách kênh mới
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = []
        for channel in channels:
            channel_id = channel.get("channel_id")
            channel_title = channel.get("title") or channel_id
            
            keyboard.append([
                InlineKeyboardButton(f"❌ Hủy {channel_title}", callback_data=f"unregister_{channel_id}")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Danh sách kênh/bot đã đăng ký:\n\n" +
            "\n".join([f"🔹 {channel.get('title') or channel.get('channel_id')}" for channel in channels]) +
            "\n\nNhấn vào nút bên dưới để hủy đăng ký kênh/bot:",
            reply_markup=reply_markup
        )

async def handle_register_callback(query, user_id, callback_data):
    """Xử lý callback đăng ký kênh"""
    # Lấy ID kênh từ callback data
    channel_id = callback_data.replace("register_", "")
    
    try:
        # Kiểm tra kênh có tồn tại không
        chat = await query.bot.get_chat(channel_id)
        
        # Đăng ký kênh cho người dùng
        db.register_channel(user_id, str(chat.id), channel_title=chat.title or channel_id)
        
        # Thông báo cho người dùng
        await query.answer("Đã đăng ký kênh thành công.")
        
        # Cập nhật tin nhắn
        await query.edit_message_text(
            f"✅ Đã đăng ký kênh {chat.title or channel_id} thành công!\n\n"
            f"Bot sẽ tự động dịch tin nhắn mới từ kênh này."
        )
    except Exception as e:
        logging.error(f"Lỗi khi đăng ký kênh: {e}")
        await query.answer("Không thể đăng ký kênh.")
        
        # Cập nhật tin nhắn
        await query.edit_message_text(
            f"❌ Không thể đăng ký kênh. Lỗi: {str(e)}\n\n"
            f"Nguyên nhân có thể là:\n"
            f"- Kênh không tồn tại\n"
            f"- Bot không có quyền truy cập kênh\n"
            f"- ID kênh không đúng định dạng\n\n"
            f"Vui lòng kiểm tra lại và thử lại."
        )

async def handle_cancel_register_callback(query, context):
    """Xử lý callback hủy đăng ký kênh"""
    # Xóa trạng thái đăng ký kênh
    if 'register_command' in context.user_data:
        context.user_data.pop('register_command')
    
    # Thông báo cho người dùng
    await query.answer("Đã hủy thao tác đăng ký kênh.")
    
    # Cập nhật tin nhắn
    await query.edit_message_text("❌ Đã hủy thao tác đăng ký kênh.")
    
    return ConversationHandler.END 