"""Màu sắc và phông chữ dùng chung cho toàn bộ giao diện."""

import customtkinter as ctk

BG = "#FCEFF4"            # nền cửa sổ
CARD = "#FFFFFF"          # nền khung
ACCENT = "#E0528A"        # hồng chính (thanh tiêu đề, nút chính)
ACCENT_DARK = "#C93D74"   # hover của nút chính
ACCENT_TEXT = "#B03566"   # chữ tiêu đề
SOFT = "#FBE1EB"          # nền nút phụ / ô ma trận nhạt
BORDER = "#EFC3D3"        # viền khung, hover nút phụ
INPUT_BORDER = "#E2A6BE"  # viền ô nhập
INPUT_BG = "#FFFAFC"      # nền ô nhập
TEXT = "#4B2337"          # chữ chính
TEXT_MUTED = "#946A7E"    # chữ phụ
WHITE = "#FFFFFF"
HEADER_SUB = "#FFD9E7"
ERROR = "#D0243F"
SUCCESS = "#2E7D32"

RADIUS = 5                # bo góc nút, ô nhập
CARD_RADIUS = 8           # bo góc khung

UI_FAMILY = "Segoe UI"
MONO_FAMILY = "Consolas"


def font(size: int = 13, bold: bool = False) -> ctk.CTkFont:
    return ctk.CTkFont(family=UI_FAMILY, size=size, weight="bold" if bold else "normal")


def mono(size: int = 13, bold: bool = False) -> ctk.CTkFont:
    return ctk.CTkFont(family=MONO_FAMILY, size=size, weight="bold" if bold else "normal")
