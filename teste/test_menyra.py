"""Testet e BRI-410 AE (hapi 2): mesazhe të çdo gjatësie, vula 416 bit, të dhëna shoqëruese."""

import json
import random
import unittest
from pathlib import Path

from shahu import bri8, menyra

GJATESITE = [0, 1, 31, 63, 64, 65, 100, 127, 128, 129, 200, 640, 1000]


class TestMenyra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rng = random.Random(120)
        cls.k = bri8.gjenero_celes()

    def test_kthimi_per_cdo_gjatesi(self):
        for n in GJATESITE:
            for a in (0, 1, 64, 100):
                m, ad = self.rng.randbytes(n), self.rng.randbytes(a)
                p = menyra.kripto(self.k, m, ad)
                self.assertEqual(len(p), 12 + n + 52)
                self.assertEqual(menyra.dekripto(self.k, p, ad), m)

    def test_cdo_bit_i_ndryshuar_kapet(self):
        m, ad = self.rng.randbytes(100), self.rng.randbytes(10)
        p = menyra.kripto(self.k, m, ad)
        for b in range(8 * len(p)):
            ndryshuar = bytearray(p)
            ndryshuar[b // 8] ^= 1 << (b % 8)
            with self.assertRaises(menyra.VulaEGabuar):
                menyra.dekripto(self.k, bytes(ndryshuar), ad)
        for b in range(8 * len(ad)):
            ad2 = bytearray(ad)
            ad2[b // 8] ^= 1 << (b % 8)
            with self.assertRaises(menyra.VulaEGabuar):
                menyra.dekripto(self.k, p, bytes(ad2))

    def test_prerja_zgjatja_dhe_nderrimi_kapen(self):
        m = self.rng.randbytes(200)
        p = menyra.kripto(self.k, m)
        c = p[12:-52]
        for keq in (p[:-1], p + b"\x00", p[:12] + c[64:] + p[-52:],
                    p[:12] + c[64:128] + c[:64] + c[128:] + p[-52:], p[:63]):
            with self.assertRaises(menyra.VulaEGabuar):
                menyra.dekripto(self.k, keq)

    def test_celesi_ose_te_dhenat_e_gabuara(self):
        p = menyra.kripto(self.k, b"pershendetje", b"Ana")
        with self.assertRaises(menyra.VulaEGabuar):
            menyra.dekripto(bri8.gjenero_celes(), p, b"Ana")
        with self.assertRaises(menyra.VulaEGabuar):
            menyra.dekripto(self.k, p, b"Besi")
        with self.assertRaises(menyra.VulaEGabuar):
            menyra.dekripto(self.k, p)

    def test_vetem_te_dhena_shoqeruese(self):
        p = menyra.kripto(self.k, b"", b"vetem koka")
        self.assertEqual(menyra.dekripto(self.k, p, b"vetem koka"), b"")
        with self.assertRaises(menyra.VulaEGabuar):
            menyra.dekripto(self.k, p, b"vetem kokA")

    def test_numri(self):
        m = self.rng.randbytes(70)
        n = bytes(range(12))
        self.assertEqual(menyra.kripto(self.k, m, numri=n), menyra.kripto(self.k, m, numri=n))
        self.assertNotEqual(menyra.kripto(self.k, m), menyra.kripto(self.k, m))
        with self.assertRaises(ValueError):
            menyra.kripto(self.k, m, numri=bytes(11))

    def test_vektoret_e_njohur(self):
        for v in json.loads(Path(__file__).with_name("vektoret_ae.json").read_text(encoding="utf-8")):
            p = menyra.kripto(bytes.fromhex(v["celesi"]), bytes.fromhex(v["mesazhi"]),
                              bytes.fromhex(v["te_dhena"]), bytes.fromhex(v["numri"]))
            self.assertEqual(p.hex(), v["paketa"])


if __name__ == "__main__":
    unittest.main()
