"""Gjeneron vektoret e njohur të BRI-410 AE → teste/vektoret_ae.json (regresion, jo verifikim i pavarur).

Përdorimi: python -m matje.f6_vektoret
"""

import json
from pathlib import Path

from shahu import menyra

CELESI = bytes(range(51)) + bytes([0x02])
NUMRI = bytes(range(12))
RASTET = [(b"", b""), (b"", b"Ana"), (bytes(range(1)), b""), (bytes(range(64)), b""),
          (bytes(range(100)), b"Ana -> Besi"), (bytes(i % 256 for i in range(200)), bytes(70))]


def main() -> None:
    vektoret = [{"celesi": CELESI.hex(), "numri": NUMRI.hex(), "mesazhi": m.hex(), "te_dhena": a.hex(),
                 "paketa": menyra.kripto(CELESI, m, a, NUMRI).hex()} for m, a in RASTET]
    dalja = Path(__file__).resolve().parent.parent / "teste" / "vektoret_ae.json"
    dalja.write_text(json.dumps(vektoret, indent=2), encoding="utf-8")
    print(f"{len(vektoret)} vektorë → {dalja}")


if __name__ == "__main__":
    main()
