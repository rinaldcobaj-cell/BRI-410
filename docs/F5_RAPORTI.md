# BRI-410 — Raporti F5: kuti 8-bitëshe, bllok 512 bit, 16 raunde (2026-10-22)

Riprodhimi (nga `C:\Users\vlora\Shahu_Kripto`):

```
python -m unittest discover -s teste -t .     # 34/34 OK (7 teste të reja për BRI-410/8)
python -m matje.f5_matjet                     # → matje/f5_rezultatet.json (~15 s)
```

Kodi: `shahu/gf256.py`, `shahu/sbox8.py`, `shahu/mds8.py`, `shahu/bri8.py` (klasa `BRI410_8`).
Versioni zyrtar 4-bitësh (`shifra.py`) **nuk u prek**.

## Pyetja

Te BRI-410 me kuti 4-bitëshe, sulmi integral shkonte **1 raund më larg se te AES-i** (F3). Shkaku: S-box-i 4-bitësh
ka shkallë 3, "mbreti" që lëviz ngadalë. A e rregullon këtë dobësi kalimi në kuti 8-bitëshe, "mbretëresha"?
Dhe a mjaftojnë **16 raunde**, aq sa gurë ka çdo lojtar në shah?

## Ndërtimi: BRI-410/8

| | BRI-410 (4-bit, zyrtar sot) | **BRI-410/8** |
|---|---|---|
| Tabela | 8×8 | **8×8** (e njëjta) |
| Bit për kuti | 4 | **8** |
| Blloku | 256 bit | **512 bit** |
| Çelësi | 410 bit | **410 bit** |
| Lëvizja e kalit, loja unike për çdo bllok | po | **po** (e njëjta) |
| Raunde | 32 | **16** |

S-box-i: inversi në GF(2⁸) + transformim afin nga SHAKE-256 (pa "mister"). Matrica: Cauchy me `y` nga SHAKE-256.
Orari: 80 bajte, i njëjti model si te V-N (4 hapa → numri → 4 hapa).

## Rezultatet

### 1. Komponentët

| S-box | Uniformiteti diferencial | Jolineariteti | Shkalla | Pika fikse |
|---|---|---|---|---|
| **BRI-410/8** | **4** | **112** | **7** | 0, 0 |
| AES (referencë) | 4 | 112 | 7 | 0, 0 |
| 10 S-box të rastësishëm | 10–16 | 90–96 | — | — |
| BRI-410 4-bit (për krahasim) | 4 nga 16 (= 1/4) | 4 | 3 | 0, 0 |

| Matrica | Nënmatrica singulare | Simetri | Involutive |
|---|---|---|---|
| **BRI-410/8** | **0 / 12 869** (MDS e provuar) | **1** (vetëm identiteti) | jo, ka matricë inverse |
| BRI-410 4-bit | 0 / 12 869 | 8 (diadike) | po |

Matrica e re **nuk ka simetritë e fshehta** që u gjetën te versioni 4-bitësh, kështu që një nga rreziqet e F1 mbyllet.

### 2. Korrektësia dhe përzierja

- Dekriptimi kthen **2 000 / 2 000** mesazhe. Testet përputhen me një version reference të shkruar veç.
- Efekti ortek: raundi 1: 6,3%, **raundi 2: 50,2%**, pra R₁ = 2. Ndryshimi i 1 biti te numri ndryshon 49,8%.

### 3. Sulmi integral (i njëjti funksion, pra rasti kur numri përsëritet)

Sa nga 64 bajte dalin të balancuara? **Rastësia jep ≈ 0,25.**

| Grupi | Tekste | 2 raunde | 3 raunde | 4 raunde |
|---|---|---|---|---|
| 1 bajt | 256 | 64 (10/10) | **64 (10/10)** | **0–1** ✅ rastësi |
| 2 bajte të rreshtuara | 65 536 | | | **0–1** ✅ rastësi |
| Me numër unik, 1 bajt | 256 | | 0–1 ✅ | |

**Krahasimi kryesor:**

| | Dalluesi integral më i gjatë i gjetur |
|---|---|
| BRI-410 4-bit | **4 raunde me 4 096 tekste** |
| **BRI-410/8** | **3 raunde**. Në 4 raunde asgjë, as me 65 536 tekste |
| AES | 3 raunde (4 raunde kërkojnë ~4 miliardë) |

**Dobësia u rregullua:** BRI-410/8 sillet si AES-i kundër sulmit integral.

### 4. Sulmi real

- **4 raunde:** 5/5, rikthehet çelësi i raundit 4 (512 bit) me 512–768 tekste, < 1 s. Pritej, sepse edhe AES-i me 4 raunde bie njësoj.
- **5 raunde:** me dalluesin 3-raundësh, sulmuesi duhet të marrë me mend 2 raunde në fund: 8 + 1 bajte = 72 bit
  për çdo bajt objektiv, pra ≈ 2^72 punë. Kjo është **jashtë mundësive praktike**. Krahaso me BRI-410 4-bit: 5 raunde në < 1 s, 6 raunde ≈ 2^48.

### 5. Kufiri teorik (wide-trail)

Probabiliteti për S-box aktiv = 2⁻⁶ (te 4-bit ishte 2⁻²).

| Raunde | 2 | 4 | 6 | 8 | 16 |
|---|---|---|---|---|---|
| S-box aktive (min) | 9 | 81 | 90 | 162 | 324 |
| log₂ e probabilitetit | −54 | −486 | **−540** | −972 | **−1944** |

Kufiri kalon 2⁻⁵¹² te **6 raunde**, pra R₂ = 6 (te 4-bit ishte 8).

### 6. Shpejtësia (Python, me lojë unike për çdo bllok)

| | Bajte/s | Krahasuar me zyrtarin sot |
|---|---|---|
| BRI-410 4-bit, 32 raunde (zyrtar sot) | 29 274 | — |
| BRI-410 4-bit, 16 raunde | 50 862 | 1,7× |
| **BRI-410/8, 16 raunde** | **149 426** | **5,1× më i shpejtë** |

Blloku më i madh (64 bajte) dhe më pak raunde e bëjnë shumë më të shpejtë, edhe pse çdo raund ka më shumë punë.

## Rregulli i raundeve

| | BRI-410 4-bit | **BRI-410/8** |
|---|---|---|
| R₁ (përzierja e plotë) | 3 | **2** |
| R₂ (kufiri teorik) | 8 | **6** |
| R₃ (sulmi i ekzekutuar / vlerësuar) | 5 / 6 (2^48) | **4 / 5 (2^72)** |
| **2 × max** | 16 | **12 ≤ 16** ✅ |
| Raunde të zgjedhura | 32 | **16** |
| Marzhi ndaj sulmit të ekzekutuar | 6,4× | **4×** |

**16 raunde kalojnë rregullin.** Edhe nëse 5 raundet do të llogariteshin si të thyera, 2 × 6 = 12 ≤ 16.

## 7. Sulme me numra të zgjedhur (F4-a për BRI-410/8)

`python -m matje.f4a8_matjet` → `matje/f4a8_rezultatet.json` (~70 s). Mesazhi dhe çelësi fiks, numri përshkon të gjitha vlerat
në 1 bajt (256 numra) ose 2 bajte të të njëjtit rresht (65 536). **Rastësia jep ≈ 0,25 nga 64.**

| Hapa pas numrit \ Raunde | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 0 | **64** ❌ | **48** ❌ (2 bajte) / 0–1 | 0 | 0 |
| 1 | **32–64** ❌ | 0 | 0 | 0 |
| 2 | 0–1 | 0 | 0 | 0–1 |
| 3 | 0–1 | 0–1 | 0–1 | 0 |
| **4 (zyrtari)** | 0–1 | 0–1 | 0 | 0 |
| **Zyrtari, 16 raunde** | 0 (4 prova) | | | |

Efekti ortek i numrit (1 bit): RK₀ ndryshon 0,2% → 5,9% → 40,4% → **49,9%** → 49,8% për 0..4 hapa. Teksti pas 1 raundi
ndryshon ≈ 50% që nga hapi 1.

**Përfundim:** e njëjta pamje si te versioni 4-bitësh. Shkurtore vetëm me ≤ 1 hap përzierjeje dhe ≤ 2 raunde.
Zyrtari ka 4 hapa (marzh 2×) dhe 16 raunde. Nuk u gjet asnjë shkurtore ✅.

Vektorët e testit u ngrinë (`teste/vektoret_f5.json`, 12 vektorë), dhe BRI-410/8 u përshkrua në specifikim (§10).
Testet: 35/35 OK.

## Ndershmëria: çfarë mbetet e hapur

- Dalluesi 4-raundësh me 3+ bajte të rreshtuara (≥ 2^24 tekste) nuk u testua, sepse në Python zgjat shumë. Te AES-i, 4 raunde kërkojnë 2^32.
  Kjo i takon F4-b (mjetet "division property").
- Kufijtë MILP/SAT, sulmet diferenciale/lineare në praktikë dhe analiza disa-vjeçare e të tjerëve mungojnë.
- Mënyra e përdorimit (mesazhe me shumë blloqe) dhe vërtetimi i mesazhit mungojnë.

## Vendimi që pret pronarin

**A bëhet BRI-410/8 me 16 raunde versioni zyrtar i BRI-410?**

Rekomandim: **po**. Testi F4-a u përsërit dhe kaloi. Arsyet:
1. Rregullon dobësinë strukturore në vend që ta mbulojë me raunde.
2. Matrica pa simetri të fshehta.
3. 5× më i shpejtë se zyrtari i sotëm.
4. Ruan gjithçka nga ideja fillestare: tabelën 8×8, lëvizjen e kalit, lojën unike, çelësin 410-bitësh, dhe tani edhe **16 raunde = 16 gurët e çdo lojtari**.
