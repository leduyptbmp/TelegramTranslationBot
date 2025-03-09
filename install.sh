#!/bin/bash

# Màu sắc cho output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Cài đặt Bot Dịch Thuật Telegram ===${NC}"

# Kiểm tra Python
echo -e "${YELLOW}Kiểm tra cài đặt Python...${NC}"
if command -v python3 &>/dev/null; then
    python_version=$(python3 --version)
    echo -e "${GREEN}Đã tìm thấy $python_version${NC}"
else
    echo -e "${RED}Không tìm thấy Python 3. Vui lòng cài đặt Python 3 trước khi tiếp tục.${NC}"
    exit 1
fi

# Kiểm tra pip
echo -e "${YELLOW}Kiểm tra cài đặt pip...${NC}"
if command -v pip3 &>/dev/null; then
    pip_version=$(pip3 --version)
    echo -e "${GREEN}Đã tìm thấy pip: $pip_version${NC}"
else
    echo -e "${RED}Không tìm thấy pip. Vui lòng cài đặt pip trước khi tiếp tục.${NC}"
    exit 1
fi

# Kiểm tra và tạo môi trường ảo
echo -e "${YELLOW}Kiểm tra và tạo môi trường ảo...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Tạo môi trường ảo mới...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Không thể tạo môi trường ảo. Vui lòng cài đặt venv: pip3 install virtualenv${NC}"
        exit 1
    fi
    echo -e "${GREEN}Đã tạo môi trường ảo.${NC}"
else
    echo -e "${GREEN}Môi trường ảo đã tồn tại.${NC}"
fi

# Kích hoạt môi trường ảo
echo -e "${YELLOW}Kích hoạt môi trường ảo...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Không thể kích hoạt môi trường ảo.${NC}"
    exit 1
fi
echo -e "${GREEN}Đã kích hoạt môi trường ảo.${NC}"

# Cài đặt các thư viện
echo -e "${YELLOW}Cài đặt các thư viện cần thiết...${NC}"
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Không thể cài đặt các thư viện cần thiết.${NC}"
    exit 1
fi
echo -e "${GREEN}Đã cài đặt các thư viện cần thiết.${NC}"

# Kiểm tra Tesseract OCR
echo -e "${YELLOW}Kiểm tra cài đặt Tesseract OCR...${NC}"
if command -v tesseract &>/dev/null; then
    tesseract_version=$(tesseract --version | head -n 1)
    echo -e "${GREEN}Đã tìm thấy Tesseract OCR: $tesseract_version${NC}"
else
    echo -e "${YELLOW}Tesseract OCR chưa được cài đặt. Bạn có muốn cài đặt Tesseract OCR không? (y/n)${NC}"
    read -r install_tesseract
    if [[ "$install_tesseract" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Cài đặt Tesseract OCR...${NC}"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew &>/dev/null; then
                brew install tesseract tesseract-lang
            else
                echo -e "${RED}Homebrew không được cài đặt. Vui lòng cài đặt Homebrew trước khi tiếp tục.${NC}"
                echo -e "${YELLOW}Bạn có thể cài đặt Homebrew bằng lệnh:${NC}"
                echo -e "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                echo -e "${YELLOW}Sau đó chạy lại script này.${NC}"
            fi
        else
            # Linux
            sudo apt-get update
            sudo apt-get install -y tesseract-ocr tesseract-ocr-vie
        fi
        
        if command -v tesseract &>/dev/null; then
            tesseract_version=$(tesseract --version | head -n 1)
            echo -e "${GREEN}Đã cài đặt Tesseract OCR: $tesseract_version${NC}"
        else
            echo -e "${RED}Không thể cài đặt Tesseract OCR tự động. Vui lòng cài đặt thủ công:${NC}"
            echo -e "${YELLOW}Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-vie${NC}"
            echo -e "${YELLOW}macOS: brew install tesseract tesseract-lang${NC}"
        fi
    else
        echo -e "${YELLOW}Bỏ qua cài đặt Tesseract OCR. Tính năng OCR sẽ không hoạt động.${NC}"
    fi
fi

# Kiểm tra file .env
echo -e "${YELLOW}Kiểm tra file .env...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Tạo file .env từ .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Đã tạo file .env. Vui lòng cập nhật thông tin trong file .env trước khi chạy bot.${NC}"
else
    echo -e "${GREEN}File .env đã tồn tại.${NC}"
fi

echo -e "${GREEN}=== Cài đặt hoàn tất ===${NC}"
echo -e "${YELLOW}Để chạy bot, hãy thực hiện các bước sau:${NC}"
echo -e "1. Cập nhật thông tin trong file .env"
echo -e "2. Kích hoạt môi trường ảo: ${GREEN}source venv/bin/activate${NC}"
echo -e "3. Chạy bot: ${GREEN}python run.py${NC}" 