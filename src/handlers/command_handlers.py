from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import logging

from src.database import db
from src.config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

# Định nghĩa các trạng thái cho ConversationHandler
WAITING_FOR_CHANNEL = 1

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /start"""
    user = update.effective_user
    user_id = user.id
    
    # Kiểm tra và tạo người dùng trong database nếu chưa tồn tại
    db_user = db.get_user(user_id)
    if not db_user:
        db.create_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            language_code=user.language_code or DEFAULT_LANGUAGE
        )
    
    # Gửi tin nhắn chào mừng
    welcome_message = (
        f"Xin chào {user.first_name}! 👋\n\n"
        f"Tôi là Bot Dịch Thuật Telegram. Tôi có thể giúp bạn dịch tin nhắn từ các kênh và bot khác.\n\n"
        f"🔹 Để cài đặt ngôn ngữ dịch, sử dụng lệnh /setlang\n"
        f"🔹 Để đăng ký kênh/bot, forward một tin nhắn từ kênh đó hoặc sử dụng lệnh /register\n"
        f"🔹 Để xem danh sách kênh đã đăng ký, sử dụng lệnh /channels\n"
        f"🔹 Để dịch tin nhắn, chỉ cần forward tin nhắn đó cho tôi\n\n"
        f"Hãy bắt đầu bằng cách cài đặt ngôn ngữ dịch với lệnh /setlang"
    )
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /help"""
    help_message = (
        "📚 *Hướng dẫn sử dụng Bot Dịch Thuật* 📚\n\n"
        "*Các lệnh cơ bản:*\n"
        "/start - Khởi động bot\n"
        "/help - Hiển thị hướng dẫn này\n"
        "/setlang - Cài đặt ngôn ngữ dịch\n"
        "/register - Đăng ký kênh/bot mới\n"
        "/channels - Xem danh sách kênh đã đăng ký\n"
        "/unregister - Hủy đăng ký kênh\n\n"
        
        "*Cách sử dụng:*\n"
        "1️⃣ Cài đặt ngôn ngữ dịch bằng lệnh /setlang\n"
        "2️⃣ Đăng ký kênh/bot bằng cách forward tin nhắn từ kênh đó hoặc sử dụng lệnh /register\n"
        "3️⃣ Bot sẽ tự động dịch tin nhắn mới từ các kênh đã đăng ký\n"
        "4️⃣ Bạn cũng có thể forward bất kỳ tin nhắn nào để dịch\n\n"
        
        "*Lưu ý:*\n"
        "- Bot cần được thêm vào kênh/nhóm để nhận tin nhắn mới\n"
        "- Nếu bạn gặp vấn đề, hãy thử khởi động lại bot với lệnh /start"
    )
    
    await update.message.reply_text(help_message, parse_mode="Markdown")

async def setlang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /setlang"""
    # Tạo danh sách nút cho các ngôn ngữ hỗ trợ
    keyboard = []
    row = []
    
    for i, (lang_code, lang_name) in enumerate(SUPPORTED_LANGUAGES.items()):
        # Tạo 3 nút trên mỗi hàng
        row.append(InlineKeyboardButton(lang_name, callback_data=f"setlang_{lang_code}"))
        
        if (i + 1) % 3 == 0 or i == len(SUPPORTED_LANGUAGES) - 1:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Vui lòng chọn ngôn ngữ bạn muốn dịch sang:",
        reply_markup=reply_markup
    )

async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /register"""
    # Kiểm tra xem người dùng đã cung cấp ID kênh chưa
    if not context.args:
        # Lưu trữ thông tin người dùng vào user_data
        context.user_data['register_command'] = True
        
        # Yêu cầu người dùng nhập ID kênh
        await update.message.reply_text(
            "Vui lòng nhập ID hoặc username của kênh/bot bạn muốn đăng ký.\n\n"
            "Ví dụ: @channel_name hoặc -1001234567890\n\n"
            "Hoặc bạn có thể forward một tin nhắn từ kênh/bot đó để đăng ký.\n\n"
            "Gửi /cancel để hủy thao tác."
        )
        
        # Chuyển sang trạng thái chờ người dùng nhập kênh
        return WAITING_FOR_CHANNEL
    
    channel_id = context.args[0]
    user_id = update.effective_user.id
    
    try:
        # Đăng ký kênh cho người dùng
        db.register_channel(user_id, channel_id, channel_title=channel_id)
        
        await update.message.reply_text(
            f"✅ Đã đăng ký kênh {channel_id} thành công!\n\n"
            f"Bot sẽ tự động dịch tin nhắn mới từ kênh này."
        )
    except Exception as e:
        logging.error(f"Lỗi khi đăng ký kênh: {e}")
        await update.message.reply_text(
            f"❌ Có lỗi xảy ra khi đăng ký kênh: {str(e)}\n\n"
            f"Vui lòng kiểm tra lại ID kênh và thử lại."
        )

async def register_channel_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input khi người dùng nhập ID kênh"""
    # Kiểm tra xem người dùng có đang trong quá trình đăng ký kênh không
    if not context.user_data.get('register_command'):
        return ConversationHandler.END
    
    # Xóa trạng thái đăng ký kênh
    context.user_data.pop('register_command', None)
    
    # Lấy ID kênh từ tin nhắn của người dùng
    channel_id = update.message.text.strip()
    
    # Kiểm tra nếu người dùng muốn hủy thao tác
    if channel_id.lower() == '/cancel':
        await update.message.reply_text("Đã hủy thao tác đăng ký kênh.")
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    
    try:
        # Đăng ký kênh cho người dùng
        db.register_channel(user_id, channel_id, channel_title=channel_id)
        
        await update.message.reply_text(
            f"✅ Đã đăng ký kênh {channel_id} thành công!\n\n"
            f"Bot sẽ tự động dịch tin nhắn mới từ kênh này."
        )
    except Exception as e:
        logging.error(f"Lỗi khi đăng ký kênh: {e}")
        await update.message.reply_text(
            f"❌ Có lỗi xảy ra khi đăng ký kênh: {str(e)}\n\n"
            f"Vui lòng kiểm tra lại ID kênh và thử lại."
        )
    
    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hủy thao tác hiện tại"""
    # Xóa tất cả dữ liệu trong user_data
    context.user_data.clear()
    
    await update.message.reply_text("Đã hủy thao tác hiện tại.")
    
    return ConversationHandler.END

async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /channels"""
    user_id = update.effective_user.id
    
    # Lấy danh sách kênh đã đăng ký
    channels = db.get_user_channels(user_id)
    
    if not channels:
        await update.message.reply_text(
            "Bạn chưa đăng ký kênh/bot nào.\n\n"
            "Sử dụng lệnh /register hoặc forward tin nhắn từ kênh/bot để đăng ký."
        )
        return
    
    # Tạo danh sách nút cho các kênh đã đăng ký
    keyboard = []
    
    for channel in channels:
        channel_id = channel.get("channel_id")
        channel_title = channel.get("title") or channel_id
        
        # Tạo nút để hủy đăng ký kênh
        keyboard.append([
            InlineKeyboardButton(f"❌ Hủy {channel_title}", callback_data=f"unregister_{channel_id}")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Danh sách kênh/bot đã đăng ký:\n\n" +
        "\n".join([f"🔹 {channel.get('title') or channel.get('channel_id')}" for channel in channels]) +
        "\n\nNhấn vào nút bên dưới để hủy đăng ký kênh/bot:",
        reply_markup=reply_markup
    )

async def unregister_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /unregister"""
    # Kiểm tra xem người dùng đã cung cấp ID kênh chưa
    if not context.args:
        # Hiển thị danh sách kênh để người dùng chọn
        await channels_command(update, context)
        return
    
    channel_id = context.args[0]
    user_id = update.effective_user.id
    
    try:
        # Hủy đăng ký kênh cho người dùng
        db.unregister_channel(user_id, channel_id)
        
        await update.message.reply_text(
            f"✅ Đã hủy đăng ký kênh {channel_id} thành công!"
        )
    except Exception as e:
        logging.error(f"Lỗi khi hủy đăng ký kênh: {e}")
        await update.message.reply_text(
            f"❌ Có lỗi xảy ra khi hủy đăng ký kênh: {str(e)}\n\n"
            f"Vui lòng kiểm tra lại ID kênh và thử lại."
        ) 