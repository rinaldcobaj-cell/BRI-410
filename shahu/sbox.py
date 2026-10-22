"""S-box 4-bitësh ("zëvendësimi i figurave"): gjenerimi dhe matja e kritereve.

S-box-i nxirret pa "mister": permutacione të njëpasnjëshme nga SHAKE-256 me etiketë publike,
dhe zgjidhet i pari që plotëson të gjitha kriteret. Kështu kushdo mund ta riprodhojë.
"""

import hashlib

# Etiketa mban emrin e punës "Shahu" (para emrit BRI-410): po të ndryshohej, do të dilte një S-box tjetër.
ETIKETA = b"Shahu S-box v1"


def gjenero_permutacion(etiketa: bytes, numeruesi: int) -> list[int]:
    """Fisher–Yates me bajte nga SHAKE-256; refuzimi mënjanon njëanshmërinë e modulit."""
    rrjedha = hashlib.shake_256(etiketa + numeruesi.to_bytes(4, "big")).digest(256)
    p = list(range(16))
    pozicioni = 0
    for i in range(15, 0, -1):
        kufiri = 256 - 256 % (i + 1)
        while True:
            b = rrjedha[pozicioni]
            pozicioni += 1
            if b < kufiri:
                break
        j = b % (i + 1)
        p[i], p[j] = p[j], p[i]
    return p


def _pesha(x: int) -> int:
    return bin(x).count("1")


def tabela_diferenciale(s: list[int]) -> list[list[int]]:
    ddt = [[0] * 16 for _ in range(16)]
    for a in range(16):
        for x in range(16):
            ddt[a][s[x] ^ s[x ^ a]] += 1
    return ddt


def uniformiteti_diferencial(s: list[int]) -> int:
    ddt = tabela_diferenciale(s)
    return max(ddt[a][b] for a in range(1, 16) for b in range(16))


def tabela_walsh(s: list[int]) -> list[list[int]]:
    """W[a][b] = Σ_x (-1)^(a·x ⊕ b·S(x))."""
    return [[sum(1 - 2 * (_pesha((a & x) ^ (b & s[x])) & 1) for x in range(16))
             for b in range(16)] for a in range(16)]


def lineariteti(s: list[int]) -> int:
    """max |W(a,b)| për b ≠ 0; për 4 bit optimumi është 8."""
    w = tabela_walsh(s)
    return max(abs(w[a][b]) for a in range(16) for b in range(1, 16))


def jolineariteti(s: list[int]) -> int:
    return 8 - lineariteti(s) // 2


def _shkalla_anf(tabela_vertetesise: list[int]) -> int:
    """Shkalla algjebrike e një funksioni boolean 4-bitësh (transformimi Möbius)."""
    f = list(tabela_vertetesise)
    for i in range(4):
        for x in range(16):
            if x & (1 << i):
                f[x] ^= f[x ^ (1 << i)]
    return max((_pesha(m) for m in range(16) if f[m]), default=0)


def shkallet_e_komponenteve(s: list[int]) -> list[int]:
    """Shkalla e çdo komponenti b·S(x), b = 1..15."""
    return [_shkalla_anf([_pesha(b & s[x]) & 1 for x in range(16)]) for b in range(1, 16)]


def pika_fikse(s: list[int]) -> tuple[int, int]:
    """(S(x) = x, S(x) = x ⊕ 0xF)."""
    return (sum(s[x] == x for x in range(16)), sum(s[x] == x ^ 0xF for x in range(16)))


def matjet(s: list[int]) -> dict:
    shkallet = shkallet_e_komponenteve(s)
    return {
        "uniformiteti_diferencial": uniformiteti_diferencial(s),
        "lineariteti": lineariteti(s),
        "jolineariteti": jolineariteti(s),
        "shkalla_min_komponenteve": min(shkallet),
        "komponente_me_shkalle_3": sum(d == 3 for d in shkallet),
        "pika_fikse": pika_fikse(s),
    }


def eshte_optimal(m: dict) -> bool:
    """Kriteret e BRI-410: DU = 4, linearitet 8, të 15 komponentët me shkallë 3, pa pika fikse."""
    return (m["uniformiteti_diferencial"] == 4 and m["lineariteti"] == 8
            and m["komponente_me_shkalle_3"] == 15 and m["pika_fikse"] == (0, 0))


def kerko_sbox(etiketa: bytes = ETIKETA, kufiri: int = 1_000_000) -> tuple[int, list[int]]:
    for numeruesi in range(kufiri):
        s = gjenero_permutacion(etiketa, numeruesi)
        if eshte_optimal(matjet(s)):
            return numeruesi, s
    raise RuntimeError("asnjë S-box optimal brenda kufirit")


def inversi(s: list[int]) -> list[int]:
    inv = [0] * 16
    for x, y in enumerate(s):
        inv[y] = x
    return inv


# Rezultati i kerko_sbox() me ETIKETA (numëruesi 537); testet verifikojnë që riprodhohet.
NUMERUESI_SBOX = 537
SBOX = [0x5, 0x6, 0xC, 0x4, 0x0, 0xF, 0xB, 0x9, 0x2, 0xE, 0x3, 0x1, 0xA, 0x7, 0x8, 0xD]
SBOX_INV = inversi(SBOX)
