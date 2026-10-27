# BRI-410 — Raporti F8: rregullimi i orarit të çelësit (v1.1) (2026-10-27)

Riprodhimi (nga `C:\Users\vlora\Shahu_Kripto`):

```
python -m unittest discover -s teste -t .     # 46/46 OK
python -m matje.f8_k_rregullimi               # → matje/f8_rezultatet.json (~20 s)
```

## Problemi (F7, kategoria K)

Te v1.0, nga **3 çelësa raundesh të njëpasnjëshëm të një blloku të vetëm** dhe numri publik, sulmuesi rikthente
**çelësin kryesor në 0,1 s**, dhe me të **të gjitha blloqet e tjera**. Kjo binte ndesh me idenë
"çdo lojë luhet vetëm një herë": zbulimi i një loje zbulonte të gjitha.

## Ndryshimi: BRI-410 v1.1 (vendim i pronarit)

```
v1.0:  G_0 = F_F7(F_F6(F_F5(F_F4( X ))))                  X = K* me numrin në bajtet 0..15
v1.1:  G_0 = F_FB(…F_F4( X )…) ⊕ X                         8 hapa + feed-forward
```

- `K*` (4 hapat që varen vetëm nga çelësi) është i përbashkët për të gjitha blloqet. Feed-forward-i `⊕ X` e bën kalimin
  `G_0 → X` të **pakthyeshëm**. Ky është ndërtimi Davies–Meyer, i përdorur te funksionet hash si SHA-2.
- Hapat pas numrit u rritën nga 4 në 8 për marzh. Sulmet e njohura kundër ndërtimeve të ngjashme me AES-in me
  feed-forward arrijnë më pak hapa. Ky është vlerësim nga literatura dhe nuk u mat këtu.
- **Raundi i shifrës nuk ndryshoi**, ndaj rezultatet D, L dhe A të F7 vlejnë njësoj.
- v1.0 mbetet e riprodhueshme (`versioni="1.0"`), dhe vektorët e saj të F5 kalojnë ende.

## Rezultatet

### 1. Sulmi i F7 kundër dy versioneve (3 prova secili)

| | G_0 i bllokut të sulmuar u rindërtua | Çelësi kryesor u gjet | Blloku tjetër u parashikua |
|---|---|---|---|
| **v1.0** | 3/3 | **3/3** ❌ | **3/3** ❌ |
| **v1.1** | 3/3 | **0/3** ✅ | **0/3** ✅ |

Me v1.1, sulmuesi mëson ende **gjendjen e bllokut që sulmoi**, pra lojën e atij blloku, dhe kjo është e pashmangshme.
Por **nuk arrin te çelësi kryesor dhe as te blloqet e tjera**.

**Kufiri i ndershëm i kësaj prove:** testi tregon që rruga e drejtpërdrejtë e kthimit mbrapsht nuk funksionon më.
Ai **nuk provon** që `F(X) ⊕ X` nuk mund të përmbyset me ndonjë metodë tjetër. Gjetja e `X` nga `G_0` është problem
"preimage" mbi 640 bit (provimi i të gjitha mundësive kërkon 2⁶⁴⁰). Rezistenca kundër metodave më të zgjuara mbetet
**pyetje e hapur për analizë të jashtme**.

### 2. Vetitë e tjera të v1.1

| Matja | Rezultati | |
|---|---|---|
| 1 bit çelësi → RK_0 / RK_1 / RK_8 / RK_16 (820 prova) | 50,1% / 50,1% / 50,1% / 50,0% | ✅ |
| 1 bit numri → RK_0 / teksti pas 16 raundeve (400 prova) | 50,0% / 50,2% | ✅ |
| Numra të zgjedhur, integral, 1 bajt (256 numra): R1 / R2 / R16 | 0–1 / 0–1 / 0–1 nga 64 (rastësia ≈ 0,25) | ✅ |
| Numra të zgjedhur, integral, 2 bajte (65 536 numra), R1 | 0 nga 64 | ✅ |
| Diferencë e kombinuar në mesazh dhe numër, R1 / R2 / R3 | 0,23 / 0,28 / 0,26 bajte zero (rastësia 0,25) | ✅ |
| 16 raunde, numri = 0, 1, 2… (10 000 blloqe) | monobit z −0,74 · vargjet z 0,78 · χ² bajte 261 · χ² nibble 6,1 | ✅ nën pragjet 99% |
| Kufiri i orarit pas numrit (diferencial, në nivel kutie) | **≥ 162 S-box aktive** (2 × 81, nga kufiri i provuar 4-hapësh i F4-b) | ✅ i dyfishuar |

### 3. Kostoja

| | Blloqe/s (Python, me lojë të re për çdo bllok) |
|---|---|
| v1.0 | 2 651 |
| **v1.1** | **2 295** (−13%) |
| BRI-410 AE, 64 KB (v1.1) | ≈ 151 KB/s |

## Çfarë ndryshoi në projekt

- `shahu/bri8.py`: v1.1 si parazgjedhje (`VERSIONI = "1.1"`), v1.0 e disponueshme.
- `teste/`: testet njohin të dy versionet; vektorë të rinj `vektoret_f5_v11.json`; vektorët AE u rigjeneruan për v1.1.
- `publikim/reference/bri410.py`: v1.1, i rishkruar veçmas dhe i përputhur bit për bit me implementimin kryesor.
  `test_vectors.json` u rigjenerua.
- Specifikimi §10: orari v1.1.
- **Asgjë nuk është dërguar ende në GitHub.**

## Mbetet e hapur

1. Rezistenca e `F(X) ⊕ X` me 8 hapa ndaj sulmeve "preimage" të specializuara (MITM, rebound).
2. Rillogaritja me CP-SAT e kufirit 8-hapësh në një kompjuter ku `ortools` nuk bllokohet.
3. Rikthimi i plotë i çelësit në 4 raunde, që te v1.0 ishte i mundshëm. Te v1.1 rikthehet vetëm loja e bllokut të sulmuar.
