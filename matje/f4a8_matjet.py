"""F4-a për BRI-410/8: sulme me numra të zgjedhur (related-tweak), si matje/f4a_matjet.py.

Numri i hapave të përzierjes PAS futjes së numrit ndryshohet 0..4 (zyrtari = 4), raundet 1..4,
dhe në fund testohet versioni i plotë me 16 raunde. Mesazhi dhe çelësi mbahen fiks.

Përdorimi (nga rrënja e projektit): python -m matje.f4a8_matjet → matje/f4a8_rezultatet.json
"""

import itertools
import json
import random
import time
from pathlib import Path

from shahu import bri8
from shahu.levizja import inversi
from shahu.mds8 import perziej_shpejt
from shahu.sbox8 import SBOX


def _para_numrit(k: int) -> list[int]:
    g = bri8.ngarko(k)
    for j in range(4):
        g = bri8.hapi(g, bri8.KONSTANTJA_PERZIERJES + j)
    return g


def _gjendja(para: list[int], numri: bytes, hapat_pas: int) -> list[int]:
    g = [v ^ (numri[j] if j < 16 else 0) for j, v in enumerate(para)]
    for j in range(4, 4 + hapat_pas):
        g = bri8.hapi(g, bri8.KONSTANTJA_PERZIERJES + j)
    return g


def _kripto(g: list[int], x: list[int], raunde: int) -> list[int]:
    x = [a ^ b for a, b in zip(x, g[:64])]
    for i in range(1, raunde + 1):
        g = bri8.hapi(g, i)
        q = inversi(bri8._LEVIZJET[bri8.levizja_nga_gjendja(g)])
        x = perziej_shpejt([SBOX[x[j]] for j in q])
        x = [a ^ b for a, b in zip(x, g[:64])]
    return x


def _int(b: list[int]) -> int:
    return int.from_bytes(bytes(b), "little")


def _kontrollo_perputhjen() -> None:
    rng = random.Random(110)
    for _ in range(5):
        k, numri, x = rng.getrandbits(410), rng.randbytes(16), [rng.randrange(256) for _ in range(64)]
        assert _kripto(_gjendja(_para_numrit(k), numri, 4), x, 6) == bri8.BRI410_8(k, 6, numri).kripto_bajte(x)


def _balancuar(k: int, aktive: list[int], hapat_pas: int, raunde: int, rng: random.Random) -> int:
    para = _para_numrit(k)
    x = [rng.randrange(256) for _ in range(64)]
    baza = bytearray(rng.randbytes(16))
    shuma = 0
    for vlerat in itertools.product(range(256), repeat=len(aktive)):
        for p, v in zip(aktive, vlerat):
            baza[p] = v
        shuma ^= _int(_kripto(_gjendja(para, bytes(baza), hapat_pas), x, raunde))
    return sum((shuma >> (8 * i)) & 255 == 0 for i in range(64))


def integral_me_numra() -> dict:
    """Rastësia jep ≈ 0,25 nga 64 bajte të balancuara. 64 do të thotë shkurtore."""
    rng = random.Random(111)
    rez = {"pritja_rastesore": 0.25}
    for hapat_pas in range(5):
        rh = {}
        for raunde in (1, 2, 3, 4):
            rh[f"1_bajt_R{raunde}"] = [_balancuar(rng.getrandbits(410), [0], hapat_pas, raunde, rng)
                                       for _ in range(2)]
        for raunde in (1, 2):
            rh[f"2_bajte_ne_nje_rresht_R{raunde}"] = [_balancuar(rng.getrandbits(410), [0, 1], hapat_pas,
                                                                 raunde, rng)]
        rez[f"hapa_pas_{hapat_pas}"] = rh
        print("integral", hapat_pas, rh, flush=True)
    rez["zyrtari_hapa_4_R16"] = {
        "1_bajt": [_balancuar(rng.getrandbits(410), [0], 4, 16, rng) for _ in range(3)],
        "2_bajte_ne_nje_rresht": [_balancuar(rng.getrandbits(410), [0, 1], 4, 16, rng)],
    }
    print("integral zyrtari", rez["zyrtari_hapa_4_R16"], flush=True)
    return rez


def ortek_i_numrit() -> dict:
    rng = random.Random(112)
    n = 300
    rez = {}
    for hapat_pas in range(5):
        rk0, c1, c4 = [], [], []
        for _ in range(n):
            k, numri = rng.getrandbits(410), rng.randbytes(16)
            numri2 = (int.from_bytes(numri, "little") ^ (1 << rng.randrange(128))).to_bytes(16, "little")
            para = _para_numrit(k)
            g1, g2 = _gjendja(para, numri, hapat_pas), _gjendja(para, numri2, hapat_pas)
            x = [rng.randrange(256) for _ in range(64)]
            rk0.append((_int(g1[:64]) ^ _int(g2[:64])).bit_count() / 512)
            c1.append((_int(_kripto(g1, x, 1)) ^ _int(_kripto(g2, x, 1))).bit_count() / 512)
            c4.append((_int(_kripto(g1, x, 4)) ^ _int(_kripto(g2, x, 4))).bit_count() / 512)
        rez[f"hapa_pas_{hapat_pas}"] = {k: {"mes": round(sum(v) / n, 4), "min": round(min(v), 4)}
                                        for k, v in (("rk0", rk0), ("kriptimi_R1", c1), ("kriptimi_R4", c4))}
    return rez


def main() -> None:
    _kontrollo_perputhjen()
    rez = {"perputhja_me_BRI410_8": True}
    for emri, f in [("ortek_i_numrit", ortek_i_numrit), ("integral_me_numra", integral_me_numra)]:
        t = time.time()
        rez[emri] = f()
        rez[emri]["sekonda"] = round(time.time() - t, 1)
        print(emri, json.dumps(rez[emri], ensure_ascii=False), flush=True)
    Path(__file__).with_name("f4a8_rezultatet.json").write_text(
        json.dumps(rez, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
