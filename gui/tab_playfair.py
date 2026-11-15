"""Tab 1 – Mã hoá PlayFair."""

import customtkinter as ctk

from atm_crypto import playfair

from . import theme as T
from . import widgets as W

SIZE_LABELS = {"5 × 5  (I/J chung ô)": 5, "6 × 6  (A–Z và 0–9)": 6}


class PlayfairTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left = W.Card(self, width=360)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left.grid_propagate(False)
        left.grid_columnconfigure(0, weight=1)
        pad = {"padx": 18, "sticky": "ew"}

        W.title_label(left, "Khoá PlayFair").grid(row=0, column=0, pady=(14, 8), **pad)
        W.field_label(left, "Từ khoá").grid(row=1, column=0, **pad)
        self.key_var = ctk.StringVar(value="PLAYFAIR")
        self.key_entry = W.entry(left, textvariable=self.key_var)
        self.key_entry.grid(row=2, column=0, pady=(2, 10), **pad)

        W.field_label(left, "Kích thước ma trận").grid(row=3, column=0, **pad)
        self.size_group = W.PillGroup(left, list(SIZE_LABELS), command=lambda _: self._refresh_matrix())
        self.size_group.grid(row=4, column=0, pady=(2, 12), **pad)

        W.field_label(left, "Ma trận khoá").grid(row=5, column=0, **pad)
        self.matrix_frame = ctk.CTkFrame(left, fg_color=T.BORDER, corner_radius=0)
        self.matrix_frame.grid(row=6, column=0, pady=(6, 10), padx=18)
        self._cells = []
        self._cell_size = None

        W.hint_label(
            left,
            "Ghi chú:\n"
            "• Ô đậm: ký tự lấy từ khoá; ô trắng: phần còn lại của bảng chữ cái.\n"
            "• Cùng dòng → lấy ký tự bên phải; cùng cột → lấy ký tự bên dưới; "
            "hình chữ nhật → lấy hai góc còn lại trên cùng dòng.\n"
            "• Dư 1 ký tự hoặc 2 ký tự trùng nhau → chèn X.\n"
            "• Chữ có dấu tiếng Việt được tự động bỏ dấu.",
        ).grid(row=7, column=0, pady=(0, 14), **pad)

        self.panel = W.IOPanel(self, self._encrypt, self._decrypt, "ví dụ: THANH PHO HO CHI MINH")
        self.panel.grid(row=0, column=1, sticky="nsew")
        W.set_text(self.panel.input, "THANH PHO HO CHI MINH")

        self.key_var.trace_add("write", lambda *_: self._refresh_matrix())
        self._refresh_matrix()

    # -- ma trận -------------------------------------------------------------
    def _size(self) -> int:
        return SIZE_LABELS[self.size_group.get()]

    def _refresh_matrix(self):
        size = self._size()
        if size != self._cell_size:
            for cell in self._cells:
                cell.destroy()
            side = 46 if size == 5 else 39
            self._cells = []
            for index in range(size * size):
                cell = ctk.CTkLabel(self.matrix_frame, text="", width=side, height=side, corner_radius=0,
                                    font=T.mono(17 if size == 5 else 15, bold=True))
                cell.grid(row=index // size, column=index % size, padx=1, pady=1)
                self._cells.append(cell)
            self._cell_size = size
        key = self.key_var.get()
        from_key = len(dict.fromkeys(playfair.normalize(key, size)))
        letters = [ch for row in playfair.build_matrix(key, size) for ch in row]
        for index, (cell, ch) in enumerate(zip(self._cells, letters)):
            if index < from_key:
                cell.configure(text=ch, fg_color=T.ACCENT, text_color=T.WHITE)
            else:
                cell.configure(text=ch, fg_color=T.WHITE, text_color=T.ACCENT_TEXT)

    # -- mã hoá / giải mã ----------------------------------------------------
    def _details(self, result, verb: str) -> str:
        size = len(result.matrix)
        lines = [f"Ma trận khoá {size}×{size}  (từ khoá: {self.key_var.get().strip() or '(trống)'})"]
        lines += ["    " + " ".join(row) for row in result.matrix]
        lines += ["", f"Tách thành từng cặp : {' '.join(result.prepared)}", "",
                  f"  #   Cặp vào      Cặp ra    Quy tắc ({verb})"]
        for number, (source, target, rule) in enumerate(result.steps, 1):
            lines.append(f"{number:>3}     {source}     →     {target}      {rule}")
        return "\n".join(lines)

    def _encrypt(self, text):
        result = playfair.encrypt(text, self.key_var.get(), self._size())
        return result.output, self._details(result, "mã hoá")

    def _decrypt(self, text):
        result = playfair.decrypt(text, self.key_var.get(), self._size())
        return result.output, self._details(result, "giải mã")
