from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import logging

from src.database import db
from src.config import SUPPORTED_LANGUAGES, BOT_INTERFACE_LANGUAGES, DEFAULT_INTERFACE_LANGUAGE

# Thiết lập logger
logger = logging.getLogger(__name__)

async def button_callback(update, context):
    """Xử lý các callback từ nút bấm"""
    query = update.callback_query
    user_id = query.from_user.id
    callback_data = query.data
    
    try:
        # Xử lý callback đăng ký
        if callback_data.startswith("register_"):
            await handle_register_callback(query, context, user_id)
        
        # Xử lý callback hủy đăng ký
        elif callback_data.startswith("unregister_"):
            await handle_unregister_callback(query, context, user_id)
        
        # Xử lý callback xác nhận hủy đăng ký
        elif callback_data.startswith("confirm_unregister_"):
            await handle_unregister_callback(query, context, user_id, confirmed=True)
        
        # Xử lý callback hủy thao tác hủy đăng ký
        elif callback_data.startswith("cancel_unregister_"):
            channel_id = callback_data.split("_")[2]
            await handle_back_to_channels_callback(query, user_id)
        
        # Xử lý callback thông tin kênh
        elif callback_data.startswith("channel_info_"):
            channel_id = callback_data.split("_")[2]
            await handle_channel_info_callback(query, user_id, channel_id)
        
        # Xử lý callback thông tin nút
        elif callback_data.startswith("button_info_"):
            button_type = callback_data.split("_")[2]
            await handle_button_info_callback(query, user_id, button_type)
        
        # Xử lý callback quay lại danh sách kênh
        elif callback_data == "back_to_channels":
            await handle_back_to_channels_callback(query, user_id)
        
        # Xử lý callback hiển thị danh sách hủy đăng ký
        elif callback_data == "show_unregister":
            await handle_show_unregister_callback(query, user_id)
        
        # Xử lý callback ngôn ngữ
        elif callback_data.startswith("lang_"):
            language = callback_data.split("_")[1]
            await handle_language_callback(query, user_id, language)
        
        # Xử lý callback cài đặt ngôn ngữ dịch
        elif callback_data.startswith("setlang_"):
            await handle_setlang_callback(query, user_id, callback_data)
        
        # Xử lý callback cài đặt ngôn ngữ giao tiếp
        elif callback_data.startswith("setinterfacelang_"):
            await handle_setinterfacelang_callback(query, user_id, callback_data)
        
        # Xử lý callback hiển thị menu cài đặt ngôn ngữ
        elif callback_data == "setlang_prompt":
            await handle_setlang_prompt_callback(query, user_id)
        
        # Xử lý callback hủy đăng ký kênh
        elif callback_data == "cancel_register":
            await handle_cancel_register_callback(query, context)
        
        # Xử lý callback không xác định
        else:
            logger.warning(f"Unhandled callback data: {callback_data}")
            await query.answer("Unsupported button.")
    
    except Exception as e:
        logger.error(f"Error in button_callback: {e}", exc_info=True)
        try:
            await query.answer("An error occurred. Please try again later.")
        except Exception:
            pass

async def handle_setlang_callback(query, user_id, callback_data):
    """Xử lý callback cài đặt ngôn ngữ dịch"""
    # Lấy mã ngôn ngữ từ callback data
    lang_code = callback_data.replace("setlang_", "")
    
    # Kiểm tra xem ngôn ngữ có được hỗ trợ không
    if lang_code not in SUPPORTED_LANGUAGES:
        await query.answer("Ngôn ngữ không được hỗ trợ.")
        return
    
    # Cập nhật ngôn ngữ cho người dùng
    db.update_user_language(user_id, lang_code)
    
    # Lấy thông tin người dùng để biết ngôn ngữ giao tiếp
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE)
    
    # Lấy tên ngôn ngữ
    lang_name = SUPPORTED_LANGUAGES[lang_code]
    
    # Thông báo cho người dùng theo ngôn ngữ giao tiếp
    if interface_language == "en":
        await query.answer(f"Target translation language set to {lang_name}.")
        
        # Cập nhật tin nhắn
        await query.edit_message_text(
            f"✅ Target translation language set to {lang_name}.\n\n"
            f"Now you can:\n"
            f"• Send any text message to translate it to {lang_name}\n"
            f"• Send an image with text to extract and translate it\n"
            f"• Send a video with caption to translate the caption\n"
            f"• Forward messages from other channels/bots to translate them\n\n"
            f"You can also register channels to automatically translate new messages using the /register command."
        )
    else:
        await query.answer(f"Đã cài đặt ngôn ngữ dịch mục tiêu sang {lang_name}.")
        
        # Cập nhật tin nhắn
        await query.edit_message_text(
            f"✅ Đã cài đặt ngôn ngữ dịch mục tiêu sang {lang_name}.\n\n"
            f"Bây giờ bạn có thể:\n"
            f"• Gửi bất kỳ tin nhắn văn bản nào để dịch sang {lang_name}\n"
            f"• Gửi hình ảnh có chứa văn bản để trích xuất và dịch\n"
            f"• Gửi video có caption để dịch caption\n"
            f"• Forward tin nhắn từ các kênh/bot khác để dịch\n\n"
            f"Bạn cũng có thể đăng ký kênh để tự động dịch tin nhắn mới bằng lệnh /register."
        )

async def handle_setinterfacelang_callback(query, user_id, callback_data):
    """Xử lý callback cài đặt ngôn ngữ giao tiếp"""
    # Lấy mã ngôn ngữ từ callback data
    lang_code = callback_data.replace("setinterfacelang_", "")
    
    # Kiểm tra xem ngôn ngữ có được hỗ trợ không
    if lang_code not in BOT_INTERFACE_LANGUAGES:
        await query.answer("Ngôn ngữ không được hỗ trợ.")
        return
    
    # Cập nhật ngôn ngữ giao tiếp cho người dùng
    db.update_user_interface_language(user_id, lang_code)
    
    # Thông báo cho người dùng theo ngôn ngữ giao tiếp mới
    lang_name = BOT_INTERFACE_LANGUAGES[lang_code]
    if lang_code == "en":
        await query.answer(f"Bot interface language set to {lang_name}.")
        
        # Cập nhật tin nhắn
        await query.edit_message_text(
            f"✅ Bot interface language set to {lang_name}.\n\n"
            f"The bot will now communicate with you in English.\n\n"
            f"• To set your target translation language, use /setlang\n"
            f"• To register a channel for automatic translation, use /register\n"
            f"• To view your registered channels, use /channels\n"
            f"• To get help, use /help"
        )
    else:
        await query.answer(f"Đã cài đặt ngôn ngữ giao tiếp của bot sang {lang_name}.")
        
        # Cập nhật tin nhắn
        await query.edit_message_text(
            f"✅ Đã cài đặt ngôn ngữ giao tiếp của bot sang {lang_name}.\n\n"
            f"Bot sẽ giao tiếp với bạn bằng Tiếng Việt.\n\n"
            f"• Để cài đặt ngôn ngữ dịch mục tiêu, sử dụng lệnh /setlang\n"
            f"• Để đăng ký kênh để tự động dịch, sử dụng lệnh /register\n"
            f"• Để xem danh sách kênh đã đăng ký, sử dụng lệnh /channels\n"
            f"• Để xem trợ giúp, sử dụng lệnh /help"
        )

async def handle_unregister_callback(query, context, user_id, confirmed=False):
    """Xử lý callback hủy đăng ký kênh"""
    # Lấy thông tin người dùng
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Lấy channel_id từ callback_data
    callback_data = query.data
    
    if confirmed:
        # Nếu đã xác nhận, lấy channel_id từ confirm_unregister_
        channel_id = callback_data.split("_")[2]
    else:
        # Nếu chưa xác nhận, lấy channel_id từ unregister_
        channel_id = callback_data.split("_")[1]
    
    # Kiểm tra xem kênh có tồn tại trong danh sách đăng ký không
    channels = db.get_user_channels(user_id)
    channel_exists = False
    channel_title = None
    
    for channel in channels:
        if channel.get("channel_id") == channel_id:
            channel_exists = True
            channel_title = channel.get("title") or channel_id
            break
    
    if not channel_exists:
        # Kênh không tồn tại hoặc đã bị hủy đăng ký
        if interface_language == "en":
            await query.answer("Channel not found or already unregistered.")
        else:
            await query.answer("Kênh không tìm thấy hoặc đã bị hủy đăng ký.")
        
        # Quay lại danh sách kênh
        await handle_show_unregister_callback(query, user_id)
        return
    
    if not confirmed:
        # Hiển thị xác nhận trước khi hủy đăng ký
        keyboard = []
        
        if interface_language == "en":
            keyboard.append([
                InlineKeyboardButton("✅ Yes, unregister", callback_data=f"confirm_unregister_{channel_id}"),
                InlineKeyboardButton("❌ No, cancel", callback_data=f"cancel_unregister_{channel_id}")
            ])
        else:
            keyboard.append([
                InlineKeyboardButton("✅ Có, hủy đăng ký", callback_data=f"confirm_unregister_{channel_id}"),
                InlineKeyboardButton("❌ Không, hủy bỏ", callback_data=f"cancel_unregister_{channel_id}")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if interface_language == "en":
            await query.edit_message_text(
                f"❓ *Are you sure you want to unregister {channel_title}?*\n\n"
                "You will no longer receive translations for messages from this channel.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                f"❓ *Bạn có chắc chắn muốn hủy đăng ký {channel_title}?*\n\n"
                "Bạn sẽ không còn nhận được bản dịch cho tin nhắn từ kênh này.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        return
    
    # Đã xác nhận, tiến hành hủy đăng ký
    try:
        # Hủy đăng ký kênh
        db.unregister_channel(user_id, channel_id)
        
        # Thông báo thành công
        if interface_language == "en":
            await query.answer(f"Successfully unregistered {channel_title}.")
        else:
            await query.answer(f"Đã hủy đăng ký {channel_title} thành công.")
        
        # Kiểm tra xem còn kênh nào đã đăng ký không
        channels = db.get_user_channels(user_id)
        
        if not channels:
            # Không còn kênh nào, hiển thị thông báo
            if interface_language == "en":
                await query.edit_message_text(
                    "You have no registered channels.\n\n"
                    "Use the /register command or forward a message from a channel to register it."
                )
            else:
                await query.edit_message_text(
                    "Bạn không còn kênh nào đã đăng ký.\n\n"
                    "Sử dụng lệnh /register hoặc forward tin nhắn từ kênh để đăng ký."
                )
        else:
            # Còn kênh, quay lại danh sách hủy đăng ký
            await handle_show_unregister_callback(query, user_id)
    
    except Exception as e:
        logger.error(f"Error unregistering channel: {e}", exc_info=True)
        
        if interface_language == "en":
            await query.answer("An error occurred while unregistering the channel. Please try again.")
        else:
            await query.answer("Đã xảy ra lỗi khi hủy đăng ký kênh. Vui lòng thử lại.")

async def handle_register_callback(query, context, user_id):
    """Xử lý callback đăng ký kênh"""
    # Lấy thông tin người dùng
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Lấy channel_id từ callback_data
    callback_data = query.data
    channel_id = callback_data.split("_")[1]
    
    try:
        # Lấy thông tin kênh từ Telegram
        chat = await context.bot.get_chat(channel_id)
        
        # Lấy thông tin kênh
        channel_title = chat.title if hasattr(chat, 'title') else chat.username
        
        # Đăng ký kênh cho người dùng
        db.register_channel(
            user_id=user_id,
            channel_id=channel_id,
            channel_title=channel_title
        )
        
        # Thông báo thành công
        if interface_language == "en":
            await query.answer(f"Successfully registered {channel_title}.")
        else:
            await query.answer(f"Đã đăng ký {channel_title} thành công.")
        
        # Hiển thị danh sách kênh đã đăng ký
        await handle_back_to_channels_callback(query, user_id)
    
    except Exception as e:
        logger.error(f"Error registering channel: {e}", exc_info=True)
        
        # Thông báo lỗi
        if interface_language == "en":
            await query.answer("Failed to register the channel. Please try again.")
        else:
            await query.answer("Không thể đăng ký kênh. Vui lòng thử lại.")

async def handle_cancel_register_callback(query, context):
    """Xử lý callback hủy đăng ký kênh"""
    # Lấy thông tin người dùng
    user_id = query.from_user.id
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Xóa trạng thái đăng ký kênh
    if 'register_command' in context.user_data:
        context.user_data.pop('register_command', None)
    
    # Thông báo hủy thao tác
    if interface_language == "en":
        await query.edit_message_text(
            "Channel registration cancelled."
        )
    else:
        await query.edit_message_text(
            "Đã hủy thao tác đăng ký kênh."
        )

async def handle_setlang_prompt_callback(query, user_id):
    """Xử lý callback hiển thị menu cài đặt ngôn ngữ"""
    # Lấy thông tin người dùng
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
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
    
    # Hiển thị tin nhắn theo ngôn ngữ giao tiếp
    if interface_language == "en":
        await query.edit_message_text(
            "Please select your target translation language:",
            reply_markup=reply_markup
        )
    else:
        await query.edit_message_text(
            "Vui lòng chọn ngôn ngữ dịch mục tiêu của bạn:",
            reply_markup=reply_markup
        )
    
    # Thông báo cho người dùng
    if interface_language == "en":
        await query.answer("Select your target translation language")
    else:
        await query.answer("Chọn ngôn ngữ dịch mục tiêu của bạn")

async def handle_channel_info_callback(query, user_id, channel_id):
    """Xử lý callback hiển thị thông tin kênh"""
    # Lấy thông tin người dùng
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Lấy thông tin kênh từ cơ sở dữ liệu
    channels = db.get_user_channels(user_id)
    channel = None
    
    for ch in channels:
        if ch.get("channel_id") == channel_id:
            channel = ch
            break
    
    if not channel:
        # Kênh không tồn tại hoặc đã bị hủy đăng ký
        if interface_language == "en":
            await query.answer("Channel not found or already unregistered.")
        else:
            await query.answer("Kênh không tìm thấy hoặc đã bị hủy đăng ký.")
        
        # Quay lại danh sách kênh
        await handle_back_to_channels_callback(query, user_id)
        return
    
    # Lấy thông tin kênh
    channel_title = channel.get("title") or channel_id
    channel_username = channel.get("username")
    
    # Tạo URL cho kênh/bot
    channel_url = None
    if channel_id.startswith("-100"):
        # Kênh công khai
        if channel_username:
            channel_url = f"https://t.me/{channel_username}"
    else:
        # Bot
        channel_url = f"https://t.me/{channel_title}"
    
    # Tạo nút quay lại và hủy đăng ký
    keyboard = []
    
    # Nút mở kênh nếu có URL
    if channel_url:
        if interface_language == "en":
            keyboard.append([InlineKeyboardButton(f"🔗 Open {channel_title}", url=channel_url)])
        else:
            keyboard.append([InlineKeyboardButton(f"🔗 Mở {channel_title}", url=channel_url)])
    
    # Nút hủy đăng ký
    if interface_language == "en":
        keyboard.append([InlineKeyboardButton(f"❌ Unregister {channel_title}", callback_data=f"unregister_{channel_id}")])
    else:
        keyboard.append([InlineKeyboardButton(f"❌ Hủy đăng ký {channel_title}", callback_data=f"unregister_{channel_id}")])
    
    # Nút quay lại
    if interface_language == "en":
        keyboard.append([InlineKeyboardButton("⬅️ Back to Channels List", callback_data="back_to_channels")])
    else:
        keyboard.append([InlineKeyboardButton("⬅️ Quay lại Danh sách Kênh", callback_data="back_to_channels")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Hiển thị thông tin kênh
    if interface_language == "en":
        await query.edit_message_text(
            f"ℹ️ *Channel Information:*\n\n"
            f"*Title:* {channel_title}\n"
            f"*Username:* {f'@{channel_username}' if channel_username else 'N/A'}\n"
            f"*ID:* `{channel_id}`\n\n"
            f"You can open the channel directly or unregister it.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(
            f"ℹ️ *Thông tin Kênh:*\n\n"
            f"*Tiêu đề:* {channel_title}\n"
            f"*Tên người dùng:* {f'@{channel_username}' if channel_username else 'N/A'}\n"
            f"*ID:* `{channel_id}`\n\n"
            f"Bạn có thể mở kênh trực tiếp hoặc hủy đăng ký.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def handle_back_to_channels_callback(query, user_id):
    """Xử lý callback quay lại danh sách kênh"""
    # Lấy thông tin người dùng
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Lấy danh sách kênh đã đăng ký
    channels = db.get_user_channels(user_id)
    
    if not channels:
        if interface_language == "en":
            await query.edit_message_text(
                "You haven't registered any channels yet.\n\n"
                "Use the /register command or forward a message from a channel to register it."
            )
        else:
            await query.edit_message_text(
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
        
        # Tạo URL cho kênh
        channel_url = None
        channel_username = channel.get("username")
        
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
    
    # Thêm nút để hiển thị danh sách hủy đăng ký
    if interface_language == "en":
        keyboard.append([InlineKeyboardButton("❌ Unregister Channels", callback_data="show_unregister")])
    else:
        keyboard.append([InlineKeyboardButton("❌ Hủy đăng ký Kênh", callback_data="show_unregister")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Hiển thị danh sách kênh
    if interface_language == "en":
        await query.edit_message_text(
            "📢 *Your registered channels:*\n\n"
            f"{channel_list_text}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(
            "📢 *Các kênh bạn đã đăng ký:*\n\n"
            f"{channel_list_text}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def handle_button_info_callback(query, user_id, button_type):
    """Xử lý callback hiển thị thông tin nút"""
    # Lấy thông tin người dùng
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Tạo nút quay lại
    keyboard = []
    if interface_language == "en":
        keyboard.append([InlineKeyboardButton("⬅️ Back to Channels List", callback_data="back_to_channels")])
    else:
        keyboard.append([InlineKeyboardButton("⬅️ Quay lại Danh sách Kênh", callback_data="back_to_channels")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Hiển thị thông tin nút tương ứng
    if button_type == "open":
        if interface_language == "en":
            await query.edit_message_text(
                "🔗 *Open Button:*\n\n"
                "This button allows you to open the channel or bot directly in Telegram.\n"
                "Click on it to view the channel's content or interact with the bot.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "🔗 *Nút Mở:*\n\n"
                "Nút này cho phép bạn mở kênh hoặc bot trực tiếp trong Telegram.\n"
                "Nhấn vào nó để xem nội dung kênh hoặc tương tác với bot.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    
    elif button_type == "info":
        if interface_language == "en":
            await query.edit_message_text(
                "ℹ️ *Info Button:*\n\n"
                "This button shows detailed information about the channel or bot.\n"
                "Click on it to view the channel's title, username, and ID.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "ℹ️ *Nút Thông tin:*\n\n"
                "Nút này hiển thị thông tin chi tiết về kênh hoặc bot.\n"
                "Nhấn vào nó để xem tiêu đề, tên người dùng và ID của kênh.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    
    elif button_type == "unregister":
        if interface_language == "en":
            await query.edit_message_text(
                "❌ *Unregister Button:*\n\n"
                "This button allows you to unregister a channel or bot.\n"
                "After unregistering, you will no longer receive translations for messages from this source.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                "❌ *Nút Hủy đăng ký:*\n\n"
                "Nút này cho phép bạn hủy đăng ký kênh hoặc bot.\n"
                "Sau khi hủy đăng ký, bạn sẽ không còn nhận được bản dịch cho tin nhắn từ nguồn này.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    
    else:
        # Loại nút không xác định
        if interface_language == "en":
            await query.answer("Unknown button type.")
        else:
            await query.answer("Loại nút không xác định.")

async def handle_show_unregister_callback(query, user_id):
    """Xử lý callback hiển thị danh sách hủy đăng ký"""
    # Lấy thông tin người dùng
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Lấy danh sách kênh đã đăng ký
    channels = db.get_user_channels(user_id)
    
    if not channels:
        if interface_language == "en":
            await query.edit_message_text(
                "You haven't registered any channels yet.\n\n"
                "Use the /register command or forward a message from a channel to register it."
            )
        else:
            await query.edit_message_text(
                "Bạn chưa đăng ký kênh nào.\n\n"
                "Sử dụng lệnh /register hoặc forward tin nhắn từ kênh để đăng ký."
            )
        return
    
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
        await query.edit_message_text(
            "*Select a channel to unregister:*",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(
            "*Chọn kênh để hủy đăng ký:*",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def handle_language_callback(query, user_id, language):
    """Xử lý callback cài đặt ngôn ngữ"""
    # Lấy thông tin người dùng
    user = db.get_user(user_id)
    interface_language = user.get("interface_language", DEFAULT_INTERFACE_LANGUAGE) if user else DEFAULT_INTERFACE_LANGUAGE
    
    # Cập nhật ngôn ngữ dịch cho người dùng
    db.update_user_language(user_id, language)
    
    # Thông báo thành công
    if interface_language == "en":
        await query.answer(f"Translation language set to {language.upper()}")
    else:
        await query.answer(f"Đã đặt ngôn ngữ dịch thành {language.upper()}")
    
    # Hiển thị thông báo cài đặt ngôn ngữ
    keyboard = []
    
    # Thêm nút quay lại
    if interface_language == "en":
        keyboard.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="back_to_main")])
    else:
        keyboard.append([InlineKeyboardButton("⬅️ Quay lại Menu Chính", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if interface_language == "en":
        await query.edit_message_text(
            f"✅ *Translation language set to {language.upper()}*\n\n"
            f"All messages will now be translated to {language.upper()}.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(
            f"✅ *Đã đặt ngôn ngữ dịch thành {language.upper()}*\n\n"
            f"Tất cả tin nhắn sẽ được dịch sang {language.upper()}.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        ) 