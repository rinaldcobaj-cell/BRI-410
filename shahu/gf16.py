"""Aritmetika në fushën GF(2^4) me polinomin e pazbërthyeshëm x^4 + x + 1."""

POLINOMI = 0x13


def _shumezo(a: int, b: int) -> int:
    rezultati = 0
    for _ in range(4):
        if b & 1:
            rezultati ^= a
        b >>= 1
        a <<= 1
        if a & 0x10:
            a ^= POLINOMI
    return rezultati


TABELA = [[_shumezo(a, b) for b in range(16)] for a in range(16)]
INVERSI = [0] + [next(b for b in range(1, 16) if TABELA[a][b] == 1) for a in range(1, 16)]


def shumezo(a: int, b: int) -> int:
    return TABELA[a][b]


def inversi(a: int) -> int:
    if a == 0:
        raise ZeroDivisionError("0 nuk ka invers në GF(16)")
    return INVERSI[a]
