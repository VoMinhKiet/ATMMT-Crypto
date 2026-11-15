"""Mã PlayFair (Bài 3 - mục 3.7).

Quy tắc theo bài giảng:
- Ma trận khoá n x n (n = 5 hoặc 6): lần lượt thêm các ký tự của khoá (không trùng),
  sau đó thêm các ký tự còn lại theo thứ tự A - Z. Với n = 5, I và J xem như một ký tự.
- Mã hoá từng cặp 2 ký tự; nếu dư 1 ký tự thì thêm "X" vào cuối.
- Cùng dòng  -> lấy ký tự bên phải (cột cuối vòng về cột đầu).
- Cùng cột   -> lấy ký tự bên dưới (hàng cuối vòng về hàng đầu).
- Hình chữ nhật -> lấy ký tự cùng dòng ở hai góc còn lại.
"""

import unicodedata
from dataclasses import dataclass, field

from . import CryptoError

FILLER = "X"
FILLER_ALT = "Q"  # dùng khi chính ký tự cần chèn là X

RULE_ROW = "cùng dòng"
RULE_COL = "cùng cột"
RULE_RECT = "hình chữ nhật"


@dataclass
class PlayfairResult:
    matrix: list
    prepared: list  # các cặp trước khi biến đổi
    steps: list = field(default_factory=list)  # (cặp vào, cặp ra, quy tắc)
    output: str = ""


def strip_accents(text: str) -> str:
    """Bỏ dấu tiếng Việt: 'Nguyễn Đức' -> 'Nguyen Duc'."""
    text = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def alphabet(size: int) -> str:
    if size == 5:
        return "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # không có J (I/J chung một ô)
    if size == 6:
        return "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    raise CryptoError("Kích thước ma trận PlayFair phải là 5 hoặc 6.")


def normalize(text: str, size: int) -> str:
    """Chỉ giữ các ký tự thuộc bảng chữ cái của ma trận, viết hoa, bỏ dấu."""
    allowed = alphabet(size)
    out = []
    for ch in strip_accents(text).upper():
        if size == 5 and ch == "J":
            ch = "I"
        if ch in allowed:
            out.append(ch)
    return "".join(out)


def build_matrix(key: str, size: int = 5) -> list:
    seen = []
    for ch in normalize(key, size) + alphabet(size):
        if ch not in seen:
            seen.append(ch)
    return [seen[r * size:(r + 1) * size] for r in range(size)]


def split_pairs(text: str, size: int = 5) -> list:
    """Tách bản rõ thành các cặp; chèn ký tự đệm giữa 2 ký tự giống nhau và ở cuối nếu lẻ."""
    chars = normalize(text, size)
    pairs = []
    i = 0
    while i < len(chars):
        a = chars[i]
        if i + 1 < len(chars) and chars[i + 1] != a:
            b = chars[i + 1]
            i += 2
        else:  # hết chuỗi hoặc 2 ký tự trùng nhau -> chèn ký tự đệm
            b = FILLER if a != FILLER else FILLER_ALT
            i += 1
        pairs.append(a + b)
    return pairs


def _positions(matrix: list) -> dict:
    return {ch: (r, c) for r, row in enumerate(matrix) for c, ch in enumerate(row)}


def _transform(pair: str, matrix: list, pos: dict, shift: int):
    size = len(matrix)
    (r1, c1), (r2, c2) = pos[pair[0]], pos[pair[1]]
    if r1 == r2:
        return matrix[r1][(c1 + shift) % size] + matrix[r2][(c2 + shift) % size], RULE_ROW
    if c1 == c2:
        return matrix[(r1 + shift) % size][c1] + matrix[(r2 + shift) % size][c2], RULE_COL
    return matrix[r1][c2] + matrix[r2][c1], RULE_RECT


def encrypt(plaintext: str, key: str, size: int = 5) -> PlayfairResult:
    matrix = build_matrix(key, size)
    pairs = split_pairs(plaintext, size)
    if not pairs:
        raise CryptoError("Bản rõ không có ký tự hợp lệ nào để mã hoá.")
    pos = _positions(matrix)
    result = PlayfairResult(matrix=matrix, prepared=pairs)
    for pair in pairs:
        out, rule = _transform(pair, matrix, pos, +1)
        result.steps.append((pair, out, rule))
    result.output = " ".join(out for _, out, _ in result.steps)
    return result


def decrypt(ciphertext: str, key: str, size: int = 5) -> PlayfairResult:
    matrix = build_matrix(key, size)
    chars = normalize(ciphertext, size)
    if not chars:
        raise CryptoError("Bản mã không có ký tự hợp lệ nào để giải mã.")
    if len(chars) % 2:
        raise CryptoError(
            f"Bản mã PlayFair phải có số ký tự chẵn (hiện có {len(chars)} ký tự hợp lệ)."
        )
    pairs = [chars[i:i + 2] for i in range(0, len(chars), 2)]
    pos = _positions(matrix)
    result = PlayfairResult(matrix=matrix, prepared=pairs)
    for pair in pairs:
        out, rule = _transform(pair, matrix, pos, -1)
        result.steps.append((pair, out, rule))
    result.output = "".join(out for _, out, _ in result.steps)
    return result
