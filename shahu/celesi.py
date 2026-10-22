"""Orari i çelësit: çelësi 410-bitësh → "loja" (çelësat e raundeve + lëvizjet e kalit).

Gjendja e çelësit ka 416 bit = 104 nibble = 13 rreshta × 8.
  bitet 0..409   : çelësi
  bitet 410..415 : konstante fikse BITET_FIKSE (plotësojnë 416)
Çdo hap F_i (i = 1, 2, …) është bijeksion:
  S-box mbi 104 nibble → MDS mbi 13 rreshta → permutim me hap P_HAPI → XOR i numëruesit i
Çelësi i raundit i: nibble 0..63 pas hapit i (RK_0 = 256 bitët e parë të çelësit, pa përpunim).
Lëvizja e raundit i: nibble 64, 65 pas hapit i → drejtimi (2 bit), beta (3 bit); alfa = 0.
Alfa (zhvendosja e rreshtave) është fiksuar në 0 sepse komuton me gjithë raundin pa çelës
(F1, M3), pra nuk ndryshon strukturën: do të ishte "lojë" vetëm në dukje.

Loja sipas bllokut (V-N, F3-bis): çdo bllok luan lojën e vet, që nuk përsëritet.
  gjendja = F_{F7..F4}( F_{F3..F0}(çelësi) ⊕ numri )
Çelësi përzihet vetëm në 4 hapa (difuzion i plotë pas 3), futet numri unik 128-bitësh
(nibble 0..31), dhe përzihet në 4 hapa të tjerë. Numri nuk futet direkt mbi çelësin:
përndryshe zgjedhja e numrit do të ishte zgjedhje e një "çelësi të lidhur".
Hapat e përzierjes përdorin konstantet 0xF0..0xF7, të ndryshme nga ato të raundeve (1..R < 0xF0).
"""

from math import gcd

from .mds import perziej_shpejt
from .levizja import DREJTIMET, perhapja_e_rreshtave
from .sbox import SBOX, SBOX_INV

GJATESIA_CELESIT = 410
BITET_FIKSE = 0b101101
NIBLA = 104
RRESHTA = NIBLA // 8


def _zgjidh_hapin() -> int:
    """Hapi më i vogël p (gcd(p, 104) = 1) që shpërndan çdo rresht në 8 rreshta të ndryshëm."""
    for p in range(2, NIBLA):
        if gcd(p, NIBLA) == 1:
            perm = [(i * p) % NIBLA for i in range(NIBLA)]
            if perhapja_e_rreshtave(perm) == 8:
                return p
    raise RuntimeError("asnjë hap i përshtatshëm")


P_HAPI = _zgjidh_hapin()
PERM = [(i * P_HAPI) % NIBLA for i in range(NIBLA)]
PERM_INV = [0] * NIBLA
for _i, _j in enumerate(PERM):
    PERM_INV[_j] = _i


def ngarko(celesi: int) -> list[int]:
    if not 0 <= celesi < 1 << GJATESIA_CELESIT:
        raise ValueError("çelësi duhet të jetë numër 410-bitësh")
    v = celesi | (BITET_FIKSE << GJATESIA_CELESIT)
    return [(v >> (4 * j)) & 0xF for j in range(NIBLA)]


def _konstantja(gjendja: list[int], i: int) -> None:
    gjendja[100] ^= i & 0xF
    gjendja[101] ^= (i >> 4) & 0xF


def hapi(gjendja: list[int], i: int) -> list[int]:
    g = perziej_shpejt([SBOX[x] for x in gjendja])
    rezultati = [0] * NIBLA
    for j, x in enumerate(g):
        rezultati[PERM[j]] = x
    _konstantja(rezultati, i)
    return rezultati


def hapi_invers(gjendja: list[int], i: int) -> list[int]:
    g = list(gjendja)
    _konstantja(g, i)
    g = [g[PERM[j]] for j in range(NIBLA)]
    return [SBOX_INV[x] for x in perziej_shpejt(g)]  # M është involutive


def levizja_nga_gjendja(gjendja: list[int]) -> tuple[tuple[int, int], int]:
    n0, n1 = gjendja[64], gjendja[65]
    return DREJTIMET[n0 & 3], (n0 >> 2) | ((n1 & 1) << 2)


NUMRI_BAJTE = 16
KONSTANTJA_PERZIERJES = 0xF0


def ngarko_me_numer(celesi: int, numri: bytes) -> list[int]:
    """Gjendja fillestare e lojës sipas bllokut (V-N): çelësi → 4 hapa → ⊕ numri → 4 hapa."""
    if len(numri) != NUMRI_BAJTE:
        raise ValueError("numri unik duhet të ketë 16 bajte")
    g = ngarko(celesi)
    for j in range(4):
        g = hapi(g, KONSTANTJA_PERZIERJES + j)
    n = int.from_bytes(numri, "little")
    for j in range(2 * NUMRI_BAJTE):
        g[j] ^= (n >> (4 * j)) & 0xF
    for j in range(4, 8):
        g = hapi(g, KONSTANTJA_PERZIERJES + j)
    return g


def orari(celesi: int, raunde: int, numri: bytes | None = None) -> list[tuple[list[int], tuple | None]]:
    """[(RK_0, None), (RK_1, lëvizja_1), …, (RK_R, lëvizja_R)]; lëvizja = (drejtimi, beta).

    Me `numri` (V-N), i gjithë orari nxirret nga (çelësi, numri).
    """
    if not 0 <= raunde < KONSTANTJA_PERZIERJES:
        raise ValueError("raundet duhet të jenë më pak se 240")
    gjendja = ngarko(celesi) if numri is None else ngarko_me_numer(celesi, numri)
    rezultati = [(gjendja[:64], None)]
    for i in range(1, raunde + 1):
        gjendja = hapi(gjendja, i)
        rezultati.append((gjendja[:64], levizja_nga_gjendja(gjendja)))
    return rezultati
