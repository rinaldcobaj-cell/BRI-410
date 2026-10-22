"""Testet e F2: shifra e plotë. Përdorimi: python -m unittest discover -s teste -t ."""

import json
import random
import unittest
from pathlib import Path

from shahu import celesi, levizja, mds, shifra
from shahu.sbox import SBOX

KONFIGURIMET = [(v, r) for v in shifra.VARIANTET for r in (16, 32)]
VEKTORET = Path(__file__).with_name("vektoret_f2.json")


def _orari_reference(k: int, raunde: int):
    """Orari i çelësit direkt nga specifikimi (F0 §6), me komponentët e ngadaltë."""
    g = celesi.ngarko(k)
    rezultati = [(g[:64], None)]
    for i in range(1, raunde + 1):
        h = mds.perziej_rreshtat([SBOX[x] for x in g], mds.M)
        g = [0] * celesi.NIBLA
        for j, x in enumerate(h):
            g[(9 * j) % celesi.NIBLA] = x
        g[100] ^= i & 0xF
        g[101] ^= (i >> 4) & 0xF
        n0, n1 = g[64], g[65]
        rezultati.append((g[:64], (levizja.DREJTIMET[n0 & 3], (n0 >> 2) | ((n1 & 1) << 2))))
    return rezultati


def _kripto_reference(k: int, x: list[int], raunde: int, varianti: str) -> list[int]:
    """Kriptimi direkt nga specifikimi (F0 §5)."""
    orari = _orari_reference(k, raunde)
    x = [a ^ b for a, b in zip(x, orari[0][0])]
    for i in range(1, raunde + 1):
        rk, (d, beta) = orari[i]
        p = levizja.levizja_kalit() if varianti == "VF" else levizja.levizja_kalit(d, beta=beta)
        x = mds.perziej_rreshtat(levizja.zbato(p, [SBOX[v] for v in x]), mds.M)
        x = [a ^ b for a, b in zip(x, rk)]
    return x


class TestShifra(unittest.TestCase):
    def test_perzierja_e_shpejte_eshte_e_njejte(self):
        rng = random.Random(20)
        for _ in range(500):
            g = [rng.randrange(16) for _ in range(104)]
            self.assertEqual(mds.perziej_shpejt(g), mds.perziej_rreshtat(g, mds.M))

    def test_orari_eshte_si_referenca(self):
        rng = random.Random(21)
        for _ in range(20):
            k = rng.getrandbits(410)
            self.assertEqual(celesi.orari(k, 32), _orari_reference(k, 32))

    def test_kriptimi_eshte_si_referenca(self):
        rng = random.Random(22)
        for varianti, raunde in KONFIGURIMET:
            for _ in range(20):
                k = rng.getrandbits(410)
                x = [rng.randrange(16) for _ in range(64)]
                self.assertEqual(shifra.BRI410(k, raunde, varianti).kripto_nibla(x),
                                 _kripto_reference(k, x, raunde, varianti))

    def test_dekriptimi_kthen_mesazhin(self):
        rng = random.Random(23)
        for varianti, raunde in KONFIGURIMET:
            for _ in range(25):
                s = shifra.BRI410(rng.getrandbits(410), raunde, varianti)
                for _ in range(8):
                    m = rng.randbytes(32)
                    self.assertEqual(s.dekripto(s.kripto(m)), m)

    def test_celes_i_gabuar_nuk_dekripton(self):
        rng = random.Random(24)
        k = rng.getrandbits(410)
        m = rng.randbytes(32)
        c = shifra.BRI410(k).kripto(m)
        self.assertNotEqual(shifra.BRI410(k ^ 1).dekripto(c), m)

    def test_celesi_si_bajte(self):
        b = shifra.gjenero_celes()
        self.assertEqual(len(b), 52)
        self.assertLess(shifra.celesi_nga_bajtet(b), 1 << 410)
        with self.assertRaises(ValueError):
            shifra.celesi_nga_bajtet(b[:51] + bytes([0x04]))
        with self.assertRaises(ValueError):
            shifra.celesi_nga_bajtet(b[:51])
        self.assertEqual(shifra.BRI410(b).kripto(bytes(32)),
                         shifra.BRI410(int.from_bytes(b, "little")).kripto(bytes(32)))

    def test_bajtet_dhe_niblat(self):
        b = bytes(range(32))
        self.assertEqual(shifra.nibla_ne_bajte(shifra.bajte_ne_nibla(b)), b)
        self.assertEqual(shifra.bajte_ne_nibla(bytes([0xAB]) + bytes(31))[:2], [0xB, 0xA])

    def test_vektoret_e_njohur(self):
        """Regresion: rezultatet e ngrira në vektoret_f2.json nuk duhet të ndryshojnë pa qëllim."""
        for v in json.loads(VEKTORET.read_text(encoding="utf-8")):
            s = shifra.BRI410(bytes.fromhex(v["celesi"]), v["raunde"], v["varianti"])
            self.assertEqual(s.kripto(bytes.fromhex(v["mesazhi"])).hex(), v["kriptuar"])


def _hapi_reference(g: list[int], i: int) -> list[int]:
    h = mds.perziej_rreshtat([SBOX[x] for x in g], mds.M)
    r = [0] * celesi.NIBLA
    for j, x in enumerate(h):
        r[(9 * j) % celesi.NIBLA] = x
    r[100] ^= i & 0xF
    r[101] ^= (i >> 4) & 0xF
    return r


class TestLojaSipasBllokut(unittest.TestCase):
    """V-N (F3-bis): loja dhe çelësat e raundeve nga (çelësi, numri unik)."""

    def test_ngarkimi_eshte_si_referenca(self):
        rng = random.Random(60)
        for _ in range(10):
            k, numri = rng.getrandbits(410), rng.randbytes(16)
            g = celesi.ngarko(k)
            for j in range(4):
                g = _hapi_reference(g, 0xF0 + j)
            for j in range(32):
                g[j] ^= (numri[j // 2] >> (4 * (j % 2))) & 0xF
            for j in range(4, 8):
                g = _hapi_reference(g, 0xF0 + j)
            self.assertEqual(celesi.ngarko_me_numer(k, numri), g)

    def test_dekriptimi_kthen_mesazhin(self):
        rng = random.Random(61)
        for raunde in (16, 32):
            for _ in range(20):
                k, numri, m = rng.getrandbits(410), rng.randbytes(16), rng.randbytes(32)
                s = shifra.BRI410(k, raunde, "VN", numri)
                self.assertEqual(shifra.BRI410(k, raunde, "VN", numri).dekripto(s.kripto(m)), m)

    def test_numri_ndryshon_lojen_dhe_kriptimin(self):
        rng = random.Random(62)
        k, m = rng.getrandbits(410), rng.randbytes(32)
        a = shifra.BRI410(k, 16, "VN", bytes(16))
        b = shifra.BRI410(k, 16, "VN", bytes(15) + b"\x01")
        self.assertNotEqual(a.kripto(m), b.kripto(m))
        self.assertNotEqual(a._rk[0], b._rk[0])
        self.assertNotEqual(a.kripto(m), shifra.BRI410(k, 16, "VL").kripto(m))

    def test_numri_i_detyrueshem_vetem_te_vn(self):
        with self.assertRaises(ValueError):
            shifra.BRI410(1, 16, "VN")
        with self.assertRaises(ValueError):
            shifra.BRI410(1, 16, "VL", bytes(16))
        with self.assertRaises(ValueError):
            shifra.BRI410(1, 16, "VN", bytes(15))


if __name__ == "__main__":
    unittest.main()
