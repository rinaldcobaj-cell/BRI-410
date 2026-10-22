"""Paketa e publikimit: implementimi reference (anglisht, një skedar) duhet të përputhet me projektin."""

import importlib.util
import json
import random
import unittest
from pathlib import Path

from shahu import bri8, menyra

_DOSJA = Path(__file__).resolve().parent.parent / "publikim" / "reference"
_spec = importlib.util.spec_from_file_location("bri410_reference", _DOSJA / "bri410.py")
ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ref)


class TestPaketaEPublikimit(unittest.TestCase):
    def test_vektoret_ne_anglisht(self):
        data = json.loads((_DOSJA / "test_vectors.json").read_text(encoding="utf-8"))
        for v in data["block_cipher"]:
            self.assertEqual(ref.encrypt_block(bytes.fromhex(v["key"]), bytes.fromhex(v["tweak"]),
                                               bytes.fromhex(v["plaintext"])).hex(), v["ciphertext"])
        for v in data["aead"]["vectors"]:
            self.assertEqual(ref.encrypt(bytes.fromhex(v["key"]), bytes.fromhex(v["message"]),
                                         bytes.fromhex(v["associated_data"]), bytes.fromhex(v["nonce"])).hex(),
                             v["packet"])

    def test_perputhja_e_rastesishme_me_projektin(self):
        rng = random.Random(140)
        for _ in range(10):
            k, t, m = bri8.gjenero_celes(), rng.randbytes(16), rng.randbytes(64)
            self.assertEqual(ref.encrypt_block(k, t, m), bri8.BRI410_8(k, 16, t).kripto(m))
            self.assertEqual(ref.decrypt_block(k, t, ref.encrypt_block(k, t, m)), m)
            n, msg, ad = rng.randbytes(12), rng.randbytes(rng.randrange(200)), rng.randbytes(rng.randrange(80))
            self.assertEqual(ref.encrypt(k, msg, ad, n), menyra.kripto(k, msg, ad, n))


if __name__ == "__main__":
    unittest.main()
