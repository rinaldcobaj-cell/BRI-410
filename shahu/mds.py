"""Matrica MDS 8×8 mbi GF(16) ("kapja"): përzien 8 kutitë e një rreshti.

Ndërtim Cauchy: M[i][j] = 1 / (x_i ⊕ y_j), me x = 0..7 dhe y = 8..15 (16 elemente të ndryshëm).
Çdo matricë Cauchy është MDS: çdo nënmatricë katrore është e kthyeshme, numri i degëve = 9.
"""

from itertools import combinations

from .gf16 import inversi, shumezo

X = list(range(8))
Y = list(range(8, 16))
M = [[inversi(x ^ y) for y in Y] for x in X]


def shumezo_vektorin(matrica: list[list[int]], v: list[int]) -> list[int]:
    rezultati = []
    for rreshti in matrica:
        s = 0
        for a, b in zip(rreshti, v):
            s ^= shumezo(a, b)
        rezultati.append(s)
    return rezultati


def percaktori(matrica: list[list[int]]) -> int:
    """Përcaktori mbi GF(16) me eliminim Gauss (në karakteristikë 2 shenja nuk ka rëndësi)."""
    a = [list(r) for r in matrica]
    n = len(a)
    d = 1
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
    """(numri i nënmatricave katrore, sa prej tyre kanë përcaktor 0). MDS ⇔ 0 singulare."""
    n = len(matrica)
    gjithsej = singulare = 0
    for k in range(1, n + 1):
        for rr in combinations(range(n), k):
            for kk in combinations(range(n), k):
                gjithsej += 1
                if percaktori([[matrica[i][j] for j in kk] for i in rr]) == 0:
                    singulare += 1
    return gjithsej, singulare


def numri_degeve_peshe_te_ulet(matrica: list[list[int]], pesha_max: int = 2) -> int:
    """Minimumi i pesha(hyrje) + pesha(dalje) mbi të gjitha hyrjet me peshë 1..pesha_max."""
    n = len(matrica)
    minimumi = 2 * n
    for w in range(1, pesha_max + 1):
        for pozicionet in combinations(range(n), w):
            for vlerat in _vlera_jozero(w):
                v = [0] * n
                for p, x in zip(pozicionet, vlerat):
                    v[p] = x
                dalja = shumezo_vektorin(matrica, v)
                minimumi = min(minimumi, w + sum(1 for x in dalja if x))
    return minimumi


def _vlera_jozero(w: int):
    if w == 0:
        yield ()
        return
    for x in range(1, 16):
        for mbetja in _vlera_jozero(w - 1):
            yield (x,) + mbetja


def perziej_rreshtat(gjendja: list[int], matrica: list[list[int]] = M) -> list[int]:
    """Zbaton matricën mbi çdo rresht 8-nibbleësh të gjendjes (version reference, i lexueshëm)."""
    rezultati = []
    for r in range(0, len(gjendja), 8):
        rezultati.extend(shumezo_vektorin(matrica, gjendja[r:r + 8]))
    return rezultati


# K[j][x] = kolona j e M shumëzuar me x, e paketuar si 8 nibble në një numër 32-bitësh.
_K = [[sum(shumezo(M[i][j], x) << (4 * i) for i in range(8)) for x in range(16)] for j in range(8)]


def perziej_shpejt(gjendja: list[int]) -> list[int]:
    """E njëjta si perziej_rreshtat(gjendja, M), me tabela; testet verifikojnë barazinë.

    Meqë M është involutive (M = M⁻¹), shërben edhe për dekriptimin.
    """
    k0, k1, k2, k3, k4, k5, k6, k7 = _K
    rezultati = []
    for r in range(0, len(gjendja), 8):
        a = gjendja[r:r + 8]
        v = (k0[a[0]] ^ k1[a[1]] ^ k2[a[2]] ^ k3[a[3]]
             ^ k4[a[4]] ^ k5[a[5]] ^ k6[a[6]] ^ k7[a[7]])
        rezultati += (v & 15, v >> 4 & 15, v >> 8 & 15, v >> 12 & 15,
                      v >> 16 & 15, v >> 20 & 15, v >> 24 & 15, v >> 28)
    return rezultati
