#!/bin/bash

# Màu sắc cho output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Cài đặt Bot Dịch Thuật Telegram như một Service ===${NC}"

# Kiểm tra quyền root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Vui lòng chạy script này với quyền root (sudo).${NC}"
    exit 1
fi

# Lấy đường dẫn tuyệt đối của thư mục hiện tại
CURRENT_DIR=$(pwd)
USER=$(logname)

# Kiểm tra môi trường ảo
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Môi trường ảo chưa được tạo. Đang tạo môi trường ảo...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Không thể tạo môi trường ảo. Vui lòng cài đặt venv: pip3 install virtualenv${NC}"
        exit 1
    fi
    echo -e "${GREEN}Đã tạo môi trường ảo.${NC}"
    
    # Kích hoạt môi trường ảo và cài đặt các thư viện
    source venv/bin/activate
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Không thể cài đặt các thư viện cần thiết.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Đã cài đặt các thư viện cần thiết.${NC}"
fi

# Kiểm tra file .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}File .env chưa được tạo. Đang tạo từ .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Vui lòng cập nhật thông tin trong file .env trước khi tiếp tục.${NC}"
        echo -e "${YELLOW}Nhấn Enter sau khi đã cập nhật file .env...${NC}"
        read
    else
        echo -e "${RED}Không tìm thấy file .env.example. Vui lòng tạo file .env thủ công.${NC}"
        exit 1
    fi
fi

# Tạo file service
echo -e "${YELLOW}Tạo file service...${NC}"
cat > /tmp/telegram-translation-bot.service << EOL
[Unit]
Description=Telegram Translation Bot Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/run.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-translation-bot
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOL

# Cài đặt service
echo -e "${YELLOW}Cài đặt service...${NC}"
cp /tmp/telegram-translation-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable telegram-translation-bot.service
systemctl start telegram-translation-bot.service

# Kiểm tra trạng thái service
echo -e "${YELLOW}Kiểm tra trạng thái service...${NC}"
systemctl status telegram-translation-bot.service

echo -e "${GREEN}=== Cài đặt hoàn tất ===${NC}"
echo -e "${YELLOW}Bạn có thể quản lý service bằng các lệnh sau:${NC}"
echo -e "  ${GREEN}sudo systemctl start telegram-translation-bot${NC} - Khởi động service"
echo -e "  ${GREEN}sudo systemctl stop telegram-translation-bot${NC} - Dừng service"
echo -e "  ${GREEN}sudo systemctl restart telegram-translation-bot${NC} - Khởi động lại service"
echo -e "  ${GREEN}sudo systemctl status telegram-translation-bot${NC} - Xem trạng thái service"
echo -e "  ${GREEN}sudo journalctl -u telegram-translation-bot -f${NC} - Xem log của service" 