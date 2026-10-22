"""BRI-410 AE: kriptimi i mesazheve të çdo gjatësie me VULË 416 bit, "sa çelësi" (hapi 2).

Vula ka 52 bajte = 416 bit, njësoj sa ruhet çelësi (vendim i pronarit). Mbi ~410 bit, vula nuk shton siguri,
sepse sulmuesi do ta provonte më mirë çelësin, ndaj 416 është maksimumi me kuptim.

ALGORITËM STUDIMI: mos e përdor për të dhëna reale.

Modeli: ΘCB3 (Krovetz–Rogaway, 2011), i provuar i sigurt nëse shifra e bllokut me "lojë" (tweak) është e sigurt.
Nuk shpiket mënyrë e re: ndërtohet modeli i provuar mbi BRI-410/8, ku çdo bllok luan lojën e vet.

Numri 16-bajtësh i çdo thirrjeje të BRI-410/8:
    bajtet 0..11  : numri i mesazhit N (96 bit; zero për të dhënat shoqëruese)
    bajtet 12..15 : (indeksi << 4) | lloji, little-endian, indeksi < 2^28
Llojet: 0 bllok mesazhi · 1 maska e pjesës së fundit · 2 vula (pa pjesë të fundit) · 3 vula (me pjesë të fundit)
        4 bllok shoqërues · 5 pjesa e fundit shoqëruese

Kriptimi, me blloqe 64 bajte, M = M_1 … M_m M_* (|M_*| < 64) dhe A = A_1 … A_a A_*:
    C_i  = E^(N,i,0)(M_i)                                      i = 1..m
    M_* ≠ ∅:  C_* = M_* ⊕ E^(N,m,1)(0⁶⁴)[:|M_*|],  Σ = ⊕ M_i ⊕ pad(M_*),  F = E^(N,m,3)(Σ)
    M_* = ∅:  Σ = ⊕ M_i,                           F = E^(N,m,2)(Σ)
    Auth = ⊕ E^(0,i,4)(A_i)  [⊕ E^(0,a,5)(pad(A_*))],   pad(x) = x ‖ 80 ‖ 00…
    Vula = (F ⊕ Auth)[:52]
Paketa: N ‖ C_1 … C_m C_* ‖ Vula. Dekriptimi nuk kthen asgjë nëse vula nuk përputhet.

RREGULLI: N nuk përsëritet kurrë me të njëjtin çelës. Me N të rastësishëm (parazgjedhja), gjasa e përsëritjes
pas q mesazhesh është ≈ q²/2⁹⁷ (p.sh. 2⁻³³ pas 4 miliardë mesazhesh).
"""

import hmac
import secrets

from . import bri8
from .shifra import celesi_nga_bajtet

GJATESIA_NUMRIT = 12
GJATESIA_VULES = 52  # 416 bit, "sa çelësi"
BLLOKU = bri8.BAJTE_BLLOKU
MAKS_BLLOQE = (1 << 28) - 1


class VulaEGabuar(ValueError):
    """Vula nuk përputhet: mesazhi, numri, të dhënat shoqëruese ose çelësi janë ndryshuar. Mesazhi refuzohet."""


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def _mbush(x: bytes) -> bytes:
    return x + b"\x80" + bytes(BLLOKU - len(x) - 1)


class _Loja:
    """E^(N, indeksi, lloji): BRI-410/8 me lojën e këtij blloku. Hapat që varen vetëm nga çelësi llogariten një herë."""

    def __init__(self, celesi: bytes):
        self._k = celesi_nga_bajtet(celesi)
        self._para = bri8.para_numrit(self._k)

    def __call__(self, n: bytes, indeksi: int, lloji: int) -> bri8.BRI410_8:
        numri = n + ((indeksi << 4) | lloji).to_bytes(4, "little")
        return bri8.BRI410_8(self._k, bri8.RAUNDE_ZYRTARE, numri, self._para)


def _auth(e: _Loja, te_dhena: bytes) -> bytes:
    a = len(te_dhena) // BLLOKU
    if a > MAKS_BLLOQE:
        raise ValueError("të dhënat shoqëruese janë shumë të gjata")
    n0 = bytes(GJATESIA_NUMRIT)
    shuma = bytes(BLLOKU)
    for i in range(a):
        shuma = _xor(shuma, e(n0, i + 1, 4).kripto(te_dhena[BLLOKU * i:BLLOKU * (i + 1)]))
    if len(te_dhena) % BLLOKU:
        shuma = _xor(shuma, e(n0, a, 5).kripto(_mbush(te_dhena[BLLOKU * a:])))
    return shuma


def _kontrollo_numrin(numri: bytes) -> None:
    if len(numri) != GJATESIA_NUMRIT:
        raise ValueError("numri i mesazhit duhet të ketë 12 bajte")


def kripto_me_numer(celesi: bytes, numri: bytes, mesazhi: bytes, te_dhena: bytes = b"") -> bytes:
    """Kthen C ‖ Vula (pa numrin). `numri` (12 bajte) nuk duhet përsëritur kurrë me të njëjtin çelës."""
    _kontrollo_numrin(numri)
    m = len(mesazhi) // BLLOKU
    if m > MAKS_BLLOQE:
        raise ValueError("mesazhi është shumë i gjatë (maksimumi 2^28 − 1 blloqe)")
    e = _Loja(celesi)
    pjeset = []
    sigma = bytes(BLLOKU)
    for i in range(m):
        mi = mesazhi[BLLOKU * i:BLLOKU * (i + 1)]
        sigma = _xor(sigma, mi)
        pjeset.append(e(numri, i + 1, 0).kripto(mi))
    mbetja = mesazhi[BLLOKU * m:]
    if mbetja:
        pjeset.append(_xor(mbetja, e(numri, m, 1).kripto(bytes(BLLOKU))))
        f = e(numri, m, 3).kripto(_xor(sigma, _mbush(mbetja)))
    else:
        f = e(numri, m, 2).kripto(sigma)
    return b"".join(pjeset) + _xor(f, _auth(e, te_dhena))[:GJATESIA_VULES]


def dekripto_me_numer(celesi: bytes, numri: bytes, c_me_vule: bytes, te_dhena: bytes = b"") -> bytes:
    """Kthen mesazhin vetëm nëse vula përputhet; përndryshe ngre VulaEGabuar."""
    _kontrollo_numrin(numri)
    if len(c_me_vule) < GJATESIA_VULES:
        raise VulaEGabuar("paketa është më e shkurtër se vula")
    c, vula = c_me_vule[:-GJATESIA_VULES], c_me_vule[-GJATESIA_VULES:]
    m = len(c) // BLLOKU
    if m > MAKS_BLLOQE:
        raise VulaEGabuar("paketa është shumë e gjatë")
    e = _Loja(celesi)
    pjeset = []
    sigma = bytes(BLLOKU)
    for i in range(m):
        mi = e(numri, i + 1, 0).dekripto(c[BLLOKU * i:BLLOKU * (i + 1)])
        sigma = _xor(sigma, mi)
        pjeset.append(mi)
    mbetja = c[BLLOKU * m:]
    if mbetja:
        m_yll = _xor(mbetja, e(numri, m, 1).kripto(bytes(BLLOKU)))
        pjeset.append(m_yll)
        f = e(numri, m, 3).kripto(_xor(sigma, _mbush(m_yll)))
    else:
        f = e(numri, m, 2).kripto(sigma)
    if not hmac.compare_digest(vula, _xor(f, _auth(e, te_dhena))[:GJATESIA_VULES]):
        raise VulaEGabuar("vula nuk përputhet: mesazhi refuzohet")
    return b"".join(pjeset)


def kripto(celesi: bytes, mesazhi: bytes, te_dhena: bytes = b"", numri: bytes | None = None) -> bytes:
    """Paketa = numri (12) ‖ teksti i kriptuar ‖ vula (52). Pa `numri`, gjenerohet rastësisht."""
    if numri is None:
        numri = secrets.token_bytes(GJATESIA_NUMRIT)
    return numri + kripto_me_numer(celesi, numri, mesazhi, te_dhena)


def dekripto(celesi: bytes, paketa: bytes, te_dhena: bytes = b"") -> bytes:
    if len(paketa) < GJATESIA_NUMRIT + GJATESIA_VULES:
        raise VulaEGabuar("paketa është shumë e shkurtër")
    return dekripto_me_numer(celesi, paketa[:GJATESIA_NUMRIT], paketa[GJATESIA_NUMRIT:], te_dhena)
