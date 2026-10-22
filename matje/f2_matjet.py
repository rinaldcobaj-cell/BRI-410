"""F2: matjet e prototipit të plotë. Përdorimi (nga rrënja e projektit): python -m matje.f2_matjet

Shkruan matje/f2_rezultatet.json. Çdo matje statistikore krahasohet me një bazë të rastësishme
të llogaritur në të njëjtën mënyrë ("si do të dukej një funksion vërtet i rastësishëm").
Farat janë fikse; çelësat janë mostra matjeje.
"""

import json
import math
import random
import time
from pathlib import Path

from shahu import shifra

RAUNDE_TE_PJESSHME = (1, 2, 3, 4, 5, 6, 8)
KONFIGURIMET = [(v, r) for v in shifra.VARIANTET for r in (16, 32)]


def _int_nga_nibla(n: list[int]) -> int:
    return sum(x << (4 * i) for i, x in enumerate(n))


def _nibla_nga_int(v: int) -> list[int]:
    return [(v >> (4 * i)) & 15 for i in range(64)]


def _pragu_chi2_99(df: int) -> float:
    return df * (1 - 2 / (9 * df) + 2.326 * math.sqrt(2 / (9 * df))) ** 3


def korrektesia() -> dict:
    rng = random.Random(30)
    rezultati = {}
    for varianti, raunde in KONFIGURIMET:
        sakte = gjithsej = 0
        koha_kriptim = 0.0
        for _ in range(100):
            s = shifra.BRI410(rng.getrandbits(410), raunde, varianti)
            for _ in range(100):
                m = rng.randbytes(32)
                t = time.perf_counter()
                c = s.kripto(m)
                koha_kriptim += time.perf_counter() - t
                sakte += s.dekripto(c) == m
                gjithsej += 1
        rezultati[f"{varianti}{raunde}"] = {"sakte": sakte, "gjithsej": gjithsej,
                                            "blloqe_ne_sekonde_python": round(gjithsej / koha_kriptim)}
    return rezultati


def _baza_ortek(rng: random.Random, n: int) -> dict:
    f = [rng.getrandbits(256).bit_count() / 256 for _ in range(n)]
    return {"mes": round(sum(f) / n, 4), "min": round(min(f), 4), "max": round(max(f), 4)}


def ortek_mesazhi() -> dict:
    """Ndryshohet 1 bit i mesazhit: sa bit ndryshojnë në dalje pas r raundeve."""
    rng = random.Random(31)
    n = 2000
    rezultati = {"baza_rastesore": _baza_ortek(rng, n)}
    for varianti in shifra.VARIANTET:
        celesat = [shifra.BRI410(rng.getrandbits(410), 32, varianti) for _ in range(100)]
        rv = {}
        for r in RAUNDE_TE_PJESSHME + (16, 32):
            f = []
            for i in range(n):
                s = celesat[i % 100]
                x = [rng.randrange(16) for _ in range(64)]
                b = rng.randrange(256)
                x2 = list(x)
                x2[b // 4] ^= 1 << (b % 4)
                d = _int_nga_nibla(s.kripto_nibla(x, r)) ^ _int_nga_nibla(s.kripto_nibla(x2, r))
                f.append(d.bit_count() / 256)
            rv[r] = {"mes": round(sum(f) / n, 4), "min": round(min(f), 4), "max": round(max(f), 4)}
        rezultati[varianti] = rv
    return rezultati


def _sac(diferencat: list[list[int]], n: int) -> dict:
    """diferencat[b] = lista e XOR-eve të daljes kur ndryshon biti b i hyrjes."""
    devijimi_max = 0.0
    qeliza_te_vdekura = 0
    for lista in diferencat:
        numero = [0] * 256
        for d in lista:
            while d:
                low = d & -d
                numero[low.bit_length() - 1] += 1
                d ^= low
        for c in numero:
            devijimi_max = max(devijimi_max, abs(c / n - 0.5))
            qeliza_te_vdekura += c in (0, n)
    return {"devijimi_max": round(devijimi_max, 4), "qeliza_0_ose_1": qeliza_te_vdekura}


def kriteri_sac() -> dict:
    """Kriteri i ortekut të rreptë: çdo bit dalje duhet të ndryshojë me gjasë 1/2 për çdo bit hyrje.

    Matrica 256×256, n mostra për çdo bit hyrje; krahasohet me bazën e rastësishme me të njëjtin n.
    """
    rng = random.Random(32)
    n = 64
    baza = _sac([[rng.getrandbits(256) for _ in range(n)] for _ in range(256)], n)
    rezultati = {"mostra_per_bit": n, "baza_rastesore": baza}
    for varianti in shifra.VARIANTET:
        celesat = [shifra.BRI410(rng.getrandbits(410), 32, varianti) for _ in range(64)]
        rv = {}
        for r in (1, 2, 3, 4, 6):
            diferencat = []
            for b in range(256):
                lista = []
                for j in range(n):
                    s = celesat[j]
                    x = [rng.randrange(16) for _ in range(64)]
                    x2 = list(x)
                    x2[b // 4] ^= 1 << (b % 4)
                    lista.append(_int_nga_nibla(s.kripto_nibla(x, r))
                                 ^ _int_nga_nibla(s.kripto_nibla(x2, r)))
                diferencat.append(lista)
            rv[r] = _sac(diferencat, n)
        rezultati[varianti] = rv
    return rezultati


def ortek_celesi() -> dict:
    """Ndryshohet 1 bit i çelësit (0..409): sa bit ndryshojnë në dalje pas r raundeve."""
    rng = random.Random(33)
    n = 1000
    rezultati = {"baza_rastesore": _baza_ortek(rng, n)}
    for varianti in shifra.VARIANTET:
        rv = {}
        for r in (1, 2, 3, 4, 6, 16, 32):
            f = []
            for _ in range(n):
                k = rng.getrandbits(410)
                m = rng.randbytes(32)
                c1 = shifra.BRI410(k, r, varianti).kripto(m)
                c2 = shifra.BRI410(k ^ (1 << rng.randrange(410)), r, varianti).kripto(m)
                f.append((int.from_bytes(c1, "little") ^ int.from_bytes(c2, "little")).bit_count() / 256)
            rv[r] = {"mes": round(sum(f) / n, 4), "min": round(min(f), 4), "max": round(max(f), 4)}
        rezultati[varianti] = rv
    return rezultati


def statistika_numeruesi() -> dict:
    """Kriptohen numrat 0, 1, 2, … (hyrje shumë të ngjashme) dhe testohet nëse dalja duket e rastësishme."""
    rng = random.Random(34)
    n = 20000
    rezultati = {"blloqe": n}
    for varianti in shifra.VARIANTET:
        s = shifra.BRI410(rng.getrandbits(410), 16, varianti)
        njesha = 0
        nibla = [0] * 16
        bajte = [0] * 256
        for i in range(n):
            c = s.kripto(i.to_bytes(32, "little"))
            njesha += int.from_bytes(c, "little").bit_count()
            for x in c:
                bajte[x] += 1
                nibla[x & 15] += 1
                nibla[x >> 4] += 1
        bitet = 256 * n
        z = (njesha - bitet / 2) / math.sqrt(bitet / 4)

        def chi2(numero):
            pritur = sum(numero) / len(numero)
            return sum((c - pritur) ** 2 / pritur for c in numero)

        rezultati[f"{varianti}16"] = {
            "monobit_z": round(z, 3), "monobit_pragu_99": 2.576,
            "nibla_chi2": round(chi2(nibla), 1), "nibla_pragu_99": round(_pragu_chi2_99(15), 1),
            "bajte_chi2": round(chi2(bajte), 1), "bajte_pragu_99": round(_pragu_chi2_99(255), 1),
        }
    return rezultati


def main() -> None:
    rezultatet = {}
    for emri, f in [("korrektesia", korrektesia), ("ortek_mesazhi", ortek_mesazhi),
                    ("kriteri_sac", kriteri_sac), ("ortek_celesi", ortek_celesi),
                    ("statistika_numeruesi", statistika_numeruesi)]:
        t = time.time()
        rezultatet[emri] = f()
        rezultatet[emri]["sekonda"] = round(time.time() - t, 1)
        print(emri, json.dumps(rezultatet[emri], ensure_ascii=False), flush=True)
    dalja = Path(__file__).with_name("f2_rezultatet.json")
    dalja.write_text(json.dumps(rezultatet, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
