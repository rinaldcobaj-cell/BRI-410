# BRI-410 — Raporti F4-a: sulme me numra të zgjedhur kundër versionit zyrtar (2026-10-22)

Riprodhimi (nga `C:\Users\vlora\Shahu_Kripto`):

```
python -m unittest discover -s teste -t .     # 27/27 OK
python -m matje.f4a_matjet                    # → matje/f4a_rezultatet.json (~30 s)
```

## Vendimet e fiksuara para F4-a

- **BRI-410 zyrtar = V-N ("çdo lojë luhet vetëm një herë") + 32 raunde** (specifikimi 0.6).
- Në kod: `kripto_bllok(celesi, numri, bllok)` dhe `dekripto_bllok(...)`.

## Pyetja e F4-a

Me V-N, sulmuesi **nuk mund ta përsërisë numrin**, por mund ta **zgjedhë**. Për shembull, mund të kërkojë kriptimin e të njëjtit
mesazh me 4 096 numra që ndryshojnë vetëm në 3 shifra. A krijon kjo shkurtore?

Për të matur **marzhin**, numri i hapave të përzierjes **pas** futjes së numrit ndryshohet nga 0 deri në 4 (zyrtari = 4),
dhe raundet e shifrës nga 1 deri në 4 (zyrtari = 32). Skripti verifikon fillimisht që versioni i tij me 4 hapa
jep rezultat identik me `BRI410(..., "VN", numri)`.

## 1. Sulmi integral me numra të zgjedhur

Mesazhi dhe çelësi fiks. Numri përshkon të gjitha vlerat në 1 nibble (16 numra) ose në 3 nibble të të njëjtit rresht (4 096 numra).
Sa nga 64 nibble të tekstit të kriptuar dalin me shumë XOR = 0? **Rastësia jep ≈ 4. 64 do të thotë shkurtore.**
Vlerat në tabelë janë minimumi dhe maksimumi i 2 provave × 2 grupeve.

| Hapa pas numrit \ Raunde | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 0 (numri direkt në RK₀) | **64** ❌ | **56–64** ❌ | 4–5 | 1–7 |
| 1 | **64** ❌ | 3–6 | 4–6 | 1–6 |
| 2 | 1–6 | 4–6 | 3–7 | 1–4 |
| 3 | 1–4 | 1–5 | 1–6 | 3–6 |
| **4 (zyrtari)** | 2–7 | 1–8 | 2–5 | 3–6 |

**Versioni zyrtar i plotë (4 hapa, 32 raunde):** 2–4 nga 64, pra rastësi ✅.

## 2. Efekti ortek i numrit

Ndryshohet 1 bit i numrit, me mesazh fiks (300 mostra):

| Hapa pas numrit | RK₀ ndryshon | Teksti, 1 raund | Teksti, 4 raunde |
|---|---|---|---|
| 0 | 0,4% (1 bit) | 10,6% | 50,0% |
| 1 | 4,5% | 46,2% | 50,2% |
| 2 | 32,9% | 49,7% | 50,4% |
| 3 | **49,8%** | 50,0% | 50,3% |
| **4 (zyrtari)** | **49,9%** | 49,6% | 50,1% |

## Përfundimet

1. **Asnjë shkurtore kundër versionit zyrtar** me sulmet që provuam: integral me numra të zgjedhur dhe efekti ortek.
2. **Marzhi i përzierjes:** shkurtorja zhduket që nga hapi 2, dhe përzierja e plotë arrihet në hapin 3. Zyrtari ka **4 hapa**,
   pra marzh **2×** kundër sulmit integral dhe 1 hap tepër mbi përzierjen e plotë.
3. **Marzhi i plotë:** edhe me 0 hapa, shkurtorja zhduket pas 3 raundesh të shifrës. Rruga nga numri te teksti i kriptuar
   në versionin zyrtar ka 4 hapa + 32 raunde. Kundër kësaj klase sulmesh, marzhi është shumë i madh.

## Çfarë NUK u bë në F4-a (ndershmëri)

- **Sulmi mbi 6 raunde** të variantit pa numër (V-L, që është edhe rasti i keqpërdorimit kur numri përsëritet) **nuk u ekzekutua**.
  Kërkon ≈ 2^48 operacione. Në Python kjo do të zgjaste me vite. Vlerësimi i F3 mbetet: i arritshëm për sulmues real,
  por 32 raunde japin marzh rreth 5×.
- **Sulmet diferenciale me numra të zgjedhur me probabilitet** (related-tweak differential) dhe kufijtë e S-box-eve aktive
  për orarin kërkojnë mjete MILP/SAT. Këto i takojnë **F4-b**.
- Kombinimi numër i zgjedhur + mesazh i zgjedhur njëkohësisht nuk u testua veçmas.

## Gjendja e raundeve pas F4-a

| Matja | Vlera |
|---|---|
| R₁ (përzierja e plotë) | 3 |
| R₂ (kufiri teorik diferencial) | ≈ 8 |
| R₃ (sulmi më i mirë i ekzekutuar) | 5 (V-L / keqpërdorim); 0 të thyera te V-N zyrtar |
| R₃ (vlerësim) | 6 te V-L me ≈ 2^48 |
| **Rregulli: 2 × max** | **16 ≤ 32** ✅. 32 raunde mbeten të justifikuara, me marzh shtesë |

## Hapi i ardhshëm (pret miratim): F4-b

Analiza me mjete të specializuara (MILP/SAT, p.sh. paketa Python `ortools` ose `pysat`):
kufijtë e saktë të S-box-eve aktive për shifrën dhe orarin, kërkimi i dalluesve integralë më të gjatë ("division property"),
dhe gjurmët diferenciale me numra të zgjedhur. Kërkon instalimin e programeve shtesë.
