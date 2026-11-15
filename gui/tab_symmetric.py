"""Tab 3 – Mã hoá đối xứng với DES và AES."""

import customtkinter as ctk

from atm_crypto import CryptoError, modes

from . import theme as T
from . import widgets as W

KEY_TEXT, KEY_HEX = "Văn bản", "Hex"
INFO = {
    "DES": "DES: khối 64 bit, khoá 64 bit (56 bit hiệu dụng), 16 vòng Feistel.",
    "AES-128": "AES-128: khối 128 bit, khoá 128 bit, 10 vòng.",
    "AES-192": "AES-192: khối 128 bit, khoá 192 bit, 12 vòng.",
    "AES-256": "AES-256: khối 128 bit, khoá 256 bit, 14 vòng.",
}


class SymmetricTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left = W.Card(self, width=360)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left.grid_propagate(False)
        left.grid_columnconfigure(0, weight=1)
        pad = {"padx": 18, "sticky": "ew"}

        W.title_label(left, "Thiết lập DES / AES").grid(row=0, column=0, pady=(14, 8), **pad)

        W.field_label(left, "Thuật toán").grid(row=1, column=0, **pad)
        self.algorithm = W.PillGroup(left, list(modes.ALGORITHMS), command=lambda _: self._refresh(),
                                     text_font=T.font(11, bold=True))
        self.algorithm.grid(row=2, column=0, pady=(2, 4), **pad)
        self.algo_info = W.hint_label(left, INFO["DES"])
        self.algo_info.grid(row=3, column=0, pady=(0, 8), **pad)

        W.field_label(left, "Chế độ hoạt động").grid(row=4, column=0, **pad)
        self.mode = W.PillGroup(left, list(modes.MODES), initial="CBC", command=lambda _: self._refresh())
        self.mode.grid(row=5, column=0, pady=(2, 10), **pad)

        head = ctk.CTkFrame(left, fg_color="transparent")
        head.grid(row=6, column=0, **pad)
        W.field_label(head, "Khoá bí mật").pack(side="left")
        self.key_count = ctk.CTkLabel(head, text="", font=T.font(11, bold=True), height=18)
        self.key_count.pack(side="right")
        self.key_var = ctk.StringVar(value="ATMMT123")
        W.entry(left, textvariable=self.key_var).grid(row=7, column=0, pady=(2, 6), **pad)
        row = ctk.CTkFrame(left, fg_color="transparent")
        row.grid(row=8, column=0, pady=(0, 10), **pad)
        row.grid_columnconfigure(0, weight=1)
        self.key_format = W.PillGroup(row, [KEY_TEXT, KEY_HEX], command=lambda _: self._refresh())
        self.key_format.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        W.soft_button(row, "Khoá ngẫu nhiên", self._random_key, width=130).grid(row=0, column=1)

        head = ctk.CTkFrame(left, fg_color="transparent")
        head.grid(row=9, column=0, **pad)
        W.field_label(head, "Vectơ khởi tạo IV (hex)").pack(side="left")
        self.iv_count = ctk.CTkLabel(head, text="", font=T.font(11, bold=True), height=18)
        self.iv_count.pack(side="right")
        row = ctk.CTkFrame(left, fg_color="transparent")
        row.grid(row=10, column=0, pady=(2, 10), **pad)
        row.grid_columnconfigure(0, weight=1)
        self.iv_var = ctk.StringVar()
        self.iv_entry = W.entry(row, textvariable=self.iv_var, font=T.mono(12))
        self.iv_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.iv_button = W.soft_button(row, "IV mới", self._random_iv, width=70)
        self.iv_button.grid(row=0, column=1)

        W.field_label(left, "Định dạng bản mã").grid(row=11, column=0, **pad)
        self.output_format = W.PillGroup(left, ["Hex", "Base64"])
        self.output_format.grid(row=12, column=0, pady=(2, 8), **pad)

        W.hint_label(
            left,
            "Ghi chú:\n"
            "• Văn bản được mã hoá theo UTF-8, đệm PKCS#7.\n"
            "• CBC: mỗi khối được XOR với khối mã trước đó (khối đầu XOR với IV). "
            "Khi giải mã phải dùng đúng khoá và IV đã mã hoá.\n"
            "• ECB: các khối được mã hoá độc lập, không cần IV.",
        ).grid(row=13, column=0, pady=(0, 12), **pad)

        self.panel = W.IOPanel(self, self._encrypt, self._decrypt)
        self.panel.grid(row=0, column=1, sticky="nsew")
        W.set_text(self.panel.input, "An toàn mạng máy tính – mã hoá với DES và AES")

        self.key_var.trace_add("write", lambda *_: self._update_counters())
        self.iv_var.trace_add("write", lambda *_: self._update_counters())
        self._random_iv()
        self._refresh()

    # -- khoá và IV ----------------------------------------------------------
    def _key_bytes(self, strict: bool = True) -> bytes:
        text = self.key_var.get()
        if self.key_format.get() == KEY_HEX:
            try:
                return modes.parse_hex(text, "Khoá")
            except CryptoError:
                if strict:
                    raise
                return None
        return text.encode("utf-8")

    def _iv_bytes(self, strict: bool = True) -> bytes:
        try:
            return modes.parse_hex(self.iv_var.get(), "IV")
        except CryptoError:
            if strict:
                raise
            return None

    def _random_key(self):
        self.key_format.set(KEY_HEX)
        self.key_var.set(modes.to_hex(modes.random_bytes(modes.key_length(self.algorithm.get()))))

    def _random_iv(self):
        self.iv_var.set(modes.to_hex(modes.random_bytes(modes.block_length(self.algorithm.get()))))

    def _refresh(self):
        name = self.algorithm.get()
        self.algo_info.configure(text=INFO[name])
        uses_iv = self.mode.get() == "CBC"
        self.iv_entry.configure(state="normal" if uses_iv else "disabled",
                                text_color=T.TEXT if uses_iv else T.INPUT_BORDER)
        self.iv_button.configure(state="normal" if uses_iv else "disabled")
        iv = self._iv_bytes(strict=False)
        if uses_iv and (iv is None or len(iv) != modes.block_length(name)):
            self._random_iv()  # IV cũ không hợp kích thước khối của thuật toán mới
        self._update_counters()

    @staticmethod
    def _show_count(label, data, needed: int, enabled: bool = True):
        if not enabled:
            label.configure(text="không dùng với ECB", text_color=T.TEXT_MUTED)
        elif data is None:
            label.configure(text="hex không hợp lệ", text_color=T.ERROR)
        elif len(data) == needed:
            label.configure(text=f"{needed}/{needed} byte", text_color=T.SUCCESS)
        else:
            label.configure(text=f"{len(data)}/{needed} byte", text_color=T.ERROR)

    def _update_counters(self):
        name = self.algorithm.get()
        self._show_count(self.key_count, self._key_bytes(strict=False), modes.key_length(name))
        self._show_count(self.iv_count, self._iv_bytes(strict=False), modes.block_length(name),
                         enabled=self.mode.get() == "CBC")

    # -- mã hoá / giải mã ----------------------------------------------------
    def _prepare(self):
        name, mode = self.algorithm.get(), self.mode.get()
        key = self._key_bytes()
        cipher = modes.make_cipher(name, key)
        iv = self._iv_bytes() if mode == "CBC" else None
        return name, mode, key, iv, cipher

    def _details(self, verb, name, mode, key, iv, cipher, plain_len, cipher_len, first_block, trace):
        size = cipher.block_size
        lines = [
            f"{verb} bằng {name} – chế độ {mode}, đệm PKCS#7",
            f"  Khoá (hex)  : {modes.to_hex(key)}",
            f"  IV (hex)    : {modes.to_hex(iv) if iv else '(không dùng)'}",
            f"  Bản rõ      : {plain_len} byte",
            f"  Bản mã      : {cipher_len} byte = {cipher_len // size} khối × {size} byte",
            "",
            "Khoá con sinh từ khoá chính:" if name == "DES" else "Khoá vòng sinh từ khoá chính (mở rộng khoá):",
        ]
        lines += ["  " + line for line in cipher.describe_key()]
        lines += ["", f"Các vòng xử lý của khối đầu tiên (đầu vào: {modes.to_hex(first_block)}):"]
        if mode == "CBC" and verb == "MÃ HOÁ":
            lines.append("  (khối bản rõ đã được XOR với IV trước khi đưa vào các vòng)")
        lines += ["  " + line for line in trace]
        if mode == "CBC" and verb == "GIẢI MÃ":
            lines.append("  (kết quả các vòng được XOR với IV để ra khối bản rõ)")
        return "\n".join(lines)

    def _encrypt(self, text):
        name, mode, key, iv, cipher = self._prepare()
        data = text.encode("utf-8")
        trace = []
        encrypted = modes.encrypt(cipher, data, mode, iv, trace)
        first = modes.pad(data, cipher.block_size)[:cipher.block_size]
        output = modes.to_hex(encrypted) if self.output_format.get() == "Hex" else modes.to_base64(encrypted)
        return output, self._details("MÃ HOÁ", name, mode, key, iv, cipher, len(data), len(encrypted),
                                     first, trace)

    def _decrypt(self, text):
        name, mode, key, iv, cipher = self._prepare()
        if self.output_format.get() == "Hex":
            data = modes.parse_hex(text, "Bản mã")
        else:
            data = modes.parse_base64(text, "Bản mã")
        trace = []
        decrypted = modes.decrypt(cipher, data, mode, iv, trace)
        try:
            output = decrypted.decode("utf-8")
        except UnicodeDecodeError:
            raise CryptoError("Giải mã thất bại: sai khoá/IV hoặc bản mã đã bị thay đổi.") from None
        return output, self._details("GIẢI MÃ", name, mode, key, iv, cipher, len(decrypted), len(data),
                                     data[:cipher.block_size], trace)
