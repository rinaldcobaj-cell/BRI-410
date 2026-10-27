"""Testet e BRI-410/8 (F5): kuti 8-bitëshe, bllok 512 bit."""

import json
import random
import unittest
from pathlib import Path

from shahu import bri8, gf256, levizja, mds8, sbox8


def _kripto_reference(k: int, numri: bytes, x: list[int], raunde: int, versioni: str = "1.1") -> list[int]:
    """Direkt nga përshkrimi i modulit, me komponentët e ngadaltë."""
    g = bri8.ngarko(k)

    def hapi(g, i):
        h = mds8.perziej_rreshtat([sbox8.SBOX[v] for v in g])
        r = [0] * 80
        for j, v in enumerate(h):
            r[(bri8.P_HAPI * j) % 80] = v
        r[79] ^= i
        return r

    for j in range(4):
        g = hapi(g, 0xF0 + j)
    g = [v ^ (numri[j] if j < 16 else 0) for j, v in enumerate(g)]
    if versioni == "1.0":
        for j in range(4, 8):
            g = hapi(g, 0xF0 + j)
    else:
        hyrja = list(g)
        for j in range(4, 12):
            g = hapi(g, 0xF0 + j)
        g = [a ^ b for a, b in zip(g, hyrja)]  # feed-forward
    x = [a ^ b for a, b in zip(x, g[:64])]
    for i in range(1, raunde + 1):
        g = hapi(g, i)
        p = levizja.levizja_kalit(levizja.DREJTIMET[g[64] & 3], beta=(g[64] >> 2) & 7)
        x = mds8.perziej_rreshtat(levizja.zbato(p, [sbox8.SBOX[v] for v in x]))
        x = [a ^ b for a, b in zip(x, g[:64])]
    return x


class TestBRI8(unittest.TestCase):
    def test_gf256(self):
        for a in range(1, 256):
            self.assertEqual(gf256.shumezo(a, gf256.inversi(a)), 1)

    def test_sbox_riprodhohet_dhe_kthehet(self):
        self.assertEqual(sbox8.kerko_sbox(), (sbox8.NUMERUESI_SBOX, sbox8.SBOX))
        self.assertEqual(sorted(sbox8.SBOX), list(range(256)))
        self.assertTrue(all(sbox8.SBOX_INV[sbox8.SBOX[x]] == x for x in range(256)))

    def test_mds_inversi_dhe_versioni_i_shpejte(self):
        rng = random.Random(90)
        for _ in range(100):
            g = [rng.randrange(256) for _ in range(80)]
            self.assertEqual(mds8.perziej_shpejt(g), mds8.perziej_rreshtat(g))
            self.assertEqual(mds8.perziej_shpejt_invers(mds8.perziej_shpejt(g)), g)

    def test_hapi_i_orarit_kthehet(self):
        rng = random.Random(91)
        for i in range(1, 100):
            g = [rng.randrange(256) for _ in range(80)]
            self.assertEqual(bri8.hapi_invers(bri8.hapi(g, i), i), g)

    def test_kriptimi_si_referenca(self):
        rng = random.Random(92)
        for versioni in bri8.VERSIONET:
            for raunde in (1, 4, 16):
                for _ in range(5):
                    k, numri = rng.getrandbits(410), rng.randbytes(16)
                    x = [rng.randrange(256) for _ in range(64)]
                    self.assertEqual(bri8.BRI410_8(k, raunde, numri, versioni=versioni).kripto_bajte(x),
                                     _kripto_reference(k, numri, x, raunde, versioni))

    def test_versionet_ndryshojne_vetem_te_orari(self):
        rng = random.Random(96)
        k, numri, m = rng.getrandbits(410), rng.randbytes(16), rng.randbytes(64)
        self.assertEqual(bri8.VERSIONI, "1.1")
        self.assertNotEqual(bri8.BRI410_8(k, 16, numri, versioni="1.0").kripto(m), bri8.BRI410_8(k, 16, numri).kripto(m))
        s = bri8.BRI410_8(k, 16, numri, versioni="1.0")
        self.assertEqual(s.dekripto(s.kripto(m)), m)

    def test_dekriptimi_kthen_mesazhin(self):
        rng = random.Random(93)
        for _ in range(50):
            k, numri, m = rng.getrandbits(410), rng.randbytes(16), rng.randbytes(64)
            s = bri8.BRI410_8(k, 16, numri)
            self.assertEqual(s.dekripto(s.kripto(m)), m)

    def test_vektoret_e_njohur(self):
        """Regresion: vektoret_f5.json (v1.0, të ngrirë në F5) dhe vektoret_f5_v11.json (v1.1) nuk ndryshojnë pa qëllim."""
        for skedari, versioni in (("vektoret_f5.json", "1.0"), ("vektoret_f5_v11.json", "1.1")):
            vektoret = json.loads(Path(__file__).with_name(skedari).read_text(encoding="utf-8"))
            self.assertEqual(len(vektoret), 12)
            for v in vektoret:
                s = bri8.BRI410_8(bytes.fromhex(v["celesi"]), v["raunde"], bytes.fromhex(v["numri"]),
                                  versioni=versioni)
                self.assertEqual(s.kripto(bytes.fromhex(v["mesazhi"])).hex(), v["kriptuar"])

    def test_para_numrit_jep_te_njejtin_rezultat(self):
        rng = random.Random(95)
        k, m = rng.getrandbits(410), rng.randbytes(64)
        para = bri8.para_numrit(k)
        for _ in range(5):
            numri = rng.randbytes(16)
            self.assertEqual(bri8.BRI410_8(k, 16, numri, para).kripto(m), bri8.BRI410_8(k, 16, numri).kripto(m))

    def test_funksionet_zyrtare(self):
        rng = random.Random(94)
        k, numri, m = bri8.gjenero_celes(), rng.randbytes(16), rng.randbytes(64)
        c = bri8.kripto_bllok(k, numri, m)
        self.assertEqual(bri8.RAUNDE_ZYRTARE, 16)
        self.assertEqual(c, bri8.BRI410_8(k, 16, numri).kripto(m))
        self.assertEqual(bri8.dekripto_bllok(k, numri, c), m)

    def test_celesi_si_bajte(self):
        b = bri8.gjenero_celes()
        self.assertEqual(bri8.BRI410_8(b, 16, bytes(16)).kripto(bytes(64)),
                         bri8.BRI410_8(int.from_bytes(b, "little"), 16, bytes(16)).kripto(bytes(64)))


if __name__ == "__main__":
    unittest.main()
