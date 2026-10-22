# BRI-410 — Raporti F4-b: kufij të provuar me CP-SAT (2026-10-22)

Riprodhimi (nga `C:\Users\vlora\Shahu_Kripto`):

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install ortools
.venv\Scripts\python.exe -m matje.f4b_milp        # → matje/f4b_rezultatet.json (~32 min, 3 × 600 s për 6–8 raunde)
```

**Shënim teknik:** `ortools` e importon `pandas`-in në fillim. Në këtë kompjuter, rregulli i sigurisë së Windows-it
(Application Control / Smart App Control) bllokon një DLL të `pandas`. **Rregulli nuk u prek.** Skripti thjesht nuk e ngarkon
`pandas` (modul bosh në vend të tij), sepse CP-SAT nuk ka nevojë për të. Paketat janë instaluar vetëm te `.venv` i projektit.

## Pyetja

Deri në F5, kufiri kundër sulmeve diferenciale dhe lineare ishte **teorik**: teorema wide-trail dhe një vlerësim i kujdesshëm.
F4-b e **llogarit saktë** me zgjidhësin CP-SAT të Google-it: cili është numri minimal i S-box-eve aktive që çdo rrugë
diferenciale ose lineare duhet të kalojë?

## Modeli

Model në nivel kutie (aktive / joaktive), standardi në literaturë:
- S-box-i nuk e ndryshon aktivitetin. θ (MDS, numri i degëve 9): hyrje + dalje aktive në çdo rresht = 0 ose ≥ 9.
- Nga loja ka rëndësi vetëm **në cilin rresht** shkon kutia (`r + k·dr`, dr = ±1). **Sulmuesit i lihet të zgjedhë dr-në në
  çdo raund**, kështu që kufiri vlen për **çdo lojë**, pra për çdo çelës dhe çdo numër.
- Vlen njësoj për sulmin linear, sepse transpozimi i një MDS-je është MDS me numër degësh 9.
- Probabiliteti për S-box aktiv: 2⁻⁶ (diferencial), dhe po aq për korrelacionin² linear (|W| ≤ 32).

## 1. Shifra BRI-410/8

| Raunde | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 16 |
|---|---|---|---|---|---|---|---|---|---|
| S-box aktive (min) | 1 | 9 | 17 | **81** | 82 | 90 | 98 | 162 | 324 |
| Si u provua | CP-SAT ✅ | CP-SAT ✅ | CP-SAT ✅ | **CP-SAT ✅** | CP-SAT ✅ | 4 + 2 | 4 + 3 | 4 + 4 | 4 × 4 |
| log₂ e probabilitetit max | −6 | −54 | −102 | **−486** | −492 | **−540** | −588 | −972 | −1944 |

- Për 1–5 raunde, CP-SAT e **provoi optimumin**.
- Për 6–8 raunde, 600 sekonda nuk mjaftuan për prova të drejtpërdrejta. Por kufiri del nga ndarja e rrugës në copa
  të provuara (p.sh. 6 = 4 + 2 ≥ 81 + 9 = 90). Për 6, 7 dhe 8 raunde, CP-SAT **gjeti rrugë me saktësisht këtë numër**
  (90, 98, 162), kështu që këta numra janë **të saktë**.
- Me lojë fikse (dr = +1): 2 raunde = 9, 4 raunde = 81. Pra loja nuk e ul kufirin, dhe asnjë lojë nuk është më e dobët.

**Përfundim:**
- Pas **4 raundeve**, çdo rrugë ka probabilitet ≤ 2⁻⁴⁸⁶, nën 2⁻⁴¹⁰ (sa çelësi).
- Pas **6 raundeve** ≤ 2⁻⁵⁴⁰, nën 2⁻⁵¹² (sa blloku).
- **R₂ = 6 tani është i provuar**, jo më vetëm teorik.
- Me 16 raunde: ≤ 2⁻¹⁹⁴⁴.

## 2. Orari me numra të zgjedhur (related-tweak)

Diferenca futet nga numri (bajtet 0..15). Sa S-box aktive duhet të kalojë në hapat e orarit pas numrit?

| Hapa pas numrit | 1 | 2 | 3 | **4 (zyrtari)** | 5 | 6 |
|---|---|---|---|---|---|---|
| S-box aktive (min) | 1 | 9 | 17 | **81** | 107 | 114 |
| log₂ e probabilitetit max | −6 | −54 | −102 | **−486** | −642 | −684 |

Të gjitha u provuan nga CP-SAT ✅. Para se të kriptohet blloku i parë, çdo diferencë e zgjedhur në numër duhet të kalojë
**≥ 81 S-box aktive**: probabiliteti për të parashikuar diferencën e RK₀ ≤ 2⁻⁴⁸⁶. Kjo konfirmon matematikisht atë që F4-a dhe
F5 e panë me teste: 4 hapat e përzierjes mjaftojnë, dhe hapi 2 ishte minimumi.

## Rregulli i raundeve pas F4-b

| | Vlera | Statusi |
|---|---|---|
| R₁ (përzierja e plotë) | 2 | e matur (F5) |
| **R₂ (diferencial/linear < 2⁻⁵¹²)** | **6** | **e provuar (F4-b)** |
| R₃ (sulmi i ekzekutuar / vlerësuar) | 4 / 5 (≈ 2^72) | F5 |
| 2 × max | **12 ≤ 16** ✅ | |

## Ndershmëria: kufijtë e këtij rezultati

- Kufiri vlen për **rrugë** (gjurmë) të veçanta. Rrugë të shumta me të njëjtën hyrje/dalje mund të mblidhen
  (diferenciale / "linear hull"). Në praktikë kjo rrallë fiton më shumë se disa bit kundër 2⁻¹⁹⁴⁴, por nuk u mat.
- Supozohen çelësa raundesh "të pavarur" (supozimi standard Markov).
- Sulmet që kombinojnë diferencë në numër + diferencë në mesazh njëkohësisht, kur loja ndryshon mes dy mesazheve,
  nuk modelohen nga ky model.
- Analiza integrale e saktë ("division property") **nuk u bë**. Do të kërkonte modelim në nivel biti të S-box-it 8-bitësh.
  Testet e F5 tregojnë dallues vetëm në 3 raunde.
