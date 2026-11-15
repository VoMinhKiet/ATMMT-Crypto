# Nhom17-Crypto

Ứng dụng desktop minh hoạ các giải thuật mã hoá – đồ án môn **An toàn mạng máy tính** của nhóm 17.
Toàn bộ giải thuật được cài đặt thuần Python, không dùng thư viện mã hoá có sẵn.

| Tab | Giải thuật |
|---|---|
| **PlayFair** | Mã cổ điển PlayFair, ma trận 5×5 (I/J chung ô) hoặc 6×6 (A–Z và 0–9) |
| **RSA** | Sinh khoá (số nguyên tố ngẫu nhiên hoặc tự nhập p, q, e), mã hoá / giải mã |
| **DES & AES** | Mã khối đối xứng DES (khoá 64 bit) và AES (khoá 128 / 192 / 256 bit), chế độ ECB / CBC, đệm PKCS#7 |

## Yêu cầu

- Windows 10/11
- [Python](https://www.python.org/downloads/) 3.10 trở lên (khi cài nhớ tick **Add Python to PATH**)

## Chạy từ mã nguồn

```powershell
git clone https://github.com/VoMinhKiet/ATMMT-Crypto
cd ATMMT-Crypto
pip install customtkinter
python main.py
```

## Đóng gói thành file .exe

```powershell
pip install customtkinter pyinstaller
.\build.bat
```

Sau khi chạy xong, file `Nhom17-Crypto.exe` nằm ngay trong thư mục project. File này chạy độc lập, máy khác không cần cài Python.

## Chạy kiểm thử

Các bài kiểm thử dùng ví dụ trong slide bài giảng và vector chuẩn FIPS / NIST:

```powershell
python -m unittest discover -s tests -v
```

Nếu máy có cài `pycryptodome` (`pip install pycryptodome`), DES/AES còn được đối chiếu thêm với thư viện này.

## Cấu trúc thư mục

```
├── main.py            # Điểm khởi chạy ứng dụng
├── build.bat          # Script đóng gói .exe bằng PyInstaller
├── atm_crypto/        # Cài đặt các giải thuật
│   ├── playfair.py
│   ├── rsa.py
│   ├── des.py
│   ├── aes.py
│   └── modes.py       # ECB / CBC và đệm PKCS#7 dùng chung cho DES, AES
├── gui/               # Giao diện (customtkinter)
├── tests/             # Kiểm thử
├── assets/            # Icon ứng dụng
└── tools/make_icon.py # Vẽ lại icon (cần Pillow: pip install pillow)
```
