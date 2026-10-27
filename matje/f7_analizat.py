"""F7: pesë kategoritë e analizave për BRI-410/8 (versioni zyrtar, 16 raunde).

D diferenciale · L lineare · A algjebrike · K orari i çelësit · T tekst dhe numër i zgjedhur
Përdorimi (nga rrënja e projektit): python -m matje.f7_analizat → matje/f7_rezultatet.json

Analizat janë paraprake: tregojnë çfarë del me mjete të thjeshta. Nuk janë provë sigurie.
Algoritmi nuk ndryshohet. Farat janë fikse; çelësat janë mostra matjeje.
"""

import json
import math
import random
import time
from pathlib import Path

from matje import aes_studim
from matje.f4a8_matjet import _gjendja, _kripto, _para_numrit
from shahu import bri8, mds8, sbox8

S = sbox8.SBOX
P = bri8.PERM  # P[j] = 9·j mod 80 (orari)
MASKA_410 = (1 << 410) - 1


def _stat(v: list[float]) -> dict:
    return {"mes": round(sum(v) / len(v), 4), "min": round(min(v), 4), "max": round(max(v), 4), "n": len(v)}


def _pragu_chi2_99(df: int) -> float:
    return df * (1 - 2 / (9 * df) + 2.326 * math.sqrt(2 / (9 * df))) ** 3


# ------------------------------------------------------------------ D: diferenciale

def d_diferenciale() -> dict:
    vlerat = {}
    for a in range(1, 256):
        num = [0] * 256
        for x in range(256):
            num[S[x] ^ S[x ^ a]] += 1
        for v in num:
            vlerat[v] = vlerat.get(v, 0) + 1

    # D2: diferencë në 1 bajt → sa bajte dalin me diferencë zero (rastësia: 64/256 = 0,25)
    rng = random.Random(200)
    instancat = [bri8.BRI410_8(rng.getrandbits(410), 3, rng.randbytes(16)) for _ in range(20)]
    shkurtuar = {}
    for r in (1, 2, 3):
        v = []
        for t in range(300):
            s = instancat[t % 20]
            x = list(rng.randbytes(64))
            x2 = list(x)
            x2[rng.randrange(64)] ^= rng.randrange(1, 256)
            v.append(sum(a == b for a, b in zip(s.kripto_bajte(x, r), s.kripto_bajte(x2, r))))
        shkurtuar[f"R{r}"] = _stat(v)

    # D3: 1 raund: frekuenca e diferencës dalëse më të shpeshtë kundrejt tabelës DDT
    nje_raund = []
    for _ in range(3):
        s = bri8.BRI410_8(rng.getrandbits(410), 1, rng.randbytes(16))
        b, delta = rng.randrange(64), rng.randrange(1, 256)
        numero = {}
        n = 1 << 14
        for _ in range(n):
            x = list(rng.randbytes(64))
            x2 = list(x)
            x2[b] ^= delta
            d = bytes(p ^ q for p, q in zip(s.kripto_bajte(x), s.kripto_bajte(x2)))
            numero[d] = numero.get(d, 0) + 1
        rreshti = [0] * 256
        for x in range(256):
            rreshti[S[x] ^ S[x ^ delta]] += 1
        nje_raund.append({"frekuenca_max": round(max(numero.values()) / n, 4),
                          "pritur_nga_DDT": round(max(rreshti) / 256, 4),
                          "dalje_te_ndryshme": len(numero), "pritur_dalje": sum(1 for c in rreshti if c)})
    return {"DDT_shperndarja": dict(sorted(vlerat.items())), "log2_prob_max_sbox": math.log2(4 / 256),
            "diferenca_e_shkurtuar_zero_bajte": shkurtuar, "pritja_rastesore_zero_bajte": 0.25,
            "nje_raund_kundrejt_DDT": nje_raund}


# ------------------------------------------------------------------ L: lineare

def _wht(v: list[int]) -> list[int]:
    h, n = 1, len(v)
    while h < n:
        for i in range(0, n, 2 * h):
            for j in range(i, i + h):
                a, b = v[j], v[j + h]
                v[j], v[j + h] = a + b, a - b
        h *= 2
    return v


def _korr_max(hist: list[int], n: int) -> float:
    """max |korrelacion| mbi të gjitha maskat jo-zero (a te hyrja, b te dalja): 255 × 255 çifte."""
    w = _wht(list(hist))
    return max(abs(w[i]) for i in range(65536) if (i >> 8) and (i & 255)) / n


def l_lineare() -> dict:
    rng = random.Random(210)
    n = 1 << 18
    baza = [0] * 65536
    for _ in range(n):
        baza[rng.randrange(65536)] += 1
    rez = {"lineariteti_sbox": sbox8.matjet(S)["lineariteti"], "log2_korr_max_sbox": math.log2(32 / 256),
           "mostra": n, "baza_rastesore_korr_max": round(_korr_max(baza, n), 5)}
    s = bri8.BRI410_8(rng.getrandbits(410), 3, rng.randbytes(16))
    for r in (1, 2, 3):
        h0, h37 = [0] * 65536, [0] * 65536
        for _ in range(n):
            x = list(rng.randbytes(64))
            y = s.kripto_bajte(x, r)
            h0[x[0] * 256 + y[0]] += 1
            h37[x[0] * 256 + y[37]] += 1
        rez[f"R{r}"] = {"hyrja_bajti_0_dalja_bajti_0": round(_korr_max(h0, n), 5),
                        "hyrja_bajti_0_dalja_bajti_37": round(_korr_max(h37, n), 5)}
        print("L", r, rez[f"R{r}"], flush=True)
    return rez


# ------------------------------------------------------------------ A: algjebrike

def _ekuacione_kuadratike(s: list[int]) -> int:
    """Numri i ekuacioneve kuadratike linearisht të pavarura që lidhin hyrjen dhe daljen e S-box-it."""
    ndryshoret = [sum(((x >> b) & 1) << x for x in range(256)) for b in range(8)]
    ndryshoret += [sum(((s[x] >> b) & 1) << x for x in range(256)) for b in range(8)]
    monomet = [(1 << 256) - 1] + ndryshoret + [ndryshoret[i] & ndryshoret[j]
                                               for i in range(16) for j in range(i + 1, 16)]
    baza, rangu = {}, 0
    for v in monomet:
        while v:
            p = v.bit_length() - 1
            if p in baza:
                v ^= baza[p]
            else:
                baza[p] = v
                rangu += 1
                break
    return len(monomet) - rangu


def _struktura_lineare(s: list[int]) -> int:
    numri = 0
    for a in range(1, 256):
        derivatet = {s[x] ^ s[x ^ a] for x in range(256)}
        for b in range(1, 256):
            if len({bin(b & d).count("1") & 1 for d in derivatet}) == 1:
                numri += 1
    return numri


def a_algjebrike() -> dict:
    rng = random.Random(220)
    s = bri8.BRI410_8(rng.getrandbits(410), 4, rng.randbytes(16))
    kubet = {}
    rastet = [("8_bit_ne_nje_bajt", 8, True), ("8_bit_te_shperndare", 8, False),
              ("12_bit_te_shperndare", 12, False), ("16_bit_te_shperndare", 16, False)]
    for emri, d, ne_nje_bajt in rastet:
        for r in (2, 3, 4):
            v = []
            for _ in range(2):
                if ne_nje_bajt:
                    b = rng.randrange(64)
                    pozicionet = [8 * b + i for i in range(8)]
                else:
                    pozicionet = [8 * b + rng.randrange(8) for b in rng.sample(range(64), d)]
                baza = list(rng.randbytes(64))
                shuma = 0
                for k in range(1 << d):
                    x = list(baza)
                    for t, p in enumerate(pozicionet):
                        if k >> t & 1:
                            x[p >> 3] ^= 1 << (p & 7)
                    shuma ^= int.from_bytes(bytes(s.kripto_bajte(x, r)), "little")
                v.append(512 - shuma.bit_count())
            kubet[f"{emri}_R{r}"] = v
        print("A kubet", emri, {k: x for k, x in kubet.items() if k.startswith(emri)}, flush=True)
    sbox_ne_cipher = 64 * 16
    sbox_ne_orar = 80 * (8 + 16)
    return {
        "ekuacione_kuadratike_sbox_bri8": _ekuacione_kuadratike(S),
        "ekuacione_kuadratike_sbox_aes": _ekuacione_kuadratike(aes_studim.SBOX),
        "struktura_lineare_sbox_bri8": _struktura_lineare(S),
        "shkalla_sbox": 7, "kufiri_naiv_i_shkalles_pas_r_raundeve": {r: min(7 ** r, 511) for r in (1, 2, 3, 4)},
        "kubet_bite_zero_nga_512_rastesia_256": kubet,
        "sistemi_16_raunde": {"sbox_shifra": sbox_ne_cipher, "sbox_orari": sbox_ne_orar,
                              "ekuacione_kuadratike_perafersisht": 39 * (sbox_ne_cipher + sbox_ne_orar),
                              "ndryshore_perafersisht": 8 * (sbox_ne_cipher + sbox_ne_orar) + 410},
    }


# ------------------------------------------------------------------ K: orari i çelësit

def _rikthe_celesin(numri: bytes, i: int, rk_i: list[int], rk_i1: list[int], rk_i2: list[int]):
    """Nga RK_i, RK_{i+1}, RK_{i+2} dhe numri (publik) → çelësi kryesor. Kthen (çelësi, kandidatët)."""
    h = mds8.perziej_shpejt([S[v] for v in rk_i])  # daljet e rreshtave 0..7 të hapit i+1
    g1 = [None] * 80
    for j in range(64):
        g1[P[j]] = h[j]
    for p in range(64):
        if g1[p] is not None and g1[p] != rk_i1[p]:
            return None, 0
        g1[p] = rk_i1[p]
    rreshti8 = [p for p in range(64, 72) if g1[p] is None]
    rreshti9 = [p for p in range(72, 80) if g1[p] is None]

    def zgjidh(fillimi: int, te_panjohura: list[int]) -> list[list[int]]:
        zgjidhjet = []
        for vlerat in range(1 << (8 * len(te_panjohura))):
            rr = [g1[p] for p in range(fillimi, fillimi + 8)]
            for t, p in enumerate(te_panjohura):
                rr[p - fillimi] = (vlerat >> (8 * t)) & 255
            dalja = mds8.perziej_shpejt([S[v] for v in rr])
            if all(P[fillimi + jj] >= 64 or dalja[jj] == rk_i2[P[fillimi + jj]] for jj in range(8)):
                zgjidhjet.append(rr)
        return zgjidhjet

    z8, z9 = zgjidh(64, rreshti8), zgjidh(72, rreshti9)
    for a in z8:
        for b in z9:
            g = [v for v in g1[:64]] + a + b
            for t in range(i + 1, 0, -1):
                g = bri8.hapi_invers(g, t)
            for j in range(7, 3, -1):
                g = bri8.hapi_invers(g, bri8.KONSTANTJA_PERZIERJES + j)
            g = [v ^ (numri[j] if j < 16 else 0) for j, v in enumerate(g)]
            for j in range(3, -1, -1):
                g = bri8.hapi_invers(g, bri8.KONSTANTJA_PERZIERJES + j)
            v = int.from_bytes(bytes(g), "little")
            if v >> 410 == bri8._MBUSHJA:
                return v & MASKA_410, len(z8) * len(z9)
    return None, len(z8) * len(z9)


def k_orari() -> dict:
    rng = random.Random(230)
    numri, r_max = rng.randbytes(16), 16
    fr = [[] for _ in range(r_max + 1)]
    levizjet = []
    for _ in range(3):
        k = rng.getrandbits(410)
        baza = bri8.orari(k, r_max, numri)
        for b in range(410):
            o = bri8.orari(k ^ (1 << b), r_max, numri)
            for i in range(r_max + 1):
                fr[i].append(sum(bin(p ^ q).count("1") for p, q in zip(baza[i][0], o[i][0])) / 512)
            levizjet.append(sum(baza[i][1] != o[i][1] for i in range(1, r_max + 1)) / r_max)

    struktura = {"zero": 0, "njesha": MASKA_410, "vetem_biti_0": 1,
                 "0x55": int("55" * 52, 16) & MASKA_410, "rrites": int.from_bytes(bytes(range(52)), "little") & MASKA_410}
    celesat_me_strukture = {}
    for emri, k in struktura.items():
        para = bri8.para_numrit(k)
        rk = bri8.orari(k, r_max, bytes(16), para)
        rk_bitet = sum(sum(bin(v).count("1") for v in r) for r, _ in rk) / (512 * (r_max + 1))
        dalja = b"".join(bri8.BRI410_8(k, r_max, i.to_bytes(16, "little"), para).kripto(bytes(64))
                         for i in range(3000))
        n = 8 * len(dalja)
        bajte = [0] * 256
        for x in dalja:
            bajte[x] += 1
        pritur = len(dalja) / 256
        celesat_me_strukture[emri] = {
            "RK_fraksioni_i_njeshave": round(rk_bitet, 4),
            "dalja_monobit_z": round((int.from_bytes(dalja, "little").bit_count() - n / 2) / math.sqrt(n / 4), 3),
            "dalja_bajte_chi2": round(sum((c - pritur) ** 2 / pritur for c in bajte), 1)}

    # K4: rikthimi i çelësit kryesor nga tre çelësa raundesh të njëpasnjëshëm (numri publik)
    te_panjohura = sum(1 for p in range(64, 80) if (9 * p) % 80 >= 64)
    rikthimi = []
    for _ in range(3):
        k, n_ = rng.getrandbits(410), rng.randbytes(16)
        i = rng.randrange(1, r_max - 1)
        o = bri8.orari(k, r_max, n_)
        t = time.time()
        k2, kandidate = _rikthe_celesin(n_, i, o[i][0], o[i + 1][0], o[i + 2][0])
        rikthimi.append({"i": i, "sukses": k2 == k, "kandidate": kandidate, "sekonda": round(time.time() - t, 1)})
    return {
        "ortek_celesi_RK": {i: _stat(fr[i]) for i in (0, 1, 2, 4, 8, 16)},
        "levizjet_qe_ndryshojne_mes": round(sum(levizjet) / len(levizjet), 4),
        "celesa_me_strukture": celesat_me_strukture, "pragu_chi2_bajte_99": round(_pragu_chi2_99(255), 1),
        "rikthimi_nga_3_RK_te_njepasnjeshem": rikthimi,
        "bajte_te_panjohura_me_2_RK_te_njepasnjeshem": te_panjohura,
    }


# ------------------------------------------------------------------ T: tekst dhe numër i zgjedhur

def _statistikat(te_dhenat: bytes) -> dict:
    n = 8 * len(te_dhenat)
    v = int.from_bytes(te_dhenat, "big")
    njesha = v.bit_count()
    pi = njesha / n
    vargje = (v ^ (v >> 1)).bit_count() + 1
    bajte, nibla = [0] * 256, [0] * 16
    for x in te_dhenat:
        bajte[x] += 1
        nibla[x >> 4] += 1
        nibla[x & 15] += 1

    def chi2(numero):
        pritur = sum(numero) / len(numero)
        return round(sum((c - pritur) ** 2 / pritur for c in numero), 1)

    return {"monobit_z": round((njesha - n / 2) / math.sqrt(n / 4), 3),
            "vargjet_z": round((vargje - 2 * n * pi * (1 - pi)) / (2 * math.sqrt(2 * n) * pi * (1 - pi)), 3),
            "bajte_chi2": chi2(bajte), "nibla_chi2": chi2(nibla)}


def t_te_zgjedhura() -> dict:
    rng = random.Random(250)
    kombinuar = {}
    for hapat in (0, 4):
        for r in (1, 2, 3):
            v = []
            for _ in range(200):
                k = rng.getrandbits(410)
                para = _para_numrit(k)
                n1 = bytearray(rng.randbytes(16))
                n2 = bytearray(n1)
                b, dt = rng.randrange(16), rng.randrange(1, 256)
                n2[b] ^= dt
                x1 = [rng.randrange(256) for _ in range(64)]
                x2 = list(x1)
                x2[b] ^= dt  # përpjekja për të anuluar diferencën e RK_0 (funksionon vetëm pa përzierje)
                y1 = _kripto(_gjendja(para, bytes(n1), hapat), x1, r)
                y2 = _kripto(_gjendja(para, bytes(n2), hapat), x2, r)
                v.append(sum(p == q for p, q in zip(y1, y2)))
            kombinuar[f"hapa_{hapat}_R{r}"] = _stat(v)

    k = rng.getrandbits(410)
    para = bri8.para_numrit(k)
    n_blloqe = 10000
    numer_i_zgjedhur = b"".join(bri8.BRI410_8(k, 16, i.to_bytes(16, "little"), para).kripto(bytes(64))
                                for i in range(n_blloqe))
    s = bri8.BRI410_8(k, 16, rng.randbytes(16), para)
    mesazh_i_zgjedhur = b"".join(s.kripto(i.to_bytes(64, "little")) for i in range(n_blloqe))
    return {
        "diferenca_e_kombinuar_mesazh_dhe_numer_zero_bajte": kombinuar, "pritja_rastesore_zero_bajte": 0.25,
        "statistikat_16_raunde": {
            "blloqe": n_blloqe,
            "numri_numerues_mesazhi_zero": _statistikat(numer_i_zgjedhur),
            "mesazhi_numerues_numri_fiks": _statistikat(mesazh_i_zgjedhur),
            "pragjet_99": {"z": 2.576, "bajte_chi2": round(_pragu_chi2_99(255), 1),
                           "nibla_chi2": round(_pragu_chi2_99(15), 1)}},
    }


def main() -> None:
    rez = {}
    for emri, f in [("D_diferenciale", d_diferenciale), ("K_orari", k_orari), ("T_te_zgjedhura", t_te_zgjedhura),
                    ("A_algjebrike", a_algjebrike), ("L_lineare", l_lineare)]:
        t = time.time()
        rez[emri] = f()
        rez[emri]["sekonda"] = round(time.time() - t, 1)
        print(emri, json.dumps(rez[emri], ensure_ascii=False), flush=True)
        Path(__file__).with_name("f7_rezultatet.json").write_text(json.dumps(rez, ensure_ascii=False, indent=2),
                                                                  encoding="utf-8")


if __name__ == "__main__":
    main()
