"""BRI-410: reference implementation (single file, Python 3.10+, standard library only).

Author: Rinald Cobaj. License: CC0 1.0 Universal (public domain), see LICENSE. BRI-410 is not patented.

BRI-410/8 is a tweakable block cipher with a 512-bit block (8x8 board of bytes), a 410-bit key,
a 128-bit tweak ("every game is played only once") and 16 rounds. This file implements version 1.1:
the tweak is injected with 8 mixing steps and a feed-forward, designed so that the round keys of one
tweak do not reveal the state shared by all tweaks. This one-wayness is a conjecture, not a proven
property. Version 1.0 used 4 steps without feed-forward.
BRI-410 AE is the ThetaCB3 authenticated-encryption mode on top of it, with a 416-bit tag.

STUDY CIPHER. Not analysed by independent cryptanalysts yet. DO NOT USE TO PROTECT REAL DATA.
This implementation is written for clarity, not speed, and is NOT constant-time.

Usage:
    key = generate_key()                                  # 52 bytes, top 6 bits zero
    packet = encrypt(key, b"message", associated_data=b"header")
    assert decrypt(key, packet, associated_data=b"header") == b"message"
"""

import hashlib
import hmac
import secrets

KEY_BITS = 410
KEY_BYTES = 52
BLOCK_BYTES = 64
TWEAK_BYTES = 16
ROUNDS = 16
NONCE_BYTES = 12
TAG_BYTES = 52
STATE_BYTES = 80          # key-schedule state: 10 rows of 8 bytes
MIX_CONSTANT = 0xF0       # step constants of the key/tweak mixing: 0xF0..0xFB
VERSION = "1.1"

# ---------------------------------------------------------------- GF(2^8), polynomial x^8+x^4+x^3+x+1


def gf_mul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11B
        b >>= 1
    return r


GF_INV = [0] + [next(b for b in range(1, 256) if gf_mul(a, b) == 1) for a in range(1, 256)]

# ---------------------------------------------------------------- S-box: affine transform of the field inverse


def _parity(x: int) -> int:
    return bin(x).count("1") & 1


def _rank(rows: list[int]) -> int:
    rows, rank = list(rows), 0
    for bit in range(8):
        pivot = next((i for i in range(rank, 8) if rows[i] >> bit & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(8):
            if i != rank and rows[i] >> bit & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def _derive_sbox() -> list[int]:
    """First n (4-byte big-endian counter) with an invertible A and no fixed / opposite-fixed points."""
    for n in range(1 << 16):
        d = hashlib.shake_256(b"BRI-410 S-box8 v1" + n.to_bytes(4, "big")).digest(9)
        a, c = d[:8], d[8]
        if _rank(list(a)) < 8:
            continue
        s = [sum(_parity(a[i] & GF_INV[x]) << i for i in range(8)) ^ c for x in range(256)]
        if all(s[x] != x and s[x] != x ^ 0xFF for x in range(256)):
            return s
    raise RuntimeError("no S-box found")


SBOX = _derive_sbox()
SBOX_INV = [SBOX.index(y) for y in range(256)]

# ---------------------------------------------------------------- theta: 8x8 Cauchy MDS matrix over GF(2^8)


def _derive_y() -> list[int]:
    y = []
    for b in hashlib.shake_256(b"BRI-410 MDS8 v1").digest(256):
        if b >= 8 and b not in y:
            y.append(b)
        if len(y) == 8:
            return y
    raise RuntimeError("not enough distinct bytes")


def _invert(m: list[list[int]]) -> list[list[int]]:
    a = [list(r) + [int(i == j) for j in range(8)] for i, r in enumerate(m)]
    for k in range(8):
        p = next(i for i in range(k, 8) if a[i][k])
        a[k], a[p] = a[p], a[k]
        inv = GF_INV[a[k][k]]
        a[k] = [gf_mul(inv, v) for v in a[k]]
        for i in range(8):
            if i != k and a[i][k]:
                f = a[i][k]
                a[i] = [v ^ gf_mul(f, w) for v, w in zip(a[i], a[k])]
    return [r[8:] for r in a]


MDS_Y = _derive_y()
MDS = [[GF_INV[x ^ y] for y in MDS_Y] for x in range(8)]
MDS_INV = _invert(MDS)


def theta(state: list[int], matrix: list[list[int]] = MDS) -> list[int]:
    """Multiply every row (8 consecutive bytes) by the matrix."""
    out = []
    for r in range(0, len(state), 8):
        row = state[r:r + 8]
        out += [_xor_all(gf_mul(matrix[i][j], row[j]) for j in range(8)) for i in range(8)]
    return out


def _xor_all(values) -> int:
    r = 0
    for v in values:
        r ^= v
    return r

# ---------------------------------------------------------------- pi: the knight's move
# Cell (r, k), index 8r + k, makes k knight jumps (dr, dk) on a toroidal board, then the board shifts by beta columns:
#     (r, k) -> (r + k*dr, k + k*dk + beta) mod 8


DIRECTIONS = [(1, 2), (1, -2), (-1, 2), (-1, -2)]


def knight_permutation(direction: tuple[int, int], beta: int) -> list[int]:
    """P[i] = new position of cell i."""
    dr, dk = direction
    return [8 * ((r + k * dr) % 8) + (k + k * dk + beta) % 8 for r in range(8) for k in range(8)]

# ---------------------------------------------------------------- key / tweak schedule ("the game")


_PADDING = int.from_bytes(hashlib.shake_256(b"BRI-410/8 mbushja").digest(29), "little") & ((1 << 230) - 1)


def _step(g: list[int], i: int) -> list[int]:
    """S on 80 bytes -> theta on 10 rows -> byte j moves to 9*j mod 80 -> byte 79 ^= i."""
    h = theta([SBOX[v] for v in g])
    out = [0] * STATE_BYTES
    for j, v in enumerate(h):
        out[(9 * j) % STATE_BYTES] = v
    out[79] ^= i
    return out


def key_from_bytes(key: bytes) -> int:
    if len(key) != KEY_BYTES:
        raise ValueError("key must be 52 bytes")
    k = int.from_bytes(key, "little")
    if k >> KEY_BITS:
        raise ValueError("the top 6 bits of the key must be zero (410-bit key)")
    return k


def schedule(key: bytes, tweak: bytes, rounds: int = ROUNDS) -> list[tuple[list[int], list[int] | None]]:
    """[(RK_0, None), (RK_1, P_1), ..., (RK_R, P_R)]: 512-bit round keys and knight permutations."""
    if len(tweak) != TWEAK_BYTES:
        raise ValueError("tweak must be 16 bytes")
    k = key_from_bytes(key)
    g = list((k | (_PADDING << KEY_BITS)).to_bytes(STATE_BYTES, "little"))
    for j in range(4):
        g = _step(g, MIX_CONSTANT + j)
    x = [v ^ (tweak[j] if j < TWEAK_BYTES else 0) for j, v in enumerate(g)]   # X = K* xor tweak
    g = x
    for j in range(4, 12):
        g = _step(g, MIX_CONSTANT + j)
    g = [a ^ b for a, b in zip(g, x)]                                          # feed-forward: G_0 = F(X) xor X
    out = [(g[:BLOCK_BYTES], None)]                                            # RK_0 = bytes 0..63 of G_0
    for i in range(1, rounds + 1):
        g = _step(g, i)
        out.append((g[:BLOCK_BYTES], knight_permutation(DIRECTIONS[g[64] & 3], (g[64] >> 2) & 7)))
    return out

# ---------------------------------------------------------------- the tweakable block cipher BRI-410/8


def encrypt_block(key: bytes, tweak: bytes, block: bytes, rounds: int = ROUNDS) -> bytes:
    if len(block) != BLOCK_BYTES:
        raise ValueError("block must be 64 bytes")
    sch = schedule(key, tweak, rounds)
    x = [a ^ b for a, b in zip(block, sch[0][0])]
    for rk, p in sch[1:]:
        y = [0] * BLOCK_BYTES
        for i, v in enumerate(x):
            y[p[i]] = SBOX[v]                         # S, then the knight's move
        x = [a ^ b for a, b in zip(theta(y), rk)]     # theta, then the round key
    return bytes(x)


def decrypt_block(key: bytes, tweak: bytes, block: bytes, rounds: int = ROUNDS) -> bytes:
    if len(block) != BLOCK_BYTES:
        raise ValueError("block must be 64 bytes")
    sch = schedule(key, tweak, rounds)
    x = list(block)
    for rk, p in reversed(sch[1:]):
        y = theta([a ^ b for a, b in zip(x, rk)], MDS_INV)
        x = [SBOX_INV[y[p[i]]] for i in range(BLOCK_BYTES)]
    return bytes(a ^ b for a, b in zip(x, sch[0][0]))

# ---------------------------------------------------------------- BRI-410 AE (ThetaCB3, Krovetz-Rogaway 2011)
# Tweak of every cipher call: nonce (12 bytes) || ((index << 4) | type) as 4 bytes little-endian, index < 2^28.
# Types: 0 message block, 1 mask of the final partial block, 2 tag (no partial block), 3 tag (partial block),
#        4 associated-data block, 5 final partial associated-data block. Associated data uses nonce = 0^12.


class InvalidTag(ValueError):
    """The tag does not verify: message, nonce, associated data or key were modified. Nothing is returned."""


MAX_BLOCKS = (1 << 28) - 1


def _tweak(nonce: bytes, index: int, kind: int) -> bytes:
    return nonce + ((index << 4) | kind).to_bytes(4, "little")


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _pad(x: bytes) -> bytes:
    return x + b"\x80" + bytes(BLOCK_BYTES - len(x) - 1)


def _hash_ad(key: bytes, ad: bytes) -> bytes:
    full = len(ad) // BLOCK_BYTES
    if full > MAX_BLOCKS:
        raise ValueError("associated data too long")
    zero, acc = bytes(NONCE_BYTES), bytes(BLOCK_BYTES)
    for i in range(full):
        acc = _xor(acc, encrypt_block(key, _tweak(zero, i + 1, 4), ad[BLOCK_BYTES * i:BLOCK_BYTES * (i + 1)]))
    if len(ad) % BLOCK_BYTES:
        acc = _xor(acc, encrypt_block(key, _tweak(zero, full, 5), _pad(ad[BLOCK_BYTES * full:])))
    return acc


def encrypt_with_nonce(key: bytes, nonce: bytes, message: bytes, associated_data: bytes = b"") -> bytes:
    """Returns ciphertext || tag (52 bytes). The nonce must NEVER repeat under the same key."""
    if len(nonce) != NONCE_BYTES:
        raise ValueError("nonce must be 12 bytes")
    m = len(message) // BLOCK_BYTES
    if m > MAX_BLOCKS:
        raise ValueError("message too long")
    out, checksum = [], bytes(BLOCK_BYTES)
    for i in range(m):
        mi = message[BLOCK_BYTES * i:BLOCK_BYTES * (i + 1)]
        checksum = _xor(checksum, mi)
        out.append(encrypt_block(key, _tweak(nonce, i + 1, 0), mi))
    rest = message[BLOCK_BYTES * m:]
    if rest:
        out.append(_xor(rest, encrypt_block(key, _tweak(nonce, m, 1), bytes(BLOCK_BYTES))))
        final = encrypt_block(key, _tweak(nonce, m, 3), _xor(checksum, _pad(rest)))
    else:
        final = encrypt_block(key, _tweak(nonce, m, 2), checksum)
    return b"".join(out) + _xor(final, _hash_ad(key, associated_data))[:TAG_BYTES]


def decrypt_with_nonce(key: bytes, nonce: bytes, ciphertext_and_tag: bytes, associated_data: bytes = b"") -> bytes:
    if len(nonce) != NONCE_BYTES:
        raise ValueError("nonce must be 12 bytes")
    if len(ciphertext_and_tag) < TAG_BYTES:
        raise InvalidTag("too short")
    c, tag = ciphertext_and_tag[:-TAG_BYTES], ciphertext_and_tag[-TAG_BYTES:]
    m = len(c) // BLOCK_BYTES
    if m > MAX_BLOCKS:
        raise InvalidTag("too long")
    out, checksum = [], bytes(BLOCK_BYTES)
    for i in range(m):
        mi = decrypt_block(key, _tweak(nonce, i + 1, 0), c[BLOCK_BYTES * i:BLOCK_BYTES * (i + 1)])
        checksum = _xor(checksum, mi)
        out.append(mi)
    rest = c[BLOCK_BYTES * m:]
    if rest:
        last = _xor(rest, encrypt_block(key, _tweak(nonce, m, 1), bytes(BLOCK_BYTES)))
        out.append(last)
        final = encrypt_block(key, _tweak(nonce, m, 3), _xor(checksum, _pad(last)))
    else:
        final = encrypt_block(key, _tweak(nonce, m, 2), checksum)
    if not hmac.compare_digest(tag, _xor(final, _hash_ad(key, associated_data))[:TAG_BYTES]):
        raise InvalidTag("tag mismatch: the message is rejected")
    return b"".join(out)


def generate_key() -> bytes:
    k = bytearray(secrets.token_bytes(KEY_BYTES))
    k[-1] &= 0x03
    return bytes(k)


def encrypt(key: bytes, message: bytes, associated_data: bytes = b"", nonce: bytes | None = None) -> bytes:
    """Packet = nonce (12) || ciphertext || tag (52). A random nonce is generated if none is given."""
    nonce = secrets.token_bytes(NONCE_BYTES) if nonce is None else nonce
    return nonce + encrypt_with_nonce(key, nonce, message, associated_data)


def decrypt(key: bytes, packet: bytes, associated_data: bytes = b"") -> bytes:
    if len(packet) < NONCE_BYTES + TAG_BYTES:
        raise InvalidTag("too short")
    return decrypt_with_nonce(key, packet[:NONCE_BYTES], packet[NONCE_BYTES:], associated_data)
