# BRI-410 — Raporti F2: prototipi i plotë (2026-10-22)

Riprodhimi (nga `C:\Users\vlora\Shahu_Kripto`):

```
python -m unittest discover -s teste -t .     # 20/20 OK
python -m matje.f2_matjet                     # → matje/f2_rezultatet.json (~65 s)
python -m matje.f2_vektoret                   # rigjeneron teste/vektoret_f2.json (vetëm me qëllim)
```

Kodi: `shahu/shifra.py` (klasa `BRI410`, `gjenero_celes()`). Konfigurimet e matura: V-F dhe V-L, me 16 dhe 32 raunde.
Çdo matje statistikore krahasohet me një **bazë të rastësishme** të llogaritur në të njëjtën mënyrë.

## Përmbledhja

| Kriteri i F2 | Rezultati | |
|---|---|---|
| Dekriptimi kthen 100% të mostrave | **40 000 / 40 000** (4 konfigurime × 10 000) | ✅ |
| Implementimi i shpejtë = implementimi reference (direkt nga specifikimi) | 80 kriptime + 20 orare, identike | ✅ |
| Efekti ortek ≈ 50% | nga **raundi 3**, si baza e rastësishme | ✅ |
| Çelësi i gabuar nuk dekripton | po | ✅ |
| Teste statistike mbi numëruesin 0..19 999 | të gjitha nën pragun 99% | ✅ |

## 1. Korrektësia dhe shpejtësia

| Konfigurimi | Sakte | Blloqe/s (Python) |
|---|---|---|
| V-F, 16 raunde | 10 000 / 10 000 | 5 825 |
| V-F, 32 raunde | 10 000 / 10 000 | 2 967 |
| V-L, 16 raunde | 10 000 / 10 000 | 5 796 |
| V-L, 32 raunde | 10 000 / 10 000 | 2 944 |

- 32 raunde janë **1,96×** më të ngadalta se 16, siç pritej.
- V-L është pothuajse po aq i shpejtë sa V-F, sepse 32 lëvizjet llogariten paraprakisht.
- Python-i është i ngadaltë për kriptografi (~186 KB/s me 16 raunde). Këto numra vlejnë vetëm për krahasim mes konfigurimeve.

Testet shtesë: implementimi reference i shkruar veç (`teste/test_shifra.py`), 24 vektorë të ngrirë regresioni
(`teste/vektoret_f2.json`, nuk janë verifikim i pavarur), validimi i çelësit si 52 bajte.

## 2. Efekti ortek: ndryshon 1 bit i mesazhit

Fraksioni i biteve të daljes që ndryshojnë (2 000 mostra për raund):

| Raunde | 1 | 2 | **3** | 4 | 6 | 8 | 16 | 32 | Baza e rastësishme |
|---|---|---|---|---|---|---|---|---|---|
| V-F mesatarja | 0,067 | 0,534 | **0,499** | 0,500 | 0,501 | 0,500 | 0,500 | 0,499 | 0,501 |
| V-L mesatarja | 0,066 | 0,534 | **0,499** | 0,499 | 0,501 | 0,500 | 0,501 | 0,500 | 0,501 |

Dy vlera të veçanta që **shpjegohen saktë nga teoria**:
- **Raundi 1, 0,067:** 1 nibble i ndryshuar → 1 rresht prej 8 nibblesh (MDS) → ~16 nga 256 bit = 0,0625. ✔
- **Raundi 2, 0,534 (jo 0,500):** pas 2 raundesh **të 64 nibblet janë garantuar të ndryshuar** (difuzioni i plotë).
  Një nibble i ndryshuar ndryshon mesatarisht 32/15 nga 4 bitët e vet, pra 0,5333. ✔
  Ky është një "dallues" i njohur në 2 raunde (edhe AES-i ka të njëjtin). Zhduket në raundin 3.

## 3. Kriteri i ortekut të rreptë (SAC)

Matrica 256 × 256: për çdo bit hyrjeje dhe çdo bit daljeje, sa shpesh ndryshon dalja (64 mostra për bit hyrjeje).

| Raunde | 1 | 2 | 3 | 4 | 6 | Baza e rastësishme |
|---|---|---|---|---|---|---|
| V-F: devijimi max nga 0,5 | 0,50 | 0,33 | **0,27** | 0,28 | 0,25 | 0,27 |
| V-F: qeliza që nuk ndryshojnë kurrë / gjithmonë | 57 344 | 0 | 0 | 0 | 0 | 0 |
| V-L: devijimi max nga 0,5 | 0,50 | 0,28 | **0,28** | 0,28 | 0,27 | 0,27 |
| V-L: qeliza 0/1 | 51 200 | 0 | 0 | 0 | 0 | 0 |

Nga raundi 3 nuk dallohet nga baza e rastësishme. Me 64 mostra, një ndryshim prej 0,016 është vetëm 1 numërim, pra zhurmë.

## 4. Efekti ortek: ndryshon 1 bit i çelësit

| Raunde | 1 | 2 | **3** | 4 | 6 | 16 | 32 | Baza |
|---|---|---|---|---|---|---|---|---|
| V-F mesatarja | 0,079 | 0,468 | **0,501** | 0,498 | 0,500 | 0,498 | 0,499 | 0,500 |
| V-L mesatarja | 0,134 | 0,486 | **0,499** | 0,499 | 0,498 | 0,500 | 0,500 | 0,500 |

V-L përhap ndryshimin e çelësit **më shpejt në raundet 1–2**, sepse një bit çelësi mund të ndryshojë edhe lëvizjen e kalit.
Nga raundi 3 të dy janë njësoj. Kjo është dallimi i parë i matur mes V-L dhe V-F, por është i vogël.

## 5. Statistika mbi hyrje shumë të ngjashme

Kriptohen numrat 0, 1, …, 19 999 (16 raunde). Hyrjet ndryshojnë vetëm në pak bite të ulëta, kështu që ky është test i vështirë për difuzionin.

| | Monobit z (prag 2,576) | χ² i nibbleve (prag 30,6) | χ² i bajteve (prag 310,5) |
|---|---|---|---|
| V-F | 0,054 | 14,2 | 255,7 |
| V-L | −0,316 | 12,7 | 249,7 |

Të gjitha kalojnë ✅.

## Përfundimet

1. **Prototipi funksionon saktë**, me 100% kthim dhe përputhje me implementimin reference.
2. **R₁ empirik = 3**: nga raundi 3, asnjë test statistik nuk e dallon BRI-410 nga një funksion i rastësishëm.
   Strukturisht R₁ = 2, siç u gjet në F1.
3. **Kujdes i ndershëm:** kalimi i testeve statistikore **nuk vërteton siguri**. Këto teste kapin vetëm gabime të trasha.
   Sulmet reale (diferencial, linear, integral, me çelësa të lidhur) testohen në F4. Deri tani:
   R₁ = 3 (empirik), R₂ ≈ 8 (teorik), R₃ = i panjohur.
4. **V-F kundrejt V-L:** në F2 dallimi i vetëm i matur është përhapja pak më e shpejtë e çelësit në raundet 1–2 te V-L.
   Pyetja e vërtetë, nëse loja e vështirëson sulmet, mbetet për F3/F4.

## Vendimet e F2 (të futura në specifikim, versioni 0.3)

- Të gjitha raundet identike, edhe raundi i fundit me θ.
- Bajtet → nibble: nibble 2i = 4 bitët e ulët të bajtit i.
- Çelësi: 52 bajte little-endian, 6 bitët e sipërm = 0.
- Orari i çelësit dhe raundi përdorin `perziej_shpejt` (tabela). F1 u rimat dhe rezultatet dolën identike.

## Hapi i radhës (pret miratim): F3

- **V-F kundrejt V-L me sulme të vogla:** p.sh. sa raunde mbijeton një dallues integral ose diferencial i shkurtuar në secilin.
- **Bllok 256 kundrejt 512 bit** (opsioni B nga plani), nëse ende ka interes.
- **Krahasim me AES** në të njëjtat teste (duhet biblioteka `cryptography` ose implementim i AES-it në Python).
