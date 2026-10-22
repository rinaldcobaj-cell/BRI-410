"""Testet e korrektësisë së komponentëve. Përdorimi: python -m unittest discover -s teste -t ."""

import random
import unittest

from shahu import celesi, levizja, mds, sbox
from shahu.gf16 import inversi, shumezo


class TestGF16(unittest.TestCase):
    def test_inversi(self):
        for a in range(1, 16):
            self.assertEqual(shumezo(a, inversi(a)), 1)

    def test_komutativiteti_dhe_distributiviteti(self):
        for a in range(16):
            for b in range(16):
                self.assertEqual(shumezo(a, b), shumezo(b, a))
                for c in range(16):
                    self.assertEqual(shumezo(a, b ^ c), shumezo(a, b) ^ shumezo(a, c))


class TestSbox(unittest.TestCase):
    def test_riprodhohet_nga_etiketa(self):
        self.assertEqual(sbox.kerko_sbox(), (sbox.NUMERUESI_SBOX, sbox.SBOX))

    def test_inversi(self):
        for x in range(16):
            self.assertEqual(sbox.SBOX_INV[sbox.SBOX[x]], x)


class TestMDS(unittest.TestCase):
    def test_inversi_i_matrices(self):
        for i in range(8):
            rreshti = [0] * 8
            for j in range(8):
                for k in range(8):
                    rreshti[j] ^= shumezo(mds.M[i][k], mds.M_INV[k][j])
            self.assertEqual(rreshti, [int(i == j) for j in range(8)])

    def test_perzierja_kthehet(self):
        rng = random.Random(1)
        for _ in range(200):
            g = [rng.randrange(16) for _ in range(64)]
            self.assertEqual(mds.perziej_rreshtat(mds.perziej_rreshtat(g), mds.M_INV), g)


class TestLevizja(unittest.TestCase):
    def test_te_gjitha_variantet_jane_bijeksione(self):
        rng = random.Random(2)
        g = [rng.randrange(16) for _ in range(64)]
        for d in levizja.DREJTIMET:
            for alfa in range(8):
                for beta in range(8):
                    p = levizja.levizja_kalit(d, alfa, beta)
                    self.assertTrue(levizja.eshte_bijeksion(p))
                    self.assertEqual(levizja.zbato(levizja.inversi(p), levizja.zbato(p, g)), g)


class TestCelesi(unittest.TestCase):
    def test_hapi_kthehet(self):
        rng = random.Random(3)
        for i in range(1, 200):
            g = [rng.randrange(16) for _ in range(celesi.NIBLA)]
            self.assertEqual(celesi.hapi_invers(celesi.hapi(g, i), i), g)

    def test_kufijte_e_celesit(self):
        with self.assertRaises(ValueError):
            celesi.ngarko(1 << 410)
        with self.assertRaises(ValueError):
            celesi.ngarko(-1)
        celesi.ngarko((1 << 410) - 1)

    def test_rk0_jane_256_bitet_e_para(self):
        k = random.Random(4).getrandbits(410)
        rk0 = celesi.orari(k, 1)[0][0]
        self.assertEqual(sum(x << (4 * j) for j, x in enumerate(rk0)), k & ((1 << 256) - 1))

    def test_gjatesia_e_orarit(self):
        o = celesi.orari(12345, 32)
        self.assertEqual(len(o), 33)
        self.assertIsNone(o[0][1])
        self.assertTrue(all(len(rk) == 64 and lv is not None for rk, lv in o[1:]))

    def test_levizja_ka_vetem_drejtim_dhe_beta(self):
        for _rk, (d, beta) in celesi.orari(random.Random(5).getrandbits(410), 32)[1:]:
            self.assertIn(d, levizja.DREJTIMET)
            self.assertIn(beta, range(8))


if __name__ == "__main__":
    unittest.main()
