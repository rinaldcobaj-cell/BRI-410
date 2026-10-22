"""F3: lëvizja fikse (V-F) kundrejt lojës (V-L), dhe krahasimi me AES-256.

Përdorimi (nga rrënja e projektit): python -m matje.f3_matjet → matje/f3_rezultatet.json
Farat janë fikse; çelësat janë mostra matjeje.
"""

import itertools
import json
import math
import random
import time
from pathlib import Path

from matje import aes_studim
from shahu import shifra
from shahu.mds import perziej_shpejt
from shahu.sbox import SBOX_INV


def _int_nibla(n: list[int]) -> int:
    return sum(x << (4 * i) for i, x in enumerate(n))


def _int_bajte(b: list[int]) -> int:
    return sum(x << (8 * i) for i, x in enumerate(b))


def _balancuar_bri(s: shifra.BRI410, r: int, aktive: list[int], rng: random.Random) -> int:
    """Sa nga 64 nibblet kanë shumë XOR = 0 mbi grupin ku nibblet `aktive` marrin të gjitha vlerat."""
    baza = [rng.randrange(16) for _ in range(64)]
    shuma = 0
    for vlerat in itertools.product(range(16), repeat=len(aktive)):
        x = list(baza)
        for p, v in zip(aktive, vlerat):
            x[p] = v
        shuma ^= _int_nibla(s.kripto_nibla(x, r))
    return sum((shuma >> (4 * i)) & 15 == 0 for i in range(64))


def _balancuar_aes(rk: list[list[int]], r: int, rng: random.Random) -> int:
    baza = [rng.randrange(256) for _ in range(16)]
    shuma = 0
    for v in range(256):
        shuma ^= _int_bajte(aes_studim.kripto([v] + baza[1:], rk, r))
    return sum((shuma >> (8 * i)) & 255 == 0 for i in range(16))


def _permbledh(vlerat: list[int], plot: int) -> dict:
    return {"mes": round(sum(vlerat) / len(vlerat), 2), "min": min(vlerat),
            "plotesisht_te_balancuara": sum(v == plot for v in vlerat), "prova": len(vlerat)}


def integral() -> dict:
    """Dallues integral: grup tekstesh ku 1 nibble (bajt te AES) merr të gjitha vlerat.

    Te një funksion i rastësishëm, mesatarisht 64/16 = 4 nibble (16/256 = 0,06 bajte) dalin të balancuar.
    """
    rng = random.Random(40)
    rezultati = {"pritja_rastesore": {"shahu_nibla": 4.0, "aes_bajte": 0.06}}
    for varianti in shifra.VARIANTET:
        celesat = [shifra.BRI410(rng.getrandbits(410), 4, varianti) for _ in range(20)]
        rv = {}
        for r in (2, 3, 4):
            rv[f"1_nibble_{r}_raunde"] = _permbledh([_balancuar_bri(s, r, [0], rng) for s in celesat], 64)
        rv["2_nibla_4_raunde"] = _permbledh([_balancuar_bri(s, 4, [0, 1], rng) for s in celesat[:10]], 64)
        # 4 nibla që lëvizja e raundit 1 i çon në të njëjtin rresht (sulmuesi e di ose e merr me mend)
        te_mira = []
        for s in celesat[:3]:
            p1 = s._mbledh_dekriptim[0]
            aktive = [i for i in range(64) if p1[i] // 8 == 0][:4]
            te_mira.append(_balancuar_bri(s, 4, aktive, rng))
        rv["4_nibla_ne_nje_rresht_4_raunde"] = _permbledh(te_mira, 64)
        rezultati[varianti] = rv
    rv = {}
    celesat_aes = [aes_studim.orari(rng.randbytes(32)) for _ in range(20)]
    for r in (2, 3, 4):
        rv[f"1_bajt_{r}_raunde"] = _permbledh([_balancuar_aes(rk, r, rng) for rk in celesat_aes], 16)
    rezultati["AES"] = rv
    return rezultati


def _sulmi_bri(s: shifra.BRI410, rng: random.Random) -> dict:
    """Sulmi integral mbi 4 raunde: rikthen RK_4 (256 bit) duke parë vetëm tekstet e kriptuara."""
    kandidatet = [set(range(16)) for _ in range(64)]
    grupe = 0
    while any(len(k) > 1 for k in kandidatet) and grupe < 10:
        baza = [rng.randrange(16) for _ in range(64)]
        daljet = []
        for v in range(16):
            x = list(baza)
            x[0] = v
            daljet.append(perziej_shpejt(s.kripto_nibla(x, 4)))  # θ(c), θ është involutive
        grupe += 1
        for j in range(64):
            ruaj = set()
            for k in kandidatet[j]:
                shuma = 0
                for d in daljet:
                    shuma ^= SBOX_INV[d[j] ^ k]
                if shuma == 0:
                    ruaj.add(k)
            kandidatet[j] = ruaj
    sukses = all(len(k) == 1 for k in kandidatet)
    if sukses:
        rk4 = perziej_shpejt([next(iter(k)) for k in kandidatet])
        sukses = rk4 == s._rk[4]
    return {"sukses": sukses, "tekste": 16 * grupe}


def _sulmi_aes(rk: list[list[int]], rng: random.Random) -> dict:
    """Sulmi Square mbi AES-256 me 4 raunde: rikthen çelësin e raundit 4 (128 bit)."""
    kandidatet = [set(range(256)) for _ in range(16)]
    grupe = 0
    while any(len(k) > 1 for k in kandidatet) and grupe < 10:
        baza = [rng.randrange(256) for _ in range(16)]
        daljet = [aes_studim.kripto([v] + baza[1:], rk, 4) for v in range(256)]
        grupe += 1
        for j in range(16):
            ruaj = set()
            for k in kandidatet[j]:
                shuma = 0
                for d in daljet:
                    shuma ^= aes_studim.SBOX_INV[d[j] ^ k]
                if shuma == 0:
                    ruaj.add(k)
            kandidatet[j] = ruaj
    sukses = all(len(k) == 1 for k in kandidatet) and [next(iter(k)) for k in kandidatet] == rk[4]
    return {"sukses": sukses, "tekste": 256 * grupe}


def sulmi_4_raunde() -> dict:
    rng = random.Random(41)
    rezultati = {}
    for emri, ndertuesi, sulmi, bite in [
        ("VF", lambda: shifra.BRI410(rng.getrandbits(410), 4, "VF"), _sulmi_bri, 256),
        ("VL", lambda: shifra.BRI410(rng.getrandbits(410), 4, "VL"), _sulmi_bri, 256),
        ("AES", lambda: aes_studim.orari(rng.randbytes(32)), _sulmi_aes, 128),
    ]:
        t = time.time()
        prova = [sulmi(ndertuesi(), rng) for _ in range(10)]
        rezultati[emri] = {
            "sukses": sum(p["sukses"] for p in prova), "prova": len(prova),
            "tekste_mes": sum(p["tekste"] for p in prova) / len(prova),
            "bite_celesi_raundi_te_rikthyer": bite,
            "sekonda_per_sulm": round((time.time() - t) / len(prova), 2),
        }
    return rezultati


def informacioni_i_lojes() -> dict:
    """Sa bit i fsheh loja sulmuesit, sipas asaj që i intereson sulmit."""
    perm = list(shifra._VL.values())
    permutime = len({tuple(p) for p in perm})
    rreshti_destinacion = len({tuple(x // 8 for x in p) for p in perm})
    ndarjet = len({frozenset(frozenset(i for i in range(64) if p[i] // 8 == r) for r in range(8))
                   for p in perm})
    return {
        "variante": len(perm),
        "permutime_te_ndryshme": permutime, "bit_pozicioni_i_sakte": round(math.log2(permutime), 2),
        "harta_kuti_rresht": rreshti_destinacion, "bit_rreshti": round(math.log2(rreshti_destinacion), 2),
        "ndarje_ne_grupe_rreshtash": ndarjet, "bit_grupimi": round(math.log2(ndarjet), 2),
    }


def ortek_aes() -> dict:
    rng = random.Random(42)
    celesat = [aes_studim.orari(rng.randbytes(32)) for _ in range(100)]
    n = 2000
    rezultati = {}
    for r in (1, 2, 3, 4, 14):
        f = []
        for i in range(n):
            x = [rng.randrange(256) for _ in range(16)]
            b = rng.randrange(128)
            x2 = list(x)
            x2[b // 8] ^= 1 << (b % 8)
            d = _int_bajte(aes_studim.kripto(x, celesat[i % 100], r)) ^ _int_bajte(
                aes_studim.kripto(x2, celesat[i % 100], r))
            f.append(d.bit_count() / 128)
        rezultati[r] = {"mes": round(sum(f) / n, 4), "min": round(min(f), 4), "max": round(max(f), 4)}
    return rezultati


def shpejtesia() -> dict:
    rng = random.Random(43)
    n = 5000
    rezultati = {}
    rk = aes_studim.orari(rng.randbytes(32))
    mesazhet = [list(rng.randbytes(16)) for _ in range(n)]
    t = time.perf_counter()
    for m in mesazhet:
        aes_studim.kripto(m, rk)
    rezultati["AES256_14"] = round(16 * n / (time.perf_counter() - t))
    for varianti in shifra.VARIANTET:
        for raunde in (16, 32):
            s = shifra.BRI410(rng.getrandbits(410), raunde, varianti)
            mesazhet = [rng.randbytes(32) for _ in range(n)]
            t = time.perf_counter()
            for m in mesazhet:
                s.kripto(m)
            rezultati[f"BRI410_{varianti}{raunde}"] = round(32 * n / (time.perf_counter() - t))
    return {"bajte_ne_sekonde_python": rezultati}


def main() -> None:
    rezultatet = {}
    for emri, f in [("informacioni_i_lojes", informacioni_i_lojes), ("integral", integral),
                    ("sulmi_4_raunde", sulmi_4_raunde), ("ortek_aes", ortek_aes),
                    ("shpejtesia", shpejtesia)]:
        t = time.time()
        rezultatet[emri] = f()
        rezultatet[emri]["sekonda"] = round(time.time() - t, 1)
        print(emri, json.dumps(rezultatet[emri], ensure_ascii=False), flush=True)
    dalja = Path(__file__).with_name("f3_rezultatet.json")
    dalja.write_text(json.dumps(rezultatet, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
