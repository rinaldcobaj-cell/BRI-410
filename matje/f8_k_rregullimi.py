"""F8: a e rregullon v1.1 (feed-forward + 8 hapa pas numrit) gjetjen K të F7?

Gjetja K (v1.0): 3 çelësa raundesh të njëpasnjëshëm të NJË blloku + numri publik → çelësi kryesor në 0,1 s.
Pyetja: te v1.1, çfarë mëson sulmuesi nga i njëjti informacion? Dhe a ruhen vetitë e tjera?

Përdorimi (nga rrënja e projektit): python -m matje.f8_k_rregullimi → matje/f8_rezultatet.json
"""

import itertools
import json
import math
import random
import time
from pathlib import Path

from matje.f7_analizat import _statistikat
from shahu import bri8, mds8, menyra, sbox8

S = sbox8.SBOX
P = bri8.PERM


def _rindertimi_i_G(i: int, rk_i: list[int], rk_i1: list[int], rk_i2: list[int]) -> list[int] | None:
    """Pjesa e parë e sulmit të F7: nga RK_i, RK_{i+1}, RK_{i+2} → gjendja e plotë G_{i+1} → G_0 e këtij blloku."""
    h = mds8.perziej_shpejt([S[v] for v in rk_i])
    g1 = [None] * 80
    for j in range(64):
        g1[P[j]] = h[j]
    for p in range(64):
        g1[p] = rk_i1[p]

    def zgjidh(fillimi: int) -> list[list[int]]:
        te_panjohura = [p for p in range(fillimi, fillimi + 8) if g1[p] is None]
        zgjidhjet = []
        for vlerat in range(1 << (8 * len(te_panjohura))):
            rr = [g1[p] for p in range(fillimi, fillimi + 8)]
            for t, p in enumerate(te_panjohura):
                rr[p - fillimi] = (vlerat >> (8 * t)) & 255
            dalja = mds8.perziej_shpejt([S[v] for v in rr])
            if all(P[fillimi + jj] >= 64 or dalja[jj] == rk_i2[P[fillimi + jj]] for jj in range(8)):
                zgjidhjet.append(rr)
        return zgjidhjet

    z8, z9 = zgjidh(64), zgjidh(72)
    if len(z8) != 1 or len(z9) != 1:
        return None
    g = list(g1[:64]) + z8[0] + z9[0]
    for t in range(i + 1, 0, -1):
        g = bri8.hapi_invers(g, t)
    return g  # G_0


def _kthimi_si_te_v10(g0: list[int], numri: bytes) -> int | None:
    """Hapi i dytë i sulmit të F7: G_0 → mbrapsht 4 hapa → ⊕ numri → mbrapsht 4 hapa → çelësi (kontroll me mbushjen)."""
    g = list(g0)
    for j in range(7, 3, -1):
        g = bri8.hapi_invers(g, bri8.KONSTANTJA_PERZIERJES + j)
    g = [v ^ (numri[j] if j < 16 else 0) for j, v in enumerate(g)]
    for j in range(3, -1, -1):
        g = bri8.hapi_invers(g, bri8.KONSTANTJA_PERZIERJES + j)
    v = int.from_bytes(bytes(g), "little")
    return v & ((1 << 410) - 1) if v >> 410 == bri8._MBUSHJA else None


def sulmi_k() -> dict:
    rng = random.Random(300)
    rez = {}
    for versioni in bri8.VERSIONET:
        prova = []
        for _ in range(3):
            k, numri = rng.getrandbits(410), rng.randbytes(16)
            i = rng.randrange(1, 14)
            o = bri8.orari(k, 16, numri, versioni=versioni)
            g0 = _rindertimi_i_G(i, o[i][0], o[i + 1][0], o[i + 2][0])
            g0_e_vertete = bri8.ngarko_me_numer(k, numri, versioni=versioni)
            k2 = _kthimi_si_te_v10(g0, numri) if g0 is not None else None
            # A i ndihmon G_0 i këtij blloku sulmuesit për një bllok tjetër?
            # Te v1.0, kthimi deri te K* jep çelësat e çdo numri. Te v1.1 provohet e njëjta rrugë.
            numri2 = rng.randbytes(16)
            rk0_tjeter_e_parashikuar = None
            if k2 is not None:
                rk0_tjeter_e_parashikuar = bri8.orari(k2, 1, numri2, versioni=versioni)[0][0]
            prova.append({
                "G0_i_bllokut_u_rindertua": g0 == g0_e_vertete,
                "celesi_kryesor_u_gjet": k2 == k,
                "bllok_tjeter_u_parashikua": rk0_tjeter_e_parashikuar == bri8.orari(k, 1, numri2,
                                                                                    versioni=versioni)[0][0],
            })
        rez[versioni] = prova
        print("K", versioni, prova, flush=True)
    return rez


def ortek() -> dict:
    rng = random.Random(301)
    numri = rng.randbytes(16)
    celes_rk = {i: [] for i in (0, 1, 8, 16)}
    numer_rk0, numer_c = [], []
    for _ in range(2):
        k = rng.getrandbits(410)
        baza = bri8.orari(k, 16, numri)
        for b in range(410):
            o = bri8.orari(k ^ (1 << b), 16, numri)
            for i in celes_rk:
                celes_rk[i].append(sum(bin(p ^ q).count("1") for p, q in zip(baza[i][0], o[i][0])) / 512)
    for _ in range(400):
        k, n1, m = rng.getrandbits(410), rng.randbytes(16), rng.randbytes(64)
        n2 = (int.from_bytes(n1, "little") ^ (1 << rng.randrange(128))).to_bytes(16, "little")
        numer_rk0.append(sum(bin(p ^ q).count("1") for p, q in
                             zip(bri8.orari(k, 1, n1)[0][0], bri8.orari(k, 1, n2)[0][0])) / 512)
        c1, c2 = bri8.BRI410_8(k, 16, n1).kripto(m), bri8.BRI410_8(k, 16, n2).kripto(m)
        numer_c.append((int.from_bytes(c1, "little") ^ int.from_bytes(c2, "little")).bit_count() / 512)

    def st(v):
        return {"mes": round(sum(v) / len(v), 4), "min": round(min(v), 4), "max": round(max(v), 4)}

    return {"1_bit_celesi": {f"RK_{i}": st(v) for i, v in celes_rk.items()},
            "1_bit_numri": {"RK_0": st(numer_rk0), "teksti_16_raunde": st(numer_c)}}


def _balancuar_numrat(k: int, aktive: list[int], raunde: int, rng: random.Random) -> int:
    para = bri8.para_numrit(k)
    x = rng.randbytes(64)
    baza = bytearray(rng.randbytes(16))
    shuma = 0
    for vlerat in itertools.product(range(256), repeat=len(aktive)):
        for p, v in zip(aktive, vlerat):
            baza[p] = v
        shuma ^= int.from_bytes(bri8.BRI410_8(k, raunde, bytes(baza), para).kripto(x), "little")
    return sum((shuma >> (8 * i)) & 255 == 0 for i in range(64))


def numra_te_zgjedhur() -> dict:
    """Shuma XOR e teksteve kur numri përshkon të gjitha vlerat në 1–2 bajte (rastësia ≈ 0,25 nga 64)."""
    rng = random.Random(302)
    rez = {}
    for raunde in (1, 2, 16):
        rez[f"1_bajt_R{raunde}"] = [_balancuar_numrat(rng.getrandbits(410), [0], raunde, rng) for _ in range(3)]
    rez["2_bajte_ne_nje_rresht_R1"] = [_balancuar_numrat(rng.getrandbits(410), [0, 1], 1, rng)]
    print("T integral", rez, flush=True)

    kombinuar = {}
    for raunde in (1, 2, 3):
        v = []
        for _ in range(200):
            k = rng.getrandbits(410)
            para = bri8.para_numrit(k)
            n1 = bytearray(rng.randbytes(16))
            n2 = bytearray(n1)
            b, dt = rng.randrange(16), rng.randrange(1, 256)
            n2[b] ^= dt
            x1 = list(rng.randbytes(64))
            x2 = list(x1)
            x2[b] ^= dt
            y1 = bri8.BRI410_8(k, raunde, bytes(n1), para).kripto_bajte(x1)
            y2 = bri8.BRI410_8(k, raunde, bytes(n2), para).kripto_bajte(x2)
            v.append(sum(p == q for p, q in zip(y1, y2)))
        kombinuar[f"R{raunde}"] = round(sum(v) / len(v), 3)
    rez["diferenca_e_kombinuar_mes_zero_bajte"] = kombinuar

    k = rng.getrandbits(410)
    para = bri8.para_numrit(k)
    rez["statistikat_16_raunde_numri_numerues"] = _statistikat(
        b"".join(bri8.BRI410_8(k, 16, i.to_bytes(16, "little"), para).kripto(bytes(64)) for i in range(10000)))
    return rez


def shpejtesia() -> dict:
    rng = random.Random(303)
    k = rng.getrandbits(410)
    para = bri8.para_numrit(k)
    rez = {}
    for versioni in bri8.VERSIONET:
        t = time.perf_counter()
        for i in range(1500):
            bri8.BRI410_8(k, 16, i.to_bytes(16, "little"), para, versioni).kripto(bytes(64))
        rez[f"blloqe_ne_sekonde_{versioni}"] = round(1500 / (time.perf_counter() - t))
    celesi = bri8.gjenero_celes()
    m = rng.randbytes(65536)
    t = time.perf_counter()
    menyra.kripto(celesi, m)
    rez["AE_64KB_bajte_ne_sekonde_v11"] = round(65536 / (time.perf_counter() - t))
    return rez


def main() -> None:
    rez = {"kufiri_i_orarit_8_hapa_pas_numrit": "≥ 162 S-box aktive (2 × 81, nga kufiri i provuar 4-hapësh i F4-b)"}
    for emri, f in [("K_sulmi_i_F7", sulmi_k), ("ortek", ortek), ("numra_te_zgjedhur", numra_te_zgjedhur),
                    ("shpejtesia", shpejtesia)]:
        t = time.time()
        rez[emri] = {"rezultati": f(), "sekonda": round(time.time() - t, 1)}
        print(emri, json.dumps(rez[emri], ensure_ascii=False), flush=True)
    Path(__file__).with_name("f8_rezultatet.json").write_text(json.dumps(rez, ensure_ascii=False, indent=2),
                                                              encoding="utf-8")


if __name__ == "__main__":
    main()
