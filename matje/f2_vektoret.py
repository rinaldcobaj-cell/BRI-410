"""Gjeneron vektoret e njohur (KAT) të F2 → teste/vektoret_f2.json.

Janë vektorë regresioni të vetë implementimit, jo verifikim i pavarur.
Përdorimi: python -m matje.f2_vektoret
"""

import json
from pathlib import Path

from shahu import shifra

CELESAT = {
    "zero": bytes(52),
    "njesha": bytes([0xFF] * 51 + [0x03]),
    "rritese": bytes(range(51)) + bytes([0x02]),
}
MESAZHET = {"zero": bytes(32), "rrites": bytes(range(32))}


def main() -> None:
    vektoret = []
    for emri_k, k in CELESAT.items():
        for emri_m, m in MESAZHET.items():
            for varianti in shifra.VARIANTET:
                for raunde in (16, 32):
                    vektoret.append({
                        "emri": f"{emri_k}/{emri_m}/{varianti}/{raunde}",
                        "celesi": k.hex(), "mesazhi": m.hex(),
                        "varianti": varianti, "raunde": raunde,
                        "kriptuar": shifra.BRI410(k, raunde, varianti).kripto(m).hex(),
                    })
    dalja = Path(__file__).resolve().parent.parent / "teste" / "vektoret_f2.json"
    dalja.write_text(json.dumps(vektoret, indent=2), encoding="utf-8")
    print(f"{len(vektoret)} vektorë → {dalja}")


if __name__ == "__main__":
    main()
