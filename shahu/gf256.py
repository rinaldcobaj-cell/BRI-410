"""Aritmetika në GF(2^8) me polinomin x^8 + x^4 + x^3 + x + 1 (0x11B, si te AES)."""

POLINOMI = 0x11B


def _shumezo(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        if a & 0x100:
            a ^= POLINOMI
        b >>= 1
    return r


TABELA = [[_shumezo(a, b) for b in range(256)] for a in range(256)]
INVERSI = [0] + [next(b for b in range(1, 256) if TABELA[a][b] == 1) for a in range(1, 256)]


def shumezo(a: int, b: int) -> int:
    return TABELA[a][b]


def inversi(a: int) -> int:
    if a == 0:
        raise ZeroDivisionError("0 nuk ka invers në GF(256)")
    return INVERSI[a]
