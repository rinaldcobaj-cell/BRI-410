"""Gjeneron vektoret e njohur (KAT) të BRI-410/8 → teste/vektoret_f5.json.

Janë vektorë regresioni të vetë implementimit, jo verifikim i pavarur.
Përdorimi: python -m matje.f5_vektoret
"""

import json
from pathlib import Path

from shahu import bri8

CELESAT = {
    "zero": bytes(52),
    "njesha": bytes([0xFF] * 51 + [0x03]),
    "rritese": bytes(range(51)) + bytes([0x02]),
}
NUMRAT = {"zero": bytes(16), "rrites": bytes(range(16))}
MESAZHET = {"zero": bytes(64), "rrites": bytes(range(64))}


def main() -> None:
    vektoret = []
    for emri_k, k in CELESAT.items():
        for emri_n, n in NUMRAT.items():
            for emri_m, m in MESAZHET.items():
                vektoret.append({
                    "emri": f"{emri_k}/{emri_n}/{emri_m}/16",
                    "celesi": k.hex(), "numri": n.hex(), "mesazhi": m.hex(), "raunde": 16,
                    "kriptuar": bri8.BRI410_8(k, 16, n).kripto(m).hex(),
                })
    dalja = Path(__file__).resolve().parent.parent / "teste" / "vektoret_f5.json"
    dalja.write_text(json.dumps(vektoret, indent=2), encoding="utf-8")
    print(f"{len(vektoret)} vektorë → {dalja}")


if __name__ == "__main__":
    main()
