from pymongo import MongoClient
from src.config import MONGODB_URI, DEFAULT_LANGUAGE, DEFAULT_INTERFACE_LANGUAGE

# Kết nối đến MongoDB
client = MongoClient(MONGODB_URI)
db = client.translation_bot

# Collections
users = db.users
channels = db.channels

def get_user(user_id):
    """Lấy thông tin người dùng từ database"""
    return users.find_one({"user_id": user_id})

def create_user(user_id, username=None, first_name=None, language_code=DEFAULT_LANGUAGE, interface_language=DEFAULT_INTERFACE_LANGUAGE):
    """Tạo người dùng mới trong database"""
    user = {
        "user_id": user_id,
        "username": username,
        "first_name": first_name,
        "language_code": language_code,
        "interface_language": interface_language,
        "registered_channels": []
    }
    users.update_one({"user_id": user_id}, {"$set": user}, upsert=True)
    return user

def update_user_language(user_id, language_code):
    """Cập nhật ngôn ngữ dịch cho người dùng"""
    users.update_one({"user_id": user_id}, {"$set": {"language_code": language_code}})

def update_user_interface_language(user_id, interface_language):
    """Cập nhật ngôn ngữ giao tiếp cho người dùng"""
    users.update_one({"user_id": user_id}, {"$set": {"interface_language": interface_language}})

def get_channel(channel_id):
    """Lấy thông tin kênh từ database"""
    return channels.find_one({"channel_id": channel_id})

def register_channel(user_id, channel_id, channel_title=None):
    """Đăng ký kênh mới cho người dùng"""
    # Thêm kênh vào danh sách đã đăng ký của người dùng
    users.update_one(
        {"user_id": user_id},
        {"$addToSet": {"registered_channels": channel_id}}
    )
    
    # Thêm hoặc cập nhật thông tin kênh
    channel = {
        "channel_id": channel_id,
        "title": channel_title,
        "subscribers": [user_id]
    }
    channels.update_one(
        {"channel_id": channel_id},
        {"$set": {"channel_id": channel_id, "title": channel_title},
         "$addToSet": {"subscribers": user_id}},
        upsert=True
    )

def unregister_channel(user_id, channel_id):
    """Hủy đăng ký kênh cho người dùng"""
    # Xóa kênh khỏi danh sách đã đăng ký của người dùng
    users.update_one(
        {"user_id": user_id},
        {"$pull": {"registered_channels": channel_id}}
    )
    
    # Xóa người dùng khỏi danh sách subscribers của kênh
    channels.update_one(
        {"channel_id": channel_id},
        {"$pull": {"subscribers": user_id}}
    )
    
    # Nếu kênh không còn subscribers, xóa kênh
    channel = channels.find_one({"channel_id": channel_id})
    if channel and len(channel.get("subscribers", [])) == 0:
        channels.delete_one({"channel_id": channel_id})

def get_user_channels(user_id):
    """Lấy danh sách kênh đã đăng ký của người dùng"""
    user = get_user(user_id)
    if not user:
        return []
    
    channel_ids = user.get("registered_channels", [])
    return list(channels.find({"channel_id": {"$in": channel_ids}}))

def get_channel_subscribers(channel_id):
    """Lấy danh sách người dùng đã đăng ký kênh"""
    channel = get_channel(channel_id)
    if not channel:
        return []
    
    return channel.get("subscribers", []) 