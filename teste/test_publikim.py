"""Paketa e publikimit: implementimi reference (anglisht, një skedar) duhet të përputhet me projektin."""

import importlib.util
import json
import random
import re
import unittest
from pathlib import Path

from shahu import bri8, mds8, menyra, sbox8

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


class TestPunimiV2PerputhetMeKodin(unittest.TestCase):
    """Konstantet dhe vektorët e shtojcave A–B të punimit v2 (anglisht dhe shqip) = kodi i v1.1."""

    def test_shtojcat(self):
        celesi2, numri2, mesazhi2 = bytes(range(51)) + b"\x02", bytes(range(16)), bytes(range(64))
        pritur = [bri8.BRI410_8(bytes(52), 16, bytes(16)).kripto(bytes(64)).hex(),
                  bri8.BRI410_8(celesi2, 16, numri2).kripto(mesazhi2).hex()]
        self.assertEqual(pritur, [ref.encrypt_block(bytes(52), bytes(16), bytes(64)).hex(),
                                  ref.encrypt_block(celesi2, numri2, mesazhi2).hex()])
        for emri, fillimi in (("BRI-410_v2.md", "## Appendix A"), ("BRI-410_v2_shqip.md", "## Shtojca A")):
            md = (_DOSJA.parent / "paper" / emri).read_text(encoding="utf-8")
            shtojca = md[md.index(fillimi):]
            blloqet = re.findall(r"```\n(.*?)```", shtojca, re.S)
            self.assertEqual([int(h, 16) for h in blloqet[0].split()], sbox8.SBOX, emri)
            rreshtat = [r.split() for r in blloqet[1].strip().splitlines()[1:]]
            self.assertEqual([[int(h, 16) for h in r[:8]] for r in rreshtat], mds8.M, emri)
            self.assertEqual([[int(h, 16) for h in r[8:]] for r in rreshtat], mds8.M_INV, emri)
            self.assertIn(hex(bri8._MBUSHJA), shtojca, emri)
            kriptuar = ["".join(m) for m in re.findall(r"=\s*([0-9a-f]{64})\s*\n\s*([0-9a-f]{64})", blloqet[2])]
            self.assertEqual(kriptuar, pritur, emri)


if __name__ == "__main__":
    unittest.main()
