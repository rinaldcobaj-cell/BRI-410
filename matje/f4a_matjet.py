"""F4-a: sulme me numra të zgjedhur (related-tweak) kundër BRI-410 zyrtar (V-N).

Sulmuesi nuk e përsërit dot numrin, por mund ta ZGJEDHË, p.sh. 4 096 numra që ndryshojnë vetëm në
3 nibble. A krijon kjo shkurtore? Që të matet marzhi, numri i hapave të përzierjes PAS futjes
së numrit ndryshohet 0..4 (zyrtari = 4). Plaintext-i mbahet fiks: ndryshon vetëm numri.

Përdorimi (nga rrënja e projektit): python -m matje.f4a_matjet → matje/f4a_rezultatet.json
"""

import itertools
import json
import random
import time
from pathlib import Path

from shahu import celesi as C
from shahu import shifra
from shahu.levizja import inversi
from shahu.mds import perziej_shpejt
from shahu.sbox import SBOX

GRUPET = {"1_nibble": [0], "3_nibla_ne_nje_rresht": [0, 1, 2]}


def _para_numrit(k: int) -> list[int]:
    g = C.ngarko(k)
    for j in range(4):
        g = C.hapi(g, C.KONSTANTJA_PERZIERJES + j)
    return g


def _gjendja(para: list[int], numri: int, hapat_pas: int) -> list[int]:
    g = list(para)
    for j in range(32):
        g[j] ^= (numri >> (4 * j)) & 0xF
    for j in range(4, 4 + hapat_pas):
        g = C.hapi(g, C.KONSTANTJA_PERZIERJES + j)
    return g


def _kripto(g: list[int], x: list[int], raunde: int) -> list[int]:
    """Kriptimi V-N nga një gjendje e dhënë orari (si BRI410.kripto_nibla)."""
    x = [a ^ b for a, b in zip(x, g[:64])]
    for i in range(1, raunde + 1):
        g = C.hapi(g, i)
        q = inversi(shifra._VL[C.levizja_nga_gjendja(g)])
        x = perziej_shpejt([SBOX[x[j]] for j in q])
        x = [a ^ b for a, b in zip(x, g[:64])]
    return x


def _int_nibla(n: list[int]) -> int:
    return sum(v << (4 * i) for i, v in enumerate(n))


def _kontrollo_perputhjen() -> None:
    rng = random.Random(80)
    for _ in range(5):
        k, numri, x = rng.getrandbits(410), rng.getrandbits(128), [rng.randrange(16) for _ in range(64)]
        pritur = shifra.BRI410(k, 6, "VN", numri.to_bytes(16, "little")).kripto_nibla(x)
        assert _kripto(_gjendja(_para_numrit(k), numri, 4), x, 6) == pritur


def _balancuar(k: int, aktive: list[int], hapat_pas: int, raunde: int, rng: random.Random) -> int:
    para = _para_numrit(k)
    x = [rng.randrange(16) for _ in range(64)]
    baza = rng.getrandbits(128)
    for p in aktive:
        baza &= ~(0xF << (4 * p))
    shuma = 0
    for vlerat in itertools.product(range(16), repeat=len(aktive)):
        numri = baza
        for p, v in zip(aktive, vlerat):
            numri |= v << (4 * p)
        shuma ^= _int_nibla(_kripto(_gjendja(para, numri, hapat_pas), x, raunde))
    return sum((shuma >> (4 * i)) & 15 == 0 for i in range(64))


def integral_me_numra() -> dict:
    """Shuma XOR e teksteve të kriptuara kur numri përshkon të gjitha vlerat në disa nibble.

    Rastësia jep ≈ 4 nga 64 nibble të balancuara. 64 do të thotë shkurtore.
    """
    rng = random.Random(81)
    rezultati = {"pritja_rastesore": 4}
    for hapat_pas in range(5):
        rh = {}
        for raunde in (1, 2, 3, 4):
            for emri, aktive in GRUPET.items():
                rh[f"{emri}_R{raunde}"] = [_balancuar(rng.getrandbits(410), aktive, hapat_pas, raunde, rng)
                                           for _ in range(2)]
        rezultati[f"hapa_pas_{hapat_pas}"] = rh
        print("integral", hapat_pas, rh, flush=True)
    rezultati["zyrtari_hapa_4_R32"] = {emri: [_balancuar(rng.getrandbits(410), aktive, 4, 32, rng)
                                              for _ in range(2)] for emri, aktive in GRUPET.items()}
    print("integral zyrtari", rezultati["zyrtari_hapa_4_R32"], flush=True)
    return rezultati


def ortek_i_numrit() -> dict:
    """Ndryshohet 1 bit i numrit: sa ndryshon RK_0 dhe teksti i kriptuar (plaintext-i fiks)."""
    rng = random.Random(82)
    n = 300
    rezultati = {}
    for hapat_pas in range(5):
        rk0, c1, c4 = [], [], []
        for _ in range(n):
            k, numri = rng.getrandbits(410), rng.getrandbits(128)
            numri2 = numri ^ (1 << rng.randrange(128))
            para = _para_numrit(k)
            g1, g2 = _gjendja(para, numri, hapat_pas), _gjendja(para, numri2, hapat_pas)
            x = [rng.randrange(16) for _ in range(64)]
            rk0.append((_int_nibla(g1[:64]) ^ _int_nibla(g2[:64])).bit_count() / 256)
            c1.append((_int_nibla(_kripto(g1, x, 1)) ^ _int_nibla(_kripto(g2, x, 1))).bit_count() / 256)
            c4.append((_int_nibla(_kripto(g1, x, 4)) ^ _int_nibla(_kripto(g2, x, 4))).bit_count() / 256)
        rezultati[f"hapa_pas_{hapat_pas}"] = {
            k: {"mes": round(sum(v) / n, 4), "min": round(min(v), 4)}
            for k, v in (("rk0", rk0), ("kriptimi_R1", c1), ("kriptimi_R4", c4))}
    return rezultati


def main() -> None:
    _kontrollo_perputhjen()
    rezultatet = {"perputhja_me_BRI410_VN": True}
    for emri, f in [("ortek_i_numrit", ortek_i_numrit), ("integral_me_numra", integral_me_numra)]:
        t = time.time()
        rezultatet[emri] = f()
        rezultatet[emri]["sekonda"] = round(time.time() - t, 1)
        print(emri, json.dumps(rezultatet[emri], ensure_ascii=False), flush=True)
    Path(__file__).with_name("f4a_rezultatet.json").write_text(
        json.dumps(rezultatet, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
