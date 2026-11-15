"""Hệ mã khoá công khai RSA (Bài 4 - mục 4).

Sinh khoá:  chọn p, q nguyên tố (p != q);  n = p*q;  phi(n) = (p-1)(q-1);
            chọn e sao cho gcd(phi(n), e) = 1, 1 < e < phi(n);  d = e^-1 mod phi(n).
Mã hoá:     C = M^e mod n  (M < n)        Khoá công khai  PU = {e, n}
Giải mã:    M = C^d mod n                 Khoá bí mật     PR = {d, n}

Đây là RSA "sách giáo khoa" (không đệm OAEP) phục vụ mục đích học tập.
"""

import secrets
from dataclasses import dataclass

from . import CryptoError
from .playfair import strip_accents

# ----------------------------------------------------------------------------
# Số học
# ----------------------------------------------------------------------------

def gcd(a: int, b: int) -> int:
    """Thuật toán Euclid: gcd(a, b) = gcd(b, a mod b) cho tới khi b = 0."""
    while b:
        a, b = b, a % b
    return a


def mod_inverse(a: int, m: int) -> int:
    """Euclid mở rộng: tìm x sao cho a*x ≡ 1 (mod m)."""
    old_r, r = a % m, m
    old_s, s = 1, 0
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
    if old_r != 1:
        raise CryptoError(f"{a} không có nghịch đảo modulo {m} (hai số không nguyên tố cùng nhau).")
    return old_s % m


def mod_pow(base: int, exponent: int, modulus: int) -> int:
    """Luỹ thừa modulo bằng giải thuật bình phương và nhân."""
    if modulus == 1:
        return 0
    result = 1
    base %= modulus
    while exponent > 0:
        if exponent & 1:
            result = result * base % modulus
        base = base * base % modulus
        exponent >>= 1
    return result


_SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
                 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
                 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229]


def is_prime(n: int, rounds: int = 32) -> bool:
    """Kiểm tra nguyên tố Miller-Rabin (chính xác tuyệt đối với n < 3.3 * 10^24)."""
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    if n < 3_317_044_064_679_887_385_961_981:
        witnesses = _SMALL_PRIMES[:13]  # bộ cơ sở tất định
    else:
        witnesses = [secrets.randbelow(n - 3) + 2 for _ in range(rounds)]
    for a in witnesses:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def random_prime(bits: int) -> int:
    """Sinh số nguyên tố ngẫu nhiên có đúng `bits` bit."""
    if bits < 4:
        raise CryptoError("Số bit của số nguyên tố phải từ 4 trở lên.")
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(candidate):
            return candidate


# ----------------------------------------------------------------------------
# Khoá
# ----------------------------------------------------------------------------

@dataclass
class RSAKey:
    p: int
    q: int
    n: int
    phi: int
    e: int
    d: int


def choose_e(phi: int) -> int:
    """Chọn số mũ công khai: ưu tiên 65537, nếu không được thì lấy số lẻ nhỏ nhất phù hợp."""
    for e in (65537, 257, 17):
        if e < phi and gcd(e, phi) == 1:
            return e
    e = 3
    while e < phi:
        if gcd(e, phi) == 1:
            return e
        e += 2
    raise CryptoError("Không tìm được số mũ công khai e phù hợp, hãy chọn p, q lớn hơn.")


def make_key(p: int, q: int, e: int = None) -> RSAKey:
    """Tính khoá RSA từ p, q (và e nếu có) theo đúng các bước trong bài giảng."""
    if not is_prime(p):
        raise CryptoError(f"p = {p} không phải là số nguyên tố.")
    if not is_prime(q):
        raise CryptoError(f"q = {q} không phải là số nguyên tố.")
    if p == q:
        raise CryptoError("p và q phải khác nhau.")
    n = p * q
    phi = (p - 1) * (q - 1)
    if e is None:
        e = choose_e(phi)
    if not 1 < e < phi:
        raise CryptoError(f"e phải thoả 1 < e < φ(n) = {phi}.")
    if gcd(e, phi) != 1:
        raise CryptoError(f"gcd(e, φ(n)) = {gcd(e, phi)} ≠ 1 nên e = {e} không hợp lệ.")
    return RSAKey(p=p, q=q, n=n, phi=phi, e=e, d=mod_inverse(e, phi))


def generate_key(bits: int = 1024) -> RSAKey:
    """Sinh cặp khoá ngẫu nhiên với n dài đúng `bits` bit."""
    if bits < 16:
        raise CryptoError("Độ dài khoá tối thiểu là 16 bit.")
    while True:
        p = random_prime(bits // 2)
        q = random_prime(bits - bits // 2)
        if p == q or (p * q).bit_length() != bits:
            continue
        phi = (p - 1) * (q - 1)
        try:
            e = choose_e(phi)
        except CryptoError:
            continue
        return RSAKey(p=p, q=q, n=p * q, phi=phi, e=e, d=mod_inverse(e, phi))


# ----------------------------------------------------------------------------
# Mã hoá / giải mã văn bản
# ----------------------------------------------------------------------------

MODE_ASCII = "ascii"      # mỗi ký tự -> mã ASCII/Unicode của nó
MODE_ALPHA = "alpha"      # chữ cái viết hoa đánh số A=0 ... Z=25
MODE_NUMBER = "number"    # người dùng nhập trực tiếp các số nguyên M
MODE_BLOCK = "block"      # gom byte UTF-8 thành khối lớn (dùng cho khoá dài)

STEP_LIMIT = 300  # số dòng chi tiết tối đa


def _check_exponent(value: int, name: str, n: int):
    if n < 2:
        raise CryptoError("Môđun n phải lớn hơn 1.")
    if value < 1:
        raise CryptoError(f"Số mũ {name} phải là số nguyên dương.")


def _parse_numbers(text: str, base: int = 10) -> list:
    tokens = text.replace(",", " ").replace(";", " ").split()
    if not tokens:
        raise CryptoError("Chưa có dữ liệu đầu vào.")
    numbers = []
    for token in tokens:
        try:
            value = int(token, base)
        except ValueError:
            kind = "thập phân" if base == 10 else "hex"
            raise CryptoError(f"'{token}' không phải là số nguyên {kind} hợp lệ.") from None
        if value < 0:
            raise CryptoError("Các giá trị phải là số nguyên không âm.")
        numbers.append(value)
    return numbers


def _block_sizes(n: int):
    """(số byte dữ liệu mỗi khối, số byte của n). Mỗi khối = 0x01 + dữ liệu, luôn nhỏ hơn n."""
    capacity = (n.bit_length() - 1) // 8  # số byte tối đa chắc chắn nhỏ hơn n
    if capacity < 2:
        raise CryptoError(
            "Chế độ theo khối cần n tối thiểu 17 bit. Hãy dùng khoá lớn hơn "
            "hoặc chọn chế độ mã hoá từng ký tự."
        )
    return capacity - 1, (n.bit_length() + 7) // 8


def encrypt_text(text: str, e: int, n: int, mode: str = MODE_ASCII):
    """Trả về (bản mã dạng chuỗi, danh sách các bước)."""
    _check_exponent(e, "e", n)
    steps = []

    if mode == MODE_BLOCK:
        data = text.encode("utf-8")
        if not data:
            raise CryptoError("Chưa có dữ liệu đầu vào.")
        chunk, width = _block_sizes(n)
        blocks = []
        for i in range(0, len(data), chunk):
            piece = data[i:i + chunk]
            m = int.from_bytes(b"\x01" + piece, "big")
            c = mod_pow(m, e, n)
            blocks.append(f"{c:0{width * 2}X}")
            if len(steps) < STEP_LIMIT:
                steps.append(f"Khối {len(blocks)}: M = 0x{m:X}\n    C = M^e mod n = 0x{c:X}")
        return " ".join(blocks), steps

    if mode == MODE_NUMBER:
        units = [(str(m), m) for m in _parse_numbers(text)]
    elif mode == MODE_ALPHA:
        letters = [ch for ch in strip_accents(text).upper() if "A" <= ch <= "Z"]
        units = [(ch, ord(ch) - 65) for ch in letters]
    else:
        units = [(repr(ch), ord(ch)) for ch in text]
    if not units:
        raise CryptoError("Chưa có dữ liệu hợp lệ để mã hoá.")

    cipher = []
    for label, m in units:
        if m >= n:
            raise CryptoError(
                f"Giá trị M = {m} ({label}) không nhỏ hơn n = {n}. "
                "RSA yêu cầu M < n, hãy chọn p, q lớn hơn."
            )
        c = mod_pow(m, e, n)
        cipher.append(str(c))
        if len(steps) < STEP_LIMIT:
            steps.append(f"{label:>6} → M = {m}:  C = {m}^{e} mod {n} = {c}")
    return " ".join(cipher), steps


def decrypt_text(text: str, d: int, n: int, mode: str = MODE_ASCII):
    """Trả về (bản rõ, danh sách các bước)."""
    _check_exponent(d, "d", n)
    steps = []

    if mode == MODE_BLOCK:
        chunk, _ = _block_sizes(n)
        data = bytearray()
        for index, c in enumerate(_parse_numbers(text, 16), 1):
            if c >= n:
                raise CryptoError(f"Khối {index} có giá trị không nhỏ hơn n, bản mã không khớp khoá.")
            m = mod_pow(c, d, n)
            raw = m.to_bytes((m.bit_length() + 7) // 8, "big")
            if not raw or raw[0] != 1 or len(raw) > chunk + 1:
                raise CryptoError("Giải mã thất bại: sai khoá bí mật hoặc bản mã đã bị thay đổi.")
            data += raw[1:]
            if len(steps) < STEP_LIMIT:
                steps.append(f"Khối {index}: C = 0x{c:X}\n    M = C^d mod n = 0x{m:X}")
        try:
            return data.decode("utf-8"), steps
        except UnicodeDecodeError:
            raise CryptoError("Giải mã thất bại: sai khoá bí mật hoặc bản mã đã bị thay đổi.") from None

    out = []
    for c in _parse_numbers(text):
        if c >= n:
            raise CryptoError(f"Giá trị C = {c} không nhỏ hơn n = {n}, bản mã không khớp khoá.")
        m = mod_pow(c, d, n)
        if mode == MODE_NUMBER:
            piece = str(m)
        elif mode == MODE_ALPHA:
            if m > 25:
                raise CryptoError(f"Giải mã ra M = {m} không ứng với chữ cái nào (A=0 … Z=25).")
            piece = chr(m + 65)
        else:
            if m > 0x10FFFF or 0xD800 <= m <= 0xDFFF:
                raise CryptoError(f"Giải mã ra M = {m} không phải mã ký tự hợp lệ (sai khoá?).")
            piece = chr(m)
        out.append(piece)
        if len(steps) < STEP_LIMIT:
            shown = piece if mode == MODE_NUMBER else repr(piece)
            steps.append(f"C = {c}:  M = {c}^{d} mod {n} = {m} → {shown}")
    return (" " if mode == MODE_NUMBER else "").join(out), steps
