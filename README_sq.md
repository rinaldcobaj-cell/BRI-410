# BRI-410

Shifër blloku **studimi** e frymëzuar nga shahu. **Nuk është për përdorim real.**

Autori: **Rinald Cobaj**. Licenca: **CC0 1.0** (domen publik, shih `LICENSE`). BRI-410 nuk është i patentuar.

**BRI-410 zyrtar = BRI-410/8 v1.1:** tabelë 8×8 me kuti 8-bitëshe (bllok 512 bit), çelës 410 bit (≈ 10^123 "lojëra"),
lojë e re për çdo bllok ("çdo lojë luhet vetëm një herë"), 16 raunde ("16 gurët e çdo lojtari"). Te v1.1, futja e numrit
bëhet me 8 hapa dhe feed-forward (docs/F8_RAPORTI.md).

**Punimi:** `publikim/paper/BRI-410_v2.pdf` (anglisht) dhe `BRI-410_v2_shqip.pdf` (shqip). **Historiku:** versioni v1.0 dhe punimi i
parë (`BRI-410.pdf`) mbeten publikë me qëllim (etiketa git `v1.0`), sepse zbulimi dhe korrigjimi i dobësisë K janë pjesë e historisë
shkencore të BRI-410.

**Përdorimi (mesazhe të çdo gjatësie, me vulë 416 bit):**

```python
from shahu import bri8, menyra
celesi = bri8.gjenero_celes()                                          # NJË herë, 52 bajte (410 bit)
paketa = menyra.kripto(celesi, b"mesazhi", te_dhena=b"Ana -> Besi")    # numri unik gjenerohet vetë
assert menyra.dekripto(celesi, paketa, te_dhena=b"Ana -> Besi") == b"mesazhi"   # ose ngre VulaEGabuar
```

Rregulli: numri i mesazhit nuk përsëritet kurrë me të njëjtin çelës. Pa `numri=`, gjenerohet rastësisht.

## Dokumentet

- `docs/F0_SPECIFIKIMI.md`: specifikimi (§10 = zyrtari BRI-410/8 v1.1; §2–§9 = BRI-410/4, versioni i parë)
- `docs/F1_RAPORTI.md`: matjet e komponentëve (BRI-410/4)
- `docs/F2_RAPORTI.md`: prototipi i plotë (BRI-410/4)
- `docs/F3_RAPORTI.md`: loja kundrejt lëvizjes fikse, sulmet integrale, krahasimi me AES
- `docs/F3BIS_RAPORTI.md`: "çdo lojë luhet vetëm një herë" (V-N) e bllokon sulmin integral
- `docs/F4A_RAPORTI.md`: sulme me numra të zgjedhur kundër BRI-410/4
- `docs/F5_RAPORTI.md`: BRI-410/8, përfshirë sulmet me numra të zgjedhur, që e bënë zyrtar
- `docs/F6_RAPORTI.md`: mënyra e përdorimit (ΘCB3) me vulë 416 bit dhe të dhëna shoqëruese
- `docs/F4B_RAPORTI.md`: kufij të provuar me CP-SAT (sulmet diferenciale/lineare, orari me numra të zgjedhur)
- `docs/F7_RAPORTI.md`: analizat në pesë kategori (diferenciale, lineare, algjebrike, orari i çelësit, tekst/numër i zgjedhur),
  përfshirë dobësinë K të v1.0
- `docs/F8_RAPORTI.md`: rregullimi i dobësisë K (v1.1) dhe kontrollet pas rregullimit

## Paketa e publikimit

- `publikim/paper/BRI-410_v2.pdf`: **punimi aktual** (versioni 2, anglisht), përshkruan BRI-410 v1.1 (burimi `BRI-410_v2.md`,
  rindërtohet me `python ndertoj_pdf.py`)
- `publikim/paper/BRI-410_v2_shqip.pdf`: përkthimi shqip i punimit v2 (versioni për publikim është ai anglisht)
- `publikim/paper/BRI-410.pdf`: punimi i parë (versioni 1, 5 faqe), përshkruan BRI-410 v1.0; është PDF-ja e dorëzuar në IACR ePrint
  më 22.10.2026, e ruajtur pa ndryshime (rindërtohet me `python ndertoj_pdf.py v1`)
- `publikim/paper/BRI-410_shqip.pdf`: përkthimi shqip i punimit të parë
- `publikim/KRITERET_IACR.md`: si i plotëson punimi v2 kriteret e pranimit të IACR ePrint
- `publikim/reference/`: `bri410.py` (një skedar, vetëm Python standard, v1.1), `test_vectors.json`, `verify.py`
- `publikim/UDHEZUESI.md`: udhëzuesi në shqip për dorëzimin e parë në IACR ePrint (punimi v1)

## Kodi

- `shahu/menyra.py`: **BRI-410 AE**, mesazhe të çdo gjatësie me vulë (`kripto`, `dekripto`, `VulaEGabuar`)
- `shahu/bri8.py`: **BRI-410/8 zyrtar** (`BRI410_8`, `kripto_bllok`, `dekripto_bllok`), me `gf256`, `sbox8`, `mds8`
- `shahu/shifra.py`: BRI-410/4 (`BRI410`, variantet VF/VL/VN), me `gf16`, `sbox`, `mds`, `levizja`, `celesi`
- `teste/`: `python -m unittest discover -s teste -t .`
- `matje/`: `f1_matjet`, `f2_matjet`, `f3_matjet`, `f3_zgjerimi`, `f3bis_matjet`, `f4a_matjet`, `f5_matjet`, `f4a8_matjet`, `f6_matjet`,
  `f7_analizat`, `f8_k_rregullimi` (`python -m matje.<emri>`); `f4b_milp` me `.venv\Scripts\python.exe` (kërkon `ortools`); `aes_studim.py` = AES-256 për krahasim

Fazat: F0 ✅ · F1 ✅ · F2 ✅ · F3 ✅ · F3-bis ✅ · F4-a ✅ · F5 ✅ (BRI-410/8 zyrtar) · hapi 2 ✅ (mënyra + vula) · F4-b ✅ (CP-SAT) · publikimi v1.0 ✅ · F7 ✅ (pesë kategoritë e analizave) ·
F8 ✅ (v1.1, rregullimi i K) · publikimi v1.1 + punimi v2 ✅ · implementim në C.
Çdo fazë pret miratimin e pronarit.
