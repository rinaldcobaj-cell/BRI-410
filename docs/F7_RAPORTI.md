# BRI-410 — Raporti F7: pesë kategoritë e analizave (2026-10-27)

Riprodhimi (nga `C:\Users\vlora\Shahu_Kripto`):

```
python -m matje.f7_analizat        # → matje/f7_rezultatet.json (~50 s)
```

Objekti: **BRI-410/8 zyrtar** (kuti 8-bitëshe, bllok 512 bit, 16 raunde, lojë e re për çdo bllok). Algoritmi **nuk u ndryshua**.
Analizat janë **paraprake**: tregojnë çfarë del me mjete të thjeshta në Python. Nuk janë provë sigurie dhe nuk zëvendësojnë analizën e të tjerëve.
Shenjat: ✅ e matur dhe në rregull · ⚠️ gjetje që duhet përmendur në punim · ❌ test i dobët ose i paqartë.

## D. Kriptanaliza diferenciale

| Matja | Rezultati | |
|---|---|---|
| Tabela DDT e S-box-it (255 × 256 hyrje) | 32 895 × "0", 32 130 × "2", 255 × "4" → gjasa max për S-box **2⁻⁶** | ✅ si AES |
| 1 raund: diferenca dalëse më e shpeshtë (3 × 2¹⁴ çifte) | 0,0161 / 0,0157 / 0,0142, ndërsa teoria jep 4/256 = 0,0156. **127 dalje të ndryshme**, aq sa parashikon DDT | ✅ implementimi përputhet me teorinë |
| Diferencë në 1 bajt: sa bajte dalin pa ndryshim (300 çifte; rastësia ≈ 0,25) | R1: **56** (vetëm 1 rresht preket) · R2: **0** (të 64 ndryshojnë gjithmonë) · R3: **0,29** | ✅ R3 si rastësia |

⚠️ R2 = 0 në 300 nga 300 raste është dallues i njohur në 2 raunde: te një funksion i rastësishëm, të paktën një bajt mbetet i pandryshuar në rreth 22% të rasteve. Kjo vjen nga përhapja e plotë dhe ndodh edhe te AES-i. Nuk shkon përtej 2 raundeve.

Kufiri kryesor (≥ 81 S-box aktive në 4 raunde, ≤ 2⁻⁴⁸⁶) vjen nga F4-b. Sot nuk u rillogarit, sepse Windows-i bllokon `ortools`.

## L. Kriptanaliza lineare

| Matja | Rezultati | |
|---|---|---|
| S-box: korrelacioni max | 32/256 = **2⁻³** (korrelacioni² 2⁻⁶) | ✅ |
| Kontroll i saktë i 1 raundit (vetëm bajti 0 ndryshon, 256 hyrje) | korrelacioni max **0,125**, saktësisht sa i S-box-it. Bajti 37 i një rreshti tjetër **nuk preket fare** | ✅ implementimi përputhet me teorinë |
| Test statistik bajt-me-bajt (2¹⁸ mostra, 65 025 maska, 1–3 raunde) | 0,008–0,0095 në çdo raund, si zhurma (baza 0,0086) | ❌ **test i projektuar dobët** |

❌ **Pse testi statistik nuk tregon asgjë:** kur gjithë mesazhi është i rastësishëm, një bajt dalës është XOR i 8 daljeve S-box nga 8 bajte hyrës të ndryshëm. Për një maskë që sheh vetëm një bajt hyrës, korrelacioni është **zero, edhe në 1 raund**. Testi nuk kishte si të gjente asgjë, prandaj nuk vlen si provë. Gabimi është i imi, dhe e zëvendësova me kontrollin e saktë të 1 raundit më sipër.

Rrugët lineare mbi 2 raunde kanë korrelacion ≤ 2⁻²⁷ dhe nuk maten me eksperiment, sepse do të duheshin ≥ 2⁵⁴ mostra. **Mbrojtja lineare mbështetet te kufiri i provuar** (F4-b), jo te eksperimentet.

## A. Sulmet algjebrike

| Matja | Rezultati | |
|---|---|---|
| Ekuacione kuadratike hyrje–dalje të S-box-it | **39** (AES-i: **39**, i llogaritur me të njëjtin kod) | ✅ si AES, i njohur për 25 vjet |
| Struktura lineare të S-box-it | **0** | ✅ |
| Shkalla algjebrike e S-box-it | 7 (maksimumi për bijeksion 8-bitësh) | ✅ |
| Madhësia e sistemit për 16 raunde | ≈ 2 944 S-box (1 024 shifra + 1 920 orari) → ≈ **115 000 ekuacione kuadratike, ≈ 24 000 ndryshore** | ℹ️ nuk dihet metodë që e zgjidh |

**Testet "cube"** (bitet e zgjedhura marrin të gjitha vlerat; numërohen bitet dalëse me shumë zero; rastësia ≈ 256 nga 512):

| Kubi | R2 | R3 | R4 |
|---|---|---|---|
| 8 bit në 1 bajt | 512, 512 | **512, 512** | 241, 264 |
| 8 bit të shpërndarë | 512, 512 | 236, 263 | 247, 255 |
| 12 bit të shpërndarë | 512, 512 | 259, 234 | 258, 248 |
| 16 bit të shpërndarë | 512, 512 | **512**, 257 | 258, 232 |

⚠️ **Shpjegimi i 512-ës në 3 raunde me 16 bit të shpërndarë.** Kjo nuk ishte e parashikuar në plan, por ka shpjegim. Në raundin 1 çdo S-box sheh vetëm 1 bit të ndryshueshëm, kështu që dalja e tij është **afine**. Nëse lëvizja e kalit i çon bitet e kubit **≤ 2 për rresht**, shkalla pas raundit 2 është ≤ 2 dhe pas raundit 3 ≤ 14 < 16, pra shuma del zero. Në përgjithësi, me k bit për rresht dhe 8k bit gjithsej, shkalla në raundin 3 është ≤ 7k < 8k. Kjo është **dallues 3-raundësh**, njësoj si integrali i njohur. **Në 4 raunde nuk u gjet asnjë shumë zero.**

## K. Orari i çelësit

| Matja | Rezultati | |
|---|---|---|
| 1 bit çelësi → bitet e ndryshuara te RK_0, RK_1, RK_2, RK_4, RK_8, RK_16 (1 230 prova) | **≈ 50%** te të gjithë, që nga **RK_0**, sepse 8 hapa përzierjeje i paraprijnë | ✅ |
| Lëvizja e kalit ndryshon kur ndryshon 1 bit çelësi | 97,0% (pritet 1 − 1/32 = 96,9%) | ✅ |
| Çelësa me strukturë (zero, njësha, vetëm biti 0, 0x55…, rritës) | RK: 50–51% njësha. Dalja (3 000 blloqe): monobit z ≤ 1,98, χ² e bajteve 218–275 < 310,5 | ✅ asnjë "çelës i dobët" i dukshëm |
| **Rikthimi i çelësit kryesor nga çelësat e raundeve** | **3 çelësa raundesh të njëpasnjëshëm + numri publik → çelësi 410-bitësh në 0,1 s**, 3/3 prova, 1 kandidat i vetëm | ⚠️ **gjetje e rëndësishme** |
| Me 2 çelësa raundesh të njëpasnjëshëm | mbeten **3 bajte të panjohur → 2²⁴ kandidatë** (llogaritje, jo e ekzekutuar) | ⚠️ |

⚠️ **Çfarë do të thotë gjetja K.** Orari është i kthyeshëm me qëllim, sepse çdo hap është bijeksion. Kjo ndodh edhe te AES-256, ku dy çelësa raundesh të njëpasnjëshëm japin drejtpërdrejt çelësin.

**Pasojat:**
1. Një sulm që rikthen 2–3 çelësa raundesh rikthen edhe **çelësin kryesor**. Sulmi ynë 4-raundësh rikthen RK_4. Me shumë gjasë, RK_3 dhe RK_2 rikthehen me "qërim" raund pas raundi, gjë që do ta bënte sulmin 4-raundësh **rikthim të plotë të çelësit**. Kjo nuk u ekzekutua.
2. Me lojën sipas bllokut, çdo bllok ka çelësat e vet të raundeve, por **nëse çelësat e raundeve të një blloku të vetëm zbulohen, zbulohet çelësi kryesor dhe të gjitha blloqet bien**. Loja unike nuk e izolon çelësin kryesor.
3. Kjo **nuk thyen** BRI-410 me 16 raunde, sepse askush nuk di të rikthejë çelësa raundesh në 16 raunde. Por **punimi duhet ta thotë qartë**.

## T. Tekst dhe numër i zgjedhur

| Matja | Rezultati (bajte pa ndryshim; rastësia ≈ 0,25) | |
|---|---|---|
| Diferencë e njëkohshme në mesazh dhe numër, që përpiqet të anulojë diferencën e RK_0. **0 hapa** përzierjeje (version i dobësuar) | R1: **56,5** · R2: 0,59 (max 13) · R3: 0,27 | ⚠️ shkurtore vetëm në versionin e dobësuar |
| E njëjta, **4 hapa (zyrtari)** | R1: 0,20 · R2: 0,32 · R3: 0,21 | ✅ si rastësia |
| 16 raunde, numri = 0, 1, 2…, mesazhi zero (10 000 blloqe, 640 KB) | monobit z 0,11 · vargjet z 0,04 · χ² bajte 260 · χ² nibble 12,4 | ✅ nën pragjet 99% |
| 16 raunde, mesazhi = 0, 1, 2…, numri fiks | monobit z 1,28 · vargjet z 1,30 · χ² bajte 257 · χ² nibble 22,5 | ✅ |

Testet statistike kapin vetëm gabime të trasha. Kalimi i tyre **nuk provon** siguri.

## Përmbledhja

| Kategoria | Çfarë qëndron | Çfarë mbetet e hapur |
|---|---|---|
| D diferenciale | S-box 2⁻⁶; implementimi = teoria; dallues vetëm deri në 2 raunde; kufiri 81/4 raunde (F4-b) | bashkimi i rrugëve; boomerang; impossible differential |
| L lineare | S-box 2⁻³; 1 raund = teoria; kufiri i provuar si te D | testi statistik ishte i dobët; linear hull |
| A algjebrike | 39 ekuacione si AES, 0 struktura lineare; zero-shumat ndalen në 3 raunde dhe kanë shpjegim | division property; Gröbner/XL për raunde të shkurtuara |
| K orari | ortek ≈ 50% nga RK_0, pa çelësa të dobët të dukshëm | ⚠️ **3 RK → çelësi kryesor (0,1 s)**; 2 RK → 2²⁴; rikthimi i plotë 4-raundësh i paekzekutuar |
| T i zgjedhur | asnjë shkurtore me 4 hapa; statistikat në rregull | sulme related-tweak me gjasë (jo vetëm integrale) |

## Çfarë duhet të hyjë në versionin 2 të punimit

1. Pesë kategoritë si strukturë e seksionit të analizës, me të gjithë numrat e mësipërm, përfshirë dobësitë.
2. Gjetja K (kthyeshmëria e orarit) e shkruar qartë, me pasojat për lojën sipas bllokut.
3. Shpjegimi algjebrik i zero-shumave në 3 raunde.
4. Testi linear statistik **nuk përfshihet si provë**. Përfshihet vetëm kontrolli i saktë i 1 raundit.
5. Për çdo kategori: çfarë kemi bërë dhe çfarë ftojmë të tjerët ta bëjnë.
