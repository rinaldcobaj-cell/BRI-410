# BRI-410: Një shifër blloku 512-bitëshe me "lojë", me rirenditje që varen nga çelësi dhe nga numri unik

**Rinald Cobaj**, Studiues i pavarur, vlorarino@gmail.com

*Përkthim në shqip për autorin i versionit 2 të punimit (2026-10-27), që përshkruan BRI-410 v1.1. Versioni për publikim është ai në anglisht. BRI-410 është shifër studimi: nuk është analizuar nga kriptanalistë të pavarur dhe nuk duhet përdorur për të mbrojtur të dhëna reale. Kodi, vektorët dhe skriptet: https://github.com/rinaldcobaj-cell/BRI-410*

## Përmbledhja

BRI-410 është një shifër blloku eksperimentale me "lojë" (*tweakable block cipher*): bllok 512-bitësh, çelës 410-bitësh, numër unik ("lojë", *tweak*) 128-bitësh dhe 16 raunde. Shoqërohet nga BRI-410 AE, një zbatim i mënyrës së kriptimit me vulë ΘCB3, me vulë 416-bitëshe. BRI-410 është një rrjet zëvendësim-rirenditje me çelës të alternuar (SPN) mbi një tabelë 8×8 bajtesh. Përdor një S-box 8-bitësh, afin-ekuivalent me S-box-in e AES-it, dhe një matricë Cauchy MDS 8×8. Veçoria e saj është shtresa e rirenditjes: në çdo raund, çelësi dhe numri zgjedhin një rirenditje të kutive nga një familje me 32 rirenditje "lëvizje kali", të cilat janë të gjitha me përhapje optimale në të dy drejtimet. Provojmë që kufiri wide-trail me 81 S-box aktive në katër raunde vlen për çdo sekuencë rirenditjesh nga kjo familje. Për karakteristikat diferenciale dhe rrugët lineare të veçanta, kjo jep të paktën 324 S-box aktive në 16 raunde. Një model CP-SAT i konfirmon vlerat për 1 deri në 5 raunde. Ky kufi nuk është provë e sigurisë së përgjithshme të BRI-410. Të gjithë çelësat e raundeve dhe rirenditjet nxirren nga çelësi dhe numri. Versioni 1.1 shton një feed-forward Davies–Meyer pas futjes së numrit, që synon ta bëjë nxjerrjen për çdo bllok të pakthyeshme, sepse te versioni 1.0 tre çelësa raundesh të njëpasnjëshëm të një blloku të vetëm zbulonin çelësin kryesor për 0,1 sekonda. Kjo pakthyeshmëri është hamendje, jo veti e provuar. E dokumentojmë këtë dobësi dhe rezultatet e tjera negative të projektimit, mes tyre një paraardhës me kuti 4-bitëshe që e thyem në 5 raunde. Raportojmë eksperimente në pesë kategori kriptanalize, i mbajmë të ndara provat, llogaritjet, eksperimentet dhe hamendjet, dhe rendisim pyetjet e hapura për analizë të pavarur. Nuk pretendojmë asnjë avantazh praktik ndaj projektimeve ekzistuese.

## 1. Hyrja

Rregullat e shahut janë publike, e megjithatë një lojë serioze pothuajse kurrë nuk përsëritet. BRI-410 nis nga kjo analogji: algoritmi është publik, ndërsa çelësi, një "lojë", është sekret. Për më tepër, çdo bllok i kriptuar luan lojën e vet, të nxjerrë nga çelësi dhe nga një numër unik për bllokun. Tabela 8×8 përcakton gjendjen. Lëvizja e kalit jep shtresën e rirenditjes. Gjatësia e çelësit vjen nga vlerësimi i Allis-it për rreth 10^123 lojëra shahu [All94], sepse log2(10^123) ≈ 408,6. **Kjo zgjedhje është simbolike.** Nuk pretendojmë që siguria mbi 256 bit ka kuptim praktik, dhe objektivi ynë i sigurisë (seksioni 9) është më i ulët se 2^410.

Qëllimi i këtij punimi nuk është të propozojë një zëvendësues për shifrat ekzistuese. Punimi e përshkruan BRI-410 aq plotësisht sa kriptanalistët e pavarur ta analizojnë, ta sfidojnë dhe, nëse është e mundur, ta thyejnë. Gjithashtu regjistron çdo dobësi që gjetëm gjatë projektimit.

**Kontributet.**

1. Specifikimi i plotë i BRI-410 v1.1 (shifër blloku 512-bitëshe me lojë, çelës 410-bitësh, numër 128-bitësh) dhe i BRI-410 AE (seksionet 3 dhe 4).
2. Prova që kufijtë wide-trail për dy raunde (9) dhe katër raunde (81), për karakteristikat diferenciale dhe rrugët lineare të veçanta, vlejnë për çdo zgjedhje të rirenditjeve të raundeve që varet nga çelësi dhe numri, si për shifrën ashtu edhe për orarin e çelësit (seksioni 5).
3. Regjistrimi i procesit të projektimit me rezultatet negative: një parametër i padobishëm (α), një "lojë" që varet nga çelësi por fsheh vetëm 1 bit për raund në nivel rreshti, një paraardhës me kuti 4-bitëshe i thyer në 5 raunde, dhe një orar çelësi i kthyeshëm te versioni 1.0, bashkë me ndryshimin që e rregullon (seksionet 7 dhe 10).
4. Eksperimente në pesë kategori: diferenciale, lineare, algjebrike, orari i çelësit, dhe tekst/numër i zgjedhur (seksioni 6). Pyetjet e hapura dhe objektivat konkrete janë te seksioni 12.

**Llojet e provave.** Çdo pohim ka një etiketë:

- **[Provë]** provë matematike e dhënë në këtë punim
- **[Llogaritje]** llogaritje e saktë me kompjuter (kontroll i plotë ose zgjidhës)
- **[Eksperiment]** matje statistikore ose me mostra
- **[Vlerësim]** vlerësim kompleksiteti që nuk u ekzekutua
- **[Hamendje]** hipotezë që e besojmë, por nuk e mbështesim dot me provë
- **[E hapur]** pyetje që nuk e studiuam

## 2. Punimet e lidhura dhe vendi i BRI-410

**Shifrat me lojë.** Liskov, Rivest dhe Wagner i prezantuan shifrat e bllokut me lojë [LRW02]. Korniza TWEAKEY [JNP14] e përpunon çelësin dhe lojën me një orar të lehtë, linear. Mbi të ndërtohen SKINNY [BJK+16] dhe Deoxys-BC [JNPS21], me blloqe 64 dhe 128 bit dhe me analizë publike të gjerë. Threefish [FLS+10], shifra e Skein-it, është më e afërta për nga madhësia: blloqe 256, 512 dhe 1024 bit, lojë 128-bitëshe, por është projektim ARX (mbledhje, rrotullim, XOR) me 72 raunde për bllokun 512-bitësh.

**SPN me bllok të gjerë.** Rijndael-i mbështet blloqe 256-bitëshe [DR02]. Kalyna [OGK+15] është standard SPN me bllok dhe çelës 512-bitësh, S-box 8-bitësh dhe matrica MDS 8×8 mbi GF(2^8), por pa lojë.

**Pjesë që varen nga çelësi dhe nxjerrja e çelësave të rinj.** Blowfish [Sch93] dhe Twofish [SKW+98] i nxjerrin S-box-et nga çelësi. Nxjerrja e një çelësi të ri për çdo mesazh ose bllok është teknikë e njohur, e analizuar p.sh. te [AB00]. Ndërtimi Davies–Meyer nga funksionet hash shton një feed-forward, me të cilin dalja besohet të jetë e vështirë për t'u përmbysur kur permutimi bazë është i fortë [PGV93].

| Shifra | Blloku | Çelësi | Loja | Raunde | Struktura | Përpunimi i lojës |
|---|---|---|---|---|---|---|
| AES-256 | 128 | 256 | — | 14 | SPN, S-box 8-bit, MDS | — |
| Kalyna-512/512 | 512 | 512 | — | 18 | SPN, S-box 8-bit, MDS | — |
| Threefish-512 | 512 | 512 | 128 | 72 | ARX | shtohet te nënçelësat |
| SKINNY, Deoxys-BC | 64 / 128 | (tweakey) | (tweakey) | 14–56 | SPN | orar linear TWEAKEY |
| **BRI-410 v1.1** | **512** | **410** | **128** | **16** | **SPN, S-box 8-bit, MDS** | **nxjerrje e plotë e të gjithë çelësave dhe rirenditjeve, që synon të jetë e pakthyeshme (Davies–Meyer, e paprovuar)** |

**Vendi i BRI-410.** BRI-410 nuk sjell përfitim shpejtësie. Rinxjerrja e gjithë orarit për çdo bllok është më e ngadaltë se TWEAKEY (seksioni 11). Ajo që studiojmë është një pikë tjetër projektimi: një shtresë rirenditjeje që varet nga çelësi dhe numri, e zgjedhur në çdo raund nga një familje me përhapje optimale për çdo zgjedhje. Si pasojë, kufijtë klasikë wide-trail vlejnë njëlloj për të gjithë çelësat dhe numrat. Me sa dimë, ky kombinim i saktë nuk është përshkruar më parë. Pjesët që varen nga çelësi dhe çelësat e raundeve që varen nga loja janë, më vete, të njohura.

## 3. Specifikimi i BRI-410 v1.1

### 3.1 Shënimet dhe parametrat

| Parametri | Vlera |
|---|---|
| Blloku | 512 bit = 64 bajte. Bajti i është kutia (r, k) = (⌊i/8⌋, i mod 8) e tabelës 8×8; rreshti r = bajtet 8r..8r+7 |
| Çelësi | 410 bit, si 52 bajte little-endian me 6 bitët e sipërm 0 |
| Numri unik (loja) | 128 bit (16 bajte) |
| Raunde | R = 16 |
| Fusha | GF(2^8) me polinomin x^8 + x^4 + x^3 + x + 1 |

### 3.2 Përbërësit

**S-box-i S.** `S(x) = A·x^-1 ⊕ c` (me 0^-1 = 0). Këtu `A` është matricë binare 8×8 e kthyeshme: rreshti i është një bajt, dhe biti i i `A·y` është barazia e `A[i] AND y`. `c` është një bajt. `A ‖ c` janë 9 bajtet e `SHAKE-256("BRI-410 S-box8 v1" ‖ n)`, ku n është numëruesi i parë (4 bajte big-endian) që jep `A` të kthyeshme dhe S-box pa pika S(x) = x ose S(x) = x ⊕ FF. Rezultati është n = 9. Tabela është te shtojca A.

**Familja e rirenditjeve π.** Për (dr, dk) ∈ D = ((1,2), (1,−2), (−1,2), (−1,−2)), në këtë rend, dhe β ∈ {0,…,7}:

```
π_(d,β):  kutia (r, k)  →  kutia (r + k·dr,  k + k·dk + β)   (mod 8)
```

Kutia (r, k) bën k kërcime kali (dr, dk) në një tabelë toroidale, pastaj tabela zhvendoset β kolona. Kjo jep 32 rirenditje, të gjitha të ndryshme.

**Shtresa lineare θ.** Çdo rresht shumëzohet me matricën 8×8 `M[i][j] = 1 / (x_i ⊕ y_j)`, ku x = (0,…,7) dhe y = (145, 234, 150, 206, 98, 226, 235, 94), 8 bajtet e para të ndryshme jashtë {0,…,7} nga `SHAKE-256("BRI-410 MDS8 v1")`. M dhe M^-1 janë te shtojca A.

### 3.3 Kriptimi dhe dekriptimi

```
X ← P ⊕ RK_0                             (zbardhja me RK_0, seksioni 3.4)
për i = 1 .. 16:
    X ← θ( π_i( S(X) ) ) ⊕ RK_i          (S mbi 64 bajtet; π_i e çon S(X)[c] te kutia π_i(c))
C ← X
```

Dekriptimi zbaton `⊕RK_i, θ^-1, π_i^-1, S^-1` për i = 16, …, 1, dhe në fund `⊕RK_0`. Të gjitha raundet janë identike. Edhe raundi i fundit zbaton θ-n.

### 3.4 Orari i çelësit dhe i numrit ("loja")

Gjendja G e orarit ka 80 bajte (10 rreshta me nga 8). Një hap është

```
F_c(G):  S mbi 80 bajtet → θ mbi secilin nga 10 rreshtat → bajti j shkon te pozicioni 9·j mod 80 → bajti 79 ⊕= c
```

Versioni 1.1 llogarit:

```
L   ← çelësi (bitet 0..409) ‖ 230 bitët e parë të SHAKE-256("BRI-410/8 mbushja") si little-endian (bitet 410..639)
K*  ← F_0xF3(F_0xF2(F_0xF1(F_0xF0(L))))            vetëm çelësi; i njëjtë për çdo numër
X   ← K* me bajtet 0..15 XOR numri
G_0 ← F_0xFB(…F_0xF4(X)…) ⊕ X                      8 hapa dhe feed-forward Davies–Meyer
RK_0 ← bajtet 0..63 të G_0                          çelësi i zbardhjes i seksionit 3.3
për i = 1 .. 16:
    G_i ← F_i(G_(i−1))
    RK_i ← bajtet 0..63 të G_i
    π_i  ← π_(D[b & 3], (b >> 2) & 7), ku b = bajti 64 i G_i
```

Pra ka 17 çelësa raundesh, RK_0 deri RK_16, dhe 16 rirenditje, π_1 deri π_16. Kostoja e orarit është (çdo hap llogarit 80 S-box):

| Procesi | Hapat | S-box |
|---|---|---|
| Përgatitja e çelësit K*, një herë për çelës dhe e përbashkët për të gjithë numrat | 4 | 320 |
| Përzierja e numrit, për çdo numër | 8 | 640 |
| Gjenerimi i çelësave të raundeve, për çdo numër | 16 | 1 280 |
| Orari për një numër, pa përgatitjen e përbashkët | 24 | 1 920 |
| Orari për numrin e parë me një çelës, me përgatitjen | 28 | 2 240 |

Me 1 024 S-box-et e 16 raundeve, blloku i parë me një çelës kushton 3 264 S-box, dhe çdo bllok pasues, që e ripërdor K*, kushton 2 944. Feed-forward-i është masë projektimi që synon ta bëjë të vështirë kthimin nga G_0 te X. **Nuk provojmë që është i pakthyeshëm** (hamendja 2 te seksioni 9).

**Versioni 1.0** (seksionet 6 deri në 8, historik) përdorte 4 hapa pas numrit dhe asnjë feed-forward: `G_0 = F_0xF7(…F_0xF4(X)…)`, pra 4 + 16 = 20 hapa për numër pas përgatitjes së përbashkët, ose 24 bashkë me të. Raundi i shifrës është i njëjtë në të dy versionet.

## 4. BRI-410 AE

BRI-410 AE zbaton ΘCB3 [KR11] me BRI-410/8 v1.1 si shifër blloku me lojë E. Çdo thirrje përdor numrin `N ‖ ((indeksi << 4) | lloji)`: numri i mesazhit N me 12 bajte, pastaj 4 bajte little-endian, me indeksi < 2^28. Llojet janë: 0 bllok mesazhi, 1 maska e bllokut të fundit të paplotë, 2 vula pa bllok të paplotë, 3 vula me bllok të paplotë, 4 bllok të dhënash shoqëruese, 5 blloku i fundit i paplotë i të dhënave shoqëruese. Të dhënat shoqëruese përdorin N = 0^12. Me M = M_1 … M_m M_* dhe A = A_1 … A_a A_* (|M_*|, |A_*| < 64 bajte), dhe pad(x) = x ‖ 80 ‖ 00…:

```
C_i   = E^(N,i,0)(M_i)                                                          i = 1..m
nëse M_* nuk është bosh:  C_* = M_* ⊕ E^(N,m,1)(0^512) i prerë;   F = E^(N,m,3)(⊕M_i ⊕ pad(M_*))
përndryshe:               F = E^(N,m,2)(⊕M_i)
Auth  = ⊕ E^(0,i,4)(A_i)   [⊕ E^(0,a,5)(pad(A_*))]
Vula  = 52 bajtet e para të (F ⊕ Auth)                                          416 bit
Paketa = N ‖ C ‖ Vula
```

Dekriptimi nuk kthen asgjë nëse vula nuk përputhet, dhe krahasimi bëhet në kohë konstante. Përputhja me ΘCB3 u kontrollua nga autori kundrejt përshkrimit të mënyrës, jo nga një palë e pavarur. **[E hapur]**

## 5. Rezultatet strukturore

**Lema 1 (familja e rirenditjeve). [Provë]** Çdo π_(d,β) është bijeksion me përhapje optimale në të dy drejtimet: 8 kutitë e çdo rreshti shkojnë në 8 rreshta të ndryshëm, dhe 8 kutitë që mbërrijnë në çdo rresht vijnë nga 8 rreshta të ndryshëm.

*Prova.* Harta e kolonave k → k(1 + dk) + β është bijeksion i Z_8, sepse 1 + dk ∈ {3, −1} është tek. Pasi dihet kolona, harta e rreshtave r → r + k·dr është bijeksion, ndaj π është bijeksion. Për një rresht burim të fiksuar r, rreshtat destinacion r + k·dr (k = 0..7) janë të ndryshëm, sepse dr = ±1 është i kthyeshëm mod 8. Për një rresht destinacion q, çdo kolonë k shfaqet saktësisht një herë mes kutive të tij, sepse harta e kolonave është bijeksion. Rreshti burim i kutisë me kolonë k është q − k·dr, dhe këta janë të ndryshëm. ∎

**Lema 2 (zhvendosja e rreshtave α nuk shton strukturë). [Provë]** Le të jetë T_α rrotullimi i rreshtave (r, k) → (r + α, k). T_α ndërrohet me S, që vepron kuti pas kutie; me çdo π_(d,β), sepse të dyja anët japin (r + α + k·dr, k(1+dk) + β); dhe me θ, që zbaton të njëjtën matricë në çdo rresht. Prandaj një T_α që varet nga raundi mund të shtyhet në fund të shifrës, duke e zëvendësuar RK_i me T(RK_i). Pra shton vetëm një rrotullim përfundimtar rreshtash që varet nga çelësi. Prandaj e hoqëm α (në një version të mëparshëm, matjet gjetën 1 792 çifte variantesh "loje" të barazvlefshëm deri në α). ∎

**Lema 3 (MDS). [Provë + Llogaritje]** Çdo nënmatricë katrore e një matrice Cauchy është matricë Cauchy, dhe përcaktori i saj është jo-zero kur x_i janë të ndryshëm, y_j janë të ndryshëm dhe x_i ≠ y_j [MS77]. Prandaj M është MDS, me numër degësh diferencial 9. Meqë kodi dual i një kodi MDS është MDS, edhe numri i degëve linear është 9. Kontrolluam gjithashtu të 12 869 nënmatricat katrore të M dhe të M^-1: asnjë nuk është singulare. M nuk ka asnjë simetri kolonash përveç identitetit.

**Teorema 1 (kufijtë për çdo sekuencë rirenditjesh). [Provë]** Merrni çdo rrugë diferenciale (ose lineare) nëpër r raunde të BRI-410 me hyrje jo-zero, për çdo çelës dhe çdo numër. Atëherë:
(a) çdo dy raunde të njëpasnjëshme përmbajnë të paktën 9 S-box aktive, dhe
(b) çdo katër raunde të njëpasnjëshme përmbajnë të paktën 81 S-box aktive,
për çdo sekuencë rirenditjesh π_i nga familja.

*Prova.* Le të jetë a_t numri i bajteve aktive në hyrje të shtresës S të raundit t, dhe ρ(·) numri i rreshtave aktivë.
(a) θ_t vepron rresht pas rreshti me numër degësh 9. Për çdo rresht aktiv në hyrje të saj, bajtet aktive në hyrje plus bajtet aktive në dalje janë ≥ 9. Bajtet hyrëse të θ_t janë daljet e S të raundit t, të zhvendosura nga π_t. Bajtet dalëse të saj janë hyrjet e S të raundit t+1, sepse shtimi i çelësit nuk e ndryshon aktivitetin. Duke mbledhur mbi rreshtat, a_t + a_(t+1) ≥ 9 · ρ(hyrja e θ_t) ≥ 9.
(b) Merrni raundet 1 deri në 4. Nga (a), a_1 + a_2 ≥ 9·ρ_1 dhe a_3 + a_4 ≥ 9·ρ_3, ku ρ_t është numri i rreshtave aktivë në hyrje të θ_t. Le të jetë q një rresht aktiv në hyrje të θ_2. Ka w_in bajte aktive, dhe rreshti i tij në dalje të θ_2 ka w_out bajte, me w_in + w_out ≥ 9. Bajtet w_in vijnë, përmes π_2, nga w_in rreshta të ndryshëm të gjendjes në hyrje të raundit 2 (Lema 1, drejtimi i kundërt). Secili prej këtyre rreshtave është rresht dalës i θ_1, ndaj është aktiv edhe në hyrje të θ_1, prandaj ρ_1 ≥ w_in. Bajtet w_out të rreshtit q janë hyrje të S të raundit 3, dhe π_3 i çon në w_out rreshta të ndryshëm (Lema 1, drejtimi i përparmë), prandaj ρ_3 ≥ w_out. Pra a_1 + … + a_4 ≥ 9(ρ_1 + ρ_3) ≥ 9(w_in + w_out) ≥ 81. Argumenti për rrugët lineare është i njëjtë: maskat përhapen nëpër transpozimin e θ, që ka gjithashtu numër degësh 9 (Lema 3). ∎

**Rrjedhim.** 4k raunde përmbajnë ≥ 81k S-box aktive. 16 raunde përmbajnë ≥ 324.

**Teorema 2 (orari i çelësit dhe i numrit). [Provë + Llogaritje]** Rirenditja j → 9j mod 80 e orarit i çon 8 bajtet e secilit nga 10 rreshtat në 8 rreshta të ndryshëm, dhe çdo rresht e merr nga 8 rreshta të ndryshëm [Llogaritje]. Prandaj prova e teoremës 1 vlen për hapat F_c. Çdo diferencë jo-zero në gjendjen e orarit, veçanërisht një diferencë në numër, aktivizon të paktën 81 S-box në 4 hapa dhe të paktën 162 në 8 hapat e v1.1 që i paraprijnë RK_0.

**Çfarë garantojnë këta kufij, dhe çfarë nuk garantojnë.**

- **Garantojnë** që çdo karakteristikë diferenciale e veçantë, ose rrugë lineare, aktivizon të paktën numrin e dhënë të S-box-eve, për çdo çelës, çdo numër dhe çdo zgjedhje rirenditjesh. Me gjasat maksimale 2^-6 për S-box, kjo do të thotë që çdo rrugë e vetme 4-raundëshe ka gjasë ≤ 2^-486 dhe çdo rrugë 16-raundëshe ≤ 2^-1944, **me supozimin e zakonshëm që çelësat e raundeve janë të pavarur**.
- **Nuk garantojnë** asgjë për (i) diferencialet, ku shumë rrugë mblidhen bashkë, (ii) "linear hull", (iii) lidhjet reale mes çelësave të raundeve që krijon orari, ose (iv) sulmet e llojeve të tjera: integrale, algjebrike, boomerang, impossible-differential, ose me çelësa të lidhur përtej kufirit të orarit.
- Veçanërisht, teoremat 1 dhe 2 **nuk janë provë e sigurisë së BRI-410 në tërësi**.

**Llogaritja. [Llogaritje]** Një model CP-SAT në nivel bajtesh aktive, ku sulmuesi zgjedh strukturën e rreshtave të π_i në çdo raund (shtojca C), dha numrin minimal të S-box-eve aktive: 1, 9, 17, 81 dhe 82 për 1 deri në 5 raunde (optimum i provuar), dhe 1, 9, 17, 81, 107 dhe 114 për 1 deri në 6 hapa të orarit. Për 6, 7 dhe 8 raunde gjeti rrugë me saktësisht 90, 98 dhe 162, që janë të barabarta me kufijtë që dalin nga teorema 1. Vlerat u llogaritën një herë (OR-Tools 9.15, 2026-10-22). Llogaritjet e mëvonshme në kompjuterin e autorit i bllokoi një rregull i sistemit operativ (application control), ndaj rillogaritja nga të tjerë është e mirëpritur. Provat e mësipërme nuk varen nga kjo llogaritje.

## 6. Eksperimentet në pesë kategori

Të gjitha eksperimentet përdorin fara fikse dhe janë në depo. Eksperimentet me shënimin "v1.0" u bënë para ndryshimit të orarit. Eksperimentet që përfshijnë vetëm raundin e shifrës nën një numër fiks (D, L, A) nuk varen nga mënyra si nxirren çelësat e raundeve. Eksperimentet K dhe T u përsëritën për v1.1 (seksioni 7).

### 6.1 Diferenciale (D)

| Matja | Rezultati | |
|---|---|---|
| Tabela e diferencave të S (255 × 256 hyrje) | 32 895 × 0, 32 130 × 2, 255 × 4; gjasa maksimale 2^-6 | [Llogaritje] |
| Një raund: diferenca dalëse më e shpeshtë (3 × 2^14 çifte) | frekuenca 0,0161 / 0,0157 / 0,0142, kundrejt 4/256 = 0,0156 të parashikuar; 127 dalje të ndryshme, siç parashikohet | [Eksperiment] |
| Një bajt aktiv në hyrje: sa bajte dalin me diferencë zero (300 çifte; rastësia 0,25) | 1 raund: 56 · 2 raunde: 0 në çdo çift · 3 raunde: 0,29 | [Eksperiment] |

Pas 2 raundeve çdo bajt është gjithmonë aktiv. Kjo i dallon 2 raunde nga një rirenditje e rastësishme, njësoj si te AES-i. Pas 3 raundeve nuk pamë asnjë shmangie.

### 6.2 Lineare (L)

| Matja | Rezultati | |
|---|---|---|
| S: korrelacioni maksimal | 32/256 = 2^-3 | [Llogaritje] |
| Një raund, e saktë: ndryshon vetëm bajti 0 (256 hyrje), bajti dalës 0 | korrelacioni maksimal 0,125, i barabartë me atë të S. Një bajt i një rreshti tjetër nuk ndryshon fare | [Llogaritje] |

**Rezultat negativ metodologjik.** Fillimisht bëmë një test statistik që lidh një bajt hyrës me një bajt dalës, mbi 2^18 mesazhe të rastësishme. Ai **nuk jep informacion për nga vetë ndërtimi**: kur bajtet e tjera hyrëse janë të rastësishme, bajti dalës është XOR i 8 daljeve S nga 8 bajte hyrës të ndryshëm, ndaj korrelacioni është zero edhe pas një raundi. Nuk e përdorim si provë. Rrugët lineare mbi dy ose më shumë raunde kanë korrelacion ≤ 2^-27 dhe nuk maten dot me eksperiment. **Argumenti i sigurisë lineare mbështetet te teorema 1.**

### 6.3 Algjebrike (A)

| Matja | Rezultati | |
|---|---|---|
| Ekuacione kuadratike linearisht të pavarura që lidhin hyrjen dhe daljen e S | 39, njësoj si S-box-i i AES-it me të njëjtin kod | [Llogaritje] |
| Struktura lineare të S | 0 | [Llogaritje] |
| Madhësia e një sistemi polinomial që shpreh një bllok në varësi të çelësit kryesor, v1.1 | 3 264 S-box (1 024 në shifër dhe 2 240 në orar, përfshirë 4 hapat që varen vetëm nga çelësi; seksioni 3.4): ≈ 127 000 ekuacione kuadratike (39 për S-box) me ≈ 26 500 ndryshore (8 për çdo dalje S-box-i plus 410 bitët e çelësit). Çdo bllok tjetër me të njëjtin çelës shton 2 944 S-box. Ky është numërim, jo sulm | [Llogaritje] |

**Testet "cube" [Eksperiment]** (shuma XOR e daljeve mbi të gjitha vlerat e d biteve të zgjedhura të mesazhit, numër fiks; sa bite dalëse kanë shumë zero, ku rastësia jep rreth 256 nga 512):

| Kubi | 2 raunde | 3 raunde | 4 raunde |
|---|---|---|---|
| 8 bit në një bajt | 512, 512 | 512, 512 | 241, 264 |
| 8 bit në 8 bajte të ndryshëm | 512, 512 | 236, 263 | 247, 255 |
| 12 bit në 12 bajte | 512, 512 | 259, 234 | 258, 248 |
| 16 bit në 16 bajte | 512, 512 | 512, 257 | 258, 232 |

**Shpjegimi i shumave zero në 3 raunde [Provë].** Në raundin 1 çdo S-box sheh të shumtën një bit të ndryshueshëm, ndaj dalja e tij është afine në atë bit. Nëse π_1 vendos të shumtën k bite kubi në çdo rresht, shkalla pas raundit 2 është e shumta k dhe pas raundit 3 e shumta 7k. Me 8k bite kubi gjithsej dhe 7k < 8k, shuma del zero. Në 4 raunde nuk vumë re asnjë shumë zero.

### 6.4 Orari i çelësit (K)

| Matja | Rezultati | |
|---|---|---|
| 1 bit çelësi i ndryshuar: bitet e ndryshuara te RK_0, RK_1, RK_8, RK_16 (v1.1, 820 prova) | 50,1%, 50,1%, 50,1%, 50,0% | [Eksperiment] |
| Rirenditja ndryshon kur ndryshon 1 bit çelësi (v1.0) | 97,0%, kundrejt 1 − 1/32 = 96,9% të pritur | [Eksperiment] |
| Çelësa me strukturë (zero, njësha, një bit, 0x55…, rritës; v1.0) | çelësat e raundeve 50–51% njësha; 3 000 blloqe dalës për secilin: monobit z ≤ 1,98, χ² e bajteve 218–275 (pragu 99%: 310,5) | [Eksperiment] |
| **Rikthimi i çelësit kryesor nga çelësat e raundeve** | v1.0: i thyer. v1.1: i bllokuar për metodën e drejtpërdrejtë (seksioni 7) | [Eksperiment] |

### 6.5 Tekst dhe numër i zgjedhur (T)

| Matja | Rezultati (rastësia: 0,25 bajte) | |
|---|---|---|
| Integral me numra, v1.1 (një bajt i numrit merr 256 vlera, mesazhi fiks), pas 1 / 2 / 16 raundeve | 0–1 / 0–1 / 0–1 nga 64 bajte të balancuar | [Eksperiment] |
| Integral me numra, v1.1 (dy bajte, 65 536 numra), 1 raund | 0 nga 64 | [Eksperiment] |
| Diferencë e njëkohshme në mesazh dhe numër, e zgjedhur për të anuluar diferencën e RK_0, v1.1, raundet 1 / 2 / 3 | 0,23 / 0,28 / 0,26 bajte me diferencë zero | [Eksperiment] |
| E njëjta **pa** asnjë përzierje pas numrit (variant i dobësuar), raundet 1 / 2 / 3 | 56,5 / 0,59 / 0,27 | [Eksperiment] |
| 16 raunde, numri = 0, 1, 2, …, mesazhi 0, 10 000 blloqe (v1.1) | monobit z −0,74, vargjet z 0,78, χ² bajte 261, χ² nibble 6,1, të gjitha nën pragjet 99% | [Eksperiment] |

Testet statistike kapin vetëm defekte të trasha dhe nuk janë provë sigurie.

## 7. Dobësia e orarit te v1.0 dhe ndryshimi te v1.1

### 7.1 Dobësia

Te v1.0 çdo hap i orarit është bijeksion, dhe hapat pas numrit nuk kanë feed-forward. **Nga tre çelësa raundesh të njëpasnjëshëm RK_i, RK_(i+1), RK_(i+2) të një blloku dhe numri i tij, çelësi kryesor del menjëherë. [Eksperiment]**

1. RK_i jep bajtet 0..63 të G_i. Ato përcaktojnë daljet e θ në rreshtat 0..7 të hapit i+1, kështu që dihen 13 nga 16 bajtet 64..79 të G_(i+1). Mbeten të panjohur bajtet 70, 71 dhe 79.
2. RK_(i+2) jep 6 ekuacione bajtesh për rreshtin 8 dhe 7 për rreshtin 9 të G_(i+1). Një kërkim i plotë mbi 2^16 dhe 2^8 vlera jep një G_(i+1) të vetëm.
3. Hapat F_i kthehen mbrapsht deri te G_0. Zhbëhen 4 hapat e përzierjes së numrit, hiqet numri dhe zhbëhen 4 hapat që varen vetëm nga çelësi. 230 bitët e njohur të mbushjes e konfirmojnë çelësin.

Në 3 nga 3 prova çelësi kryesor u rikthye për rreth 0,1 s, me një kandidat të vetëm. Me **dy** çelësa raundesh të njëpasnjëshëm mbeten 3 bajte të panjohur: 2^24 kandidatë, secili i verifikueshëm me bitet e mbushjes **[Vlerësim]**. Pasi dihet çelësi, dalin çelësat e raundeve të **çdo** numri tjetër. Pra "loja" sipas bllokut nuk i izolonte blloqet. Kjo dobësi nuk thyen 16 raunde, sepse nuk dihet asnjë metodë për të marrë çelësa raundesh atje. Por do të thotë që, te v1.0, çdo sulm që rikthen dy ose tre çelësa raundesh të njëpasnjëshëm të një blloku bëhet thyerje e plotë.

### 7.2 Ndryshimi

Versioni 1.1 shton një feed-forward Davies–Meyer pas futjes së numrit dhe i dyfishon hapat aty nga 4 në 8: G_0 = F(X) ⊕ X, ku F përbëhet nga 8 hapa dhe X = K* ⊕ numri. Gjendja G_0 e një blloku të sulmuar mund të rindërtohet ende. Por kalimi nga G_0 mbrapsht te X kërkon tani përmbysjen e hartës X → F(X) ⊕ X, një problem "preimage" mbi 640 bit. Kthimi hap pas hapi i seksionit 7.1 nuk funksionon më, sepse feed-forward-i e përzien hyrjen me daljen. **Nëse harta mund të përmbyset me mjete të tjera nuk është provuar, as në një drejtim as në tjetrin**: feed-forward-i është masë projektimi, dhe pakthyeshmëria e tij është hamendja 2. Raundi i shifrës nuk ndryshon.

### 7.3 Vlerësimi

| Sulmi i 7.1 (3 prova secili) | G_0 i bllokut të sulmuar u rindërtua | Çelësi kryesor u gjet | Çelësat e raundeve të një numri tjetër u parashikuan |
|---|---|---|---|
| v1.0 | 3/3 | **3/3** | **3/3** |
| v1.1 | 3/3 | **0/3** | **0/3** |

Kostoja: v1.1 është 13% më i ngadaltë se v1.0 në implementimin tonë (2 295 kundrejt 2 651 blloqe në sekondë, me numër të ri për çdo bllok dhe me përgatitjen K* të përbashkët).

**Kjo nuk është provë.** Tre dështimet tregojnë vetëm që përmbysja e drejtpërdrejtë e seksionit 7.1 nuk funksionon më. Nuk tregojnë që F(X) ⊕ X nuk mund të përmbyset me metoda të tjera, si teknikat meet-in-the-middle ose rebound që janë përdorur kundër mënyrave hash të bazuara në AES [Sas11]. Hipoteza jonë jepet si hamendja 2.

## 8. Sulmet mbi raunde të shkurtuara (numër fiks)

**Lema 4 (dallues integral në 3 raunde). [Provë + Eksperiment]** Me numër fiks, merrni 256 mesazhe ku një bajt merr të gjitha vlerat dhe pjesa tjetër mbetet konstante. Pas 3 raundeve, secili nga 64 bajtet dalës ka shumë zero.

*Prova.* Pas raundit 1, rreshti që merr bajtin aktiv përmban 8 bajte të formës c ⊕ m·S(v) me m ≠ 0, ndaj secili merr të 256 vlerat. Në raundin 2, π_2 i çon këto 8 bajte në 8 rreshta të ndryshëm (lema 1). Çdo rresht ka atëherë një bajt që merr të gjitha vlerat dhe 7 bajte konstante, ndaj pas θ të 64 bajtet marrin të gjitha vlerat. Në raundin 3, θ jep kombinime XOR të bajteve të tilla, ndaj çdo bajt dalës ka shumë zero. Shtimi i çelësit e ruan këtë veti. ∎

Matur: 10 nga 10 prova të balancuara pas 2 dhe 3 raundeve. Pas 4 raundeve 0–1 nga 64 bajte, dhe 0–1 edhe me dy bajte të rreshtuara (2^16 mesazhe). Me numër të ri për çdo mesazh, vetia zhduket **[Eksperiment]**.

**Rikthimi i çelësit në 4 raunde. [Eksperiment]** Lema 4, plus marrja me mend e çdo bajti të θ^-1(RK_4) veçmas (sepse θ^-1(C) = π_4(S(X_3)) ⊕ θ^-1(RK_4) dhe çdo bajt i X_3 është i balancuar), e rikthyen RK_4 (512 bit) në 5 nga 5 prova, me 512–768 mesazhe të zgjedhura dhe për më pak se një sekondë. **Ky sulm rikthen vetëm RK_4, jo çelësin kryesor.** Te v1.0, çelësi kryesor do të dilte nga tre çelësa raundesh të njëpasnjëshëm të një blloku, ose nga dy me rreth 2^24 punë (seksioni 7.1). Heqja e raundit 4 me RK_4 të gjetur dhe sulmi i raundeve të mbetura në të njëjtën mënyrë mund të japin edhe RK_3 dhe RK_2, por këtë nuk e zbatuam. Prandaj mbetet **[E hapur]** nëse rikthimi i çelësit kryesor në 4 raunde te v1.0 është praktik. Te v1.1, çelësat e raundeve të një numri nuk çojnë te çelësi kryesor me metodën e drejtpërdrejtë të seksionit 7.1.

**5 raunde. [Vlerësim]** Shtimi i një raundi më shumë kërkon të merren me mend 8 bajte të θ^-1(RK_5) dhe një bajt i θ^-1(RK_4) për çdo bajt objektiv: rreth 2^72 hamendje me 2^8 mesazhe, plus struktura e panjohur e rreshtave të π_4 dhe π_5. Në mënyrë naive, kjo është rreth 2^80 llogaritje S-box-i. Teknikat e shumave të pjesshme mund ta ulin. Këtë sulm nuk e zbatuam, dhe vlerësimi mund të jetë i gabuar në të dy drejtimet.

**Marzhi.** Sulmi më i mirë i ekzekutuar mbulon 4 nga 16 raunde. Rregulli ynë praktik R ≥ 2·max(R1, R2, R3), që është rregull përvoje dhe jo provë, plotësohet. Këtu R1 = 2 raunde deri në përhapjen e plotë, R2 = 6 raunde deri sa rruga më e mirë të bjerë nën 2^-512 (nga teorema 1), dhe R3 = 4–5 raunde të sulmuara, pra 2·6 = 12 ≤ 16.

## 9. Pretendimet dhe hamendjet e sigurisë

**Çfarë është provuar:** lemat 1–4, teoremat 1 dhe 2 dhe rrjedhimet e tyre, ashtu siç janë shprehur, bashkë me kufijtë e tyre (seksioni 5).

**Hamendja 1 (objektivi i sigurisë).** Me një çelës të vetëm dhe me mesazhe, tekste të kriptuara dhe numra të zgjedhur (përfshirë numrat e përsëritur), BRI-410 v1.1 me 16 raunde nuk ka asnjë sulm dallues ose rikthimi çelësi me kohë nën 2^256 dhe me më pak se 2^128 blloqe për çelës. Kjo është hipotezë kërkimore dhe ftesë për analizë, **jo rezultat i demonstruar**. Këtë objektiv e vendosim me qëllim shumë nën gjatësinë e çelësit, dhe çelësi mbetet 410-bitësh. Çelësi 410-bitësh është zgjedhje simbolike, dhe analiza jonë mbulon vetëm klasat e sulmeve të seksioneve 5–8.

**Hamendja 2 (izolimi i lojërave).** Harta X → F(X) ⊕ X me 8 hapat e saj është në praktikë e pakthyeshme. Si pasojë, njohja e të gjithë çelësave të raundeve dhe rirenditjeve për një numër nuk jep asnjë avantazh praktik për llogaritjen e atyre të një numri tjetër ose të çelësit kryesor. Kjo hipotezë mbështetet vetëm nga arsyetimi i projektimit dhe nga dështimi i sulmit të drejtpërdrejtë (seksioni 7.3).

**BRI-410 AE.** Nëse vlen hamendja 1, teorema e sigurisë së ΘCB3 [KR11] jep fshehtësi dhe vërtetësi kundër sulmuesve që nuk e përsërisin numrin e mesazhit. Gjasa e falsifikimit për përpjekje është rreth 2^-416 plus avantazhi kundër shifrës. Kufijtë: mesazhe deri në 2^28 − 1 blloqe. Me numra të rastësishëm 96-bitësh, deri në 2^32 mesazhe për çelës, që e mban gjasën e përsëritjes së numrit rreth 2^-33.

**Çfarë nuk pretendohet:**
- siguria kundër çelësave të lidhur
- siguria e BRI-410 brenda një funksioni hash (çelës i njohur ose i zgjedhur)
- qëndrueshmëria e BRI-410 AE kur numri përsëritet (një numër i përsëritur zbulon blloqet e barabarta)
- mbrojtja e kodit reference nga matja e kohës dhe kanalet e tjera anësore (nuk është në kohë konstante)

## 10. Historia e projektimit dhe rezultatet negative

| Versioni | Përshkrimi | Çfarë gjetëm | Veprimi |
|---|---|---|---|
| BRI-410/4, projektimi i parë | kuti 4-bitëshe, bllok 256-bitësh, "loja" (π) vetëm nga çelësi, me α | α ndërrohet me raundin (lema 2): 1 792 çifte të barazvlefshëm | α u hoq |
| BRI-410/4, lojë sipas çelësit | si më lart | loja fsheh vetëm 1 bit për raund në nivel rreshti (rreshti destinacion varet vetëm nga dr) | u dokumentua |
| BRI-410/4, lojë sipas çelësit | si më lart | dallues integral në **4 raunde me 2^12 mesazhe**, **rikthim çelësi në 5 raunde për më pak se 1 s** | u prezantua loja sipas bllokut (numri unik): i njëjti sulm dështoi 0/3 |
| BRI-410/4 me numër unik | 32 raunde | S-box-i 4-bitësh (shkallë 3) e lë vetinë integrale të mbijetojë një raund më shumë se te projektimet si AES | u zëvendësua me kuti 8-bitëshe |
| BRI-410/8 v1.0 | kuti 8-bitëshe, bllok 512-bitësh, 16 raunde | orar i kthyeshëm: 3 çelësa raundesh → çelësi kryesor në 0,1 s (seksioni 7) | v1.1 (feed-forward, 8 hapa) |
| BRI-410/8 v1.1 | ky punim | — | i hapur për analizë |

**Gabimet e korrigjuara nga versioni 1 i këtij punimi.**
- Jepte një pretendim sigurie në nivelin 2^410 që analiza jonë nuk e mbështeste.
- E quante implementimin e dytë "të pavarur", edhe pse u shkrua veçmas nga i njëjti autor.
- I quante vlerat e CP-SAT "të sakta" pa thënë që janë të sakta vetëm brenda modelit.
- Raportonte "49,9%" për një vlerë që matet 49,8%.
- Përshkruante versionin v1.0 të shifrës.

## 11. Riprodhueshmëria dhe shpejtësia

Depoja përmban:
- implementimin kërkimor (Python, bibliotekë standarde)
- një implementim reference më vete, në një skedar të vetëm në anglisht, që përputhet bit për bit me implementimin kërkimor
- vektorë testi për v1.0 dhe v1.1
- 46 teste njësie
- çdo skript eksperimenti, me fara fikse

Modeli CP-SAT kërkon OR-Tools. Në Python të pastër, implementimi arrin rreth 2 300 blloqe në sekondë me numër të ri për çdo bllok dhe me përgatitjen K* të përbashkët, dhe BRI-410 AE rreth 150 KB/s. Një implementim në C në kohë konstante mbetet detyrë e hapur.

## 12. Pyetjet e hapura dhe objektivat për analizë

1. **Diferenciale dhe lineare:** bashkimi i diferencialeve, "linear hull", sulmet boomerang dhe impossible-differential; rillogaritja e pavarur e kufijve CP-SAT.
2. **Algjebrike dhe integrale:** analiza me "division property" për 4 e më shumë raunde, dhe sulmet algjebrike mbi raunde të shkurtuara.
3. **Orari i çelësit:** përmbysja e X → F(X) ⊕ X me 8 hapa (hamendja 2); sulmet me çelësa të lidhur; nëse sulmet mbi raunde të shkurtuara çojnë te çelësi kryesor.
4. **Numri unik:** sulmet që kombinojnë diferenca në numër dhe në mesazh, përfshirë çiftet me rirenditje të ndryshme.
5. **Mënyra dhe implementimi:** kontrolli i pavarur i zbatimit të ΘCB3, dhe implementime në kohë konstante.

**Objektivat.** Dallues për 5, 6, 7 ose 8 raunde; rikthimi i çelësave të raundeve për 5 deri në 8 raunde; rikthimi i çelësit kryesor, ose i çelësave të raundeve të një numri të dytë, nga ata të një numri të vetëm, qoftë me numër fiks qoftë me numra të zgjedhur. Autori do ta falënderojë publikisht çdo rezultat.

## Pronësia intelektuale

BRI-410 nuk është i patentuar, dhe autori nuk ka ndër mend të kërkojë patentë për të. Specifikimi, implementimet, vektorët e testit dhe skriptet e analizës i kushtohen domenit publik me licencën CC0 1.0.

## Falënderime

Idetë dhe vendimet e projektimit janë të autorit: analogjia e shahut dhe çelësi 410-bitësh, "loja që luhet vetëm një herë" për çdo bllok, kalimi te kutitë 8-bitëshe dhe 16 raundet, vula 416-bitëshe dhe ndryshimi i orarit te v1.1. Autori përdori një model AI (Claude, nga Anthropic) si asistent për të shkruar implementimet, për të ekzekutuar eksperimentet dhe llogaritjet, dhe për të hartuar këtë punim. Çdo rezultat mund të riprodhohet me kodin e publikuar, dhe autori mban përgjegjësi për përmbajtjen.

## Referencat

Referencat janë të njëjta me ato të versionit anglisht: [AB00], [All94], [BJK+16], [BS91], [DKR97], [DR02], [FLS+10], [JNP14], [JNPS21], [KR11], [LRW02], [Mat93], [MS77], [MWGP11], [OGK+15], [PGV93], [Sas11], [Sch93], [SKW+98], [Sha50], [Tod15]. Titujt e plotë janë në anglisht te BRI-410_v2.pdf.

## Shtojca A. Konstantet

**S-box-i S** (rreshti = nibble-i i lartë, kolona = nibble-i i ulët, heksadecimal):

```
15 86 4d a2 24 91 fa cd 75 c1 7e 8d cb c8 f6 34
6d f5 22 ff a0 6a 80 12 ab 87 0b 9d 1f 56 5f df
2a 84 bf 1b 28 d5 36 30 1e 2f 33 6b 10 68 0c 99
d3 fb 09 90 0f ad aa 42 9c bd c3 17 ea 62 38 7b
45 8c a9 39 40 83 25 3d a1 be b1 41 bb 6e e6 a8
d8 95 b8 b7 46 fd 77 5c e8 14 d7 88 16 4b 13 7f
ec 81 8f d9 eb 32 3a d1 b6 ef 8e c9 97 9a 50 b9
ee 72 a4 63 c6 66 f1 00 e1 53 5e 3f 8b b2 5d da
49 57 c4 ce 37 d4 cf af b4 19 b0 e3 31 01 76 26
5a ba 04 03 70 f4 f0 47 f9 f8 8a e0 35 4e 73 27
21 43 c7 0a 59 e5 2d 78 e9 a3 d2 6c 89 e2 4a 94
05 5b 51 cc 55 fe 7d c0 b5 ca 79 93 48 db e4 3c
bc ed 54 9f 64 60 65 82 a5 7a 02 2b 6f 98 08 71
69 ac 1c 07 20 f7 4f 61 23 67 b3 f3 9e a6 1d 29
58 96 74 f2 a7 11 1a 9b 3b 52 e7 dc 06 85 c2 4c
2c 44 3e 2e ae 7c 92 de dd 0d d0 18 0e fc c5 d6
```

**Matrica M** (θ) dhe **M^-1** (θ^-1), heksadecimal, rresht pas rreshti:

```
M                          M^-1
6a d7 84 ac af d6 e3 61    f1 a7 cf 26 40 46 f8 48
de e3 72 e6 d3 eb d7 17    36 69 5f 5b d4 15 11 c7
6d 08 d8 1b 16 b1 4e 51    4d b9 41 23 50 a3 55 92
32 4e 8a fc 5e 0d 08 ec    80 53 52 4d f4 8b 31 19
8a 1e 32 53 36 cf b3 22    ed 73 15 f2 78 4f aa 26
d8 b3 6d 04 43 ad 1e f0    99 ae e0 09 6f d6 1e 68
72 5d de a9 49 c6 50 18    e6 e2 05 06 d1 2e 74 a8
84 50 6a 27 a6 0e 5d 3e    2b 85 a1 97 df 11 f5 3e
```

**Konstantja e mbushjes** (bitet 410..639 të L, si numër):
`0x391d69042f080a4aa81f1dc9676116fafcd238b21e43a01e5fb06f0fe6`

## Shtojca B. Vektorët e testit (v1.1, heksadecimal)

```
Çelësi     = 00 × 52     Numri = 00 × 16     Mesazhi = 00 × 64
Kriptuar   = 67b7e691273da3b40bedf3cf4abad7a3c960473b1ef4356d961413423c718053
             2fab02454f11cb600955edd094de6490024eb8f06f40d4f0d30443e004069d72

Çelësi     = 000102…2f303132 02 (bajtet 0..50 rritës, bajti 51 = 02)
Numri      = 000102030405060708090a0b0c0d0e0f     Mesazhi = 000102…3e3f
Kriptuar   = 9f52662ad01ba4bafe6fa894e81fd6b23fa22078bb5054587d09214cd8306ba1
             c3bf6167b07494d2d5f379c26b991a79403de492f4e310639917d33af96ada4c
```

12 vektorë për shifrën e bllokut (me RK_0 dhe RK_16) dhe 6 vektorë për BRI-410 AE janë te `reference/test_vectors.json`.

## Shtojca C. Modeli CP-SAT

Ndryshoret janë x[t][c] ∈ {0,1}: kutia c është aktive në hyrje të shtresës S të raundit t. Për çdo raund t dhe rresht q, një ndryshore binare d[t][q] e shënon rreshtin si aktiv. Çdo kuti aktive në hyrje ose në dalje të rreshtit e detyron d[t][q], dhe kushti është (kuti aktive në hyrje të θ_t në rreshtin q) + (kuti aktive në dalje x[t+1][8q..8q+7]) ≥ 9·d[t][q]. Hyrjet e rreshtit q janë kutitë c me r + k·dr ≡ q, ku c = (r, k). Një ndryshore binare s[t] zgjedh dr = +1 ose −1 në raundin t, kështu që zgjidhësi zgjedh rastin më të keq. Objektivi minimizon Σ x[t][c] mbi raundet 1..R, me kushtin Σ x[0][c] ≥ 1. Modeli i orarit është i njëjtë, me 10 rreshta dhe hartën j → 9j mod 80, dhe nis nga një diferencë jo-zero në bajtet 0..15 (numri). Kodi: `matje/f4b_milp.py`.
