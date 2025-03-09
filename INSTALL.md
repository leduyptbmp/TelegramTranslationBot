# Hướng dẫn cài đặt Bot Dịch Thuật Telegram

## Yêu cầu hệ thống

- Python 3.7 trở lên
- pip (trình quản lý gói của Python)
- MongoDB (cơ sở dữ liệu)
- Token bot Telegram (lấy từ BotFather)

## Cài đặt tự động

### Trên Linux/macOS

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

### Trên Windows

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

## Cài đặt thủ công

### 1. Cài đặt Python và pip

- **Linux/macOS**:
  ```
  sudo apt-get update
  sudo apt-get install python3 python3-pip
  ```

- **Windows**: Tải và cài đặt Python từ [python.org](https://www.python.org/downloads/)

### 2. Cài đặt MongoDB

- **Linux/macOS**:
  ```
  sudo apt-get install mongodb
  sudo systemctl start mongodb
  ```

- **Windows**: Tải và cài đặt MongoDB từ [mongodb.com](https://www.mongodb.com/try/download/community)

### 3. Tạo môi trường ảo

- **Linux/macOS**:
  ```
  python3 -m venv venv
  source venv/bin/activate
  ```

- **Windows**:
  ```
  python -m venv venv
  venv\Scripts\activate
  ```

### 4. Cài đặt các thư viện cần thiết

```
pip install -r requirements.txt
```

### 5. Cấu hình bot

Tạo file `.env` từ file `.env.example` và cập nhật thông tin:

- **Linux/macOS**:
  ```
  cp .env.example .env
  nano .env
  ```

- **Windows**:
  ```
  copy .env.example .env
  notepad .env
  ```

## Chạy bot

### Sử dụng môi trường ảo

1. Kích hoạt môi trường ảo:
   - **Linux/macOS**: `source venv/bin/activate`
   - **Windows**: `venv\Scripts\activate`

2. Chạy bot:
   ```
   python run.py
   ```

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

./run.sh  # Trên Linux/macOS 

run.bat  # Trên Windows 