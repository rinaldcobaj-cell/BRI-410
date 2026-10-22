"""S-box 8-bitësh i BRI-410/8 (F5): "mbretëresha" në vend të "mbretit".

Ndërtimi: inversi në GF(2^8), pastaj transformim afin A·y ⊕ c, ku A (e kthyeshme) dhe c nxirren
nga SHAKE-256 me etiketë publike. Zgjidhet i pari pa pika fikse (S(x) = x dhe S(x) = x ⊕ FF).
Transformimi afin nuk ndryshon uniformitetin diferencial, linearitetin dhe shkallën, kështu që këto
janë si te inversi (AES): DU 4, jolinearitet 112, shkallë 7. Testet dhe F5 i masin drejtpërdrejt.
"""

import hashlib

from .gf256 import INVERSI

ETIKETA = b"BRI-410 S-box8 v1"


def _pesha(x: int) -> int:
    return bin(x).count("1")


def _rangu(rreshtat: list[int]) -> int:
    rr = list(rreshtat)
    rangu = 0
    for bit in range(8):
        boshti = next((i for i in range(rangu, 8) if rr[i] >> bit & 1), None)
        if boshti is None:
            continue
        rr[rangu], rr[boshti] = rr[boshti], rr[rangu]
        for i in range(8):
            if i != rangu and rr[i] >> bit & 1:
                rr[i] ^= rr[rangu]
        rangu += 1
    return rangu


def _afin(a: list[int], c: int, y: int) -> int:
    return sum((_pesha(a[i] & y) & 1) << i for i in range(8)) ^ c


def gjenero(etiketa: bytes, numeruesi: int) -> list[int] | None:
    b = hashlib.shake_256(etiketa + numeruesi.to_bytes(4, "big")).digest(9)
    a, c = list(b[:8]), b[8]
    if _rangu(a) < 8:
        return None
    return [_afin(a, c, INVERSI[x]) for x in range(256)]


def kerko_sbox(etiketa: bytes = ETIKETA, kufiri: int = 100_000) -> tuple[int, list[int]]:
    for n in range(kufiri):
        s = gjenero(etiketa, n)
        if s and all(s[x] != x and s[x] != x ^ 0xFF for x in range(256)):
            return n, s
    raise RuntimeError("asnjë S-box pa pika fikse brenda kufirit")


def _fwht(f: list[int]) -> list[int]:
    w = list(f)
    h = 1
    while h < len(w):
        for i in range(0, len(w), 2 * h):
            for j in range(i, i + h):
                a, b = w[j], w[j + h]
                w[j], w[j + h] = a + b, a - b
        h *= 2
    return w


def _shkalla(tabela: list[int]) -> int:
    f = list(tabela)
    for i in range(8):
        for x in range(256):
            if x & (1 << i):
                f[x] ^= f[x ^ (1 << i)]
    return max((_pesha(m) for m in range(256) if f[m]), default=0)


def matjet(s: list[int]) -> dict:
    du = 0
    for a in range(1, 256):
        numero = [0] * 256
        for x in range(256):
            numero[s[x] ^ s[x ^ a]] += 1
        du = max(du, max(numero))
    lin = 0
    shkallet = []
    for b in range(1, 256):
        komponenti = [_pesha(b & s[x]) & 1 for x in range(256)]
        lin = max(lin, max(abs(v) for v in _fwht([1 - 2 * v for v in komponenti])))
        shkallet.append(_shkalla(komponenti))
    return {
        "uniformiteti_diferencial": du, "lineariteti": lin, "jolineariteti": 128 - lin // 2,
        "shkalla_min": min(shkallet), "shkalla_max": max(shkallet),
        "pika_fikse": (sum(s[x] == x for x in range(256)), sum(s[x] == x ^ 0xFF for x in range(256))),
    }


def inversi(s: list[int]) -> list[int]:
    inv = [0] * 256
    for x, y in enumerate(s):
        inv[y] = x
    return inv


NUMERUESI_SBOX, SBOX = kerko_sbox()
SBOX_INV = inversi(SBOX)
