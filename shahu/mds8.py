"""Matrica MDS 8×8 mbi GF(2^8) e BRI-410/8 ("kapja" me kuti 8-bitëshe).

Cauchy: M[i][j] = 1 / (x_i ⊕ y_j), x = 0..7, y = 8 bajtet e para të ndryshëm (dhe jo në x) nga
SHAKE-256("BRI-410 MDS8 v1"). Ndryshe nga matrica 4-bitëshe (x ⊕ y = 8 ⊕ i ⊕ j, pra diadike me 8
simetri), y-të "të rastësishme" synojnë të mos lënë simetri. F5 e mat këtë.
"""

import hashlib
from itertools import combinations

from .gf256 import inversi, shumezo

X = list(range(8))


def _y() -> list[int]:
    y = []
    for b in hashlib.shake_256(b"BRI-410 MDS8 v1").digest(256):
        if b not in X and b not in y:
            y.append(b)
        if len(y) == 8:
            return y
    raise RuntimeError


Y = _y()
M = [[inversi(x ^ y) for y in Y] for x in X]


def shumezo_vektorin(matrica: list[list[int]], v: list[int]) -> list[int]:
    rez = []
    for rreshti in matrica:
        s = 0
        for a, b in zip(rreshti, v):
            s ^= shumezo(a, b)
        rez.append(s)
    return rez


def percaktori(matrica: list[list[int]]) -> int:
    a = [list(r) for r in matrica]
    n, d = len(a), 1
    for k in range(n):
        boshti = next((i for i in range(k, n) if a[i][k]), None)
        if boshti is None:
            return 0
        a[k], a[boshti] = a[boshti], a[k]
        d = shumezo(d, a[k][k])
        inv = inversi(a[k][k])
        for i in range(k + 1, n):
            if a[i][k]:
                f = shumezo(a[i][k], inv)
                a[i] = [x ^ shumezo(f, y) for x, y in zip(a[i], a[k])]
    return d


def matrica_inverse(matrica: list[list[int]]) -> list[list[int]]:
    n = len(matrica)
    a = [list(r) + [int(i == j) for j in range(n)] for i, r in enumerate(matrica)]
    for k in range(n):
        boshti = next(i for i in range(k, n) if a[i][k])
        a[k], a[boshti] = a[boshti], a[k]
        inv = inversi(a[k][k])
        a[k] = [shumezo(inv, x) for x in a[k]]
        for i in range(n):
            if i != k and a[i][k]:
                f = a[i][k]
                a[i] = [x ^ shumezo(f, y) for x, y in zip(a[i], a[k])]
    return [r[n:] for r in a]


M_INV = matrica_inverse(M)


def nenmatricat_singulare(matrica: list[list[int]]) -> tuple[int, int]:
    n = len(matrica)
    gjithsej = singulare = 0
    for k in range(1, n + 1):
        for rr in combinations(range(n), k):
            for kk in combinations(range(n), k):
                gjithsej += 1
                singulare += percaktori([[matrica[i][j] for j in kk] for i in rr]) == 0
    return gjithsej, singulare


def perziej_rreshtat(gjendja: list[int], matrica: list[list[int]] = M) -> list[int]:
    """Version reference: matrica mbi çdo rresht 8-bajtësh."""
    rez = []
    for r in range(0, len(gjendja), 8):
        rez.extend(shumezo_vektorin(matrica, gjendja[r:r + 8]))
    return rez


def _tabelat(matrica: list[list[int]]) -> list[list[int]]:
    return [[sum(shumezo(matrica[i][j], x) << (8 * i) for i in range(8)) for x in range(256)]
            for j in range(8)]


_K, _K_INV = _tabelat(M), _tabelat(M_INV)


def _perziej(gjendja: list[int], k: list[list[int]]) -> list[int]:
    k0, k1, k2, k3, k4, k5, k6, k7 = k
    rez = []
    for r in range(0, len(gjendja), 8):
        a = gjendja[r:r + 8]
        v = (k0[a[0]] ^ k1[a[1]] ^ k2[a[2]] ^ k3[a[3]]
             ^ k4[a[4]] ^ k5[a[5]] ^ k6[a[6]] ^ k7[a[7]])
        rez += v.to_bytes(8, "little")
    return rez


def perziej_shpejt(gjendja: list[int]) -> list[int]:
    return _perziej(gjendja, _K)


def perziej_shpejt_invers(gjendja: list[int]) -> list[int]:
    return _perziej(gjendja, _K_INV)
