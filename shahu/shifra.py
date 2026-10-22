"""BRI-410/4: versioni i parë (kuti 4-bitëshe, bllok 256 bit), i mbajtur për matjet F1–F4-a.

VERSIONI ZYRTAR është BRI-410/8 me 16 raunde (shahu/bri8.py, vendim i pronarit 2026-10-22, pas F5).
ALGORITËM STUDIMI: mos e përdor për të dhëna reale.

    X ← X ⊕ RK_0
    për i = 1 .. R:  X ← θ(π_i(S(X))) ⊕ RK_i

Të gjitha raundet janë identike: θ mbahet edhe në raundin e fundit (vendim F2; θ është
involutive, kështu që dekriptimi përdor të njëjtën matricë).
Bajtet → nibble: nibble 2i = 4 bitët e ulët të bajtit i, nibble 2i+1 = 4 bitët e lartë.
Çelësi si bajte: 52 bajte little-endian, 6 bitët e sipërm (të bajtit 51) duhet të jenë 0.

Variantet: VF (lëvizje fikse), VL (loja sipas çelësit), VN (loja sipas bllokut, F3-bis).
VN kërkon `numri`: 16 bajte publike, UNIKE për çdo bllok (p.sh. numri i mesazhit + numri i bllokut).
Nëse i njëjti numër përdoret dy herë me të njëjtin çelës, VN bie në nivelin e VL.
"""

import secrets

from . import celesi as _celesi
from .levizja import DREJTIMET, inversi, levizja_kalit
from .mds import M, M_INV, perziej_shpejt
from .sbox import SBOX, SBOX_INV

GJATESIA_BLLOKUT = 32
GJATESIA_CELESIT_BAJTE = 52
VARIANTET = ("VF", "VL")  # variantet ku loja varet vetëm nga çelësi
VARIANTET_TE_GJITHA = VARIANTET + ("VN",)

assert M == M_INV, "perziej_shpejt shërben për dekriptimin vetëm nëse M është involutive"

_VF = levizja_kalit()
_VL = {(d, b): levizja_kalit(d, beta=b) for d in DREJTIMET for b in range(8)}


def gjenero_celes() -> bytes:
    """Çelës i ri 410-bitësh nga gjeneratori kriptografik i sistemit."""
    b = bytearray(secrets.token_bytes(GJATESIA_CELESIT_BAJTE))
    b[-1] &= 0x03
    return bytes(b)


def celesi_nga_bajtet(b: bytes) -> int:
    if len(b) != GJATESIA_CELESIT_BAJTE:
        raise ValueError("çelësi duhet të ketë 52 bajte")
    k = int.from_bytes(b, "little")
    if k >> _celesi.GJATESIA_CELESIT:
        raise ValueError("6 bitët e sipërm të çelësit duhet të jenë 0 (çelësi ka 410 bit)")
    return k


def bajte_ne_nibla(b: bytes) -> list[int]:
    if len(b) != GJATESIA_BLLOKUT:
        raise ValueError("blloku duhet të ketë 32 bajte")
    nibla = []
    for x in b:
        nibla += (x & 15, x >> 4)
    return nibla


def nibla_ne_bajte(n: list[int]) -> bytes:
    return bytes(n[i] | n[i + 1] << 4 for i in range(0, 64, 2))


class BRI410:
    def __init__(self, celesi: bytes | int, raunde: int = 32, varianti: str = "VL",
                 numri: bytes | None = None):
        if varianti not in VARIANTET_TE_GJITHA:
            raise ValueError(f"varianti duhet të jetë njëri nga {VARIANTET_TE_GJITHA}")
        if (varianti == "VN") != (numri is not None):
            raise ValueError("`numri` kërkohet te VN dhe nuk pranohet te VF/VL")
        if raunde < 1:
            raise ValueError("duhet të paktën 1 raund")
        k = celesi if isinstance(celesi, int) else celesi_nga_bajtet(celesi)
        orari = _celesi.orari(k, raunde, numri)
        self.raunde = raunde
        self.varianti = varianti
        self._rk = [rk for rk, _ in orari]
        self._levizjet = [lv for _, lv in orari[1:]]
        p = [_VF] * raunde if varianti == "VF" else [_VL[lv] for lv in self._levizjet]
        # Formë "mbledhjeje": y[j] = x[q[j]], me q = p⁻¹ për kriptimin dhe q = p për dekriptimin.
        self._mbledh_kriptim = [inversi(pi) for pi in p]
        self._mbledh_dekriptim = p

    def kripto_nibla(self, x: list[int], raunde: int | None = None) -> list[int]:
        """`raunde` < R jep versionin e shkurtuar (vetëm për matje)."""
        rk = self._rk
        x = [a ^ b for a, b in zip(x, rk[0])]
        for i in range(1, (raunde or self.raunde) + 1):
            q = self._mbledh_kriptim[i - 1]
            x = perziej_shpejt([SBOX[x[j]] for j in q])
            x = [a ^ b for a, b in zip(x, rk[i])]
        return x

    def dekripto_nibla(self, y: list[int]) -> list[int]:
        rk = self._rk
        for i in range(self.raunde, 0, -1):
            y = perziej_shpejt([a ^ b for a, b in zip(y, rk[i])])
            p = self._mbledh_dekriptim[i - 1]
            y = [SBOX_INV[y[j]] for j in p]
        return [a ^ b for a, b in zip(y, rk[0])]

    def kripto(self, bllok: bytes) -> bytes:
        return nibla_ne_bajte(self.kripto_nibla(bajte_ne_nibla(bllok)))

    def dekripto(self, bllok: bytes) -> bytes:
        return nibla_ne_bajte(self.dekripto_nibla(bajte_ne_nibla(bllok)))

