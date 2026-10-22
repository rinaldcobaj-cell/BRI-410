"""F3-bis: a e bllokon "loja sipas bllokut" (V-N) sulmin integral që theu BRI-410 me 5 raunde?

Tri mënyra, i njëjti sulm:
  VL             loja sipas çelësit (e thyer në F3)
  VN             loja e re për çdo bllok: çdo tekst kriptohet me numër unik
  VN_perseritur  keqpërdorim: i njëjti numër për të gjitha tekstet

Përdorimi (nga rrënja e projektit): python -m matje.f3bis_matjet → matje/f3bis_rezultatet.json
"""

import itertools
import json
import random
import time
from pathlib import Path

from matje.f3_zgjerimi import GRUPI, _int_nibla
from shahu import shifra
from shahu.mds import perziej_shpejt
from shahu.sbox import SBOX_INV

MENYRAT = ("VL", "VN", "VN_perseritur")


class _Kriptuesi:
    """Kriptuesi i parë nga sulmuesi: i jep tekste dhe merr tekstet e kriptuara."""

    def __init__(self, k: int, raunde: int, menyra: str, rng: random.Random):
        self.k, self.raunde, self.menyra = k, raunde, menyra
        self._numeruesi = rng.getrandbits(64) << 64  # numra unikë: pjesa e lartë e rastësishme + numërues
        self._fiks = None
        if menyra == "VL":
            self._fiks = shifra.BRI410(k, raunde, "VL")
        elif menyra == "VN_perseritur":
            self._fiks = shifra.BRI410(k, raunde, "VN", rng.randbytes(16))

    def __call__(self, x: list[int]) -> list[int]:
        if self._fiks is not None:
            return self._fiks.kripto_nibla(x)
        self._numeruesi += 1
        return shifra.BRI410(self.k, self.raunde, "VN", self._numeruesi.to_bytes(16, "little")).kripto_nibla(x)

    def dr_e_vertete(self) -> int | None:
        """Vetëm për matjen e dalluesit në rastin më të mirë për sulmuesin; sulmi nuk e përdor."""
        return None if self._fiks is None else self._fiks._levizjet[0][0][0]


def _balancuar(kripto: _Kriptuesi, aktive: list[int], rng: random.Random) -> int:
    baza = [rng.randrange(16) for _ in range(64)]
    shuma = 0
    for vlerat in itertools.product(range(16), repeat=len(aktive)):
        x = list(baza)
        for p, v in zip(aktive, vlerat):
            x[p] = v
        shuma ^= _int_nibla(kripto(x))
    return sum((shuma >> (4 * i)) & 15 == 0 for i in range(64))


def dalluesi() -> dict:
    """Pritja te një funksion i rastësishëm: 4 nga 64 nibble të balancuara."""
    rng = random.Random(70)
    rezultati = {"pritja_rastesore": 4}
    for menyra in MENYRAT:
        rv = {"1_nibble_3_raunde": [_balancuar(_Kriptuesi(rng.getrandbits(410), 3, menyra, rng), [0], rng)
                                    for _ in range(10)]}
        vlerat = []
        for _ in range(5):
            kr = _Kriptuesi(rng.getrandbits(410), 4, menyra, rng)
            dr = kr.dr_e_vertete() or +1  # te VN nuk ka një dr të vetëm: çdo bllok ka lojën e vet
            vlerat.append(_balancuar(kr, GRUPI[dr][:3], rng))
        rv["3_nibla_te_rreshtuara_4_raunde"] = vlerat
        rezultati[menyra] = rv
        print("dalluesi", menyra, rv, flush=True)
    return rezultati


def _sulmi(kripto: _Kriptuesi, rng: random.Random) -> dict:
    """I njëjti sulm si në F3 (5 raunde): sulmuesi provon dr = +1 dhe pastaj dr = −1."""
    tekste = 0
    for dr in (+1, -1):
        kandidatet = [set(range(16)) for _ in range(64)]
        for _ in range(8):
            baza = [rng.randrange(16) for _ in range(64)]
            numero = [[0] * 16 for _ in range(64)]
            for vlerat in itertools.product(range(16), repeat=3):
                x = list(baza)
                for p, v in zip(GRUPI[dr][:3], vlerat):
                    x[p] = v
                for j, v in enumerate(perziej_shpejt(kripto(x))):
                    numero[j][v] ^= 1
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
            e_sakte = kripto._fiks is not None and rk == kripto._fiks._rk[5]
            return {"rezultati": "çelësi i raundit u rikthye" if e_sakte else "çelës i gabuar",
                    "sukses": e_sakte, "tekste": tekste}
    return {"rezultati": "kontradiktë: asnjë çelës nuk përputhet", "sukses": False, "tekste": tekste}


def sulmi() -> dict:
    rng = random.Random(71)
    rezultati = {}
    for menyra in MENYRAT:
        prova = []
        for _ in range(3):
            t = time.time()
            p = _sulmi(_Kriptuesi(rng.getrandbits(410), 5, menyra, rng), rng)
            p["sekonda"] = round(time.time() - t, 1)
            prova.append(p)
        rezultati[menyra] = prova
        print("sulmi", menyra, prova, flush=True)
    return rezultati


def perputhjet_e_lojes() -> dict:
    """A mund sulmuesi të gjejë blloqe me "të njëjtën lojë" rastësisht? Dhe a mjafton kjo?"""
    rng = random.Random(72)
    k = rng.getrandbits(410)
    n = 20000
    sipas_lojes: dict[tuple, list[list[int]]] = {}
    for i in range(n):
        s = shifra.BRI410(k, 4, "VN", i.to_bytes(16, "little"))
        sipas_lojes.setdefault(tuple(s._levizjet), []).append(s._rk[1])
    cifte = [(a, b) for rks in sipas_lojes.values() for a, b in itertools.combinations(rks, 2)]
    ndryshimi = [sum(bin(x ^ y).count("1") for x, y in zip(a, b)) / 256 for a, b in cifte]

    ortek = []
    for _ in range(500):
        k2, m, numri = rng.getrandbits(410), rng.randbytes(32), rng.randbytes(16)
        b = rng.randrange(128)
        numri2 = (int.from_bytes(numri, "little") ^ (1 << b)).to_bytes(16, "little")
        c1 = shifra.BRI410(k2, 16, "VN", numri).kripto(m)
        c2 = shifra.BRI410(k2, 16, "VN", numri2).kripto(m)
        ortek.append((int.from_bytes(c1, "little") ^ int.from_bytes(c2, "little")).bit_count() / 256)
    return {
        "blloqe": n,
        "cifte_me_loje_te_njejte_ne_4_raunde": len(cifte),
        "cifte_te_pritura": round(n * (n - 1) / 2 / 2 ** 20, 1),
        "ndryshimi_i_rk1_ne_keto_cifte": {"mes": round(sum(ndryshimi) / len(ndryshimi), 4),
                                          "min": round(min(ndryshimi), 4)} if ndryshimi else None,
        "ortek_1_bit_numri_16_raunde": {"mes": round(sum(ortek) / len(ortek), 4),
                                        "min": round(min(ortek), 4), "max": round(max(ortek), 4)},
    }


def shpejtesia() -> dict:
    rng = random.Random(73)
    n = 3000
    rezultati = {}
    for raunde in (16, 32):
        k = rng.getrandbits(410)
        mesazhet = [rng.randbytes(32) for _ in range(n)]
        s = shifra.BRI410(k, raunde, "VL")
        t = time.perf_counter()
        for m in mesazhet:
            s.kripto(m)
        rezultati[f"VL{raunde}"] = round(n / (time.perf_counter() - t))
        t = time.perf_counter()
        for i, m in enumerate(mesazhet):
            shifra.BRI410(k, raunde, "VN", i.to_bytes(16, "little")).kripto(m)
        rezultati[f"VN{raunde}"] = round(n / (time.perf_counter() - t))
    return {"blloqe_ne_sekonde_python": rezultati}


def main() -> None:
    rezultatet = {}
    for emri, f in [("dalluesi", dalluesi), ("sulmi_5_raunde", sulmi),
                    ("perputhjet_e_lojes", perputhjet_e_lojes), ("shpejtesia", shpejtesia)]:
        t = time.time()
        rezultatet[emri] = f()
        rezultatet[emri]["sekonda"] = round(time.time() - t, 1)
        print(emri, json.dumps(rezultatet[emri], ensure_ascii=False), flush=True)
    Path(__file__).with_name("f3bis_rezultatet.json").write_text(
        json.dumps(rezultatet, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
