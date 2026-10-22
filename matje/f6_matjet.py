"""Hapi 2: matjet e BRI-410 AE. Përdorimi: python -m matje.f6_matjet → matje/f6_rezultatet.json"""

import json
import random
import time
from pathlib import Path

from shahu import bri8, menyra


def shpejtesia() -> dict:
    rng = random.Random(130)
    k = bri8.gjenero_celes()
    rez = {}
    for n in (64, 1024, 65536):
        m = rng.randbytes(n)
        t = time.perf_counter()
        p = menyra.kripto(k, m)
        tk = time.perf_counter() - t
        t = time.perf_counter()
        menyra.dekripto(k, p)
        td = time.perf_counter() - t
        rez[f"{n}_bajte"] = {"kriptimi_bajte_s": round(n / tk), "dekriptimi_bajte_s": round(n / td),
                             "shtesa_bajte": len(p) - n}
    return rez


def falsifikimi() -> dict:
    """Sulmuesi provon 2 000 paketa të ndryshuara rastësisht (bit, bajte, vula të rastësishme)."""
    rng = random.Random(131)
    k = bri8.gjenero_celes()
    p = menyra.kripto(k, rng.randbytes(150), b"koka")
    pranuar = 0
    for i in range(2000):
        q = bytearray(p)
        if i % 2:
            q[-52:] = rng.randbytes(52)  # vulë e rastësishme
        else:
            for _ in range(rng.randint(1, 5)):
                q[rng.randrange(len(q))] ^= rng.randrange(1, 256)
        try:
            menyra.dekripto(k, bytes(q), b"koka")
            pranuar += 1
        except menyra.VulaEGabuar:
            pass
    return {"prova": 2000, "te_pranuara": pranuar}


def numri_i_perseritur() -> dict:
    """Demonstrim i keqpërdorimit: dy mesazhe me të njëjtin numër dhe të njëjtin bllok të parë."""
    rng = random.Random(132)
    k = bri8.gjenero_celes()
    i_perbashket = rng.randbytes(64)
    m1, m2 = i_perbashket + rng.randbytes(64), i_perbashket + rng.randbytes(64)
    n = bytes(12)
    c1, c2 = menyra.kripto(k, m1, numri=n), menyra.kripto(k, m2, numri=n)
    d1, d2 = menyra.kripto(k, m1), menyra.kripto(k, m2)
    return {
        "numer_i_njejte_blloku_1_i_njejte": c1[12:76] == c2[12:76],
        "numer_i_njejte_blloku_2_i_njejte": c1[76:140] == c2[76:140],
        "numer_i_ndryshem_blloku_1_i_njejte": d1[12:76] == d2[12:76],
    }


def main() -> None:
    rez = {}
    for emri, f in [("shpejtesia", shpejtesia), ("falsifikimi", falsifikimi), ("numri_i_perseritur", numri_i_perseritur)]:
        t = time.time()
        rez[emri] = f()
        rez[emri]["sekonda"] = round(time.time() - t, 1)
        print(emri, json.dumps(rez[emri], ensure_ascii=False), flush=True)
    Path(__file__).with_name("f6_rezultatet.json").write_text(json.dumps(rez, ensure_ascii=False, indent=2),
                                                              encoding="utf-8")


if __name__ == "__main__":
    main()
