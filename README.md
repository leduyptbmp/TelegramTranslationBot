# Bot Dịch Tin Nhắn Telegram

Bot Telegram giúp dịch tin nhắn được chuyển tiếp từ các kênh sang ngôn ngữ mà người dùng chọn và gửi trực tiếp đến chat riêng.

## Chức năng chính

### 1. Dịch tin nhắn
- Tự động dịch tin nhắn từ kênh sang ngôn ngữ đã chọn
- Hỗ trợ dịch:
  - Tin nhắn văn bản
  - Chú thích của hình ảnh (caption)
  - Chú thích của video (caption)

### 2. Cài đặt ngôn ngữ
- `/setlang` - Cài đặt ngôn ngữ dịch (ngôn ngữ đích)
- `/setinterfacelang` - Cài đặt ngôn ngữ giao diện (en/vi)

### 3. Quản lý kênh
- `/channels` - Xem danh sách kênh đã đăng ký
- `/unregister` - Hủy đăng ký kênh

### 4. Các lệnh cơ bản
- `/start` - Bắt đầu sử dụng bot
- `/help` - Xem hướng dẫn sử dụng
- `/cancel` - Hủy thao tác hiện tại

## TODO: Đăng ký kênh mới
- [ ] Thêm hướng dẫn chi tiết cách đăng ký kênh
- [ ] Liệt kê các phương thức đăng ký kênh được hỗ trợ
- [ ] Mô tả quy trình xác thực và phân quyền
- [ ] Thêm ví dụ cụ thể cho từng cách đăng ký

## Cách hoạt động

1. Khi có tin nhắn mới từ kênh: (đang phát triển)
   - Bot sẽ nhận tin nhắn
   - Tìm danh sách người dùng đã đăng ký kênh
   - Nhóm người dùng theo ngôn ngữ đích
   - Dịch tin nhắn một lần cho mỗi ngôn ngữ
   - Gửi tin nhắn đã dịch đến chat riêng của từng người dùng

2. Định dạng tin nhắn dịch:
   ```
   📢 Tin nhắn mới từ [Tên kênh]
   
   Nội dung gốc:
   [Tin nhắn gốc]
   
   Bản dịch:
   [Nội dung đã dịch]
   ```

## Cài đặt

1. Yêu cầu:
   - Python 3.7+
   - Telegram Bot Token
   - Các thư viện trong `requirements.txt`

2. Cài đặt:
   ```bash
   # Clone repository
   git clone [URL_repository]
   
   # Cài đặt dependencies
   pip install -r requirements.txt
   
   # Tạo file .env và thêm token
   echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env
   
   # Chạy bot
   python run.py
   ```

## Cấu trúc thư mục

```
├── src/
│   ├── handlers/
│   │   ├── command_handlers.py
│   │   ├── message_handlers.py
│   │   └── callback_handlers.py
│   ├── config.py
│   └── main.py
├── logs/
│   └── bot.log
├── .env
├── requirements.txt
└── README.md
```

## Ghi chú

- Bot sử dụng logging để ghi lại các hoạt động
- Log được lưu trong thư mục `logs/`
- Cấp độ log mặc định: INFO

## Tính năng

- Dịch tin nhắn từ các kênh/bot đã đăng ký sang ngôn ngữ đã cài đặt (đang phát triển)
- Tự động dịch tin nhắn mới từ các kênh/bot đã đăng ký (đang phát triển)
- Forward tin nhắn từ kênh/bot khác để dịch
- Đăng ký kênh/bot mới thông qua giao diện người dùng
- Trích xuất và dịch văn bản từ hình ảnh (OCR)

## Yêu cầu hệ thống

- Python 3.7 trở lên
- pip (trình quản lý gói của Python)
- MongoDB (cơ sở dữ liệu)
- Token bot Telegram (lấy từ BotFather)
- Tesseract OCR (để trích xuất văn bản từ hình ảnh)

## Cách chạy nhanh

### Trên Linux/macOS

1. Tạo và kích hoạt môi trường ảo:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

3. Cài đặt Tesseract OCR:
   ```
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install tesseract-ocr tesseract-ocr-vie
   
   # macOS
   brew install tesseract tesseract-lang
   ```

4. Cấp quyền thực thi cho script:
   ```
   chmod +x run.sh
   ```

5. Chạy script:
   ```
   ./run.sh
   ```

### Trên Windows

1. Tạo và kích hoạt môi trường ảo:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

3. Cài đặt Tesseract OCR:
   - Tải Tesseract OCR từ https://github.com/UB-Mannheim/tesseract/wiki
   - Cài đặt và thêm đường dẫn vào biến môi trường PATH
   - Tải thêm dữ liệu ngôn ngữ tiếng Việt nếu cần

4. Chạy script:
   ```
   run.bat
   ```

## Cài đặt như một Service

Bot có thể được cài đặt như một service để chạy tự động khi khởi động hệ thống và tự động khởi động lại khi gặp lỗi.

### Trên Linux (systemd)

1. Cấp quyền thực thi cho script cài đặt service:
   ```
   chmod +x install_service.sh
   ```

2. Chạy script cài đặt service với quyền root:
   ```
   sudo ./install_service.sh
   ```

3. Quản lý service:
   ```
   sudo systemctl start telegram-translation-bot    # Khởi động service
   sudo systemctl stop telegram-translation-bot     # Dừng service
   sudo systemctl restart telegram-translation-bot  # Khởi động lại service
   sudo systemctl status telegram-translation-bot   # Xem trạng thái service
   sudo journalctl -u telegram-translation-bot -f   # Xem log của service
   ```

### Trên Windows (NSSM)

1. Chạy Command Prompt hoặc PowerShell với quyền Administrator
2. Di chuyển đến thư mục dự án:
   ```
   cd đường_dẫn_đến_thư_mục_dự_án
   ```
3. Chạy script cài đặt service:
   ```
   install_service.bat
   ```
   Script sẽ tự động tải và cài đặt NSSM (Non-Sucking Service Manager) nếu chưa được cài đặt.

4. Quản lý service:
   ```
   nssm start TelegramTranslationBot    # Khởi động service
   nssm stop TelegramTranslationBot     # Dừng service
   nssm restart TelegramTranslationBot  # Khởi động lại service
   nssm status TelegramTranslationBot   # Xem trạng thái service
   nssm edit TelegramTranslationBot     # Chỉnh sửa cấu hình service
   nssm remove TelegramTranslationBot   # Xóa service
   ```

## Cài đặt

### Cài đặt tự động

#### Trên Linux/macOS

1. Mở Terminal
2. Di chuyển đến thư mục dự án:
   ```
   cd đường_dẫn_đến_thư_mục_dự_án
   ```
3. Cấp quyền thực thi cho script cài đặt:
   ```
   chmod +x install.sh
   ```
4. Chạy script cài đặt:
   ```
   ./install.sh
   ```
5. Cập nhật thông tin trong file `.env`:
   ```
   nano .env
   ```
   Thay đổi `TELEGRAM_BOT_TOKEN` và `MONGODB_URI` thành giá trị thực tế của bạn.

#### Trên Windows

1. Mở Command Prompt hoặc PowerShell
2. Di chuyển đến thư mục dự án:
   ```
   cd đường_dẫn_đến_thư_mục_dự_án
   ```
3. Chạy script cài đặt:
   ```
   install.bat
   ```
4. Mở file `.env` bằng Notepad hoặc trình soạn thảo văn bản khác và cập nhật thông tin:
   - Thay đổi `TELEGRAM_BOT_TOKEN` thành token bot Telegram của bạn
   - Thay đổi `MONGODB_URI` thành URI kết nối MongoDB của bạn

### Cài đặt thủ công

1. Tạo và kích hoạt môi trường ảo:
   ```
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

2. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

3. Cài đặt Tesseract OCR:
   - **Ubuntu/Debian**:
     ```
     sudo apt-get update
     sudo apt-get install tesseract-ocr tesseract-ocr-vie
     ```
   - **Windows**: Tải từ https://github.com/UB-Mannheim/tesseract/wiki
   - **macOS**: `brew install tesseract tesseract-lang`

4. Tạo file `.env` từ file `.env.example` và cập nhật thông tin:
   ```
   cp .env.example .env
   ```

5. Chạy bot:
   ```
   python run.py
   ```

## Sử dụng

1. Bắt đầu chat với bot bằng lệnh `/start`
2. Cài đặt ngôn ngữ dịch bằng lệnh `/setlang`
3. Đăng ký kênh/bot bằng cách forward tin nhắn từ kênh đó hoặc sử dụng lệnh `/register`
4. Forward tin nhắn từ bất kỳ kênh nào để dịch
5. Gửi hình ảnh có chứa văn bản để bot trích xuất và dịch

## Lấy token bot Telegram

1. Mở Telegram và tìm kiếm `@BotFather`
2. Gửi lệnh `/newbot` và làm theo hướng dẫn
3. Sau khi tạo bot, BotFather sẽ cung cấp cho bạn một token
4. Sao chép token này và đặt vào file `.env`

## Cấu hình MongoDB

### Sử dụng MongoDB cục bộ

Nếu bạn đã cài đặt MongoDB trên máy tính của mình, bạn có thể sử dụng URI mặc định:

```
MONGODB_URI=mongodb://localhost:27017/translation_bot
```

### Sử dụng MongoDB Atlas (dịch vụ đám mây)

1. Đăng ký tài khoản tại [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Tạo một cluster mới
3. Tạo người dùng cơ sở dữ liệu
4. Lấy URI kết nối và đặt vào file `.env`

## Các lệnh bot

- `/start` - Khởi động bot
- `/help` - Hiển thị hướng dẫn sử dụng
- `/setlang` - Cài đặt ngôn ngữ dịch
- `/register` - Đăng ký kênh/bot mới
- `/channels` - Xem danh sách kênh đã đăng ký
- `/unregister` - Hủy đăng ký kênh

## Khắc phục sự cố

### Không thể kết nối đến MongoDB

- Kiểm tra xem MongoDB đã được cài đặt và đang chạy
- Kiểm tra URI kết nối trong file `.env`
- Kiểm tra tường lửa và quyền truy cập

### Bot không phản hồi

- Kiểm tra token bot trong file `.env`
- Kiểm tra xem bot có đang chạy không
- Kiểm tra logs để xem lỗi

### Lỗi khi cài đặt các thư viện

- Cập nhật pip: `pip install --upgrade pip`
- Cài đặt các gói phụ thuộc hệ thống (nếu cần)
- Thử cài đặt từng thư viện một

### Lỗi "No module named 'PIL'"

- Đảm bảo bạn đã kích hoạt môi trường ảo: `source venv/bin/activate` (Linux/macOS) hoặc `venv\Scripts\activate` (Windows)
- Cài đặt lại thư viện Pillow: `pip install Pillow==10.1.0`

### Lỗi khi sử dụng OCR

- Đảm bảo Tesseract OCR đã được cài đặt
- Kiểm tra đường dẫn đến Tesseract OCR
- Cài đặt dữ liệu ngôn ngữ cần thiết

## Tài liệu tham khảo

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [deep-translator](https://github.com/nidhaloff/deep-translator)
- [pytesseract](https://github.com/madmaze/pytesseract)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)

## Đóng góp

Nếu bạn muốn đóng góp vào dự án, vui lòng tạo pull request hoặc báo cáo lỗi qua mục Issues. 