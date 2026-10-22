"""F4-b: kufij të saktë (CP-SAT) për numrin minimal të S-box-eve aktive në BRI-410/8.

Përdorimi (nga rrënja e projektit, me mjedisin që ka ortools):
    .venv\\Scripts\\python.exe -m matje.f4b_milp → matje/f4b_rezultatet.json

Model në nivel kutie (bajti aktiv / joaktiv), standardi për kufijtë wide-trail:
  - S-box-i nuk e ndryshon aktivitetin.
  - θ (MDS, numri i degëve 9) në çdo rresht: hyrje + dalje aktive ∈ {0} ∪ [9, 16].
  - π: vetëm "në cilin rresht shkon kutia" ka rëndësi për θ-n: rreshti i ri = r + k·dr, dr = ±1.
    SULMUESIT I LIHET TË ZGJEDHË dr-në në çdo raund, pra kufiri vlen për çdo lojë (çdo çelës, çdo numër).
  - XOR-i me çelësin nuk ndryshon aktivitetin (diferencial me të njëjtin çelës/numër).
Kufiri vlen edhe për sulmin linear: matrica e transpozuar e një MDS është MDS me të njëjtin numër degësh.

Pjesa 2: orari me numra të zgjedhur (related-tweak). Diferenca futet në bajtet 0..15 pas 4 hapave
që varen vetëm nga çelësi, dhe numërohen S-box-et aktive në hapat pasues të orarit (80 bajte, 10 rreshta).
"""

import json
import math
import sys
import time
import types
from pathlib import Path

# ortools e importon pandas në fillim, por CP-SAT nuk ka nevojë për të. Në këtë kompjuter, rregulli i sigurisë
# i Windows-it bllokon një DLL të pandas-it; rregulli NUK preket. Thjesht pandas nuk ngarkohet: modul bosh.
if "pandas" not in sys.modules:
    _pd = types.ModuleType("pandas")
    for _emri in ("Index", "Series", "DataFrame"):
        setattr(_pd, _emri, type(_emri, (), {}))
    sys.modules["pandas"] = _pd

from ortools.sat.python import cp_model  # noqa: E402

from shahu import bri8, sbox8

DEGET = 9
KOHA_MAKS = 600.0


def _rreshti_i_ri(kutia: int, dr: int) -> int:
    r, k = divmod(kutia, 8)
    return (r + k * dr) % 8


def kufiri_i_shifres(raunde: int, loja_e_lire: bool = True) -> dict:
    m = cp_model.CpModel()
    x = [[m.NewBoolVar(f"x{t}_{c}") for c in range(64)] for t in range(raunde + 1)]
    for t in range(raunde):
        # z[t][q] = kutitë aktive që hyjnë në rreshtin q të θ-s pas π (vetëm rreshti ka rëndësi)
        s = m.NewBoolVar(f"s{t}") if loja_e_lire else None
        for q in range(8):
            hyrjet = []
            for c in range(64):
                if _rreshti_i_ri(c, +1) == q and _rreshti_i_ri(c, -1) == q:
                    hyrjet.append(x[t][c])
                elif _rreshti_i_ri(c, +1) == q or _rreshti_i_ri(c, -1) == q:
                    if not loja_e_lire:
                        if _rreshti_i_ri(c, +1) == q:
                            hyrjet.append(x[t][c])
                        continue
                    z = m.NewBoolVar(f"z{t}_{c}_{q}")
                    zgjedhja = s if _rreshti_i_ri(c, -1) == q else s.Not()  # s = 1 ⇔ dr = −1
                    m.AddImplication(z, x[t][c])
                    m.AddImplication(z, zgjedhja)
                    m.AddBoolOr([z, x[t][c].Not(), zgjedhja.Not()])
                    hyrjet.append(z)
            daljet = x[t + 1][8 * q:8 * q + 8]
            d = m.NewBoolVar(f"d{t}_{q}")
            for v in hyrjet + daljet:
                m.AddImplication(v, d)
            m.Add(sum(hyrjet) + sum(daljet) >= DEGET * d)
    m.Add(sum(x[0]) >= 1)
    m.Minimize(sum(v for t in range(raunde) for v in x[t]))
    return _zgjidh(m)


def kufiri_i_orarit(hapa: int) -> dict:
    """Hapat e orarit pas futjes së numrit: S → θ (10 rreshta) → bajti j shkon te 9·j mod 80."""
    n = bri8.BAJTE_GJENDJE
    m = cp_model.CpModel()
    x = [[m.NewBoolVar(f"k{t}_{j}") for j in range(n)] for t in range(hapa + 1)]
    for j in range(16, n):
        m.Add(x[0][j] == 0)  # numri prek vetëm bajtet 0..15; çelësi është i njëjtë
    m.Add(sum(x[0][:16]) >= 1)
    for t in range(hapa):
        for q in range(n // 8):
            hyrjet = x[t][8 * q:8 * q + 8]
            daljet = [x[t + 1][bri8.PERM[8 * q + i]] for i in range(8)]  # dalja i e rreshtit q → PERM
            d = m.NewBoolVar(f"e{t}_{q}")
            for v in hyrjet + daljet:
                m.AddImplication(v, d)
            m.Add(sum(hyrjet) + sum(daljet) >= DEGET * d)
    m.Minimize(sum(v for t in range(hapa) for v in x[t]))
    return _zgjidh(m)


def _zgjidh(m: cp_model.CpModel) -> dict:
    zgjidhesi = cp_model.CpSolver()
    zgjidhesi.parameters.max_time_in_seconds = KOHA_MAKS
    zgjidhesi.parameters.num_workers = 8
    t = time.time()
    statusi = zgjidhesi.Solve(m)
    return {"minimumi": int(zgjidhesi.ObjectiveValue()), "kufiri_i_poshtem": int(math.ceil(zgjidhesi.BestObjectiveBound())),
            "i_provuar": statusi == cp_model.OPTIMAL, "sekonda": round(time.time() - t, 1)}


def main() -> None:
    p_sbox = sbox8.matjet(sbox8.SBOX)["uniformiteti_diferencial"] / 256  # 2^-6
    log_p = math.log2(p_sbox)
    rez = {"log2_prob_per_sbox": log_p, "shifra_loja_e_lire": {}, "shifra_loja_fikse_dr_plus": {}, "orari": {}}
    for r in range(1, 9):
        v = kufiri_i_shifres(r)
        v["log2_prob_max"] = v["kufiri_i_poshtem"] * log_p
        rez["shifra_loja_e_lire"][r] = v
        print("shifra (loja e lirë)", r, v, flush=True)
    for r in (2, 4):
        rez["shifra_loja_fikse_dr_plus"][r] = kufiri_i_shifres(r, loja_e_lire=False)
        print("shifra (dr = +1 fiks)", r, rez["shifra_loja_fikse_dr_plus"][r], flush=True)
    for h in range(1, 7):
        v = kufiri_i_orarit(h)
        v["log2_prob_max"] = v["kufiri_i_poshtem"] * log_p
        rez["orari"][h] = v
        print("orari pas numrit", h, v, flush=True)
    Path(__file__).with_name("f4b_rezultatet.json").write_text(json.dumps(rez, ensure_ascii=False, indent=2),
                                                               encoding="utf-8")


if __name__ == "__main__":
    main()
