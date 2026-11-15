"""Các thành phần giao diện dùng chung: thẻ, nút, ô nhập, nhóm nút chọn và khung vào/ra."""

import customtkinter as ctk

from atm_crypto import CryptoError

from . import theme as T


class Card(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", T.CARD)
        kwargs.setdefault("corner_radius", T.CARD_RADIUS)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", T.BORDER)
        super().__init__(master, **kwargs)


def title_label(master, text):
    return ctk.CTkLabel(master, text=text, font=T.font(15, bold=True), text_color=T.ACCENT_TEXT, anchor="w")


def field_label(master, text):
    return ctk.CTkLabel(master, text=text, font=T.font(12, bold=True), text_color=T.TEXT, anchor="w",
                        height=18)


def hint_label(master, text, wraplength=310):
    return ctk.CTkLabel(master, text=text, font=T.font(11), text_color=T.TEXT_MUTED, anchor="w",
                        justify="left", wraplength=wraplength)


def primary_button(master, text, command, **kwargs):
    kwargs.setdefault("height", 36)
    kwargs.setdefault("width", 120)
    return ctk.CTkButton(master, text=text, command=command, font=T.font(13, bold=True),
                         fg_color=T.ACCENT, hover_color=T.ACCENT_DARK, text_color=T.WHITE,
                         corner_radius=T.RADIUS, **kwargs)


def soft_button(master, text, command, **kwargs):
    kwargs.setdefault("height", 32)
    kwargs.setdefault("width", 90)
    return ctk.CTkButton(master, text=text, command=command, font=T.font(12, bold=True),
                         fg_color=T.SOFT, hover_color=T.BORDER, text_color=T.ACCENT_TEXT,
                         corner_radius=T.RADIUS, border_width=1, border_color=T.BORDER, **kwargs)


def entry(master, **kwargs):
    kwargs.setdefault("height", 34)
    kwargs.setdefault("font", T.mono(13))
    return ctk.CTkEntry(master, fg_color=T.INPUT_BG, border_color=T.INPUT_BORDER, border_width=1,
                        text_color=T.TEXT, placeholder_text_color=T.TEXT_MUTED, corner_radius=T.RADIUS,
                        **kwargs)


def textbox(master, height=90, **kwargs):
    kwargs.setdefault("font", T.mono(13))
    kwargs.setdefault("wrap", "word")
    return ctk.CTkTextbox(master, height=height, fg_color=T.INPUT_BG, border_color=T.INPUT_BORDER,
                          border_width=1, text_color=T.TEXT, corner_radius=T.RADIUS,
                          scrollbar_button_color=T.INPUT_BORDER,
                          scrollbar_button_hover_color=T.ACCENT, **kwargs)


def option_menu(master, values, command=None, **kwargs):
    kwargs.setdefault("height", 32)
    return ctk.CTkOptionMenu(master, values=values, command=command, font=T.font(12),
                             dropdown_font=T.font(12), fg_color=T.ACCENT, button_color=T.ACCENT_DARK,
                             button_hover_color=T.ACCENT_TEXT, text_color=T.WHITE,
                             dropdown_fg_color=T.CARD, dropdown_hover_color=T.BORDER,
                             dropdown_text_color=T.TEXT, corner_radius=T.RADIUS, **kwargs)


def get_text(box) -> str:
    return box.get("1.0", "end-1c")


def set_text(box, text: str, readonly: bool = False):
    box.configure(state="normal")
    box.delete("1.0", "end")
    box.insert("1.0", text)
    if readonly:
        box.configure(state="disabled")


def set_entry(widget, text: str):
    widget.delete(0, "end")
    widget.insert(0, text)


class PillGroup(ctk.CTkFrame):
    """Một hàng nút rời, bấm nút nào thì nút đó được chọn (giống nhóm radio button)."""

    def __init__(self, master, values, command=None, initial=None, height=28, text_font=None,
                 track="transparent", selected=T.ACCENT, selected_text=T.WHITE, text=T.ACCENT_TEXT,
                 hover=T.SOFT, button_width=40, idle=T.CARD, edge=T.BORDER):
        super().__init__(master, fg_color=track, corner_radius=0)
        self._command = command
        self._colors = (selected, selected_text, text, hover, idle)
        self._buttons = {}
        self._value = None
        for column, value in enumerate(values):
            button = ctk.CTkButton(self, text=value, height=height, width=button_width,
                                   corner_radius=T.RADIUS, font=text_font or T.font(12, bold=True),
                                   fg_color=idle, hover_color=hover, text_color=text,
                                   border_width=1, border_color=edge,
                                   command=lambda v=value: self.set(v, notify=True))
            button.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 4, 0))
            self.grid_columnconfigure(column, weight=1)
            self._buttons[value] = button
        self.set(initial or values[0])

    def get(self) -> str:
        return self._value

    def set(self, value: str, notify: bool = False):
        selected, selected_text, text, hover, idle = self._colors
        changed = value != self._value
        self._value = value
        for name, button in self._buttons.items():
            if name == value:
                button.configure(fg_color=selected, text_color=selected_text, hover_color=selected)
            else:
                button.configure(fg_color=idle, text_color=text, hover_color=hover)
        if notify and changed and self._command:
            self._command(value)


class IOPanel(Card):
    """Khung bên phải của mỗi tab: dữ liệu vào, nút Mã hoá / Giải mã, kết quả và chi tiết.

    on_encrypt / on_decrypt nhận chuỗi đầu vào và trả về (kết quả, chi tiết);
    báo lỗi nhập liệu bằng CryptoError.
    """

    def __init__(self, master, on_encrypt, on_decrypt, input_hint=""):
        super().__init__(master)
        self._on_encrypt = on_encrypt
        self._on_decrypt = on_decrypt
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(5, weight=2)
        self.grid_rowconfigure(7, weight=7)
        pad = {"padx": 18}

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", pady=(14, 4), **pad)
        title_label(head, "Dữ liệu vào").pack(side="left")
        if input_hint:
            ctk.CTkLabel(head, text=input_hint, font=T.font(11), text_color=T.TEXT_MUTED).pack(
                side="left", padx=10)
        self.input = textbox(self, height=84)
        self.input.grid(row=1, column=0, sticky="nsew", **pad)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, sticky="ew", pady=(10, 2), **pad)
        primary_button(actions, "Mã hoá", lambda: self._run(self._on_encrypt, "Mã hoá")).pack(side="left")
        primary_button(actions, "Giải mã", lambda: self._run(self._on_decrypt, "Giải mã")).pack(
            side="left", padx=8)
        soft_button(actions, "Xoá hết", self.clear).pack(side="right")
        soft_button(actions, "Đưa kết quả lên ô nhập", self._swap, width=180).pack(side="right", padx=8)

        self.status = ctk.CTkLabel(self, text="Nhập dữ liệu rồi bấm Mã hoá hoặc Giải mã.", height=20,
                                   font=T.font(12), text_color=T.TEXT_MUTED, anchor="w", justify="left")
        self.status.grid(row=3, column=0, sticky="ew", pady=(4, 0), **pad)

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=4, column=0, sticky="ew", pady=(6, 4), **pad)
        title_label(head, "Kết quả").pack(side="left")
        self._copy_button = soft_button(head, "Sao chép", self._copy, height=26, width=84)
        self._copy_button.pack(side="right")
        self.output = textbox(self, height=84)
        self.output.grid(row=5, column=0, sticky="nsew", **pad)
        self.output.configure(state="disabled")

        title_label(self, "Chi tiết các bước").grid(row=6, column=0, sticky="ew", pady=(10, 4), **pad)
        self.details = textbox(self, height=120, wrap="none", font=T.mono(12))
        self.details.grid(row=7, column=0, sticky="nsew", pady=(0, 16), **pad)
        self.details.configure(state="disabled")

        self.bind("<Configure>", lambda e: self.status.configure(wraplength=max(200, e.width / self._scale() - 50)))

    def _scale(self) -> float:
        return ctk.ScalingTracker.get_widget_scaling(self)

    # -- trạng thái ---------------------------------------------------------
    def set_status(self, message: str, kind: str = "info"):
        color = {"error": T.ERROR, "ok": T.SUCCESS}.get(kind, T.TEXT_MUTED)
        self.status.configure(text=message, text_color=color)

    def show(self, output: str = None, details: str = None):
        if output is not None:
            set_text(self.output, output, readonly=True)
        if details is not None:
            set_text(self.details, details, readonly=True)

    # -- hành động ----------------------------------------------------------
    def _run(self, handler, verb: str):
        text = get_text(self.input)
        if not text:
            self.set_status("Chưa có dữ liệu vào – hãy nhập nội dung trước.", "error")
            return
        try:
            output, details = handler(text)
        except CryptoError as error:
            self.set_status(f"{error}", "error")
            return
        except Exception as error:  # lỗi ngoài dự kiến: vẫn báo cho người dùng thay vì im lặng
            self.set_status(f"Lỗi không mong muốn: {error}", "error")
            return
        self.show(output, details)
        self.set_status(f"{verb} thành công.", "ok")

    def _swap(self):
        result = get_text(self.output)
        if not result:
            self.set_status("Chưa có kết quả để đưa lên.", "error")
            return
        set_text(self.input, result)
        self.set_status("Đã đưa kết quả lên ô nhập – bấm Giải mã (hoặc Mã hoá) để thử chiều ngược lại.")

    def _copy(self):
        result = get_text(self.output)
        if not result:
            self.set_status("Chưa có kết quả để sao chép.", "error")
            return
        self.clipboard_clear()
        self.clipboard_append(result)
        self._copy_button.configure(text="Đã chép")
        self.after(1400, lambda: self._copy_button.configure(text="Sao chép"))

    def clear(self):
        set_text(self.input, "")
        self.show("", "")
        self.set_status("Nhập dữ liệu rồi bấm Mã hoá hoặc Giải mã.")
