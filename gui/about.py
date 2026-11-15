"""Cửa sổ "Giới thiệu": lịch sử ra đời, nguyên lý và cách dùng từng thuật toán trong chương trình."""

import customtkinter as ctk

from . import theme as T
from . import widgets as W

# Mỗi trang là danh sách (kiểu, nội dung): "h" = tiêu đề mục, "p" = đoạn văn.
PAGES = {
    "Tổng quan": [
        ("h", "Nhom17-Crypto"),
        ("p", "Chương trình minh hoạ bốn thuật toán mã hoá: PlayFair, RSA, DES và AES. Mỗi thuật toán "
              "nằm ở một tab riêng. Bấm tên tab trên thanh tiêu đề để chuyển."),
        ("p", "Tab nào cũng chia làm hai phần. Bên trái là phần khoá và tham số của thuật toán. Bên phải "
              "có ô Dữ liệu vào, hai nút Mã hoá / Giải mã, ô Kết quả và ô Chi tiết các bước. Ô cuối cùng "
              "ghi lại các bước trung gian để đối chiếu với cách tính tay."),
        ("h", "Thao tác chung"),
        ("p", "1. Chọn hoặc nhập khoá ở khung bên trái.\n"
              "2. Gõ (hoặc dán) dữ liệu vào ô Dữ liệu vào.\n"
              "3. Bấm Mã hoá hoặc Giải mã. Kết quả hiện ở ô Kết quả, các bước tính hiện ở ô bên dưới.\n"
              "4. Muốn kiểm tra chiều ngược lại thì bấm \"Đưa kết quả lên ô nhập\" rồi bấm nút còn lại. "
              "Giữ nguyên khoá thì sẽ thu lại đúng dữ liệu ban đầu."),
        ("p", "Nếu dữ liệu hoặc khoá sai định dạng, dòng chữ màu đỏ dưới hai nút sẽ báo lỗi cụ thể."),
        ("h", "Phân loại"),
        ("p", "PlayFair là mật mã cổ điển, thay thế từng cặp chữ cái.\n"
              "DES và AES là mã khoá đối xứng: hai bên dùng chung một khoá bí mật.\n"
              "RSA là mã khoá công khai: khoá công khai dùng để mã hoá, khoá bí mật dùng để giải mã."),
    ],
    "PlayFair": [
        ("h", "Lịch sử"),
        ("p", "Charles Wheatstone, nhà vật lý người Anh, nghĩ ra PlayFair năm 1854. Tên gọi lại lấy theo "
              "Lord Lyon Playfair, người bạn đã vận động chính phủ Anh đưa nó vào sử dụng. Quân đội Anh "
              "dùng PlayFair trong Chiến tranh Boer và Thế chiến thứ nhất, quân Úc còn dùng trong Thế "
              "chiến thứ hai. Ưu điểm lúc đó là chỉ cần giấy bút và có thể làm nhanh ngoài chiến trường."),
        ("p", "Đây là mật mã đầu tiên trong thực tế mã hoá theo cặp chữ (digraph) chứ không theo từng chữ "
              "đơn lẻ. Nhờ vậy, phân tích tần suất một chữ cái không còn hiệu quả. Tuy vậy, có đủ bản mã "
              "thì vẫn phá được bằng thống kê tần suất cặp chữ, nên ngày nay PlayFair chỉ còn dùng để học."),
        ("h", "Nguyên lý"),
        ("p", "Từ khoá được viết vào ma trận 5×5 (bỏ chữ trùng, I và J chung một ô), các ô còn lại điền "
              "nốt bảng chữ cái. Bản rõ tách thành từng cặp; cặp có hai chữ giống nhau, hoặc chữ lẻ cuối "
              "cùng, được chèn thêm X (nếu chính chữ đó là X thì chèn Q). Mỗi cặp được thay theo ba quy tắc:\n"
              "- Hai chữ cùng hàng: lấy chữ ngay bên phải mỗi chữ (cuối hàng thì quay về đầu hàng).\n"
              "- Hai chữ cùng cột: lấy chữ ngay bên dưới.\n"
              "- Khác hàng, khác cột: hai chữ là hai góc của một hình chữ nhật, thay mỗi chữ bằng góc "
              "còn lại trên cùng hàng với nó.\n"
              "Giải mã làm ngược lại: sang trái thay cho sang phải, lên trên thay cho xuống dưới."),
        ("h", "Cách dùng trong chương trình"),
        ("p", "1. Nhập từ khoá. Ma trận bên dưới cập nhật ngay khi gõ; ô màu đậm là chữ lấy từ khoá.\n"
              "2. Chọn ma trận 5×5 (chỉ chữ cái) hoặc 6×6 (thêm chữ số 0–9).\n"
              "3. Nhập bản rõ rồi bấm Mã hoá. Chữ có dấu tiếng Việt được tự bỏ dấu, ký tự lạ bị lược bỏ.\n"
              "4. Ô Chi tiết liệt kê từng cặp chữ và quy tắc đã áp dụng (cùng hàng, cùng cột, hình chữ nhật).\n"
              "Lưu ý: bản giải mã vẫn còn các chữ X đã chèn, người đọc tự lược bỏ."),
    ],
    "RSA": [
        ("h", "Lịch sử"),
        ("p", "RSA do ba nhà nghiên cứu ở MIT là Ron Rivest, Adi Shamir và Leonard Adleman công bố năm "
              "1977. Tên thuật toán ghép từ chữ cái đầu họ của ba người. Một năm trước đó, Diffie và "
              "Hellman đã nêu ý tưởng mã khoá công khai nhưng chưa có thuật toán cụ thể; RSA là lời giải "
              "đầu tiên dùng được trong thực tế."),
        ("p", "Sau này mới biết Clifford Cocks ở GCHQ (cơ quan tình báo tín hiệu Anh) đã tìm ra một hệ "
              "tương tự từ năm 1973, nhưng công trình bị giữ mật tới năm 1997. Đến nay RSA vẫn được dùng "
              "trong HTTPS, chữ ký số và trao đổi khoá."),
        ("h", "Nguyên lý"),
        ("p", "Tạo khoá:\n"
              "- Chọn hai số nguyên tố lớn p, q; tính n = p × q và φ(n) = (p − 1)(q − 1).\n"
              "- Chọn e sao cho 1 < e < φ(n) và gcd(e, φ(n)) = 1.\n"
              "- Tính d là nghịch đảo của e theo modulo φ(n), tức (e × d) mod φ(n) = 1.\n"
              "Khoá công khai là {e, n}, khoá bí mật là {d, n}.\n"
              "Mã hoá: C = M^e mod n.   Giải mã: M = C^d mod n.\n"
              "Độ an toàn dựa vào chỗ phân tích n ra p và q là bài toán rất khó khi n đủ lớn. Hiện nay "
              "khoá nên dài từ 2048 bit trở lên."),
        ("h", "Cách dùng trong chương trình"),
        ("p", "1. Tạo khoá theo một trong hai cách:\n"
              "   - Nhập p, q (và e nếu muốn) rồi bấm \"Tính khoá từ p, q, e\". Bỏ trống e thì chương "
              "trình tự chọn.\n"
              "   - Chọn độ dài rồi bấm \"Sinh khoá ngẫu nhiên\". Khoá 2048 bit có thể mất vài giây.\n"
              "2. Chọn cách chuyển văn bản thành số:\n"
              "   - Từng ký tự: mỗi ký tự lấy mã ASCII/Unicode, hợp với khoá nhỏ khi làm bài tập.\n"
              "   - Từng chữ cái: A=0 … Z=25, giống cách làm trong bài giảng.\n"
              "   - Số nguyên: nhập thẳng các số M cách nhau bởi dấu cách.\n"
              "   - Khối byte UTF-8: dùng với khoá từ 512 bit, mã được cả tiếng Việt có dấu.\n"
              "3. Nhập dữ liệu rồi bấm Mã hoá (dùng e, n) hoặc Giải mã (dùng d, n).\n"
              "Ví dụ có sẵn khi mở chương trình: p = 61, q = 53, e = 17, cho n = 3233 và d = 2753."),
    ],
    "DES & AES": [
        ("h", "DES – lịch sử"),
        ("p", "Đầu những năm 1970, IBM phát triển DES từ thuật toán Lucifer của Horst Feistel. Năm 1977, "
              "Cục Tiêu chuẩn Quốc gia Mỹ (NBS, nay là NIST) chọn nó làm chuẩn mã hoá liên bang FIPS 46. "
              "DES là thuật toán mã hoá được dùng rộng rãi nhất trong suốt hai thập kỷ sau đó, nhất là "
              "trong ngân hàng."),
        ("p", "Điểm yếu của DES là khoá hiệu dụng chỉ 56 bit. Năm 1998, máy Deep Crack của tổ chức EFF "
              "dò ra khoá DES trong khoảng 56 giờ. Vì vậy người ta chuyển sang Triple DES và sau đó là AES."),
        ("h", "DES – nguyên lý"),
        ("p", "DES mã hoá từng khối 64 bit bằng khoá 64 bit (8 bit kiểm tra chẵn lẻ, còn lại 56 bit). Khối "
              "đi qua hoán vị đầu IP, rồi 16 vòng Feistel: mỗi vòng mở rộng nửa phải lên 48 bit, XOR với "
              "khoá con, cho qua 8 hộp S, hoán vị P rồi XOR vào nửa trái. Cuối cùng là hoán vị ngược IP⁻¹. "
              "Giải mã dùng đúng mạch đó nhưng lấy khoá con theo thứ tự ngược lại."),
        ("h", "AES – lịch sử"),
        ("p", "Năm 1997, NIST mở cuộc thi công khai để tìm thuật toán thay DES. Trong 15 ứng viên, NIST "
              "chọn Rijndael của hai nhà mật mã người Bỉ Joan Daemen và Vincent Rijmen vào tháng 10/2000. "
              "Thuật toán được công bố thành chuẩn FIPS 197 năm 2001. Hiện nay AES có mặt hầu như ở mọi "
              "nơi: Wi-Fi WPA2/WPA3, HTTPS, mã hoá ổ đĩa, ứng dụng nhắn tin."),
        ("h", "AES – nguyên lý"),
        ("p", "AES mã hoá khối 128 bit, khoá dài 128, 192 hoặc 256 bit, tương ứng 10, 12 hoặc 14 vòng. Khối "
              "được xếp thành ma trận trạng thái 4×4 byte. Mỗi vòng gồm SubBytes (thay byte qua hộp S), "
              "ShiftRows (dịch vòng các hàng), MixColumns (trộn cột trên trường GF(2^8)) và AddRoundKey "
              "(XOR với khoá vòng). Vòng cuối bỏ bước MixColumns."),
        ("h", "Chế độ ECB và CBC"),
        ("p", "ECB mã hoá từng khối độc lập, nên hai khối rõ giống nhau cho ra hai khối mã giống nhau và "
              "để lộ cấu trúc dữ liệu. CBC XOR mỗi khối rõ với khối mã trước nó (khối đầu XOR với IV), "
              "nên an toàn hơn. Cả hai chế độ đều đệm bản rõ theo PKCS#7 cho đủ bội số kích thước khối."),
        ("h", "Cách dùng trong chương trình"),
        ("p", "1. Chọn thuật toán: DES, AES-128, AES-192 hoặc AES-256.\n"
              "2. Chọn chế độ CBC hoặc ECB.\n"
              "3. Nhập khoá dạng văn bản hoặc hex. Bộ đếm bên phải nhãn cho biết khoá đã đủ số byte chưa "
              "(DES 8, AES-128 16, AES-192 24, AES-256 32). Có thể bấm \"Khoá ngẫu nhiên\".\n"
              "4. Với CBC cần IV (8 byte cho DES, 16 byte cho AES); chương trình tự tạo sẵn, bấm \"IV mới\" "
              "để đổi.\n"
              "5. Chọn định dạng bản mã Hex hoặc Base64, nhập bản rõ rồi bấm Mã hoá.\n"
              "6. Muốn giải mã phải giữ đúng thuật toán, chế độ, khoá, IV và định dạng lúc mã hoá.\n"
              "Ô Chi tiết in ra các khoá con / khoá vòng và giá trị sau từng vòng của khối đầu tiên."),
    ],
}


class AboutWindow(ctk.CTkToplevel):
    def __init__(self, master, icon_path=None):
        super().__init__(master, fg_color=T.BG)
        self.title("Giới thiệu – Nhom17-Crypto")
        self.geometry("780x620")
        self.minsize(600, 420)
        self.transient(master)
        if icon_path:
            # CTkToplevel tự đặt icon mặc định sau ~200 ms, nên phải đặt lại sau đó.
            self.after(250, lambda: self._set_icon(icon_path))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.pages = W.PillGroup(self, list(PAGES), command=self.show, height=30, button_width=110)
        self.pages.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 10))

        card = W.Card(self)
        card.grid(row=1, column=0, sticky="nsew", padx=16)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        self.text = ctk.CTkTextbox(card, fg_color=T.CARD, text_color=T.TEXT, font=T.font(13), wrap="word",
                                   border_width=0, corner_radius=0, scrollbar_button_color=T.INPUT_BORDER,
                                   scrollbar_button_hover_color=T.ACCENT)
        self.text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        scale = ctk.ScalingTracker.get_widget_scaling(self)
        inner = self.text._textbox  # CTkTextbox không cho đặt font theo tag, dùng thẳng tk.Text bên trong
        inner.tag_configure("h", font=(T.UI_FAMILY, -round(16 * scale), "bold"), foreground=T.ACCENT_TEXT,
                            spacing1=round(10 * scale), spacing3=round(4 * scale))
        inner.tag_configure("h", lmargin1=2, lmargin2=2)
        inner.tag_configure("p", spacing3=round(2 * scale), lmargin1=2, lmargin2=2)
        inner.tag_configure("end", spacing3=round(10 * scale))

        W.soft_button(self, "Đóng", self.destroy, width=90).grid(row=2, column=0, sticky="e", padx=16,
                                                                 pady=12)
        self.bind("<Escape>", lambda _: self.destroy())
        self.show(next(iter(PAGES)))
        self.after(100, self._bring_to_front)

    def _set_icon(self, path):
        try:
            self.iconbitmap(path)
        except Exception:
            pass

    def _bring_to_front(self):
        self.lift()
        self.focus_force()

    def show(self, name: str):
        self.pages.set(name)
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        inner = self.text._textbox
        for kind, content in PAGES[name]:
            lines = content.split("\n")
            for i, line in enumerate(lines):
                # Chỉ dòng cuối của đoạn văn mới có khoảng cách lớn phía dưới.
                tags = (kind, "end") if kind == "p" and i == len(lines) - 1 else (kind,)
                inner.insert("end", line + "\n", tags)
        self.text.configure(state="disabled")
        self.text.yview_moveto(0)
