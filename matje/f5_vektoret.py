"""Gjeneron vektoret e njohur (KAT) të BRI-410/8.

    python -m matje.f5_vektoret          → teste/vektoret_f5_v11.json (v1.1, versioni zyrtar)
    python -m matje.f5_vektoret 1.0      → teste/vektoret_f5.json     (v1.0, të ngrirë në F5)

Janë vektorë regresioni të vetë implementimit, jo verifikim i pavarur.
"""

import json
import sys
from pathlib import Path

from shahu import bri8

CELESAT = {
    "zero": bytes(52),
    "njesha": bytes([0xFF] * 51 + [0x03]),
    "rritese": bytes(range(51)) + bytes([0x02]),
}
NUMRAT = {"zero": bytes(16), "rrites": bytes(range(16))}
MESAZHET = {"zero": bytes(64), "rrites": bytes(range(64))}
SKEDARI = {"1.0": "vektoret_f5.json", "1.1": "vektoret_f5_v11.json"}


def main(versioni: str = bri8.VERSIONI) -> None:
    vektoret = []
    for emri_k, k in CELESAT.items():
        for emri_n, n in NUMRAT.items():
            for emri_m, m in MESAZHET.items():
                vektoret.append({
                    "emri": f"{emri_k}/{emri_n}/{emri_m}/16", "versioni": versioni,
                    "celesi": k.hex(), "numri": n.hex(), "mesazhi": m.hex(), "raunde": 16,
                    "kriptuar": bri8.BRI410_8(k, 16, n, versioni=versioni).kripto(m).hex(),
                })
    dalja = Path(__file__).resolve().parent.parent / "teste" / SKEDARI[versioni]
    dalja.write_text(json.dumps(vektoret, indent=2), encoding="utf-8")
    print(f"{len(vektoret)} vektorë ({versioni}) → {dalja}")


if __name__ == "__main__":
    main(*sys.argv[1:2])
