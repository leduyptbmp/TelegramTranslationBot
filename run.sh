#!/bin/bash

# Màu sắc cho output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Khởi động Bot Dịch Thuật Telegram ===${NC}"

# Kiểm tra môi trường ảo
if [ -d "venv" ]; then
    echo -e "${YELLOW}Kích hoạt môi trường ảo...${NC}"
    source venv/bin/activate
    if [ $? -ne 0 ]; then
        echo -e "${RED}Không thể kích hoạt môi trường ảo. Tiếp tục với Python hệ thống.${NC}"
    else
        echo -e "${GREEN}Đã kích hoạt môi trường ảo.${NC}"
    fi
else
    echo -e "${YELLOW}Không tìm thấy môi trường ảo. Sử dụng Python hệ thống.${NC}"
fi

# Kiểm tra file .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Không tìm thấy file .env. Tạo từ .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}Đã tạo file .env. Vui lòng cập nhật thông tin trong file .env trước khi chạy bot.${NC}"
        echo -e "${RED}Bạn cần cập nhật TELEGRAM_BOT_TOKEN trong file .env trước khi tiếp tục.${NC}"
        exit 1
    else
        echo -e "${RED}Không tìm thấy file .env.example. Vui lòng tạo file .env thủ công.${NC}"
        exit 1
    fi
fi

# Chạy bot
echo -e "${GREEN}Đang chạy bot...${NC}"
python3 run.py

# Kiểm tra kết quả
if [ $? -ne 0 ]; then
    echo -e "${RED}Bot đã dừng với lỗi.${NC}"
    exit 1
fi 