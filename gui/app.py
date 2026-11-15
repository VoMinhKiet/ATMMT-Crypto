"""Cửa sổ chính: thanh tiêu đề, thanh chuyển tab, nút Giới thiệu và 3 tab mã hoá."""

import os
import sys

import customtkinter as ctk

from . import theme as T
from . import widgets as W
from .about import AboutWindow
from .tab_playfair import PlayfairTab
from .tab_rsa import RSATab
from .tab_symmetric import SymmetricTab

APP_TITLE = "Nhom17-Crypto"
TABS = [("PlayFair", PlayfairTab), ("RSA", RSATab), ("DES & AES", SymmetricTab)]


def resource_path(relative: str) -> str:
    """Đường dẫn tới tài nguyên, dùng được cả khi chạy từ mã nguồn lẫn file .exe (PyInstaller)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, relative)


ICON_PATH = resource_path(os.path.join("assets", "icon.ico"))


class App(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("light")
        super().__init__(fg_color=T.BG)
        self.title(APP_TITLE)
        self._center(1240, 800)
        self.minsize(1000, 650)
        try:
            self.iconbitmap(ICON_PATH)
        except Exception:
            pass  # thiếu icon không ảnh hưởng tới chức năng

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=T.ACCENT, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Ứng dụng mã hoá dữ liệu", font=T.font(19, bold=True),
                     text_color=T.WHITE, anchor="w").grid(row=0, column=0, sticky="sw", padx=(20, 0),
                                                          pady=(10, 0))
        ctk.CTkLabel(header, text="Sản phẩm của nhóm 17", font=T.font(12), text_color=T.HEADER_SUB,
                     anchor="w").grid(row=1, column=0, sticky="nw", padx=(20, 0), pady=(0, 10))

        self.tab_bar = W.PillGroup(header, [name for name, _ in TABS], command=self.show_tab, height=30,
                                   text_font=T.font(13, bold=True), selected=T.WHITE, selected_text=T.ACCENT_TEXT,
                                   text=T.WHITE, hover=T.ACCENT_DARK, idle=T.ACCENT, edge=T.HEADER_SUB,
                                   button_width=100)
        self.tab_bar.grid(row=0, column=1, rowspan=2, padx=(0, 12))
        ctk.CTkButton(header, text="Giới thiệu", command=self.show_about, width=100, height=32,
                      font=T.font(13, bold=True), fg_color="transparent", hover_color=T.ACCENT_DARK,
                      text_color=T.WHITE, border_width=1, border_color=T.HEADER_SUB,
                      corner_radius=T.RADIUS).grid(row=0, column=2, rowspan=2, padx=(0, 20))
        self._about = None

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=14, pady=14)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(0, weight=1)
        self.tabs = {}
        for name, factory in TABS:
            tab = factory(body)
            tab.grid(row=0, column=0, sticky="nsew")
            self.tabs[name] = tab
        self.show_tab(TABS[0][0])

    def _work_area(self):
        """Vùng làm việc của màn hình (trừ thanh taskbar), tính bằng pixel thật: (x, y, rộng, cao)."""
        try:
            import ctypes
            from ctypes import wintypes
            rect = wintypes.RECT()
            if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
                return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top
        except Exception:
            pass
        return 0, 0, self.winfo_screenwidth(), self.winfo_screenheight()

    def _center(self, width: int, height: int):
        """Đặt cửa sổ giữa màn hình, thu nhỏ nếu màn hình không đủ chỗ (kích thước theo đơn vị logic)."""
        scale = ctk.ScalingTracker.get_window_scaling(self)
        left, top, area_w, area_h = self._work_area()
        title_bar = 40 * scale
        width = int(min(width, area_w / scale - 24))
        height = int(min(height, (area_h - title_bar) / scale - 12))
        x = int(left + max(0, (area_w - width * scale) / 2))
        y = int(top + max(0, (area_h - title_bar - height * scale) / 2))
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_about(self):
        """Mở cửa sổ giới thiệu; nếu đang mở rồi thì chỉ đưa lên trước."""
        if self._about is not None and self._about.winfo_exists():
            self._about.lift()
            self._about.focus_force()
            return
        self._about = AboutWindow(self, ICON_PATH)

    def show_tab(self, name: str):
        self.tab_bar.set(name)
        self.tabs[name].tkraise()


def run():
    App().mainloop()
