"""Chế độ hoạt động của mã khối (ECB, CBC) và đệm PKCS#7, dùng chung cho DES và AES."""

import base64
import binascii
import secrets

from . import CryptoError
from .aes import AES
from .des import DES

ALGORITHMS = {
    "DES": (DES, 8),
    "AES-128": (AES, 16),
    "AES-192": (AES, 24),
    "AES-256": (AES, 32),
}
MODES = ("ECB", "CBC")
BLOCK_SIZES = {"DES": 8, "AES-128": 16, "AES-192": 16, "AES-256": 16}


def key_length(algorithm: str) -> int:
    return ALGORITHMS[algorithm][1]


def block_length(algorithm: str) -> int:
    return BLOCK_SIZES[algorithm]


def make_cipher(algorithm: str, key: bytes):
    if algorithm not in ALGORITHMS:
        raise CryptoError(f"Không hỗ trợ thuật toán '{algorithm}'.")
    cls, size = ALGORITHMS[algorithm]
    if len(key) != size:
        raise CryptoError(
            f"Khoá {algorithm} phải dài đúng {size} byte ({size * 8} bit), "
            f"khoá đang nhập dài {len(key)} byte."
        )
    return cls(key)


def random_bytes(count: int) -> bytes:
    return secrets.token_bytes(count)


def pad(data: bytes, block_size: int) -> bytes:
    """PKCS#7: thêm n byte, mỗi byte mang giá trị n (1 <= n <= block_size)."""
    n = block_size - len(data) % block_size
    return data + bytes([n]) * n


def unpad(data: bytes, block_size: int) -> bytes:
    if not data or len(data) % block_size:
        raise CryptoError("Dữ liệu sau giải mã có độ dài không hợp lệ.")
    n = data[-1]
    if not 1 <= n <= block_size or data[-n:] != bytes([n]) * n:
        raise CryptoError("Giải mã thất bại: sai khoá/IV hoặc bản mã đã bị thay đổi.")
    return data[:-n]


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _check_iv(mode: str, iv, block_size: int):
    if mode not in MODES:
        raise CryptoError(f"Không hỗ trợ chế độ '{mode}'.")
    if mode == "CBC" and (iv is None or len(iv) != block_size):
        got = 0 if iv is None else len(iv)
        raise CryptoError(
            f"Chế độ CBC cần IV dài đúng {block_size} byte ({block_size * 2} ký tự hex), "
            f"IV đang nhập dài {got} byte."
        )


def encrypt(cipher, data: bytes, mode: str = "CBC", iv: bytes = None, trace: list = None) -> bytes:
    """Mã hoá `data` (đệm PKCS#7). Nếu có `trace`, ghi lại chi tiết các vòng của khối đầu tiên."""
    size = cipher.block_size
    _check_iv(mode, iv, size)
    data = pad(data, size)
    out = bytearray()
    previous = iv
    for i in range(0, len(data), size):
        block = data[i:i + size]
        if mode == "CBC":
            block = _xor(block, previous)
        previous = cipher.encrypt_block(block, trace if i == 0 else None)
        out += previous
    return bytes(out)


def decrypt(cipher, data: bytes, mode: str = "CBC", iv: bytes = None, trace: list = None) -> bytes:
    size = cipher.block_size
    _check_iv(mode, iv, size)
    if not data or len(data) % size:
        raise CryptoError(
            f"Độ dài bản mã ({len(data)} byte) phải là bội số của {size} byte."
        )
    out = bytearray()
    previous = iv
    for i in range(0, len(data), size):
        block = data[i:i + size]
        plain = cipher.decrypt_block(block, trace if i == 0 else None)
        if mode == "CBC":
            plain = _xor(plain, previous)
            previous = block
        out += plain
    return unpad(bytes(out), size)


# ----------------------------------------------------------------------------
# Chuyển đổi định dạng
# ----------------------------------------------------------------------------

def parse_hex(text: str, what: str = "Dữ liệu") -> bytes:
    cleaned = "".join(text.split())
    if cleaned.lower().startswith("0x"):
        cleaned = cleaned[2:]
    try:
        return bytes.fromhex(cleaned)
    except ValueError:
        raise CryptoError(f"{what} không phải chuỗi hex hợp lệ (chỉ gồm 0-9, A-F, số ký tự chẵn).") from None


def parse_base64(text: str, what: str = "Dữ liệu") -> bytes:
    try:
        return base64.b64decode("".join(text.split()), validate=True)
    except (binascii.Error, ValueError):
        raise CryptoError(f"{what} không phải chuỗi Base64 hợp lệ.") from None


def to_hex(data: bytes) -> str:
    return data.hex().upper()


def to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")
