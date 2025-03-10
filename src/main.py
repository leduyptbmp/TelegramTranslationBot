import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler
import os

from src.config import TELEGRAM_BOT_TOKEN
from src.handlers.command_handlers import (
    start_command, help_command, setlang_command, setinterfacelang_command,
    register_command, channels_command, unregister_command,
    register_channel_input, cancel_command, WAITING_FOR_CHANNEL,
    handle_cancel_register
)
from src.handlers.callback_handlers import button_callback
from src.handlers.message_handlers import handle_message, handle_channel_post

# Tạo thư mục logs nếu chưa tồn tại
if not os.path.exists('logs'):
    os.makedirs('logs')

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,  # Thay đổi level từ DEBUG sang INFO
    handlers=[
        logging.FileHandler('logs/bot.log'),  # Lưu log vào file
        logging.StreamHandler()  # Hiển thị log trên console
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Khởi động bot"""
    # Kiểm tra token
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN không được cấu hình. Vui lòng kiểm tra file .env")
        return
    
    # Khởi tạo ứng dụng
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Đăng ký các command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("setlang", setlang_command))
    application.add_handler(CommandHandler("setinterfacelang", setinterfacelang_command))
    application.add_handler(CommandHandler("channels", channels_command))
    application.add_handler(CommandHandler("unregister", unregister_command))
    
    # Đăng ký ConversationHandler cho lệnh /register
    register_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register_command)],
        states={
            WAITING_FOR_CHANNEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, register_channel_input),
                CallbackQueryHandler(handle_cancel_register, pattern="^cancel_register$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)]
    )
    application.add_handler(register_conv_handler)
    
    # Đăng ký callback handler cho các nút inline
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Đăng ký message handler cho tin nhắn thông thường, hình ảnh và video
    application.add_handler(MessageHandler(
        (filters.TEXT | filters.PHOTO | filters.VIDEO) & ~filters.COMMAND, 
        handle_message
    ))
    
    # Đăng ký channel post handler cho tin nhắn từ kênh
    application.add_handler(MessageHandler(
        filters.ChatType.CHANNEL & (filters.TEXT | filters.PHOTO | filters.VIDEO), 
        handle_channel_post
    ))
    
    # Khởi động bot
    logger.info("Bot đã khởi động")
    application.run_polling()

if __name__ == "__main__":
    main() 