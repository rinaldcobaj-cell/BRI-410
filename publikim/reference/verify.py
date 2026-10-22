"""Verifies bri410.py against test_vectors.json. Run: python verify.py"""

import json
from pathlib import Path

import bri410

here = Path(__file__).resolve().parent
data = json.loads((here / "test_vectors.json").read_text(encoding="utf-8"))
failures = 0

for v in data["block_cipher"]:
    key, tweak, pt = (bytes.fromhex(v[x]) for x in ("key", "tweak", "plaintext"))
    sch = bri410.schedule(key, tweak)
    ok = (bri410.encrypt_block(key, tweak, pt).hex() == v["ciphertext"]
          and bri410.decrypt_block(key, tweak, bytes.fromhex(v["ciphertext"])) == pt
          and bytes(sch[0][0]).hex() == v["round_key_0"] and bytes(sch[16][0]).hex() == v["round_key_16"])
    failures += not ok
    print("OK  " if ok else "FAIL", v["name"])

for i, v in enumerate(data["aead"]["vectors"]):
    key, nonce, msg, ad = (bytes.fromhex(v[x]) for x in ("key", "nonce", "message", "associated_data"))
    packet = bri410.encrypt(key, msg, ad, nonce)
    ok = packet.hex() == v["packet"] and bri410.decrypt(key, packet, ad) == msg
    failures += not ok
    print("OK  " if ok else "FAIL", f"aead vector {i} ({len(msg)} bytes, {len(ad)} bytes of associated data)")

print("ALL PASSED" if failures == 0 else f"{failures} FAILURES")
raise SystemExit(1 if failures else 0)
