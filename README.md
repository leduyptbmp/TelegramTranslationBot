# Bot Dịch Thuật Telegram

Bot Telegram tự động dịch tin nhắn từ các kênh và bot khác.

## Tính năng

- Dịch tin nhắn từ các kênh/bot đã đăng ký sang ngôn ngữ đã cài đặt
- Tự động dịch tin nhắn mới từ các kênh/bot đã đăng ký
- Forward tin nhắn từ kênh/bot khác để dịch
- Đăng ký kênh/bot mới thông qua giao diện người dùng

## Yêu cầu hệ thống

- Python 3.7 trở lên
- pip (trình quản lý gói của Python)
- MongoDB (cơ sở dữ liệu)
- Token bot Telegram (lấy từ BotFather)

## Cách chạy nhanh

### Trên Linux/macOS

1. Cấp quyền thực thi cho script:
   ```
   chmod +x run.sh
   ```

2. Chạy script:
   ```
   ./run.sh
   ```

### Trên Windows

1. Nhấp đúp vào file `run.bat` hoặc chạy từ Command Prompt:
   ```
   run.bat
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

1. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

2. Tạo file `.env` từ file `.env.example` và cập nhật thông tin:
   ```
   cp .env.example .env
   ```

3. Chạy bot:
   ```
   python run.py
   ```

## Sử dụng

1. Bắt đầu chat với bot bằng lệnh `/start`
2. Cài đặt ngôn ngữ dịch bằng lệnh `/setlang`
3. Đăng ký kênh/bot bằng cách forward tin nhắn từ kênh đó hoặc sử dụng lệnh `/register`
4. Forward tin nhắn từ bất kỳ kênh nào để dịch

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

## Tài liệu tham khảo

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [googletrans](https://github.com/ssut/py-googletrans)
- [MongoDB Python Driver](https://pymongo.readthedocs.io/)

## Đóng góp

Nếu bạn muốn đóng góp vào dự án, vui lòng tạo pull request hoặc báo cáo lỗi qua mục Issues. 