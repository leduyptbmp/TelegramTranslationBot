from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes, ConversationHandler
import logging
import re

from src.database import db
from src.config import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, BOT_INTERFACE_LANGUAGES, DEFAULT_INTERFACE_LANGUAGE

# Định nghĩa các trạng thái cho ConversationHandler
WAITING_FOR_CHANNEL = 1

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /start"""
    user = update.effective_user
    user_id = user.id
    
    # Kiểm tra và tạo người dùng trong database nếu chưa tồn tại
    db_user = db.get_user(user_id)
    if not db_user:
        # Xác định ngôn ngữ giao tiếp từ ngôn ngữ của người dùng nếu được hỗ trợ
        user_lang = user.language_code
        interface_language = user_lang if user_lang in BOT_INTERFACE_LANGUAGES else DEFAULT_INTERFACE_LANGUAGE
        
        # Tạo người dùng mới trong database
        db.create_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language=DEFAULT_LANGUAGE,
            interface_language=interface_language
        )
    else:
        # Lấy ngôn ngữ giao tiếp từ database
        interface_language = db_user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE)
    
    # Tạo nút cài đặt ngôn ngữ
    keyboard = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Gửi tin nhắn chào mừng
    if interface_language == "en":
        await update.message.reply_text(
            f"👋 Hello, {user.first_name}!\n\n"
            f"I am a Telegram Translation Bot. I can automatically translate messages from channels you register.\n\n"
            f"Here are the available commands:\n"
            f"/register - Register a channel for translation\n"
            f"/channels - View your registered channels\n"
            f"/unregister - Unregister a channel\n"
            f"/setlang - Set your translation language\n"
            f"/setinterfacelang - Set the bot interface language\n"
            f"/help - Show help information\n\n"
            f"To register a channel, use the /register command or forward a message from the channel to me.",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            f"👋 Xin chào, {user.first_name}!\n\n"
            f"Tôi là Bot Dịch Telegram. Tôi có thể tự động dịch tin nhắn từ các kênh bạn đăng ký.\n\n"
            f"Dưới đây là các lệnh có sẵn:\n"
            f"/register - Đăng ký kênh để dịch\n"
            f"/channels - Xem các kênh đã đăng ký\n"
            f"/unregister - Hủy đăng ký kênh\n"
            f"/setlang - Đặt ngôn ngữ dịch của bạn\n"
            f"/setinterfacelang - Đặt ngôn ngữ giao diện bot\n"
            f"/help - Hiển thị thông tin trợ giúp\n\n"
            f"Để đăng ký kênh, sử dụng lệnh /register hoặc chuyển tiếp một tin nhắn từ kênh đến tôi.",
            reply_markup=reply_markup
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /help"""
    # Lấy thông tin người dùng
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    # Lấy ngôn ngữ giao tiếp của người dùng
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Hiển thị hướng dẫn theo ngôn ngữ giao tiếp
    if interface_language == "en":
        help_message = (
            "📚 *Telegram Translation Bot User Guide* 📚\n\n"
            "*Basic Commands:*\n"
            "/start - Start the bot\n"
            "/help - Display this guide\n"
            "/setlang - Set translation language\n"
            "/setinterfacelang - Set bot interface language\n"
            "/register - Register a new channel\n"
            "/channels - View list of registered channels\n"
            "/unregister - Unregister a channel\n\n"
            
            "*How to Use:*\n"
            "1️⃣ Set translation language with /setlang command\n"
            "2️⃣ Register a channel by forwarding a message from that channel or using /register command\n"
            "3️⃣ The bot will automatically translate new messages from registered channels\n"
            "4️⃣ You can also forward any message to translate\n"
            "5️⃣ Send an image containing text for the bot to extract and translate\n\n"
            
            "*Notes:*\n"
            "- The bot needs to be added to the channel/group to receive new messages\n"
            "- To use OCR feature, send clear images with readable text\n"
            "- If you encounter any issues, try restarting the bot with /start command"
        )
    else:
        help_message = (
            "📚 *Hướng dẫn sử dụng Bot Dịch Thuật* 📚\n\n"
            "*Các lệnh cơ bản:*\n"
            "/start - Khởi động bot\n"
            "/help - Hiển thị hướng dẫn này\n"
            "/setlang - Cài đặt ngôn ngữ dịch\n"
            "/setinterfacelang - Cài đặt ngôn ngữ giao tiếp của bot\n"
            "/register - Đăng ký kênh mới\n"
            "/channels - Xem danh sách kênh đã đăng ký\n"
            "/unregister - Hủy đăng ký kênh\n\n"
            
            "*Cách sử dụng:*\n"
            "1️⃣ Cài đặt ngôn ngữ dịch bằng lệnh /setlang\n"
            "2️⃣ Đăng ký kênh bằng cách forward tin nhắn từ kênh đó hoặc sử dụng lệnh /register\n"
            "3️⃣ Bot sẽ tự động dịch tin nhắn mới từ các kênh đã đăng ký\n"
            "4️⃣ Bạn cũng có thể forward bất kỳ tin nhắn nào để dịch\n"
            "5️⃣ Gửi hình ảnh có chứa văn bản để bot trích xuất và dịch\n\n"
            
            "*Lưu ý:*\n"
            "- Bot cần được thêm vào kênh/nhóm để nhận tin nhắn mới\n"
            "- Để sử dụng tính năng OCR, hãy gửi hình ảnh rõ nét và có văn bản dễ đọc\n"
            "- Nếu bạn gặp vấn đề, hãy thử khởi động lại bot với lệnh /start"
        )
    
    await update.message.reply_text(help_message, parse_mode="Markdown")

async def setlang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /setlang"""
    # Lấy thông tin người dùng
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    # Lấy ngôn ngữ dịch và giao tiếp của người dùng
    target_language = user.get("language_code", DEFAULT_LANGUAGE) if user else DEFAULT_LANGUAGE
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Tạo danh sách nút cho các ngôn ngữ hỗ trợ
    keyboard = []
    row = []
    
    for i, (lang_code, lang_name) in enumerate(SUPPORTED_LANGUAGES.items()):
        # Đánh dấu ngôn ngữ hiện tại
        button_text = f"{lang_name} ✓" if lang_code == target_language else lang_name
        
        # Tạo 3 nút trên mỗi hàng
        row.append(InlineKeyboardButton(button_text, callback_data=f"setlang_{lang_code}"))
        
        if (i + 1) % 3 == 0 or i == len(SUPPORTED_LANGUAGES) - 1:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Hiển thị tin nhắn theo ngôn ngữ giao tiếp
    current_lang_name = SUPPORTED_LANGUAGES.get(target_language, target_language)
    if interface_language == "en":
        message = f"Your current target translation language is: {current_lang_name}\n\nPlease select the language you want to translate to:"
    else:
        message = f"Ngôn ngữ dịch mục tiêu hiện tại của bạn là: {current_lang_name}\n\nVui lòng chọn ngôn ngữ bạn muốn dịch sang:"
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def setinterfacelang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /setinterfacelang"""
    # Lấy thông tin người dùng
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    
    # Lấy ngôn ngữ giao tiếp của người dùng
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Tạo danh sách nút cho các ngôn ngữ giao tiếp
    keyboard = []
    row = []
    
    for i, (lang_code, lang_name) in enumerate(BOT_INTERFACE_LANGUAGES.items()):
        # Đánh dấu ngôn ngữ hiện tại
        button_text = f"{lang_name} ✓" if lang_code == interface_language else lang_name
        
        # Tạo 2 nút trên mỗi hàng
        row.append(InlineKeyboardButton(button_text, callback_data=f"setinterfacelang_{lang_code}"))
        
        if (i + 1) % 2 == 0 or i == len(BOT_INTERFACE_LANGUAGES) - 1:
            keyboard.append(row)
            row = []
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Hiển thị tin nhắn theo ngôn ngữ giao tiếp
    current_lang_name = BOT_INTERFACE_LANGUAGES.get(interface_language, interface_language)
    if interface_language == "en":
        message = f"Your current bot interface language is: {current_lang_name}\n\nPlease select the bot interface language:"
    else:
        message = f"Ngôn ngữ giao tiếp hiện tại của bot là: {current_lang_name}\n\nVui lòng chọn ngôn ngữ giao tiếp của bot:"
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /register"""
    # Kiểm tra xem người dùng đã cung cấp ID kênh chưa
    if not context.args:
        # Lưu trữ thông tin người dùng vào user_data
        context.user_data['register_command'] = True
        
        # Tạo nút hủy bỏ
        keyboard = [[InlineKeyboardButton("❌ Hủy bỏ", callback_data="cancel_register")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Yêu cầu người dùng nhập ID kênh
        await update.message.reply_text(
            "Vui lòng nhập ID hoặc username của kênh bạn muốn đăng ký.\n\n"
            "Ví dụ: @channel_name hoặc -1001234567890\n\n"
            "Hoặc bạn có thể forward một tin nhắn từ kênh đó để đăng ký.\n\n"
            "Bạn cũng có thể gửi /cancel để hủy thao tác.",
            reply_markup=reply_markup
        )
        
        # Chuyển sang trạng thái chờ người dùng nhập kênh
        return WAITING_FOR_CHANNEL
    
    channel_id = context.args[0]
    user_id = update.effective_user.id
    
    # Lấy thông tin người dùng
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Kiểm tra định dạng channel_id
    if not is_valid_channel_id(channel_id):
        if interface_language == "en":
            await update.message.reply_text(
                "Invalid channel ID format. Please provide a valid channel ID or username."
            )
        else:
            await update.message.reply_text(
                "❌ ID kênh không hợp lệ. Vui lòng nhập đúng định dạng:\n"
                "- @username cho kênh công khai\n"
                "- -100xxxxxxxxxx cho kênh riêng tư\n\n"
                "Hoặc bạn có thể forward một tin nhắn từ kênh đó để đăng ký."
            )
        return ConversationHandler.END
    
    try:
        # Lấy thông tin kênh từ Telegram
        chat = await context.bot.get_chat(channel_id)
        
        # Lấy thông tin kênh
        channel_title = chat.title if hasattr(chat, 'title') else chat.username
        channel_username = chat.username if hasattr(chat, 'username') else None
        
        # Đăng ký kênh cho người dùng
        db.register_channel(
            user_id=user_id,
            channel_id=str(chat.id),
            channel_title=channel_title
        )
        
        # Thông báo thành công
        if interface_language == "en":
            await update.message.reply_text(
                f"Successfully registered channel: {channel_title}"
            )
        else:
            await update.message.reply_text(
                f"✅ Đã đăng ký kênh {channel_title} thành công!\n\n"
                f"Bot sẽ tự động dịch tin nhắn mới từ kênh này."
            )
    
    except Exception as e:
        logging.error(f"Error registering channel: {e}")
        
        # Thông báo lỗi
        if interface_language == "en":
            await update.message.reply_text(
                "Failed to register the channel. Please check if the ID/username is correct and the bot has access to the channel."
            )
        else:
            await update.message.reply_text(
                f"❌ Không thể đăng ký kênh. Lỗi: {str(e)}\n\n"
                f"Nguyên nhân có thể là:\n"
                f"- Kênh không tồn tại\n"
                f"- Bot không có quyền truy cập kênh\n"
                f"- ID kênh không đúng định dạng\n\n"
                f"Vui lòng kiểm tra lại và thử lại."
            )
    
    return ConversationHandler.END

async def register_channel_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý input khi người dùng nhập ID kênh"""
    # Lấy thông tin người dùng
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Kiểm tra xem người dùng có đang trong quá trình đăng ký kênh không
    if not context.user_data.get('register_command'):
        return ConversationHandler.END
    
    # Lấy ID kênh từ tin nhắn của người dùng
    channel_id = update.message.text.strip()
    
    # Kiểm tra nếu người dùng muốn hủy thao tác
    if channel_id.lower() == '/cancel':
        if interface_language == "en":
            await update.message.reply_text("Channel registration cancelled.")
        else:
            await update.message.reply_text("Đã hủy thao tác đăng ký kênh.")
        
        # Xóa trạng thái đăng ký kênh
        context.user_data.pop('register_command', None)
        return ConversationHandler.END
    
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
    
    # Tạo nút hủy thao tác
    cancel_button = InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ Cancel" if interface_language == "en" else "❌ Hủy", callback_data="cancel_register")
    ]])
    
    # Kiểm tra định dạng channel_id
    if not is_valid_channel_id(channel_id):
        if interface_language == "en":
            await update.message.reply_text(
                "❌ Invalid channel ID. Please enter in the correct format:\n"
                "- @username for public channels\n"
                "- -100xxxxxxxxxx for private channels\n\n"
                "Or you can forward a message from that channel to register it.\n\n"
                "Please try again or type /cancel to cancel the operation.",
                reply_markup=cancel_button
            )
        else:
            await update.message.reply_text(
                "❌ ID kênh không hợp lệ. Vui lòng nhập đúng định dạng:\n"
                "- @username cho kênh công khai\n"
                "- -100xxxxxxxxxx cho kênh riêng tư\n\n"
                "Hoặc bạn có thể forward một tin nhắn từ kênh đó để đăng ký.\n\n"
                "Vui lòng thử lại hoặc gõ /cancel để hủy thao tác.",
                reply_markup=cancel_button
            )
        return WAITING_FOR_CHANNEL
    
    try:
        # Kiểm tra kênh có tồn tại không
        chat = await context.bot.get_chat(channel_id)
        
        # Kiểm tra xem kênh đã được đăng ký chưa
        user_channels = db.get_user_channels(user_id)
        for existing_channel in user_channels:
            if str(existing_channel.get("channel_id")) == str(chat.id):
                if interface_language == "en":
                    await update.message.reply_text(
                        f"⚠️ You have already registered the channel {chat.title or channel_id}.\n\n"
                        f"You can view your registered channels with the /channels command.",
                        reply_markup=cancel_button
                    )
                else:
                    await update.message.reply_text(
                        f"⚠️ Bạn đã đăng ký kênh {chat.title or channel_id} rồi.\n\n"
                        f"Bạn có thể xem danh sách kênh đã đăng ký bằng lệnh /channels.",
                        reply_markup=cancel_button
                    )
                return WAITING_FOR_CHANNEL
        
        # Lấy thông tin kênh
        channel_title = chat.title if hasattr(chat, 'title') else chat.username
        channel_username = chat.username if hasattr(chat, 'username') else None
        
        # Đăng ký kênh cho người dùng
        db.register_channel(
            user_id=user_id,
            channel_id=str(chat.id),
            channel_title=channel_title
        )
        
        if interface_language == "en":
            await update.message.reply_text(
                f"✅ Successfully registered channel {chat.title or channel_id}!\n\n"
                f"The bot will automatically translate new messages from this channel."
            )
        else:
            await update.message.reply_text(
                f"✅ Đã đăng ký kênh {chat.title or channel_id} thành công!\n\n"
                f"Bot sẽ tự động dịch tin nhắn mới từ kênh này."
            )
        
        # Xóa trạng thái đăng ký kênh
        context.user_data.pop('register_command', None)
    except Exception as e:
        logging.error(f"Error registering channel: {e}")
        if interface_language == "en":
            await update.message.reply_text(
                f"❌ Cannot register the channel. Error: {str(e)}\n\n"
                f"Possible reasons:\n"
                f"- The channel does not exist\n"
                f"- The bot does not have access to the channel\n"
                f"- The channel ID format is incorrect\n\n"
                f"Please check and try again, or type /cancel to cancel the operation.",
                reply_markup=cancel_button
            )
        else:
            await update.message.reply_text(
                f"❌ Không thể đăng ký kênh. Lỗi: {str(e)}\n\n"
                f"Nguyên nhân có thể là:\n"
                f"- Kênh không tồn tại\n"
                f"- Bot không có quyền truy cập kênh\n"
                f"- ID kênh không đúng định dạng\n\n"
                f"Vui lòng kiểm tra lại và thử lại, hoặc gõ /cancel để hủy thao tác.",
                reply_markup=cancel_button
            )
        return WAITING_FOR_CHANNEL
    
    return ConversationHandler.END

def is_valid_channel_id(channel_id):
    """Kiểm tra xem channel_id có đúng định dạng không"""
    # Kiểm tra định dạng @username
    if channel_id.startswith('@') and len(channel_id) > 1:
        return True
    
    # Kiểm tra định dạng -100xxxxxxxxxx (ID kênh riêng tư)
    if re.match(r'^-100\d+$', channel_id):
        return True
    
    # Kiểm tra định dạng số nguyên (ID kênh)
    if re.match(r'^-?\d+$', channel_id):
        return True
    
    return False

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /cancel"""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Kiểm tra xem người dùng có đang trong quá trình đăng ký kênh không
    if context.user_data.get('register_command'):
        # Xóa trạng thái đăng ký kênh
        context.user_data.pop('register_command', None)
        
        if interface_language == "en":
            await update.message.reply_text("Channel registration cancelled.")
        else:
            await update.message.reply_text("Đã hủy thao tác đăng ký kênh.")
        
        return ConversationHandler.END
    else:
        if interface_language == "en":
            await update.message.reply_text("No active operation to cancel.")
        else:
            await update.message.reply_text("Không có thao tác nào đang hoạt động để hủy.")

async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /channels để hiển thị danh sách kênh đã đăng ký"""
    user_id = update.effective_user.id
    
    # Lấy thông tin người dùng
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Lấy danh sách kênh đã đăng ký
    channels = db.get_user_channels(user_id)
    
    if not channels:
        # Không có kênh nào đã đăng ký
        if interface_language == "en":
            await update.message.reply_text(
                "You haven't registered any channels yet.\n\n"
                "Use the /register command or forward a message from a channel to register it."
            )
        else:
            await update.message.reply_text(
                "Bạn chưa đăng ký kênh nào.\n\n"
                "Sử dụng lệnh /register hoặc forward tin nhắn từ kênh để đăng ký."
            )
        return
    
    # Tạo danh sách kênh để hiển thị
    channel_list_text = ""
    keyboard = []
    
    for i, channel in enumerate(channels, 1):
        channel_id = channel.get("channel_id")
        channel_title = channel.get("title") or channel_id
        channel_username = channel.get("username")
        
        # Tạo URL cho kênh
        channel_url = None
        
        if channel_id.startswith("-100"):
            # Kênh công khai
            if channel_username:
                channel_url = f"https://t.me/{channel_username}"
                # Thêm @ vào tên kênh nếu có username
                channel_display = f"{channel_title} (@{channel_username})"
            else:
                channel_display = channel_title
        else:
            # Bot
            channel_url = f"https://t.me/{channel_title}"
            # Thêm @ vào tên bot
            channel_display = f"{channel_title} (@{channel_title})"
        
        # Thêm vào danh sách kênh
        channel_list_text += f"{i}. {channel_display}\n"
        
        # Tạo nút mở kênh nếu có URL
        if channel_url:
            if interface_language == "en":
                keyboard.append([InlineKeyboardButton(f"🔗 Open {channel_title}", url=channel_url)])
            else:
                keyboard.append([InlineKeyboardButton(f"🔗 Mở {channel_title}", url=channel_url)])
    
    # Thêm nút để chuyển đến chức năng hủy đăng ký
    if interface_language == "en":
        keyboard.append([InlineKeyboardButton("❌ Unregister Channels", callback_data="show_unregister")])
    else:
        keyboard.append([InlineKeyboardButton("❌ Hủy đăng ký Kênh", callback_data="show_unregister")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Hiển thị danh sách kênh
    if interface_language == "en":
        await update.message.reply_text(
            "📢 *Your registered channels:*\n\n"
            f"{channel_list_text}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "📢 *Các kênh bạn đã đăng ký:*\n\n"
            f"{channel_list_text}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def unregister_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /unregister để hủy đăng ký kênh"""
    user_id = update.effective_user.id
    
    # Lấy thông tin người dùng
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Lấy danh sách kênh đã đăng ký
    channels = db.get_user_channels(user_id)
    
    if not channels:
        # Không có kênh nào đã đăng ký
        if interface_language == "en":
            await update.message.reply_text(
                "You haven't registered any channels yet.\n\n"
                "Use the /register command or forward a message from a channel to register it."
            )
        else:
            await update.message.reply_text(
                "Bạn chưa đăng ký kênh nào.\n\n"
                "Sử dụng lệnh /register hoặc forward tin nhắn từ kênh để đăng ký."
            )
        return
    
    # Kiểm tra xem có tham số không
    if context.args:
        # Lấy ID kênh từ tham số
        channel_id = context.args[0]
        
        # Kiểm tra xem kênh có tồn tại trong danh sách đăng ký không
        channel_exists = False
        for channel in channels:
            if channel.get("channel_id") == channel_id:
                channel_exists = True
                break
        
        if not channel_exists:
            # Kênh không tồn tại hoặc đã bị hủy đăng ký
            if interface_language == "en":
                await update.message.reply_text(
                    "Channel not found or already unregistered."
                )
            else:
                await update.message.reply_text(
                    "Kênh không tìm thấy hoặc đã bị hủy đăng ký."
                )
            return
        
        try:
            # Hủy đăng ký kênh
            db.unregister_channel(user_id, channel_id)
            
            # Thông báo thành công
            if interface_language == "en":
                await update.message.reply_text(
                    "Successfully unregistered the channel."
                )
            else:
                await update.message.reply_text(
                    "Đã hủy đăng ký kênh thành công."
                )
        
        except Exception as e:
            logging.error(f"Error unregistering channel: {e}")
            
            # Thông báo lỗi
            if interface_language == "en":
                await update.message.reply_text(
                    "An error occurred while unregistering the channel. Please try again."
                )
            else:
                await update.message.reply_text(
                    "Đã xảy ra lỗi khi hủy đăng ký kênh. Vui lòng thử lại."
                )
    
    else:
        # Tạo danh sách nút hủy đăng ký cho mỗi kênh
        keyboard = []
        
        for channel in channels:
            channel_id = channel.get("channel_id")
            channel_title = channel.get("title") or channel_id
            
            # Tạo nút hủy đăng ký cho mỗi kênh
            if interface_language == "en":
                keyboard.append([InlineKeyboardButton(f"❌ Unregister {channel_title}", callback_data=f"unregister_{channel_id}")])
            else:
                keyboard.append([InlineKeyboardButton(f"❌ Hủy đăng ký {channel_title}", callback_data=f"unregister_{channel_id}")])
        
        # Thêm nút quay lại danh sách kênh
        if interface_language == "en":
            keyboard.append([InlineKeyboardButton("⬅️ Back to Channels List", callback_data="back_to_channels")])
        else:
            keyboard.append([InlineKeyboardButton("⬅️ Quay lại Danh sách Kênh", callback_data="back_to_channels")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Hiển thị các nút hủy đăng ký
        if interface_language == "en":
            await update.message.reply_text(
                "*Select a channel to unregister:*",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                "*Chọn kênh để hủy đăng ký:*",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            ) 