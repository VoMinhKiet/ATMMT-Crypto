"""Tab 2 – Mã hoá RSA."""

import threading

import customtkinter as ctk

from atm_crypto import CryptoError, rsa

from . import theme as T
from . import widgets as W

MODES = {
    "Từng ký tự – mã ASCII/Unicode": rsa.MODE_ASCII,
    "Từng chữ cái – A=0 … Z=25": rsa.MODE_ALPHA,
    "Số nguyên M (cách nhau bởi dấu cách)": rsa.MODE_NUMBER,
    "Theo khối byte UTF-8 (khoá lớn)": rsa.MODE_BLOCK,
}
KEY_SIZES = ["16 bit", "32 bit", "512 bit", "1024 bit", "2048 bit"]


def _parse_int(text: str, name: str) -> int:
    cleaned = "".join(text.split())
    if not cleaned:
        raise CryptoError(f"Chưa nhập giá trị {name}.")
    try:
        return int(cleaned)
    except ValueError:
        raise CryptoError(f"{name} phải là một số nguyên (hệ thập phân).") from None


class RSATab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left = W.Card(self, width=360)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left.grid_propagate(False)
        left.grid_columnconfigure(0, weight=1)
        left.grid_columnconfigure(1, weight=1)
        pad = {"padx": 18, "sticky": "ew", "columnspan": 2}

        W.title_label(left, "Tạo khoá RSA").grid(row=0, column=0, pady=(14, 6), **pad)

        W.field_label(left, "Số nguyên tố p").grid(row=1, column=0, sticky="ew", padx=(18, 5))
        W.field_label(left, "Số nguyên tố q").grid(row=1, column=1, sticky="ew", padx=(5, 18))
        self.p_entry = W.entry(left)
        self.p_entry.grid(row=2, column=0, sticky="ew", padx=(18, 5), pady=(2, 8))
        self.q_entry = W.entry(left)
        self.q_entry.grid(row=2, column=1, sticky="ew", padx=(5, 18), pady=(2, 8))

        W.field_label(left, "Số mũ công khai e  (để trống = tự chọn)").grid(row=3, column=0, **pad)
        self.e_entry = W.entry(left)
        self.e_entry.grid(row=4, column=0, pady=(2, 8), **pad)

        self.compute_button = W.primary_button(left, "Tính khoá từ p, q, e", self._compute, height=34)
        self.compute_button.grid(row=5, column=0, pady=(0, 8), **pad)

        row = ctk.CTkFrame(left, fg_color="transparent")
        row.grid(row=6, column=0, pady=(0, 10), **pad)
        row.grid_columnconfigure(1, weight=1)
        self.size_menu = W.option_menu(row, KEY_SIZES, width=104)
        self.size_menu.set("1024 bit")
        self.size_menu.grid(row=0, column=0, padx=(0, 8))
        self.generate_button = W.soft_button(row, "Sinh khoá ngẫu nhiên", self._generate)
        self.generate_button.grid(row=0, column=1, sticky="ew")

        W.field_label(left, "Môđun n = p × q  (công khai)").grid(row=7, column=0, **pad)
        self.n_box = W.textbox(left, height=50, wrap="char", font=T.mono(12))
        self.n_box.grid(row=8, column=0, pady=(2, 8), **pad)

        W.field_label(left, "Số mũ bí mật d = e⁻¹ mod φ(n)").grid(row=9, column=0, **pad)
        self.d_box = W.textbox(left, height=50, wrap="char", font=T.mono(12))
        self.d_box.grid(row=10, column=0, pady=(2, 8), **pad)

        W.field_label(left, "Cách chuyển văn bản thành số").grid(row=11, column=0, **pad)
        self.mode_menu = W.option_menu(left, list(MODES), command=self._mode_changed)
        self.mode_menu.grid(row=12, column=0, pady=(2, 6), **pad)

        W.hint_label(
            left,
            "Ghi chú:\n"
            "Mã hoá: C = Mᵉ mod n với khoá công khai {e, n}.\n"
            "Giải mã: M = Cᵈ mod n với khoá bí mật {d, n}.\n"
            "Có thể dán trực tiếp e, d, n của khoá có sẵn.",
        ).grid(row=13, column=0, pady=(0, 12), **pad)

        self.panel = W.IOPanel(self, self._encrypt, self._decrypt)
        self.panel.grid(row=0, column=1, sticky="nsew")

        # Ví dụ trong bài giảng (Bài 4, slide 41): p = 61, q = 53, e = 17
        W.set_entry(self.p_entry, "61")
        W.set_entry(self.q_entry, "53")
        W.set_entry(self.e_entry, "17")
        W.set_text(self.panel.input, "AN TOAN MANG MAY TINH")
        self._compute(announce=False)

    # -- khoá ----------------------------------------------------------------
    def _fill_key(self, key: rsa.RSAKey, heading: str):
        W.set_entry(self.p_entry, str(key.p))
        W.set_entry(self.q_entry, str(key.q))
        W.set_entry(self.e_entry, str(key.e))
        W.set_text(self.n_box, str(key.n))
        W.set_text(self.d_box, str(key.d))
        details = "\n".join([
            heading,
            "",
            f"Bước 1: chọn hai số nguyên tố  p = {key.p}",
            f"                               q = {key.q}",
            f"Bước 2: n = p × q = {key.n}   ({key.n.bit_length()} bit)",
            f"Bước 3: φ(n) = (p − 1)(q − 1) = {key.phi}",
            f"Bước 4: chọn e = {key.e}  với gcd(φ(n), e) = 1 và 1 < e < φ(n)",
            f"Bước 5: d = e⁻¹ mod φ(n) = {key.d}   (thuật toán Euclid mở rộng)",
            f"        kiểm tra: (e × d) mod φ(n) = {key.e * key.d % key.phi}",
            "",
            f"Khoá công khai  PU = {{e, n}} = {{{key.e}, {key.n}}}",
            f"Khoá bí mật     PR = {{d, n}} = {{{key.d}, {key.n}}}",
        ])
        self.panel.show(details=details)

    def _compute(self, announce: bool = True):
        try:
            p = _parse_int(self.p_entry.get(), "p")
            q = _parse_int(self.q_entry.get(), "q")
            e_text = self.e_entry.get().strip()
            e = _parse_int(e_text, "e") if e_text else None
            key = rsa.make_key(p, q, e)
        except CryptoError as error:
            self.panel.set_status(f"{error}", "error")
            return
        self._fill_key(key, "TÍNH KHOÁ RSA TỪ p, q, e")
        if announce:
            self.panel.set_status(f"Đã tính khoá: n = {key.n.bit_length()} bit.", "ok")

    def _generate(self):
        bits = int(self.size_menu.get().split()[0])
        self.generate_button.configure(state="disabled", text="Đang sinh khoá…")
        self.panel.set_status(f"Đang sinh cặp khoá {bits} bit, vui lòng chờ…")
        holder = {}

        def work():
            try:
                holder["key"] = rsa.generate_key(bits)
            except Exception as error:  # trả lỗi về luồng giao diện
                holder["error"] = error

        def poll():
            if thread.is_alive():
                self.after(60, poll)
                return
            self.generate_button.configure(state="normal", text="Sinh khoá ngẫu nhiên")
            if "error" in holder:
                self.panel.set_status(f"Không sinh được khoá: {holder['error']}", "error")
                return
            self._fill_key(holder["key"], f"SINH KHOÁ RSA NGẪU NHIÊN {bits} BIT")
            self.panel.set_status(f"Đã sinh cặp khoá {bits} bit.", "ok")
            if bits >= 512 and self._mode() != rsa.MODE_BLOCK:
                self.mode_menu.set(list(MODES)[3])
                self._mode_changed()

        thread = threading.Thread(target=work, daemon=True)
        thread.start()
        self.after(60, poll)

    # -- mã hoá / giải mã ----------------------------------------------------
    def _mode(self) -> str:
        return MODES[self.mode_menu.get()]

    def _mode_changed(self, _=None):
        hints = {
            rsa.MODE_ASCII: "Mỗi ký tự được đổi thành mã ASCII/Unicode rồi mã hoá riêng (cần n lớn hơn mã ký tự).",
            rsa.MODE_ALPHA: "Chỉ dùng chữ cái: A=0, B=1, …, Z=25 (bỏ dấu, bỏ khoảng trắng).",
            rsa.MODE_NUMBER: "Nhập các số nguyên M < n, ví dụ: 88 hoặc 17 19 7 9 0 12 24.",
            rsa.MODE_BLOCK: "Văn bản UTF-8 được gom thành các khối lớn; bản mã ở dạng hex.",
        }
        self.panel.set_status(hints[self._mode()])

    def _modulus(self) -> int:
        return _parse_int(W.get_text(self.n_box), "n")

    def _header(self, verb: str, exponent_name: str, exponent: int, n: int) -> list:
        key_name = "công khai PU = {e, n}" if exponent_name == "e" else "bí mật PR = {d, n}"
        formula = "C = M^e mod n" if exponent_name == "e" else "M = C^d mod n"
        return [f"{verb} RSA bằng khoá {key_name}", f"  {exponent_name} = {exponent}", f"  n = {n}",
                f"  Công thức: {formula}  (luỹ thừa modulo bằng giải thuật bình phương và nhân)", ""]

    def _encrypt(self, text):
        e, n = _parse_int(self.e_entry.get(), "e"), self._modulus()
        output, steps = rsa.encrypt_text(text, e, n, self._mode())
        return output, "\n".join(self._header("MÃ HOÁ", "e", e, n) + steps)

    def _decrypt(self, text):
        d, n = _parse_int(W.get_text(self.d_box), "d"), self._modulus()
        output, steps = rsa.decrypt_text(text, d, n, self._mode())
        return output, "\n".join(self._header("GIẢI MÃ", "d", d, n) + steps)
