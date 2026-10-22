# BRI-410 — Raporti F1: matja e komponentëve (2026-10-22)

Riprodhimi (nga `C:\Users\vlora\Shahu_Kripto`):

```
python -m unittest discover -s teste -t .     # 12/12 OK
python -m matje.f1_matjet                     # → matje/f1_rezultatet.json (~20 s)
```

Farat e rastësisë janë fikse. Çelësat në matje janë mostra, jo çelësa për përdorim.

## Përmbledhja

| Komponenti | Kriteri | Rezultati | |
|---|---|---|---|
| S-box | DU 4, linearitet 8, 15/15 komponentë shkallë 3, 0 pika fikse | të gjitha | ✅ |
| MDS 8×8 | numri i degëve 9 (MDS) | 0 nga 12 869 nënmatrica singulare | ✅ |
| Lëvizja e kalit V-F | bijeksion, përhapje e plotë e rreshtave | po, 8/8 | ✅ |
| Lëvizja e kalit V-L | të 256 variantet bijeksione me përhapje të plotë | 256/256 | ✅ |
| Difuzioni strukturor | çdo dalje varet nga çdo hyrje | pas **2 raundeve** (V-F dhe rasti më i keq i V-L) | ✅ |
| Orari i çelësit | bijeksion, efekt ortek ≈ 50%, lëvizje uniforme | po; ≈ 50% nga hapi 3; χ² 254,8 < 310,5 | ✅ |
| **V-L: vlera reale e lojës** | të gjitha bitet e lëvizjes të ndikojnë strukturën | 5 nga 8 → **u rregullua me α = 0** | ✅ (shih rimatjen) |

## M1 — S-box-i

| Matja | BRI-410 | PRESENT (referencë) |
|---|---|---|
| Uniformiteti diferencial | 4 | 4 |
| Lineariteti / jolineariteti | 8 / 4 | 8 / 4 |
| Komponentë me shkallë 3 (nga 15) | **15** | 12 |
| Pika fikse (x, x⊕F) | **0, 0** | 0, 1 |
| Hyrje DDT me vlerë 4 (diferenciale më të mira për sulmuesin) | **15** | 24 |
| Hyrje Walsh me \|8\| (afrimet lineare më të mira) | **30** | 36 |

Baza e rastësishme: nga 3 000 permutacione të rastësishme, 122 (4,1%) janë optimale për DU dhe linearitet,
dhe vetëm 7 (0,23%) plotësojnë të gjitha kriteret tona. S-box-i i BRI-410 ka më pak
diferenciale dhe afrime lineare maksimale se PRESENT-i.

## M2 — Matrica MDS

```
F 2 C 5 A 4 3 8
2 F 5 C 4 A 8 3
C 5 F 2 3 8 A 4
5 C 2 F 8 3 4 A
A 4 3 8 F 2 C 5
4 A 8 3 2 F 5 C
3 8 A 4 C 5 F 2
8 3 4 A 5 C 2 F
```

- 12 869 nënmatrica katrore, **0 singulare**, pra matrica është provuar MDS. Edhe kontrolli i drejtpërdrejtë mbi të gjitha hyrjet me peshë 1–2 jep numër degësh 9.
- **Involutive dhe simetrike** (M = M⁻¹ = Mᵀ). Kjo është përfitim: dekriptimi përdor të njëjtën matricë.
- Është **diadike**: `M[i][j]` varet vetëm nga `i ⊕ j`. Prandaj ka saktësisht 8 simetri kolonash, të gjitha zhvendosje XOR.
  Nga zhvendosjet ciklike, vetëm 0 dhe 4 komutojnë me të.
- Asnjë element nuk është 1, kështu që çdo shumëzim është i vërtetë. Kjo ka kosto për shpejtësinë, jo për sigurinë.

## M3 — Lëvizja e kalit

- V-F: bijeksion, përhapje 8/8. Ka 8 pika fikse (kolona 0 nuk lëviz), njësoj si rreshti 0 te ShiftRows i AES-it.
- V-L: 256 variante, të gjitha të ndryshme, bijeksione dhe me përhapje 8/8.

### ⚠️ Gjetja kryesore: α është "kozmetike"

Zhvendosja vetëm e rreshtave T(α, 0) **komuton me gjithë raundin pa çelës** (S → π → θ) për të 4 drejtimet
dhe të 8 vlerat e α. Asnjë zhvendosje tjetër nuk komuton. Arsyeja:

- S-box-i është i njëjtë në çdo kuti.
- θ zbatohet me të njëjtën matricë në çdo rresht.
- Lëvizja e kalit përkthehet njësoj në çdo rresht.

Pra α mund të "shtyhet" deri në fund të algoritmit. Kriptimi me α_i është i barabartë me kriptimin pa α,
me çelësat e raundeve të rirenditur dhe me një zhvendosje të vetme rreshtash në fund.
**Nga 8 bitët e lojës për raund, vetëm 5 (drejtimi + β) ndryshojnë realisht strukturën.**

## M4 — Difuzioni

| Raunde | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| Sa nga 64 daljet varen nga hyrja më e dobët (V-F) | 8 | **64** | 64 | 64 |
| I njëjti, rasti më i keq mbi 256 + 2 000 sekuenca V-L | 8 | **64** | 64 | 64 |

**R₁ = 2** (si AES-i me tabelën 4×4).

Kufiri teorik wide-trail (S-box aktive ≥ …; probabiliteti maksimal i një gjurme = 2^(−2 × aktive)):

| Raunde | 2 | 4 | 6 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|
| S-box aktive (min) | 9 | 81 | 90 | **162** | 324 | 648 |
| log₂ e probabilitetit maksimal | −18 | −162 | −180 | **−324** | −648 | −1296 |

Kufiri kalon 2⁻²⁵⁶ për herë të parë te **8 raunde**, pra **R₂ ≈ 8 (teorik)**. Kjo vlen edhe për sulmin linear
(korrelacioni² për S-box = 2⁻²). Është kufi për gjurmë të veçanta dhe mbështetet në teoremën e 4 raundeve
(kushti, përhapja e plotë e π, u mat ✅). Verifikimi me MILP/SAT bëhet në F4.

## M5 — Orari i çelësit

- Hapi i permutimit p = 9 (më i vogli me përhapje 8/8 mbi 13 rreshta). Difuzion strukturor i plotë pas **3 hapash**.
- Bijeksion: 299 gjendje të rastësishme kthehen saktë.
- Efekti ortek: ndryshohet 1 bit çelësi dhe matet sa bit ndryshojnë te RK_i (4 çelësa × 410 bit):

| Hapi i | 0 | 1 | 2 | 3 | 4 | 8 | 16 | 32 |
|---|---|---|---|---|---|---|---|---|
| Mesatarja | 0,002 | 0,041 | 0,328 | **0,500** | 0,499 | 0,500 | 0,499 | 0,500 |
| Lëvizja e raundit ndryshon | — | 16% | 84% | **99,6%** | 99,5% | 99,6% | 99,6% | 99,5% |

  (99,6% = 1 − 1/256, pikërisht sa pritet për 8 bit të rastësishëm.)
- Uniformiteti i lëvizjeve: 64 000 mostra në 256 vlera, χ² = 254,8 (pragu 99%: 310,5). Shpërndarja është uniforme ✅.
- Shënim: RK_0 dhe RK_1 varen pak nga çelësi, njësoj si te AES-256, ku RK_0 dhe RK_1 janë vetë çelësi.
  Kjo është normale, por duhet përfshirë në analizën me çelësa të lidhur (F4).

## Rimatja pas vendimit α = 0 (2026-10-22)

Pronari zgjodhi opsionin (a). Loja ka tani 32 variante për raund (4 drejtime × 8 β), pra 5 bit.
Testet: 12/12 OK (u shtua testi që lëvizja ka vetëm drejtim dhe β).

| Matja | Para (α e lirë) | Pas (α = 0) |
|---|---|---|
| Variante për raund | 256 | 32 |
| Bijeksione / përhapje e plotë | 256 / 256 | **32 / 32** ✅ |
| Çifte variantesh që ndryshojnë vetëm me zhvendosje kozmetike | **1 792** (secili variant kishte 7 "binjakë") | **0** ✅ |
| Difuzion i plotë (rasti më i keq) | 2 raunde | **2 raunde** ✅ |
| Lëvizja ndryshon kur ndryshon 1 bit çelësi (hapi ≥ 3) | ≈ 99,6% (= 1 − 1/256) | ≈ 96–97% (pritet 1 − 1/32 = 96,9%) ✅ |
| Uniformiteti i lëvizjeve | χ² 254,8 < 310,5 | χ² 20,8 < 52,2 ✅ |

S-box-i, matrica dhe orari i çelësit për RK_i nuk ndryshuan, dhe numrat e tyre janë identikë.
Tani çdo bit i lojës ndryshon realisht strukturën.

## Vendimet që presin pronarin

1. ~~Çfarë bëjmë me α?~~ **U vendos: α = 0.** Opsioni (b), zhvendosje të ndryshme për çdo rresht,
   mbetet i mundshëm për F3 nëse V-L tregohet i dobishëm.
2. **V-F kundrejt V-L:** a e shton realisht sigurinë loja që varet nga çelësi? Kjo vendoset në F3 me numra.
   Kostoja e V-L: zbatimi në kohë konstante është më i vështirë.
3. **Raundet:** deri tani R₁ = 2 dhe R₂ ≈ 8 (teorik). Sipas rregullit, R ≥ 16. R₃ (sulmet) mungon deri në F4.

## Saktësim ndaj planit

Në tabelën e planit shkruajta "MDS: numri i degëve 5". Kjo vlen për rreshta me 4 kuti (AES).
Për rreshta me 8 kuti optimumi është **9**, dhe kjo është ajo që u mat.
