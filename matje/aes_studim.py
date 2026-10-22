"""AES-256 në Python, VETËM për krahasim në matje (lejon raunde të shkurtuara).

Nuk është implementim për përdorim: është i ngadaltë dhe jo në kohë konstante.
Verifikohet me vektorin FIPS-197 C.3 te teste/test_aes_studim.py.
Raundi i fundit (r) nuk ka MixColumns, si te AES-i standard edhe kur shkurtohet.
"""


def _xtime(a: int) -> int:
    a <<= 1
    return a ^ 0x11B if a & 0x100 else a


def _shumezo(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a = _xtime(a)
        b >>= 1
    return r


def _inversi(a: int) -> int:
    return next((b for b in range(1, 256) if _shumezo(a, b) == 1), 0)


def _rotl8(x: int, n: int) -> int:
    return ((x << n) | (x >> (8 - n))) & 0xFF


SBOX = []
for _x in range(256):
    _b = _inversi(_x)
    SBOX.append(_b ^ _rotl8(_b, 1) ^ _rotl8(_b, 2) ^ _rotl8(_b, 3) ^ _rotl8(_b, 4) ^ 0x63)
SBOX_INV = [0] * 256
for _x, _y in enumerate(SBOX):
    SBOX_INV[_y] = _x
_M2 = [_shumezo(x, 2) for x in range(256)]
_M3 = [_shumezo(x, 3) for x in range(256)]
_RCON = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40]


def orari(celesi: bytes) -> list[list[int]]:
    """15 çelësa raundi për AES-256, secili 16 bajte në rendin e gjendjes (kolonë pas kolone)."""
    if len(celesi) != 32:
        raise ValueError("AES-256 kërkon çelës 32 bajte")
    w = [list(celesi[4 * i:4 * i + 4]) for i in range(8)]
    for i in range(8, 60):
        t = list(w[i - 1])
        if i % 8 == 0:
            t = [SBOX[b] for b in t[1:] + t[:1]]
            t[0] ^= _RCON[i // 8 - 1]
        elif i % 8 == 4:
            t = [SBOX[b] for b in t]
        w.append([a ^ b for a, b in zip(w[i - 8], t)])
    return [w[4 * j] + w[4 * j + 1] + w[4 * j + 2] + w[4 * j + 3] for j in range(15)]


def kripto(bllok: bytes | list[int], rk: list[list[int]], raunde: int = 14) -> list[int]:
    s = [b ^ k for b, k in zip(bllok, rk[0])]
    for i in range(1, raunde + 1):
        s = [SBOX[s[r + 4 * ((c + r) % 4)]] for c in range(4) for r in range(4)]  # SubBytes + ShiftRows
        if i < raunde:
            t = []
            for c in range(0, 16, 4):
                a0, a1, a2, a3 = s[c:c + 4]
                t += (_M2[a0] ^ _M3[a1] ^ a2 ^ a3, a0 ^ _M2[a1] ^ _M3[a2] ^ a3,
                      a0 ^ a1 ^ _M2[a2] ^ _M3[a3], _M3[a0] ^ a1 ^ a2 ^ _M2[a3])
            s = t
        s = [a ^ b for a, b in zip(s, rk[i])]
    return s
