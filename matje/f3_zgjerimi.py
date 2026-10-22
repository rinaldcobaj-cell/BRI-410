"""F3, zgjerimi: sa larg shkon dalluesi integral kur nibblet aktive bien në të njëjtin rresht pas π_1.

Përdorimi: python -m matje.f3_zgjerimi [pjesa]   pjesa ∈ {dalluesi, sulmi}
Shkruan matje/f3_zgjerimi_<pjesa>.json.
"""

import itertools
import json
import random
import sys
import time
from pathlib import Path

from shahu import shifra
from shahu.mds import perziej_shpejt
from shahu.sbox import SBOX_INV

# Kutitë (r, k) me r + k·dr ≡ 0 (mod 8): pas π_1 bien të gjitha në rreshtin 0.
GRUPI = {+1: [0, 57, 50, 43, 36, 29, 22, 15], -1: [0, 9, 18, 27, 36, 45, 54, 63]}


def _int_nibla(n: list[int]) -> int:
    return sum(x << (4 * i) for i, x in enumerate(n))


def _balancuar(s: shifra.BRI410, r: int, aktive: list[int], rng: random.Random) -> int:
    baza = [rng.randrange(16) for _ in range(64)]
    shuma = 0
    for vlerat in itertools.product(range(16), repeat=len(aktive)):
        x = list(baza)
        for p, v in zip(aktive, vlerat):
            x[p] = v
        shuma ^= _int_nibla(s.kripto_nibla(x, r))
    return sum((shuma >> (4 * i)) & 15 == 0 for i in range(64))


def _dr(s: shifra.BRI410) -> int:
    """dr i lëvizjes së raundit 1 (vetëm për matjen e dalluesit; sulmi nuk e përdor)."""
    return +1 if s.varianti == "VF" else s._levizjet[0][0][0]


def dalluesi() -> dict:
    rng = random.Random(50)
    rezultati = {}
    for varianti in shifra.VARIANTET:
        rv = {}
        for k, r, prova in [(2, 4, 5), (3, 4, 5), (4, 5, 3), (4, 6, 2)]:
            vlerat = []
            for _ in range(prova):
                s = shifra.BRI410(rng.getrandbits(410), 6, varianti)
                vlerat.append(_balancuar(s, r, GRUPI[_dr(s)][:k], rng))
            rv[f"{k}_nibla_{r}_raunde"] = {"te_balancuara": vlerat, "nga": 64}
            print(varianti, k, r, vlerat, flush=True)
        rezultati[varianti] = rv
    return rezultati


def _sulmi(s: shifra.BRI410, raunde: int, rng: random.Random) -> dict:
    """Rikthen RK_raunde duke përdorur dalluesin me 3 nibla të rreshtuara në (raunde − 1) = 4 raunde.

    Sulmuesi nuk e di dr-në e lojës te V-L: provon njëherë grupin dr = +1, pastaj dr = −1.
    """
    provat_dr = [+1] if s.varianti == "VF" else [+1, -1]
    tekste = 0
    for dr in provat_dr:
        kandidatet = [set(range(16)) for _ in range(64)]
        for _ in range(8):
            baza = [rng.randrange(16) for _ in range(64)]
            numero = [[0] * 16 for _ in range(64)]
            for vlerat in itertools.product(range(16), repeat=3):
                x = list(baza)
                for p, v in zip(GRUPI[dr][:3], vlerat):
                    x[p] = v
                for j, v in enumerate(perziej_shpejt(s.kripto_nibla(x, raunde))):
                    numero[j][v] ^= 1  # mjafton barazia e numërimit
            tekste += 1 << 12
            for j in range(64):
                tek = [v for v in range(16) if numero[j][v]]
                ruaj = set()
                for k in kandidatet[j]:
                    shuma = 0
                    for v in tek:
                        shuma ^= SBOX_INV[v ^ k]
                    if shuma == 0:
                        ruaj.add(k)
                kandidatet[j] = ruaj
            if any(not k for k in kandidatet) or all(len(k) == 1 for k in kandidatet):
                break
        if all(len(k) == 1 for k in kandidatet):
            rk = perziej_shpejt([next(iter(k)) for k in kandidatet])
            return {"sukses": rk == s._rk[raunde], "tekste": tekste, "dr_e_gjetur": dr}
    return {"sukses": False, "tekste": tekste, "dr_e_gjetur": None}


def sulmi() -> dict:
    rng = random.Random(51)
    raunde = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    rezultati = {"raunde": raunde}
    for varianti in shifra.VARIANTET:
        prova = []
        for _ in range(3):
            t = time.time()
            p = _sulmi(shifra.BRI410(rng.getrandbits(410), raunde, varianti), raunde, rng)
            p["sekonda"] = round(time.time() - t, 1)
            prova.append(p)
            print(varianti, p, flush=True)
        rezultati[varianti] = prova
    return rezultati


if __name__ == "__main__":
    pjesa = sys.argv[1] if len(sys.argv) > 1 else "dalluesi"
    rezultati = {"dalluesi": dalluesi, "sulmi": sulmi}[pjesa]()
    Path(__file__).with_name(f"f3_zgjerimi_{pjesa}.json").write_text(
        json.dumps(rezultati, ensure_ascii=False, indent=2), encoding="utf-8")
