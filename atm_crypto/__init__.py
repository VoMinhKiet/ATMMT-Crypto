"""Các giải thuật mã hoá của đồ án An toàn mạng máy tính (phần A).

- playfair : mã cổ điển PlayFair (ma trận 5x5 và 6x6)
- rsa      : hệ mã khoá công khai RSA
- des, aes : mã khối đối xứng DES và AES (cài đặt thuần Python)
- modes    : chế độ ECB / CBC và đệm PKCS#7 dùng chung cho DES, AES
"""


class CryptoError(ValueError):
    """Lỗi do dữ liệu/khoá người dùng nhập không hợp lệ (thông báo bằng tiếng Việt)."""
