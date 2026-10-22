# BRI-410 — Specifikimi F0 (version pune 0.7, 2026-10-22; 0.2: α = 0; 0.3: formatet dhe θ e fundit, F2; 0.4: emri; 0.5: V-N; 0.6: V-N + 32 raunde; 0.7: BRI-410/8 zyrtar)

> **BRI-410 ZYRTAR (vendim i pronarit, 2026-10-22, pas F5): BRI-410/8, i përshkruar te §10.**
> Tabela 8×8 me kuti 8-bitëshe, bllok 512 bit, çelës 410 bit, lojë e re për çdo bllok ("çdo lojë luhet vetëm një herë"),
> **16 raunde** ("16 gurët e çdo lojtari"). Në kod: `shahu.bri8.kripto_bllok(celesi, numri, bllok)` / `dekripto_bllok(...)`.
>
> **§2–§9 përshkruajnë BRI-410/4**, versionin e parë me kuti 4-bitëshe (bllok 256 bit). Ai mbahet për historikun dhe për
> riprodhimin e matjeve F1–F4-a. U zëvendësua sepse kutitë 4-bitëshe e lejonin sulmin integral 1 raund më larg se te AES-i (F3, F5).

> **Statusi:** algoritëm studimi. Nuk është analizuar nga kriptografë të pavarur.
> **Mos e përdor për të dhëna reale.** Për to përdor AES-GCM ose ChaCha20-Poly1305.

> **Autori:** Rinald Cobaj. **Licenca:** CC0 1.0 (domen publik). BRI-410 nuk është i patentuar.
>
> **Emri:** BRI-410, i zgjedhur nga pronari më 2026-10-22. Gjatë F0–F3 emri i punës ishte "Shahu".
> Para zgjedhjes u kontrollua që nuk ekziston shifër me emrin BRI. Emrat e afërt (BRIE, B-R) janë të tjerë dhe pak të njohur.
> Etiketa e S-box-it mbetet `"Shahu S-box v1"`, sepse ndryshimi i saj do të prodhonte një S-box tjetër (§4.1).
> Dosja e projektit (`Shahu_Kripto`) dhe paketa e kodit (`shahu`) mbajnë emrin e vjetër. Klasat: `BRI410_8` (zyrtari), `BRI410` (BRI-410/4).

## 1. Ideja

Rregullat e shahut i di gjithkush, por loja e luajtur është unike dhe nuk përsëritet.
Kështu edhe këtu: **algoritmi është publik**, kurse **çelësi** (një "lojë" nga ≈ 10^123) është sekret.
Siguria mbështetet vetëm te çelësi (parimi i Kerckhoffs-it).

| Publike | Sekrete |
|---|---|
| ky specifikim, kodi, numri i raundeve, matjet | çelësi 410-bitësh dhe gjithçka që nxirret prej tij |

## 2. Parametrat

| Parametri | Vlera | Burimi |
|---|---|---|
| Blloku | 256 bit = tabelë 8×8, çdo kuti 4 bit (nibble) | 64 kutitë e shahut |
| Çelësi | 410 bit (ruhet si 52 bajte, 6 bitët e tepërt = 0) | 2^410 ≈ 10^123 (vlerësimi i Allis-it për lojërat) |
| Raunde R | **32** (vendim pas F3/F3-bis; F4 verifikon nëse mjaftojnë) | §8 |
| Numri unik | 128 bit, publik, i ndryshëm për çdo bllok me të njëjtin çelës | §6.1 |
| Burimi i çelësit | gjeneratori kriptografik i sistemit (`secrets`) | jo lojë e zgjedhur nga njeriu |

## 3. Shënimet

- Gjendja `X` = 64 nibble. Kutia `(r, k)` (rreshti r, kolona k, 0..7) ka indeksin `8·r + k`.
- Aritmetika e kutive: fusha GF(2⁴) me polinomin `x⁴ + x + 1`.
- Bajtet → nibble (fiksuar në F2): nibble `2i` = 4 bitët e ulët të bajtit `i`, nibble `2i+1` = 4 të lartët.
- Çelësi si bajte (fiksuar në F2): 52 bajte little-endian; 6 bitët e sipërm të bajtit 51 duhet të jenë 0.

## 4. Komponentët

### 4.1 Zëvendësimi i figurave: S-box 4-bitësh (jolineariteti)

```
S = 5 6 C 4 0 F B 9 2 E 3 1 A 7 8 D   (heks, S[0]..S[15])
```

Nxirret pa "mister": permutacioni i parë nga `SHAKE-256("Shahu S-box v1" ‖ numëruesi)`
(Fisher–Yates me refuzim) që plotëson **të gjitha** kriteret:
uniformitet diferencial 4, linearitet 8 (optimale për 4 bit), të 15 komponentët me shkallë 3,
pa pika fikse `S(x) = x` dhe `S(x) = x ⊕ F`. U gjet te numëruesi 537. Kushdo mund ta riprodhojë.

### 4.2 Lëvizja e kalit: permutimi π (difuzioni ndërmjet rreshtave)

Çdo kuti në kolonën k bën **k kërcime kali** (dr, dk) në një tabelë toroidale, pastaj tabela zhvendoset (α, β):

```
(r, k) → (r + k·dr + α,  k + k·dk + β)   mod 8
```

- **V-F (fiks):** (dr, dk) = (1, 2), α = β = 0.
- **V-L ("loja"):** në çdo raund çelësi zgjedh drejtimin nga {(1,2), (1,−2), (−1,2), (−1,−2)} dhe β ∈ 0..7, pra **5 bit për raund**.
  Vetëm këto 4 drejtime (dr tek, dk çift) garantojnë që çdo rresht të shpërndahet në të 8 rreshtat.
  **α = 0 gjithmonë** (vendim i pronarit, 2026-10-22). F1 tregoi që zhvendosja e rreshtave komuton me
  gjithë raundin pa çelës, pra 3 bitët e saj do të ishin lojë vetëm në dukje.

### 4.3 Kapja: MDS 8×8 mbi GF(16) (difuzioni brenda rreshtit)

Matrica Cauchy `M[i][j] = 1 / (x_i ⊕ y_j)`, x = 0..7, y = 8..15. Zbatohet mbi secilin nga 8 rreshtat.
Numri i degëve = 9 (maksimumi për 8 kuti): nëse ndryshon 1 kuti, ndryshojnë të 8 kutitë e rreshtit.
Matrica është **involutive** (M·M = I), kështu që dekriptimi përdor të njëjtën matricë.

### 4.4 Shtimi i çelësit

`X ← X ⊕ RK_i` (256 bit).

## 5. Kriptimi dhe dekriptimi

```
X ← X ⊕ RK_0
për i = 1 .. R:
    X ← S(X)            (në të 64 kutitë)
    X ← π_i(X)          (V-F: π fiks; V-L: π me lëvizjen e raundit i)
    X ← θ(X)            (MDS mbi çdo rresht)
    X ← X ⊕ RK_i
```

Dekriptimi kryen të njëjtat hapa mbrapsht: `⊕ RK_i → θ → π_i⁻¹ → S⁻¹`, për i = R .. 1, dhe në fund `⊕ RK_0`.
**Vendim F2:** të gjitha raundet janë identike, pra edhe raundi i fundit e mban θ-n. AES e heq atë për
simetrinë e implementimit, por këtu M është involutive, kështu që dekriptimi përdor gjithsesi të njëjtën matricë.
θ-ja e fundit nuk shton as heq siguri, sepse është lineare dhe pa çelës pas saj.

## 6. Orari i çelësit ("loja")

Gjendja e çelësit ka 416 bit = 104 nibble = 13 rreshta × 8:
bitet 0..409 janë çelësi, bitet 410..415 janë konstantja `101101`.

Çdo hap `F_i` (i = 1, 2, …) është **bijeksion**:
`S` mbi 104 nibble → `M` mbi 13 rreshta → permutim `j → 9·j mod 104` → `nibble[100..101] ⊕= i`.

- `RK_0` = 256 bitët e parë të çelësit (pa përpunim, si te AES).
- `RK_i` = nibble 0..63 pas hapit i.
- Lëvizja e raundit i = nibble 64, 65 pas hapit i → drejtimi (2 bitët e ulët të nibble 64),
  β (2 bitët e lartë të nibble 64 + biti i ulët i nibble 65); α = 0.

Numëruesi `i` në çdo hap thyen simetrinë mes raundeve (kundër sulmeve slide).

### 6.1 Loja sipas bllokut: V-N (F3-bis, ideja "çdo lojë luhet vetëm një herë")

Çelësi gjenerohet **një herë**. Çdo bllok merr një **numër unik** 128-bitësh, publik, që **nuk përsëritet kurrë** me të njëjtin çelës:

```
g ← ngarko(çelësi)
g ← F_{0xF3}(F_{0xF2}(F_{0xF1}(F_{0xF0}(g))))      (përzierja e çelësit)
g[0..31] ⊕= numri                                  (32 nibble, little-endian)
g ← F_{0xF7}(F_{0xF6}(F_{0xF5}(F_{0xF4}(g))))      (përzierja e numrit)
```

Nga kjo gjendje nxirren, si në §6, `RK_0`, `RK_1..R` dhe lëvizjet. Pra **loja dhe të gjithë çelësat e raundeve** ndryshojnë për çdo bllok.
Konstantet 0xF0..0xF7 ndryshojnë nga ato të raundeve, ndaj R < 240.
Përsëritja e numrit me të njëjtin çelës e kthen V-N në nivelin e V-L (u mat në F3-bis).

## 7. Kriteret e fazave

| Faza | Çfarë matet | Kriteri |
|---|---|---|
| F1 | komponentët veç e veç | S-box optimal; MDS me numër degësh 9; π me përhapje të plotë; orari bijektiv dhe me efekt ortek |
| F2 | prototipi i plotë | dekriptimi kthen 100% të mostrave; efekti ortek ≈ 50% |
| F3 | V-F kundrejt V-L, 256 kundrejt 512 bit, krahasim me AES | vendim me numra |
| F4 | kufijtë e S-box-eve aktive (MILP/SAT), sulme me raunde të reduktuara | numri i raundeve |

## 8. Rregulli i raundeve

Matim R₁ (difuzioni i plotë), R₂ (kufiri i S-box-eve aktive kalon 128) dhe R₃ (sulmi më i mirë që provojmë).
**R = 2 × max(R₁, R₂, R₃).** Nëse R ≤ 16, zgjidhet 16. Nëse 16 < R ≤ 32, zgjidhet 32. Përndryshe rritet.

## 9. Rreziqet e njohura që duhen analizuar

1. Simetritë e tabelës dhe të matricës mund të krijojnë nënhapësira invariante (sulme që nuk varen nga numri i raundeve).
2. Lëvizjet që varen nga çelësi (V-L) duhet të zbatohen në kohë konstante, pa akses në memorie që varet nga sekreti.
3. Orari i çelësit e përdor të njëjtin S-box dhe matricë si raundi, ndaj duhet analizë me çelësa të lidhur (related-key).
4. Kufijtë wide-trail vlejnë për gjurmë të veçanta, jo për diferenciale të grumbulluara, dhe verifikohen në F4.
5. **(F3)** Dallues integral në 4 raunde me 2^12 tekste (3 nibble të rreshtuara pas π₁). Sulm i ekzekutuar mbi 5 raunde,
   6 raunde të vlerësuara me ≈ 2^48 punë. Kjo është 1 raund më keq se AES-i, me shumë gjasë për shkak të S-box-it 4-bitësh me shkallë 3.
6. **(F3)** Loja (V-L) fsheh 5 bit për pozicionin, por vetëm 1 bit për rreshtin, sepse rreshti varet vetëm nga dr.
7. **(F3-bis)** V-N e bllokon sulmin integral (0/3 kundrejt 3/3 te V-L). Sipërfaqja e re e sulmit janë **numrat e zgjedhur
   me ndryshime të qëllimshme** (related-tweak) mbi përzierjen çelës + numër. Kjo analizohet në F4.
8. **(F4-a)** Integrali me numra të zgjedhur: shkurtore vetëm me ≤ 1 hap përzierjeje pas numrit dhe ≤ 2 raunde.
   Zyrtari (4 hapa, 32 raunde): rastësi. Mbeten për F4-b diferencialet related-tweak dhe kufijtë MILP/SAT.
9. **(F5)** Kutitë 4-bitëshe janë burimi i dobësisë integrale. BRI-410/8 (§10) e rregullon: dallues vetëm në 3 raunde.
10. **(F4-b)** Për BRI-410/8, CP-SAT provoi: 4 raunde ≥ 81 S-box aktive (≤ 2⁻⁴⁸⁶), 6 raunde ≥ 90 (≤ 2⁻⁵⁴⁰), për çdo lojë.
    Orari pas numrit: 4 hapa ≥ 81 (≤ 2⁻⁴⁸⁶). Mbeten: diferencialet e grumbulluara, linear hull, division property.

## 10. BRI-410/8 — VERSIONI ZYRTAR (F5)

> **Statusi:** zyrtar që nga 2026-10-22 (vendim i pronarit). Kod: `shahu/bri8.py`, klasa `BRI410_8(celesi, raunde, numri)`,
> funksionet `kripto_bllok` / `dekripto_bllok` (16 raunde). Vektorët e testit: `teste/vektoret_f5.json`.

| Parametri | Vlera |
|---|---|
| Tabela | 8×8 = 64 kuti, **8 bit për kuti** |
| Blloku | **512 bit** (64 bajte; bajti i = kutia i) |
| Çelësi | 410 bit (52 bajte, si më lart) |
| Numri unik | 128 bit, publik, i ndryshëm për çdo bllok (vetëm V-N; nuk ka V-F/V-L) |
| Raunde | **16** ("16 gurët e çdo lojtari"), rregulli 2 × max(2, 6, 4–5) = 12 ≤ 16 |

**Komponentët**
- **GF(2⁸)** me polinomin `x⁸ + x⁴ + x³ + x + 1` (0x11B).
- **S-box:** `S(x) = A · x⁻¹ ⊕ c` (me `0⁻¹ = 0`). `A` (8 rreshta-bajte, e kthyeshme) dhe `c` janë 9 bajtet e
  `SHAKE-256("BRI-410 S-box8 v1" ‖ n)`. `n` është numëruesi i parë (4 bajte big-endian) që jep `A` të kthyeshme dhe
  asnjë pikë fikse `S(x) = x` ose `S(x) = x ⊕ FF`. Rezultati: `n = 9`. Biti `i` i `A·y` = barazia e `A[i] & y`.
  Matjet: DU 4, jolinearitet 112, shkallë 7 (si AES).
- **Lëvizja e kalit π:** e njëjta si §4.2 (64 kuti, drejtimi + β nga loja, α = 0).
- **Kapja θ:** Cauchy 8×8 mbi GF(2⁸), `M[i][j] = 1/(x_i ⊕ y_j)`, `x = 0..7`, `y` = 8 bajtet e para të ndryshëm dhe
  jo në `x` nga `SHAKE-256("BRI-410 MDS8 v1")` = `[145, 234, 150, 206, 98, 226, 235, 94]`. MDS e provuar (0 / 12 869
  nënmatrica singulare), pa simetri kolonash, jo involutive: dekriptimi përdor `M⁻¹`.

**Orari (80 bajte = 10 rreshta × 8)**
- Ngarkimi: bitet 0..409 = çelësi; bitet 410..639 = 230 bitët e ulët të `SHAKE-256("BRI-410/8 mbushja")` (29 bajte, little-endian).
- Hapi `F_i`: S mbi 80 bajte → θ (M) mbi 10 rreshta → bajti `j` shkon te `9·j mod 80` → `bajti[79] ⊕= i`.
- Numri: `F_{F0..F3}` → `bajtet[0..15] ⊕= numri` → `F_{F4..F7}`.
- `RK_0` = bajtet 0..63 pas kësaj. `RK_i` = bajtet 0..63 pas `F_i`. Lëvizja e raundit `i` nga bajti 64:
  drejtimi = `DREJTIMET[b & 3]`, β = `(b >> 2) & 7`.

**Kriptimi:** si §5, me S, π, θ të mësipërm dhe 16 raunde. **Dekriptimi:** `⊕ RK_i → θ⁻¹ → π_i⁻¹ → S⁻¹`.

## 11. BRI-410 AE: mënyra e përdorimit me vulë (hapi 2)

Kod: `shahu/menyra.py` (`kripto`, `dekripto`, `kripto_me_numer`, `dekripto_me_numer`, `VulaEGabuar`). Raporti: `docs/F6_RAPORTI.md`.

- **Modeli:** ΘCB3 (Krovetz–Rogaway 2011) mbi BRI-410/8 (16 raunde) si shifër me lojë.
- **Vula:** 416 bit = 52 bajte ("sa çelësi", vendim i pronarit). **Numri i mesazhit:** 12 bajte, unik për çdo mesazh me të njëjtin çelës.
- **Numri i BRI-410/8 për çdo thirrje:** `N (12 bajte) ‖ ((indeksi << 4) | lloji)` (4 bajte little-endian), `indeksi < 2²⁸`.
  Llojet: 0 bllok mesazhi, 1 maska e pjesës së fundit, 2 vula (pa pjesë të fundit), 3 vula (me pjesë të fundit),
  4 bllok shoqërues, 5 pjesa e fundit shoqëruese. Për të dhënat shoqëruese `N = 0¹²`.
- **Kriptimi** (blloqe 64 bajte, `pad(x) = x ‖ 80 ‖ 00…`):
  `C_i = E^(N,i,0)(M_i)`; nëse ka pjesë të fundit: `C_* = M_* ⊕ E^(N,m,1)(0⁶⁴)`, `F = E^(N,m,3)(⊕M_i ⊕ pad(M_*))`,
  përndryshe `F = E^(N,m,2)(⊕M_i)`; `Auth = ⊕E^(0,i,4)(A_i) [⊕ E^(0,a,5)(pad(A_*))]`; `Vula = (F ⊕ Auth)[:52]`.
- **Paketa:** `N ‖ C ‖ Vula` (64 bajte shtesë). Dekriptimi nuk kthen asgjë nëse vula nuk përputhet (krahasim në kohë konstante).
