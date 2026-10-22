"""Verifikimi i AES-it të krahasimit me vektorin zyrtar FIPS-197, Shtojca C.3 (AES-256)."""

import unittest

from matje import aes_studim


class TestAESStudim(unittest.TestCase):
    def test_sbox_vlera_te_njohura(self):
        self.assertEqual((aes_studim.SBOX[0x00], aes_studim.SBOX[0x01], aes_studim.SBOX[0x53]),
                         (0x63, 0x7C, 0xED))

    def test_fips197_c3(self):
        celesi = bytes(range(32))
        mesazhi = bytes.fromhex("00112233445566778899aabbccddeeff")
        pritur = "8ea2b7ca516745bfeafc49904b496089"
        self.assertEqual(bytes(aes_studim.kripto(mesazhi, aes_studim.orari(celesi))).hex(), pritur)


if __name__ == "__main__":
    unittest.main()
