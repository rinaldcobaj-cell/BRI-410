"""BRI-410/8: VERSIONI ZYRTAR i BRI-410 (vendim i pronarit 2026-10-22, pas F5).

Tabela 8×8 me kuti 8-bitëshe, bllok 512 bit, çelës 410 bit, lojë e re për çdo bllok, 16 raunde.
Përdorimi zyrtar: kripto_bllok(celesi, numri, bllok) / dekripto_bllok(...).
ALGORITËM STUDIMI: mos e përdor për të dhëna reale.

Raundi është si te BRI-410: X ← θ(π_i(S(X))) ⊕ RK_i, me S 8-bitësh, π = lëvizja e kalit (e njëjta,
64 kuti), θ = MDS 8×8 mbi GF(2^8) në çdo rresht. Loja (drejtimi + β, 5 bit) dhe RK_i (512 bit)
nxirren nga (çelësi, numri unik), si te V-N.

Gjendja e orarit: 80 bajte = 10 rreshta × 8.
  bitet 0..409: çelësi; bitet 410..639: konstante publike nga SHAKE-256 (plotësojnë gjendjen)
  hapi F_i: S mbi 80 bajte → MDS mbi 10 rreshta → permutim j → p·j mod 80 → bajti 79 ⊕= i
  K* = F_0xF3(…F_0xF0(çelësi)): 4 hapa që varen vetëm nga çelësi (të përbashkët për të gjitha blloqet)
  X  = K* me bajtet 0..15 ⊕= numri
  v1.0: G_0 = F_0xF7(…F_0xF4(X))                 (4 hapa; i kthyeshëm → nga G_0 del K*)
  v1.1: G_0 = F_0xFB(…F_0xF4(X)) ⊕ X             (8 hapa + feed-forward, që synon ta bëjë kalimin
                                                  G_0 → X të pakthyeshëm; hamendje, e paprovuar)
  RK_0 = bajtet 0..63 të G_0; G_i = F_i(G_{i-1}); RK_i = bajtet 0..63 të G_i;
  lëvizja e raundit i = bajti 64 i G_i (drejtimi: 2 bit, β: 3 bit)

Versioni zyrtar është v1.1 (pas F7: me v1.0, tre çelësa raundesh të një blloku jepnin çelësin kryesor
në 0,1 s, kështu që loja e një blloku zbulonte të gjitha blloqet). v1.0 mbahet për riprodhimin e F5–F7.
"""

import hashlib
from math import gcd

from .levizja import DREJTIMET, inversi, levizja_kalit, perhapja_e_rreshtave
from .mds8 import perziej_shpejt, perziej_shpejt_invers
from .sbox8 import SBOX, SBOX_INV

GJATESIA_CELESIT = 410
BAJTE_GJENDJE = 80
BAJTE_BLLOKU = 64
NUMRI_BAJTE = 16
KONSTANTJA_PERZIERJES = 0xF0
RAUNDE_ZYRTARE = 16  # "16 gurët e çdo lojtari"; rregulli 2 × max(2, 6, 4–5) = 12 ≤ 16 (F5)
VERSIONI = "1.1"
VERSIONET = ("1.0", "1.1")
_MBUSHJA = int.from_bytes(hashlib.shake_256(b"BRI-410/8 mbushja").digest(29), "little") & ((1 << 230) - 1)


def _zgjidh_hapin() -> int:
    for p in range(2, BAJTE_GJENDJE):
        if gcd(p, BAJTE_GJENDJE) == 1:
            perm = [(i * p) % BAJTE_GJENDJE for i in range(BAJTE_GJENDJE)]
            if perhapja_e_rreshtave(perm) == 8:
                return p
    raise RuntimeError("asnjë hap i përshtatshëm")


P_HAPI = _zgjidh_hapin()
PERM = [(i * P_HAPI) % BAJTE_GJENDJE for i in range(BAJTE_GJENDJE)]
PERM_INV = inversi(PERM)
_LEVIZJET = {(d, b): levizja_kalit(d, beta=b) for d in DREJTIMET for b in range(8)}


def ngarko(celesi: int) -> list[int]:
    if not 0 <= celesi < 1 << GJATESIA_CELESIT:
        raise ValueError("çelësi duhet të jetë numër 410-bitësh")
    return list((celesi | (_MBUSHJA << GJATESIA_CELESIT)).to_bytes(BAJTE_GJENDJE, "little"))


def hapi(g: list[int], i: int) -> list[int]:
    h = perziej_shpejt([SBOX[x] for x in g])
    r = [h[j] for j in PERM_INV]  # r[PERM[j]] = h[j]
    r[79] ^= i
    return r


def hapi_invers(g: list[int], i: int) -> list[int]:
    h = list(g)
    h[79] ^= i
    h = [h[PERM[j]] for j in range(BAJTE_GJENDJE)]
    return [SBOX_INV[x] for x in perziej_shpejt_invers(h)]


def para_numrit(celesi: int) -> list[int]:
    """4 hapat e parë të ngarkimit varen vetëm nga çelësi: mjafton t'i llogaritësh një herë për çelës."""
    g = ngarko(celesi)
    for j in range(4):
        g = hapi(g, KONSTANTJA_PERZIERJES + j)
    return g


def ngarko_me_numer(celesi: int, numri: bytes, para: list[int] | None = None,
                    versioni: str = VERSIONI) -> list[int]:
    """G_0 (shih përshkrimin e modulit). Te v1.1, feed-forward-i synon ta bëjë G_0 → X të pakthyeshëm (e paprovuar)."""
    if len(numri) != NUMRI_BAJTE:
        raise ValueError("numri unik duhet të ketë 16 bajte")
    if versioni not in VERSIONET:
        raise ValueError(f"versioni duhet të jetë njëri nga {VERSIONET}")
    x = list(para) if para is not None else para_numrit(celesi)
    for j in range(NUMRI_BAJTE):
        x[j] ^= numri[j]
    g = x
    for j in range(4, 8 if versioni == "1.0" else 12):
        g = hapi(g, KONSTANTJA_PERZIERJES + j)
    return g if versioni == "1.0" else [a ^ b for a, b in zip(g, x)]


def levizja_nga_gjendja(g: list[int]) -> tuple[tuple[int, int], int]:
    return DREJTIMET[g[64] & 3], (g[64] >> 2) & 7


def orari(celesi: int, raunde: int, numri: bytes, para: list[int] | None = None,
          versioni: str = VERSIONI) -> list[tuple[list[int], tuple | None]]:
    if not 1 <= raunde < KONSTANTJA_PERZIERJES:
        raise ValueError("raundet duhet të jenë 1..239")
    g = ngarko_me_numer(celesi, numri, para, versioni)
    rez = [(g[:BAJTE_BLLOKU], None)]
    for i in range(1, raunde + 1):
        g = hapi(g, i)
        rez.append((g[:BAJTE_BLLOKU], levizja_nga_gjendja(g)))
    return rez


def gjenero_celes() -> bytes:
    """52 bajte, 6 bitët e sipërm 0 (i njëjti format si BRI-410)."""
    from .shifra import gjenero_celes as _g
    return _g()


class BRI410_8:
    def __init__(self, celesi: bytes | int, raunde: int, numri: bytes, para: list[int] | None = None,
                 versioni: str = VERSIONI):
        """`para` = para_numrit(çelësi), opsionale: kursen 4 hapa kur i njëjti çelës kripton shumë blloqe."""
        if isinstance(celesi, bytes):
            from .shifra import celesi_nga_bajtet
            celesi = celesi_nga_bajtet(celesi)
        o = orari(celesi, raunde, numri, para, versioni)
        self.raunde = raunde
        self.versioni = versioni
        self._rk = [rk for rk, _ in o]
        self._levizjet = [lv for _, lv in o[1:]]
        p = [_LEVIZJET[lv] for lv in self._levizjet]
        self._mbledh_kriptim = [inversi(pi) for pi in p]
        self._mbledh_dekriptim = p

    def kripto_bajte(self, x: list[int], raunde: int | None = None) -> list[int]:
        rk = self._rk
        x = [a ^ b for a, b in zip(x, rk[0])]
        for i in range(1, (raunde or self.raunde) + 1):
            q = self._mbledh_kriptim[i - 1]
            x = perziej_shpejt([SBOX[x[j]] for j in q])
            x = [a ^ b for a, b in zip(x, rk[i])]
        return x

    def dekripto_bajte(self, y: list[int]) -> list[int]:
        rk = self._rk
        for i in range(self.raunde, 0, -1):
            y = perziej_shpejt_invers([a ^ b for a, b in zip(y, rk[i])])
            p = self._mbledh_dekriptim[i - 1]
            y = [SBOX_INV[y[j]] for j in p]
        return [a ^ b for a, b in zip(y, rk[0])]

    def kripto(self, bllok: bytes) -> bytes:
        if len(bllok) != BAJTE_BLLOKU:
            raise ValueError("blloku duhet të ketë 64 bajte")
        return bytes(self.kripto_bajte(list(bllok)))

    def dekripto(self, bllok: bytes) -> bytes:
        if len(bllok) != BAJTE_BLLOKU:
            raise ValueError("blloku duhet të ketë 64 bajte")
        return bytes(self.dekripto_bajte(list(bllok)))


def kripto_bllok(celesi: bytes, numri: bytes, bllok: bytes) -> bytes:
    """BRI-410 zyrtar: 64 bajte, 16 raunde. `numri` (16 bajte) duhet të jetë unik për çdo bllok me këtë çelës."""
    return BRI410_8(celesi, RAUNDE_ZYRTARE, numri).kripto(bllok)


def dekripto_bllok(celesi: bytes, numri: bytes, bllok: bytes) -> bytes:
    return BRI410_8(celesi, RAUNDE_ZYRTARE, numri).dekripto(bllok)
