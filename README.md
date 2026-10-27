# BRI-410

**A 512-bit tweakable block cipher with key- and tweak-dependent permutations. Current version: BRI-410 v1.1.**

Author: **Rinald Cobaj** (vlorarino@gmail.com) · License: **CC0 1.0** (public domain, see `LICENSE`) · Not patented

> **Study cipher.** BRI-410 has not yet been analysed by independent cryptanalysts. **Do not use it to protect real data.**
> Its purpose is to be analysed, challenged and, if possible, broken. Every result will be acknowledged. See Section 12 of the paper.

| | |
|---|---|
| Block | 512 bits (8×8 board of bytes) |
| Key | 410 bits (a symbolic choice: ≈ 10^123, the game-tree complexity of chess) |
| Tweak | 128 bits: every block plays its own "game" |
| Rounds | 16 |
| Mode | BRI-410 AE (ΘCB3) with a 416-bit tag |
| Proven | ≥ 81 active S-boxes in any 4-round differential characteristic or linear trail, for every key, tweak and choice of permutations (this is **not** a proof of overall security) |
| Security target | 2^256 time, 2^128 data: a **conjecture**, not a demonstrated result |
| Best attack found | 4 rounds in practice (round key RK_4 only); 5 rounds estimated |

## Start here

- **Paper (version 2, describes v1.1):** [`publikim/paper/BRI-410_v2.pdf`](publikim/paper/BRI-410_v2.pdf). It contains the specification,
  proofs, experiments in five categories, the design history with all negative results, security conjectures and open problems.
  Every statement is labelled as a proof, computation, experiment, estimate, conjecture or open question.
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

## Versions and history

| Version | Git tag | Status |
|---|---|---|
| BRI-410 v1.0 | [`v1.0`](../../tree/v1.0) | Superseded. In v1.0, three consecutive round keys of one block revealed the master key in 0.1 s (paper v2, Section 7). Kept public on purpose, as part of the scientific record. Paper version 1: `publikim/paper/BRI-410.pdf`. |
| **BRI-410 v1.1** | [`v1.1`](../../tree/v1.1) | **Current.** Same round function. The tweak injection uses 8 steps and a Davies–Meyer feed-forward. |

The research code can still reproduce v1.0 (`BRI410_8(..., versioni="1.0")`), and its test vectors are kept in `teste/vektoret_f5.json`.

## Repository layout

| Path | Contents |
|---|---|
| `publikim/` | papers (version 2 and version 1, English PDFs and sources, Albanian translations), reference implementation, test vectors |
| `shahu/` | research implementation: `bri8.py` (BRI-410/8, v1.1 and v1.0), `menyra.py` (AE), and the earlier 4-bit version `shifra.py` (BRI-410/4) |
| `matje/` | every experiment and measurement in the papers, e.g. `python -m matje.f8_k_rregullimi`. `f4b_milp.py` (CP-SAT bounds) needs `pip install ortools` |
| `teste/` | test suite: `python -m unittest discover -s teste -t .` (it also checks that the constants and test vectors in the paper match the code) |
| `docs/` | design reports F0–F8 (in Albanian), in the order the design was developed |

The research code uses Albanian identifiers. The reference implementation and the papers are in English.
"Shahu" (Albanian for "chess") was the working name of the project.

## Contact

Results, attacks and questions: vlorarino@gmail.com. Every result will be acknowledged.
