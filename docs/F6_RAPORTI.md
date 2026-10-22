# BRI-410 — Raporti i hapit 2: mënyra e përdorimit dhe vula (2026-10-22)

Riprodhimi (nga `C:\Users\vlora\Shahu_Kripto`):

```
python -m unittest discover -s teste -t .     # 43/43 OK (7 teste të reja për mënyrën)
python -m matje.f6_matjet                     # → matje/f6_rezultatet.json (~6 s)
python -m matje.f6_vektoret                   # rigjeneron teste/vektoret_ae.json (vetëm me qëllim)
```

Kodi: `shahu/menyra.py`. **BRI-410 kalon nga "motor" (1 bllok) në "makinë"**: kripton mesazhe të çdo gjatësie
dhe refuzon çdo mesazh të ndryshuar.

```python
from shahu import bri8, menyra
celesi = bri8.gjenero_celes()
paketa = menyra.kripto(celesi, b"mesazhi", te_dhena=b"Ana -> Besi")   # numri i mesazhit gjenerohet vetë
mesazhi = menyra.dekripto(celesi, paketa, te_dhena=b"Ana -> Besi")    # ose ngre VulaEGabuar
```

## Vendimet e pronarit

| Zgjedhja | Vendimi |
|---|---|
| Gjatësia e vulës | **416 bit (52 bajte), "sa çelësi"**. Fillimisht 256, pastaj 416 |
| Numri i mesazhit | 96 bit: e jep përdoruesi, ose gjenerohet rastësisht |
| Të dhëna shoqëruese | po: mbrohen nga ndryshimi pa u kriptuar |

## Projektimi

Modeli **ΘCB3** (Krovetz–Rogaway, 2011), i provuar matematikisht i sigurt nëse shifra me "lojë" është e sigurt.
Nuk u shpik mënyrë e re, sepse aty dështojnë shumica e algoritmeve të reja.

- **Çdo bllok luan lojën e vet**, edhe brenda të njëjtit mesazh. Numri 16-bajtësh i BRI-410/8 = numri i mesazhit (12 bajte)
  + indeksi i bllokut (28 bit) + lloji (4 bit: bllok, maskë e pjesës së fundit, vulë, të dhëna shoqëruese).
- **Vula** del nga shuma e të gjithë blloqeve origjinale, e kriptuar me një lojë të veçantë, plus "gjurma" e të dhënave shoqëruese.
- **Dekriptimi nuk kthen asnjë bajt** nëse vula nuk përputhet. Krahasimi bëhet në kohë konstante (`hmac.compare_digest`).
- Kostoja: 1 thirrje e BRI-410/8 për bllok + 1–2 për fundin dhe vulën + 1 për çdo 64 bajte të dhënash shoqëruese.
  Hapat që varen vetëm nga çelësi llogariten një herë për mesazh.
- Kufijtë: deri në 2²⁸ − 1 blloqe (~16 GB) për mesazh.

## Rezultatet

### Korrektësia

- **Kthim i saktë** për 13 gjatësi mesazhi (0 deri në 1 000 bajte) × 4 gjatësi të dhënash shoqëruese.
- **Çdo bit i ndryshuar kapet:** u ndryshuan një nga një **të 1 312 bitët** e një pakete (numri, teksti, vula) dhe
  të 80 bitët e të dhënave shoqëruese. **Të gjitha u refuzuan.**
- Prerja, zgjatja, heqja e një blloku dhe ndërrimi i vendeve të dy blloqeve u refuzuan.
- Çelësi i gabuar ose të dhënat shoqëruese të gabuara u refuzuan.
- 6 vektorë testi të ngrirë (`teste/vektoret_ae.json`).

### Përpjekje falsifikimi

| Sulmi | Prova | Të pranuara |
|---|---|---|
| Ndryshime të rastësishme 1–5 bajte | 1 000 | **0** |
| Vulë krejt e rastësishme | 1 000 | **0** |

Teorikisht, gjasa që një vulë e rastësishme të pranohet është 1 në 2⁴¹⁶ ≈ 10¹²⁵.

### Shpejtësia (Python)

| Madhësia | Kriptimi | Dekriptimi | Bajte shtesë |
|---|---|---|---|
| 64 bajte | 62 KB/s | 60 KB/s | 64 (numri 12 + vula 52) |
| 1 KB | 141 KB/s | 136 KB/s | 64 |
| 64 KB | 154 KB/s | 160 KB/s | 64 |

### Demonstrim: çfarë ndodh nëse numri përsëritet (keqpërdorim)

Dy mesazhe me të njëjtin bllok të parë:

| | Blloku 1 i kriptuar del i njëjtë? |
|---|---|
| Me **të njëjtin numër** | **PO** ❌: sulmuesi kupton që mesazhet fillojnë njësoj |
| Me numra të ndryshëm | jo ✅ |

Kjo e provon sërish rregullin: **numri i mesazhit nuk duhet përsëritur kurrë me të njëjtin çelës.**
Nëse përsëritet, rrjedh informacion dhe mbrojtja e vulës dobësohet (si te AES-GCM dhe OCB).
Me numra të rastësishëm 96-bitësh, gjasa e përsëritjes pas 4 miliardë mesazhesh është ≈ 2⁻³³.

## Ndershmëria

- Siguria e mënyrës është **e provuar vetëm me kusht** që BRI-410/8 të jetë një shifër e sigurt me lojë. Kjo nuk është vërtetuar,
  dhe mund të vërtetohet vetëm me vite analize. Testet tona e mbështesin, por nuk e provojnë.
- Implementimi në Python nuk është në kohë konstante (përveç krahasimit të vulës).
- Vektorët e testit janë regresion i implementimit tonë, jo verifikim i pavarur.

## Hapat e mbetur nga lista e boshllëqeve

3. Sulmet diferenciale/lineare + MILP/SAT (F4-b) · 4. Deklarata e sigurisë · 5. Implementim në C në kohë konstante.
