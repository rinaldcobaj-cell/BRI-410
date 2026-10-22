"""F1: matja e komponentëve të BRI-410. Përdorimi (nga rrënja e projektit): python -m matje.f1_matjet

Shkruan matje/f1_rezultatet.json. Farat e rastësisë janë fikse që matjet të riprodhohen;
çelësat këtu janë vetëm mostra matjeje, jo çelësa për përdorim.
"""

import json
import math
import random
import time
from itertools import permutations
from pathlib import Path

from shahu import celesi, levizja, mds, sbox

PRESENT = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
PLOT = (1 << 64) - 1


def m1_sbox() -> dict:
    numeruesi, s = sbox.kerko_sbox()
    assert (numeruesi, s) == (sbox.NUMERUESI_SBOX, sbox.SBOX)

    def zgjeruar(p):
        m = sbox.matjet(p)
        ddt = sbox.tabela_diferenciale(p)
        w = sbox.tabela_walsh(p)
        m["hyrje_ddt_me_4"] = sum(ddt[a][b] == 4 for a in range(1, 16) for b in range(16))
        m["hyrje_walsh_me_8"] = sum(abs(w[a][b]) == 8 for a in range(16) for b in range(1, 16))
        return m

    rng = random.Random(2026)
    n = 3000
    du_lin = te_plota = 0
    for _ in range(n):
        p = list(range(16))
        rng.shuffle(p)
        m = sbox.matjet(p)
        du_lin += m["uniformiteti_diferencial"] == 4 and m["lineariteti"] == 8
        te_plota += sbox.eshte_optimal(m)
    return {
        "sbox": [f"{x:X}" for x in s],
        "numeruesi": numeruesi,
        "shahu": zgjeruar(s),
        "present_reference": zgjeruar(PRESENT),
        "baza_rastesore": {"mostra": n, "du4_lin8": du_lin, "te_gjitha_kriteret": te_plota},
    }


def m2_mds() -> dict:
    gjithsej, singulare = mds.nenmatricat_singulare(mds.M)
    gjithsej_inv, singulare_inv = mds.nenmatricat_singulare(mds.M_INV)
    simetrite = [s for s in permutations(range(8))
                 if all(mds.M[s[i]][s[j]] == mds.M[i][j] for i in range(8) for j in range(8))]
    zhvendosjet = [b for b in range(8)
                   if all(mds.M[(i + b) % 8][(j + b) % 8] == mds.M[i][j]
                          for i in range(8) for j in range(8))]
    return {
        "matrica": [[f"{x:X}" for x in r] for r in mds.M],
        "nenmatrica_gjithsej": gjithsej,
        "nenmatrica_singulare": singulare,
        "nenmatrica_singulare_inversi": singulare_inv,
        "numri_degeve_peshe_1_2": mds.numri_degeve_peshe_te_ulet(mds.M, 2),
        "elemente_te_ndryshem": len({x for r in mds.M for x in r}),
        "elemente_te_barabarte_me_1": sum(x == 1 for r in mds.M for x in r),
        "simetrite_e_kolonave": len(simetrite),
        "simetrite_jane_xor": all(any(all(s[j] == j ^ t for j in range(8)) for t in range(8))
                                  for s in simetrite),
        "zhvendosjet_ciklike_qe_komutojne": zhvendosjet,
    }


def _raund_pa_celes(p: list[int], g: list[int]) -> list[int]:
    return mds.perziej_rreshtat(levizja.zbato(p, [sbox.SBOX[x] for x in g]))


def _cifte_te_barazvlefshme(perm: dict, komutuese: list) -> int:
    """Çifte variantesh që ndryshojnë vetëm me një zhvendosje që komuton me raundin (pra janë kozmetike)."""
    zhvendosjet = [levizja.levizja_kalit((0, 0), a, b) for a, b in komutuese if (a, b) != (0, 0)]
    te_gjitha = {tuple(p) for p in perm.values()}
    return sum(tuple(levizja.zbato(t, list(p))) in te_gjitha
               for p in perm.values() for t in zhvendosjet)


def m3_levizja() -> dict:
    vf = levizja.levizja_kalit()
    variantet_256 = {(d, a, b): levizja.levizja_kalit(d, a, b)
                     for d in levizja.DREJTIMET for a in range(8) for b in range(8)}
    variantet = [(d, b) for d in levizja.DREJTIMET for b in range(8)]
    perm = {v: levizja.levizja_kalit(v[0], beta=v[1]) for v in variantet}

    rng = random.Random(7)
    gjendjet = [[rng.randrange(16) for _ in range(64)] for _ in range(20)]
    # A komuton zhvendosja e pastër T(alfa, beta) me raundin pa çelës, për çdo drejtim?
    komutuese = []
    for a in range(8):
        for b in range(8):
            t = levizja.levizja_kalit((0, 0), a, b)
            if all(levizja.zbato(t, _raund_pa_celes(perm[(d, 0)], g))
                   == _raund_pa_celes(perm[(d, 0)], levizja.zbato(t, g))
                   for d in levizja.DREJTIMET for g in gjendjet):
                komutuese.append((a, b))
    return {
        "vf_bijeksion": levizja.eshte_bijeksion(vf),
        "vf_perhapja_rreshtave": levizja.perhapja_e_rreshtave(vf),
        "vf_pika_fikse": levizja.pika_fikse(vf),
        "vl_variante": len(variantet),
        "vl_bijeksione": sum(levizja.eshte_bijeksion(p) for p in perm.values()),
        "vl_perhapje_optimale": sum(levizja.perhapja_e_rreshtave(p) == 8 for p in perm.values()),
        "vl_permutime_te_ndryshme": len({tuple(p) for p in perm.values()}),
        "zhvendosje_qe_komutojne_me_raundin": komutuese,
        "cifte_kozmetike_familja_e_vjeter_256": _cifte_te_barazvlefshme(variantet_256, komutuese),
        "cifte_kozmetike_familja_e_re_32": _cifte_te_barazvlefshme(perm, komutuese),
    }


def _varesia(p_sekuenca: list[list[int]]) -> list[int]:
    """Pas çdo raundi: sa dalje varen nga hyrja më pak e përhapur (minimumi mbi 64 hyrjet)."""
    dep = [1 << i for i in range(64)]
    rezultati = []
    for p in p_sekuenca:
        lev = [0] * 64
        for i, d in enumerate(dep):
            lev[p[i]] = d
        dep = []
        for r in range(0, 64, 8):
            bashkimi = 0
            for d in lev[r:r + 8]:
                bashkimi |= d
            dep.extend([bashkimi] * 8)
        rezultati.append(min(sum(1 for d in dep if d >> j & 1) for j in range(64)))
    return rezultati


def m4_difuzioni() -> dict:
    vf = levizja.levizja_kalit()
    variantet = [levizja.levizja_kalit(d, beta=b) for d in levizja.DREJTIMET for b in range(8)]
    rng = random.Random(11)
    me_keq = [64] * 4
    for sekuenca in [[p] * 4 for p in variantet] + [[rng.choice(variantet) for _ in range(4)]
                                                   for _ in range(2000)]:
        me_keq = [min(x, y) for x, y in zip(me_keq, _varesia(sekuenca))]

    def kufiri(r):
        return 81 * (r // 4) + [0, 1, 9, 10][r % 4]

    return {
        "vf_daljet_e_varura_pas_raundit_1_4": _varesia([vf] * 4),
        "vl_me_e_keqja_pas_raundit_1_4": me_keq,
        "kufiri_wide_trail": {r: {"sbox_aktive_min": kufiri(r), "log2_prob_max": -2 * kufiri(r)}
                              for r in (1, 2, 3, 4, 6, 8, 12, 16, 32)},
    }


def m5_celesi() -> dict:
    rng = random.Random(13)
    for i in range(1, 300):
        g = [rng.randrange(16) for _ in range(celesi.NIBLA)]
        assert celesi.hapi_invers(celesi.hapi(g, i), i) == g

    # difuzioni strukturor i gjendjes së çelësit
    dep = [1 << j for j in range(celesi.NIBLA)]
    plot = (1 << celesi.NIBLA) - 1
    hapat_deri_plot = None
    for hapi in range(1, 10):
        rr = []
        for r in range(0, celesi.NIBLA, 8):
            b = 0
            for d in dep[r:r + 8]:
                b |= d
            rr.extend([b] * 8)
        dep = [0] * celesi.NIBLA
        for j, d in enumerate(rr):
            dep[celesi.PERM[j]] = d
        if all(d == plot for d in dep):
            hapat_deri_plot = hapi
            break

    raunde = 32
    celesat = [rng.getrandbits(celesi.GJATESIA_CELESIT) for _ in range(4)]
    fraksionet = [[] for _ in range(raunde + 1)]
    levizje_ndryshuar = [[] for _ in range(raunde + 1)]
    for k in celesat:
        baza = celesi.orari(k, raunde)
        for b in range(celesi.GJATESIA_CELESIT):
            o = celesi.orari(k ^ (1 << b), raunde)
            for i in range(raunde + 1):
                ndryshime = sum(bin(x ^ y).count("1") for x, y in zip(baza[i][0], o[i][0]))
                fraksionet[i].append(ndryshime / 256)
                if i:
                    levizje_ndryshuar[i].append(baza[i][1] != o[i][1])
    ortek = {i: {"mes": round(sum(f) / len(f), 4), "min": round(min(f), 4), "max": round(max(f), 4)}
             for i, f in enumerate(fraksionet) if i <= 6 or i in (8, 16, 32)}
    levizjet = {i: round(sum(v) / len(v), 4) for i, v in enumerate(levizje_ndryshuar)
                if i and (i <= 6 or i in (8, 16, 32))}

    numerimet = [0] * 32
    for _ in range(2000):
        for _rk, (d, b) in celesi.orari(rng.getrandbits(celesi.GJATESIA_CELESIT), raunde)[1:]:
            numerimet[celesi.DREJTIMET.index(d) * 8 + b] += 1
    n = sum(numerimet)
    pritur = n / len(numerimet)
    chi2 = sum((c - pritur) ** 2 / pritur for c in numerimet)
    df = len(numerimet) - 1
    pragu_99 = df * (1 - 2 / (9 * df) + 2.326 * math.sqrt(2 / (9 * df))) ** 3
    return {
        "p_hapi": celesi.P_HAPI,
        "perhapja_rreshtave": levizja.perhapja_e_rreshtave(celesi.PERM),
        "hapat_deri_difuzion_te_plote": hapat_deri_plot,
        "ortek_rk_fraksion_bitesh": ortek,
        "ortek_levizja_ndryshuar": levizjet,
        "uniformiteti_levizjeve": {"mostra": n, "chi2": round(chi2, 1), "pragu_99": round(pragu_99, 1),
                                   "min": min(numerimet), "max": max(numerimet)},
    }


def main() -> None:
    rezultatet = {}
    for emri, f in [("M1_sbox", m1_sbox), ("M2_mds", m2_mds), ("M3_levizja", m3_levizja),
                    ("M4_difuzioni", m4_difuzioni), ("M5_celesi", m5_celesi)]:
        t = time.time()
        rezultatet[emri] = f()
        rezultatet[emri]["sekonda"] = round(time.time() - t, 1)
        print(emri, json.dumps(rezultatet[emri], ensure_ascii=False))
    dalja = Path(__file__).with_name("f1_rezultatet.json")
    dalja.write_text(json.dumps(rezultatet, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
