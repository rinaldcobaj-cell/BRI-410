# BRI-410

**A chess-inspired tweakable block cipher with a 410-bit key, designed by measurement.**

Author: **Rinald Cobaj** (vlorarino@gmail.com) · License: **CC0 1.0** (public domain, see `LICENSE`) · Not patented

> **Study cipher.** BRI-410 has not yet been analysed by independent cryptanalysts. **Do not use it to protect real data.**
> Cryptanalysis is very welcome. See the challenges in the paper.

| | |
|---|---|
| Block | 512 bits (8×8 board of bytes) |
| Key | 410 bits (≈ 10^123, the game-tree complexity of chess) |
| Tweak | 128 bits: every block plays its own "game" |
| Rounds | 16 |
| Mode | BRI-410 AE (ΘCB3) with a 416-bit tag |
| Proven bound | ≥ 81 active S-boxes in 4 rounds (≤ 2^-486), ≥ 90 in 6 rounds (≤ 2^-540), for every key and tweak |
| Best attack found | 4 rounds in practice, 5 rounds estimated at ≈ 2^72 |

## Start here

- **Paper:** [`publikim/paper/BRI-410.pdf`](publikim/paper/BRI-410.pdf). It contains the specification, design rationale,
  analysis, security claims, open problems and challenges.
- **Reference implementation:** [`publikim/reference/bri410.py`](publikim/reference/bri410.py). A single file that uses only the
  Python standard library.
- **Test vectors:** `publikim/reference/test_vectors.json`. To check them:

```
cd publikim/reference
python verify.py          # prints ALL PASSED
```

```python
import bri410
key = bri410.generate_key()
packet = bri410.encrypt(key, b"message", associated_data=b"header")
assert bri410.decrypt(key, packet, associated_data=b"header") == b"message"
```

## Repository layout

| Path | Contents |
|---|---|
| `publikim/` | paper (English PDF + source), reference implementation, test vectors |
| `shahu/` | research implementation: `bri8.py` (BRI-410/8), `menyra.py` (AE), and the earlier 4-bit version `shifra.py` (BRI-410/4) |
| `matje/` | every experiment and measurement in the paper, e.g. `python -m matje.f5_matjet`. `f4b_milp.py` (CP-SAT bounds) needs `pip install ortools` |
| `teste/` | test suite: `python -m unittest discover -s teste -t .` |
| `docs/` | design reports F0–F6 (in Albanian), in the order the design was developed |

The research code uses Albanian identifiers. The reference implementation and the paper are in English.
"Shahu" (Albanian for "chess") was the working name of the project.

## Contact

Results, attacks and questions: vlorarino@gmail.com. Every result will be acknowledged.
