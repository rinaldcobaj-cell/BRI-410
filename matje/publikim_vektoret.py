"""Eksporton vektorët e testit në anglisht për paketën e publikimit → publikim/reference/test_vectors.json.

Burimi: implementimi i projektit (shahu.bri8, shahu.menyra). Përdorimi: python -m matje.publikim_vektoret
"""

import json
from pathlib import Path

from shahu import bri8, menyra

KEYS = {"zero": bytes(52), "ones": bytes([0xFF] * 51 + [0x03]), "counting": bytes(range(51)) + bytes([0x02])}


def main() -> None:
    block = []
    for nk, k in KEYS.items():
        for nt, t in {"zero": bytes(16), "counting": bytes(range(16))}.items():
            for nm, m in {"zero": bytes(64), "counting": bytes(range(64))}.items():
                s = bri8.BRI410_8(k, 16, t)
                block.append({"name": f"key={nk} tweak={nt} plaintext={nm}", "key": k.hex(), "tweak": t.hex(),
                              "plaintext": m.hex(), "ciphertext": s.kripto(m).hex(),
                              "round_key_0": bytes(s._rk[0]).hex(), "round_key_16": bytes(s._rk[16]).hex()})
    ae = []
    k, n = KEYS["counting"], bytes(range(12))
    for m, a in [(b"", b""), (b"", b"Ana"), (b"\x00", b""), (bytes(range(64)), b""),
                 (bytes(range(100)), b"Ana -> Besi"), (bytes(i % 256 for i in range(200)), bytes(70))]:
        ae.append({"key": k.hex(), "nonce": n.hex(), "message": m.hex(), "associated_data": a.hex(),
                   "packet": menyra.kripto(k, m, a, n).hex()})
    dalja = Path(__file__).resolve().parent.parent / "publikim" / "reference" / "test_vectors.json"
    dalja.write_text(json.dumps({"cipher": "BRI-410/8, 16 rounds", "block_cipher": block,
                                 "aead": {"mode": "BRI-410 AE (ThetaCB3), 416-bit tag", "vectors": ae}}, indent=2),
                     encoding="utf-8")
    print(f"{len(block)} + {len(ae)} vectors → {dalja}")


if __name__ == "__main__":
    main()
