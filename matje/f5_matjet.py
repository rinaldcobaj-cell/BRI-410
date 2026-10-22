"""F5: BRI-410/8 (kuti 8-bitëshe, bllok 512 bit). A mjaftojnë 16 raunde?

Përdorimi (nga rrënja e projektit): python -m matje.f5_matjet → matje/f5_rezultatet.json
Sulmet integrale bëhen mbi "të njëjtin funksion" (numër i përsëritur = rasti i keqpërdorimit),
sepse me numër unik për çdo bllok ato bllokohen që në F3-bis.
"""

import itertools
import json
import math
import random
import time
from itertools import permutations
from pathlib import Path

from matje import aes_studim
from matje.f3_zgjerimi import GRUPI
from shahu import bri8, mds8, sbox8, shifra

RAUNDE_OBJEKTIV = 16


def _int(b: list[int]) -> int:
    return int.from_bytes(bytes(b), "little")


def m1_sbox() -> dict:
    rng = random.Random(100)
    baza = []
    for _ in range(10):
        p = list(range(256))
        rng.shuffle(p)
        baza.append(sbox8.matjet(p))
    return {
        "numeruesi": sbox8.NUMERUESI_SBOX,
        "bri8": sbox8.matjet(sbox8.SBOX),
        "aes_reference": sbox8.matjet(aes_studim.SBOX),
        "baza_rastesore_10": {
            "DU_min_max": [min(b["uniformiteti_diferencial"] for b in baza),
                           max(b["uniformiteti_diferencial"] for b in baza)],
            "jolineariteti_min_max": [min(b["jolineariteti"] for b in baza),
                                      max(b["jolineariteti"] for b in baza)],
        },
    }


def m2_mds() -> dict:
    gjithsej, singulare = mds8.nenmatricat_singulare(mds8.M)
    _, singulare_inv = mds8.nenmatricat_singulare(mds8.M_INV)
    simetri = sum(all(mds8.M[s[i]][s[j]] == mds8.M[i][j] for i in range(8) for j in range(8))
                  for s in permutations(range(8)))
    return {"y": mds8.Y, "nenmatrica": gjithsej, "singulare": singulare, "singulare_inversi": singulare_inv,
            "involutive": mds8.M == mds8.M_INV, "simetrite_e_kolonave": simetri,
            "elemente_te_ndryshem": len({x for r in mds8.M for x in r})}


def m3_korrektesia() -> dict:
    rng = random.Random(101)
    sakte = 0
    n = 2000
    for _ in range(n):
        s = bri8.BRI410_8(rng.getrandbits(410), RAUNDE_OBJEKTIV, rng.randbytes(16))
        m = rng.randbytes(64)
        sakte += s.dekripto(s.kripto(m)) == m
    return {"sakte": sakte, "gjithsej": n}


def m4_ortek() -> dict:
    rng = random.Random(102)
    n = 1000
    baza = [rng.getrandbits(512).bit_count() / 512 for _ in range(n)]
    rez = {"baza_rastesore": {"mes": round(sum(baza) / n, 4), "min": round(min(baza), 4)}}
    instancat = [bri8.BRI410_8(rng.getrandbits(410), RAUNDE_OBJEKTIV, rng.randbytes(16)) for _ in range(50)]
    for r in (1, 2, 3, 4, RAUNDE_OBJEKTIV):
        f = []
        for i in range(n):
            s = instancat[i % 50]
            x = [rng.randrange(256) for _ in range(64)]
            b = rng.randrange(512)
            x2 = list(x)
            x2[b // 8] ^= 1 << (b % 8)
            f.append((_int(s.kripto_bajte(x, r)) ^ _int(s.kripto_bajte(x2, r))).bit_count() / 512)
        rez[f"mesazhi_R{r}"] = {"mes": round(sum(f) / n, 4), "min": round(min(f), 4)}
    f = []
    for _ in range(300):
        k, m, numri = rng.getrandbits(410), rng.randbytes(64), rng.randbytes(16)
        numri2 = (int.from_bytes(numri, "little") ^ (1 << rng.randrange(128))).to_bytes(16, "little")
        c1 = bri8.BRI410_8(k, RAUNDE_OBJEKTIV, numri).kripto(m)
        c2 = bri8.BRI410_8(k, RAUNDE_OBJEKTIV, numri2).kripto(m)
        f.append((int.from_bytes(c1, "little") ^ int.from_bytes(c2, "little")).bit_count() / 512)
    rez[f"numri_R{RAUNDE_OBJEKTIV}"] = {"mes": round(sum(f) / len(f), 4), "min": round(min(f), 4)}
    return rez


def _balancuar(kripto, aktive: list[int], rng: random.Random) -> int:
    baza = [rng.randrange(256) for _ in range(64)]
    shuma = 0
    for vlerat in itertools.product(range(256), repeat=len(aktive)):
        x = list(baza)
        for p, v in zip(aktive, vlerat):
            x[p] = v
        shuma ^= _int(kripto(x))
    return sum((shuma >> (8 * i)) & 255 == 0 for i in range(64))


def m5_integral() -> dict:
    """Rastësia jep ≈ 64/256 = 0,25 bajte të balancuara. 64 do të thotë dallues."""
    rng = random.Random(103)
    rez = {"pritja_rastesore": 0.25}
    for r in (2, 3, 4):
        v = []
        for _ in range(10):
            s = bri8.BRI410_8(rng.getrandbits(410), r, rng.randbytes(16))
            v.append(_balancuar(s.kripto_bajte, [0], rng))
        rez[f"1_bajt_R{r}"] = v
        print("integral 1 bajt", r, v, flush=True)
    v = []
    for _ in range(2):
        s = bri8.BRI410_8(rng.getrandbits(410), 4, rng.randbytes(16))
        v.append(_balancuar(s.kripto_bajte, GRUPI[s._levizjet[0][0][0]][:2], rng))
        print("integral 2 bajte të rreshtuara R4", v, flush=True)
    rez["2_bajte_te_rreshtuara_R4"] = v

    def numer_unik(k):
        numeruesi = itertools.count(rng.getrandbits(64) << 64)
        return lambda x: bri8.BRI410_8(k, 3, next(numeruesi).to_bytes(16, "little")).kripto_bajte(x)

    rez["VN_unik_1_bajt_R3"] = [_balancuar(numer_unik(rng.getrandbits(410)), [0], rng) for _ in range(5)]
    return rez


def m6_sulmi_4_raunde() -> dict:
    """Dalluesi 3-raundësh me 1 bajt + deshifrim i pjesshëm i raundit 4 → rikthen RK_4 (512 bit)."""
    rng = random.Random(104)
    prova = []
    for _ in range(5):
        s = bri8.BRI410_8(rng.getrandbits(410), 4, rng.randbytes(16))
        kandidatet = [set(range(256)) for _ in range(64)]
        grupe = 0
        while any(len(k) > 1 for k in kandidatet) and grupe < 8:
            baza = [rng.randrange(256) for _ in range(64)]
            daljet = []
            for v in range(256):
                x = list(baza)
                x[0] = v
                daljet.append(mds8.perziej_shpejt_invers(s.kripto_bajte(x)))
            grupe += 1
            for j in range(64):
                ruaj = set()
                for k in kandidatet[j]:
                    shuma = 0
                    for d in daljet:
                        shuma ^= sbox8.SBOX_INV[d[j] ^ k]
                    if shuma == 0:
                        ruaj.add(k)
                kandidatet[j] = ruaj
        ok = all(len(k) == 1 for k in kandidatet)
        if ok:
            # c = θ(u) ⊕ RK  ⇒  θ⁻¹(c) = u ⊕ θ⁻¹(RK)
            ok = mds8.perziej_shpejt([next(iter(k)) for k in kandidatet]) == s._rk[4]
        prova.append({"sukses": ok, "tekste": 256 * grupe})
    return {"prova": prova, "sukses": sum(p["sukses"] for p in prova)}


def m7_kufiri_teorik(du: int) -> dict:
    log_p = math.log2(du / 256)

    def aktive(r):
        return 81 * (r // 4) + [0, 1, 9, 10][r % 4]

    tabela = {r: {"aktive_min": aktive(r), "log2_prob": round(aktive(r) * log_p, 1)} for r in (2, 4, 6, 8, 16)}
    r2 = next(r for r in range(1, 40) if aktive(r) * log_p < -512)
    return {"log2_prob_per_sbox": round(log_p, 2), "tabela": tabela, "R2_kunder_2^-512": r2}


def m8_shpejtesia() -> dict:
    rng = random.Random(105)
    n = 1500
    rez = {}
    k = rng.getrandbits(410)
    t = time.perf_counter()
    for i in range(n):
        bri8.BRI410_8(k, RAUNDE_OBJEKTIV, i.to_bytes(16, "little")).kripto(bytes(64))
    rez["BRI410_8_VN16"] = round(64 * n / (time.perf_counter() - t))
    for raunde in (16, 32):
        t = time.perf_counter()
        for i in range(n):
            shifra.BRI410(k, raunde, "VN", i.to_bytes(16, "little")).kripto(bytes(32))
        rez[f"BRI410_4bit_VN{raunde}"] = round(32 * n / (time.perf_counter() - t))
    return {"bajte_ne_sekonde_python": rez}


def main() -> None:
    rez = {}
    for emri, f in [("M1_sbox", m1_sbox), ("M2_mds", m2_mds), ("M3_korrektesia", m3_korrektesia),
                    ("M4_ortek", m4_ortek), ("M5_integral", m5_integral),
                    ("M6_sulmi_4_raunde", m6_sulmi_4_raunde), ("M8_shpejtesia", m8_shpejtesia)]:
        t = time.time()
        rez[emri] = f()
        rez[emri]["sekonda"] = round(time.time() - t, 1)
        print(emri, json.dumps(rez[emri], ensure_ascii=False), flush=True)
    rez["M7_kufiri_teorik"] = m7_kufiri_teorik(rez["M1_sbox"]["bri8"]["uniformiteti_diferencial"])
    print("M7_kufiri_teorik", json.dumps(rez["M7_kufiri_teorik"]), flush=True)
    Path(__file__).with_name("f5_rezultatet.json").write_text(
        json.dumps(rez, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
