"""Lëvizja e kalit: permutimi i 64 kutive të tabelës ("difuzioni").

Kutia (r, k), me indeks 8·r + k, kryen k kërcime kali (dr, dk) në tabelë toroidale,
pastaj e gjithë tabela zhvendoset me (alfa, beta):
    (r, k) → (r + k·dr + alfa, k + k·dk + beta)  mod 8

Varianti fiks (V-F): drejtimi (1, 2), alfa = beta = 0.
Varianti "loja" (V-L): çelësi zgjedh drejtimin (4) dhe beta (8) në çdo raund, pra 5 bit; alfa = 0,
sepse zhvendosja e rreshtave komuton me raundin (F1, M3) dhe nuk shton strukturë.
Vetëm drejtimet me dr tek dhe dk çift japin permutim me përhapje të plotë të rreshtave.
"""

DREJTIMET = [(1, 2), (1, -2), (-1, 2), (-1, -2)]


def levizja_kalit(drejtimi: tuple[int, int] = (1, 2), alfa: int = 0, beta: int = 0) -> list[int]:
    """P[i] = vendi i ri i kutisë i."""
    dr, dk = drejtimi
    p = [0] * 64
    for r in range(8):
        for k in range(8):
            p[8 * r + k] = 8 * ((r + k * dr + alfa) % 8) + (k + k * dk + beta) % 8
    return p


def zbato(p: list[int], gjendja: list[int]) -> list[int]:
    rezultati = [0] * len(gjendja)
    for i, x in enumerate(gjendja):
        rezultati[p[i]] = x
    return rezultati


def inversi(p: list[int]) -> list[int]:
    inv = [0] * len(p)
    for i, j in enumerate(p):
        inv[j] = i
    return inv


def eshte_bijeksion(p: list[int]) -> bool:
    return sorted(p) == list(range(len(p)))


def perhapja_e_rreshtave(p: list[int], gjeresia: int = 8) -> int:
    """Minimumi, mbi rreshtat burim, i numrit të rreshtave të ndryshëm ku shkojnë kutitë e tyre.

    Optimale (= gjeresia) do të thotë se çdo rresht shpërndahet në të gjithë rreshtat
    ("diffusion-optimal" sipas Daemen–Rijmen), kusht për kufirin wide-trail në 4 raunde.
    """
    return min(len({p[i] // gjeresia for i in range(r, r + gjeresia)})
               for r in range(0, len(p), gjeresia))


def pika_fikse(p: list[int]) -> int:
    return sum(p[i] == i for i in range(len(p)))
