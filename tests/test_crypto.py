"""Kiểm thử các giải thuật bằng ví dụ trong slide bài giảng và vector chuẩn (FIPS / NIST).

Chạy:  python -m unittest discover -s tests -v      (từ thư mục ATM)
Nếu máy có cài pycryptodome, DES/AES còn được đối chiếu ngẫu nhiên với thư viện này.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atm_crypto import CryptoError, modes, playfair, rsa
from atm_crypto.aes import AES
from atm_crypto.des import DES

H = bytes.fromhex


class PlayfairTests(unittest.TestCase):
    def test_slide_matrix(self):
        # Bài 3, slide 37: khoá PLAYFAIR
        self.assertEqual(
            ["".join(row) for row in playfair.build_matrix("PLAYFAIR", 5)],
            ["PLAYF", "IRBCD", "EGHKM", "NOQST", "UVWXZ"],
        )

    def test_slide_example(self):
        result = playfair.encrypt("THANH PHO HO CHI MINH", "PLAYFAIR")
        self.assertEqual(" ".join(result.prepared), "TH AN HP HO HO CH IM IN HX")
        self.assertEqual(result.output, "QM PQ EA GQ GQ BK DE EU KW")
        self.assertEqual(playfair.decrypt(result.output, "PLAYFAIR").output, "THANHPHOHOCHIMINHX")

    def test_double_letters_and_accents(self):
        self.assertEqual(playfair.split_pairs("BALLOON"), ["BA", "LX", "LO", "ON"])
        self.assertEqual(playfair.normalize("Nguyễn Đức Jâm", 5), "NGUYENDUCIAM")
        self.assertEqual(playfair.split_pairs("XX"), ["XQ", "XQ"])

    def test_roundtrip_6x6(self):
        text = "BAO MAT THONG TIN 2026"
        enc = playfair.encrypt(text, "KHOA123", 6)
        self.assertEqual(playfair.decrypt(enc.output, "KHOA123", 6).output, "BAOMATTHONGTIN2026")

    def test_odd_ciphertext_rejected(self):
        with self.assertRaises(CryptoError):
            playfair.decrypt("ABC", "KEY")


class RSATests(unittest.TestCase):
    def test_slide_keys(self):
        self.assertEqual(rsa.make_key(17, 11, 7).d, 23)              # slide 35
        self.assertEqual(rsa.make_key(61, 53, 17).d, 2753)           # slide 41
        key = rsa.make_key(2357, 2551, 3674911)                      # slide 38
        self.assertEqual((key.n, key.phi, key.d), (6012707, 6007800, 422191))

    def test_slide_values(self):
        self.assertEqual(rsa.mod_pow(88, 7, 187), 11)
        self.assertEqual(rsa.mod_pow(11, 23, 187), 88)
        self.assertEqual(rsa.encrypt_text("123", 17, 3233, rsa.MODE_NUMBER)[0], "855")
        self.assertEqual(rsa.decrypt_text("855", 2753, 3233, rsa.MODE_NUMBER)[0], "123")
        self.assertEqual(rsa.gcd(35, 64), 1)                         # slide 40

    def test_exercise_alpha(self):
        # Bài tập 2 (slide 55): p=5, q=7, e=5, chữ cái đánh số từ 0
        key = rsa.make_key(5, 7, 5)
        plain, _ = rsa.decrypt_text("17 19 7 9 0 12 24", key.d, key.n, rsa.MODE_ALPHA)
        self.assertEqual(plain, "MYHEART")
        cipher, _ = rsa.encrypt_text("BAO MAT THONG TIN", key.e, key.n, rsa.MODE_ALPHA)
        self.assertEqual(rsa.decrypt_text(cipher, key.d, key.n, rsa.MODE_ALPHA)[0], "BAOMATTHONGTIN")

    def test_ascii_roundtrip(self):
        key = rsa.make_key(23, 41, 13)                               # Bài tập 3 (slide 55)
        cipher, _ = rsa.encrypt_text("Nguyen Van A", key.e, key.n, rsa.MODE_ASCII)
        self.assertEqual(rsa.decrypt_text(cipher, key.d, key.n, rsa.MODE_ASCII)[0], "Nguyen Van A")

    def test_message_must_be_smaller_than_n(self):
        with self.assertRaises(CryptoError):
            rsa.encrypt_text("ế", 7, 187, rsa.MODE_ASCII)

    def test_invalid_keys(self):
        for args in ((15, 11, 7), (11, 11, 7), (17, 11, 8)):
            with self.assertRaises(CryptoError):
                rsa.make_key(*args)

    def test_primes(self):
        self.assertEqual([n for n in range(60) if rsa.is_prime(n)],
                         [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59])
        self.assertTrue(rsa.is_prime(2 ** 127 - 1))
        self.assertFalse(rsa.is_prime(561))
        self.assertFalse(rsa.is_prime((2 ** 61 - 1) * (2 ** 89 - 1)))

    def test_generated_key_block_mode(self):
        for bits in (32, 512):
            key = rsa.generate_key(bits)
            self.assertEqual(key.n.bit_length(), bits)
            text = "Mã hoá RSA – An toàn mạng máy tính 🌸\x00 kết thúc"
            cipher, _ = rsa.encrypt_text(text, key.e, key.n, rsa.MODE_BLOCK)
            self.assertEqual(rsa.decrypt_text(cipher, key.d, key.n, rsa.MODE_BLOCK)[0], text)
            other = rsa.generate_key(bits)
            with self.assertRaises(CryptoError):
                rsa.decrypt_text(cipher, other.d, other.n, rsa.MODE_BLOCK)


class DESTests(unittest.TestCase):
    def test_known_vectors(self):
        vectors = [
            ("133457799BBCDFF1", "0123456789ABCDEF", "85E813540F0AB405"),
            ("0123456789ABCDEF", "4E6F772069732074", "3FA40E8A984D4815"),
            ("0101010101010101", "8000000000000000", "95F8A5E5DD31D900"),
        ]
        for key, plain, cipher in vectors:
            des = DES(H(key))
            self.assertEqual(des.encrypt_block(H(plain)).hex().upper(), cipher)
            self.assertEqual(des.decrypt_block(H(cipher)).hex().upper(), plain)

    def test_first_subkey(self):
        self.assertEqual(DES(H("133457799BBCDFF1")).subkeys[0], 0x1B02EFFC7072)

    def test_bad_key_length(self):
        with self.assertRaises(CryptoError):
            DES(b"short")


class AESTests(unittest.TestCase):
    def test_fips197(self):
        plain = H("00112233445566778899aabbccddeeff")
        vectors = [
            ("000102030405060708090a0b0c0d0e0f", "69c4e0d86a7b0430d8cdb78070b4c55a"),
            ("000102030405060708090a0b0c0d0e0f1011121314151617", "dda97ca4864cdfe06eaf70a0ec0d7191"),
            ("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f",
             "8ea2b7ca516745bfeafc49904b496089"),
        ]
        for key, cipher in vectors:
            aes = AES(H(key))
            self.assertEqual(aes.encrypt_block(plain).hex(), cipher)
            self.assertEqual(aes.decrypt_block(H(cipher)), plain)

    def test_sbox(self):
        from atm_crypto.aes import SBOX
        self.assertEqual((SBOX[0x00], SBOX[0x01], SBOX[0x53], SBOX[0xFF]), (0x63, 0x7C, 0xED, 0x16))

    def test_sp800_38a_cbc(self):
        aes = AES(H("2b7e151628aed2a6abf7158809cf4f3c"))
        plain = H("6bc1bee22e409f96e93d7e117393172aae2d8a571e03ac9c9eb76fac45af8e51")
        out = modes.encrypt(aes, plain, "CBC", H("000102030405060708090a0b0c0d0e0f"))
        self.assertEqual(out[:32].hex(), "7649abac8119b246cee98e9b12e9197d5086cb9b507219ee95db113a917678b2")
        ecb = modes.encrypt(aes, plain, "ECB")
        self.assertEqual(ecb[:16].hex(), "3ad77bb40d7a3660a89ecaf32466ef97")


class ModeTests(unittest.TestCase):
    def test_roundtrip_all(self):
        text = "Đồ án An toàn mạng máy tính – mã hoá DES và AES 🌷".encode("utf-8")
        for name in modes.ALGORITHMS:
            key = modes.random_bytes(modes.key_length(name))
            iv = modes.random_bytes(modes.block_length(name))
            for mode in modes.MODES:
                for size in (0, 1, 7, 8, 15, 16, 17, len(text)):
                    cipher = modes.make_cipher(name, key)
                    enc = modes.encrypt(cipher, text[:size], mode, iv)
                    self.assertEqual(len(enc) % cipher.block_size, 0)
                    self.assertEqual(modes.decrypt(cipher, enc, mode, iv), text[:size])

    def test_errors(self):
        cipher = modes.make_cipher("AES-128", bytes(16))
        with self.assertRaises(CryptoError):
            modes.make_cipher("AES-128", bytes(8))
        with self.assertRaises(CryptoError):
            modes.encrypt(cipher, b"abc", "CBC", bytes(8))
        with self.assertRaises(CryptoError):
            modes.decrypt(cipher, bytes(15), "ECB")
        with self.assertRaises(CryptoError):
            modes.parse_hex("xyz")

    def test_against_pycryptodome(self):
        try:
            from Crypto.Cipher import AES as RefAES, DES as RefDES
            from Crypto.Util.Padding import pad
        except ImportError:
            self.skipTest("chưa cài pycryptodome")
        for trial in range(40):
            data = os.urandom(trial * 3)
            for name in modes.ALGORITHMS:
                key = os.urandom(modes.key_length(name))
                size = modes.block_length(name)
                iv = os.urandom(size)
                ref = RefDES if name == "DES" else RefAES
                mine = modes.make_cipher(name, key)
                self.assertEqual(modes.encrypt(mine, data, "ECB"),
                                 ref.new(key, ref.MODE_ECB).encrypt(pad(data, size)))
                self.assertEqual(modes.encrypt(mine, data, "CBC", iv),
                                 ref.new(key, ref.MODE_CBC, iv).encrypt(pad(data, size)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
