# BRI-410: Një shifër blloku me "lojë", e frymëzuar nga shahu, me çelës 410-bitësh, e projektuar me matje

**Rinald Cobaj**, Studiues i pavarur, vlorarino@gmail.com

*Përkthim në shqip për autorin, 2026-10-22. Versioni për publikim është ai në anglisht (BRI-410.pdf). Shifër studimi: nuk është analizuar ende nga kriptanalistë të pavarur dhe nuk duhet përdorur për të mbrojtur të dhëna reale.*

## Përmbledhja

Paraqesim BRI-410, një shifër blloku me "lojë" (në anglisht *tweakable block cipher*). Ka bllok 512-bitësh, çelës 410-bitësh,
numër unik ("lojë", *tweak*) 128-bitësh dhe 16 raunde. Bashkë me të paraqesim BRI-410 AE, një mënyrë kriptimi me vulë, të
bazuar te ΘCB3, me vulë 416-bitëshe. Projektimi nisi nga një analogji me shahun: rregullat e lojës janë publike, por çdo
lojë e luajtur është unike. Kompleksiteti i pemës së lojërave të shahut, rreth 10^123 ≈ 2^410, përcakton gjatësinë e çelësit.
Tabela 8×8 përcakton gjendjen, dhe lëvizja e kalit jep një rirenditje të kutive që varet nga çelësi dhe nga numri.
Ideja që *çdo lojë luhet vetëm një herë* çoi në nxjerrjen e të gjithë çelësave të raundeve dhe të rirenditjes nga çelësi **dhe**
nga një numër unik për çdo bllok. Shifra është një rrjet zëvendësim-rirenditje (SPN) me S-box 8-bitësh si ai i AES-it
(uniformitet diferencial 4, jolinearitet 112, shkallë 7) dhe me matricë Cauchy MDS 8×8 mbi GF(2^8).

Projektimi u drejtua nga matjet. Një version i mëparshëm me kuti 4-bitëshe (BRI-410/4) kishte një dallues integral në 4 raunde
me 2^12 mesazhe të zgjedhura dhe një sulm praktik që rikthente çelësin në 5 raunde. Prandaj u zëvendësua. Për versionin
përfundimtar provojmë me një model CP-SAT që, për çdo zgjedhje të rirenditjeve që varen nga çelësi, çdo rrugë diferenciale ose
lineare në 4 raunde kalon të paktën 81 S-box aktive (gjasa ≤ 2^-486), dhe çdo rrugë në 6 raunde të paktën 90 (≤ 2^-540).
Sulmet më të mira që gjetëm arrijnë në praktikë 4 nga 16 raunde. Një sulm mbi 5 raunde vlerësohet rreth 2^72.
Japim deklarata të qarta sigurie, rendisim pyetjet e hapura dhe propozojmë sfida me raunde të shkurtuara.

## 1. Hyrja dhe motivimi

Rregullat e shahut i di gjithkush, e megjithatë një lojë serioze pothuajse kurrë nuk përsëritet. Shannon e vlerësoi numrin e
lojërave rreth 10^120 [Sha50]. Allis e vlerësoi kompleksitetin e pemës së lojërave rreth 10^123 [All94]. BRI-410 e kthen këtë
në parim projektimi:

| Shahu | BRI-410 |
|---|---|
| rregullat publike | algoritmi publik (parimi i Kerckhoffs-it) |
| një lojë nga ≈ 10^123 | një çelës nga 2^410 ≈ 10^123,4 |
| tabela 8×8 | gjendja 512-bitëshe: 64 kuti me nga 8 bit |
| lëvizja e kalit | rirenditja e kutive π |
| çdo lojë luhet vetëm një herë | çdo bllok ka çelësat e raundeve dhe rirenditjet e veta (numri unik) |

Projekti ndoqi një rregull të prerë: asnjë vendim projektimi nuk pranohet pa matje. Çdo dobësi e gjetur gjatë projektimit
paraqitet në seksionin 5, bashkë me ndryshimin që shkaktoi.

## 2. Specifikimi i BRI-410/8

### 2.1 Shënimet dhe parametrat

| Parametri | Vlera |
|---|---|
| Blloku | 512 bit = 64 bajte. Bajti i është kutia (r, k) = (⌊i/8⌋, i mod 8) e tabelës 8×8 |
| Çelësi | 410 bit, i ruajtur si 52 bajte little-endian; 6 bitët e sipërm duhet të jenë 0 |
| Numri unik (lojë) | 128 bit (16 bajte) |
| Raunde | R = 16 |

Llogaritjet mbi kutitë bëhen në fushën GF(2^8) me polinomin x^8 + x^4 + x^3 + x + 1.

### 2.2 Raundi

```
X ← X ⊕ RK_0
për i = 1 .. 16:   X ← θ(π_i(S(X))) ⊕ RK_i
```

Të gjitha raundet janë identike, dhe edhe raundi i fundit zbaton θ-n. Dekriptimi zbaton `⊕RK_i, θ^-1, π_i^-1, S^-1` për
i = 16..1, dhe në fund `⊕RK_0`.

**S (S-box-i, "zëvendësimi i figurave").** `S(x) = A·x^-1 ⊕ c` (me `0^-1 = 0`), ku `A` është një matricë binare 8×8 e kthyeshme
(rreshti i është një bajt; biti i i `A·y` është barazia e `A[i] AND y`) dhe `c` është një bajt. `A ‖ c` janë 9 bajtet e
`SHAKE-256("BRI-410 S-box8 v1" ‖ n)`, për numëruesin e parë `n` (4 bajte big-endian) që jep `A` të kthyeshme dhe asnjë pikë
me `S(x) = x` ose `S(x) = x ⊕ FF`. Rezultati është `n = 9`. Meqë është transformim afin i inversit, S ka uniformitet
diferencial 4, linearitet 32 (jolinearitet 112) dhe shkallë algjebrike 7 në çdo komponent.

**π (lëvizja e kalit).** Kutia (r, k) bën k kërcime kali (dr, dk) në një tabelë toroidale (skajet lidhen me njëri-tjetrin),
pastaj tabela zhvendoset β kolona:
`(r, k) → (r + k·dr, k + k·dk + β) mod 8`, me (dr, dk) ∈ {(1,2), (1,−2), (−1,2), (−1,−2)} dhe β ∈ {0..7}.
Të 32 rirenditjet i çojnë 8 kutitë e çdo rreshti në 8 rreshta të ndryshëm ("përhapje optimale"). Gjatë projektimit u hoq një
zhvendosje rreshtash α, sepse ndërrohet me gjithë raundin pa çelës dhe kështu nuk shton asnjë strukturë (seksioni 5.2).

**θ (MDS, "kapja").** Çdo rresht prej 8 bajtesh shumëzohet me `M[i][j] = 1 / (x_i ⊕ y_j)`, `x = 0..7`, ku `y` janë 8 bajtet e
para të ndryshme, që nuk janë në {0..7}, nga `SHAKE-256("BRI-410 MDS8 v1")`, pra `y = [145, 234, 150, 206, 98, 226, 235, 94]`.
M është MDS (u verifikua: asnjë nga 12 869 nënmatricat e saj katrore nuk është singulare), prandaj numri i degëve është 9.
Nuk ka simetri kolonash dhe nuk është e kundërta e vetvetes.

### 2.3 Orari i çelësit dhe i numrit ("loja")

Gjendja e orarit ka 80 bajte (10 rreshta me nga 8). Ngarkohet me çelësin në bitet 0..409 dhe me 230 bitët e ulët të
`SHAKE-256("BRI-410/8 mbushja")` (29 bajte, little-endian) në bitet 410..639. Një hap `F_i` është:

```
S mbi të 80 bajtet → θ mbi 10 rreshtat → bajti j shkon në pozicionin 9·j mod 80 → bajti 79 ⊕= i
```

Futja e numrit: `F_0xF0 … F_0xF3` (vetëm çelësi), pastaj bajtet 0..15 ⊕= numri, pastaj `F_0xF4 … F_0xF7`.
Pas kësaj `RK_0` = bajtet 0..63. Për i = 1..16: zbatohet `F_i`, `RK_i` = bajtet 0..63, dhe rirenditja e raundit i merret nga
bajti 64 = b: drejtimi = lista[b & 3], β = (b >> 2) & 7.

Katër hapat e parë varen vetëm nga çelësi dhe mund të llogariten një herë për çelës.

## 3. BRI-410 AE

BRI-410 AE është ndërtimi ΘCB3 i Krovetz-it dhe Rogaway-t [KR11], me BRI-410/8 si shifër blloku me lojë E.
Çdo thirrje përdor numrin `N ‖ ((indeksi << 4) | lloji)` (numri i mesazhit 12 bajte, pastaj 4 bajte little-endian,
indeksi < 2^28). Llojet janë: 0 bllok mesazhi, 1 maska e bllokut të fundit të paplotë, 2 vula pa bllok të paplotë,
3 vula me bllok të paplotë, 4 bllok të dhënash shoqëruese, 5 blloku i fundit i paplotë i të dhënave shoqëruese.
Të dhënat shoqëruese përdorin `N = 0^12`. Me `M = M_1 … M_m M_*` dhe `A = A_1 … A_a A_*` (|M_*|, |A_*| < 64 bajte)
dhe `pad(x) = x ‖ 80 ‖ 00…`:

```
C_i  = E^(N,i,0)(M_i)                                            i = 1..m
nëse M_* ≠ ε:  C_* = M_* ⊕ E^(N,m,1)(0^512)[|M_*| bajtet e para];  F = E^(N,m,3)(⊕M_i ⊕ pad(M_*))
përndryshe:    F = E^(N,m,2)(⊕M_i)
Auth = ⊕ E^(0,i,4)(A_i)  [⊕ E^(0,a,5)(pad(A_*))]
Vula = (F ⊕ Auth)[52 bajtet e para]               — 416 bit
Paketa = N ‖ C ‖ Vula
```

Dekriptimi nuk kthen asgjë nëse vula nuk përputhet (krahasim në kohë konstante).

## 4. Deklaratat e sigurisë

**Deklarata 1 (shifra e bllokut me lojë).** BRI-410/8 me 16 raunde është shifër e sigurt blloku me lojë, në rastin me një
çelës të vetëm dhe me numra të zgjedhur nga sulmuesi, përfshirë numrat e përsëritur. Nuk ekziston sulm që rikthen çelësin,
as sulm që e dallon nga një rirenditje ideale, me kohë llogaritjeje nën 2^410 dhe me më pak se 2^256 pyetje për çelës.

**Deklarata 2 (kriptimi me vulë).** Nëse vlen deklarata 1, BRI-410 AE jep fshehtësi dhe mbrojtje nga ndryshimi kundër
sulmuesve që nuk e përsërisin numrin e mesazhit, sipas teoremës së sigurisë së ΘCB3 [KR11]. Çdo përpjekje falsifikimi ka
sukses me gjasë rreth 2^-410 në rastin më të mirë për sulmuesin: vula ka 416 bit, por siguria kufizohet nga çelësi.
Kufijtë: deri në 2^28 − 1 blloqe për mesazh. Me numra të rastësishëm, deri në 2^32 mesazhe për çelës
(gjasa e përsëritjes së numrit ≈ 2^-33).

**Çfarë nuk premtohet.** Siguria kur sulmuesi përdor çelësa të lidhur me njëri-tjetrin. Siguria e BRI-410/8 kur përdoret brenda
një funksioni hash (kur çelësi njihet ose zgjidhet). Qëndrueshmëria e AE kur numri i mesazhit përsëritet: numri i përsëritur
zbulon blloqet e barabarta dhe mund të lejojë falsifikime. Mbrojtja e implementimit reference ndaj matjes së kohës dhe
kanaleve anësore, sepse nuk është në kohë konstante.

## 5. Arsyetimi i projektimit dhe analiza

Të gjithë numrat mund të riprodhohen me skriptet e depos që shoqëron punimin.

### 5.1 Komponentët

| Komponenti | Matja |
|---|---|
| S-box | DU 4, jolinearitet 112, shkallë 7, pa pika fikse (10 permutacione 8-bitëshe të rastësishme: DU 10–16, NL 90–96) |
| θ | MDS (0 nga 12 869 nënmatrica singulare), 1 simetri kolonash (identiteti) |
| π | 32 rirenditje të ndryshme, të gjitha me përhapje optimale |
| Përzierja e plotë | çdo bajt dalës varet nga çdo bajt hyrës pas 2 raundeve; efekti ortek 50,2% pas 2 raundeve |

### 5.2 Historia: çfarë u mat dhe çfarë u ndryshua

1. **U hoq zhvendosja e rreshtave α.** Në projektimin e parë, lëvizja e kalit kishte edhe një zhvendosje rreshtash α (3 bit).
   Matëm që α ndërrohet me raundin pa çelës, ndaj mund të shtyhet deri në fund të shifrës. Kjo krijonte 1 792 çifte
   variantesh "loje" që ishin të barazvlefshme, me ndryshim vetëm te α. Pasi u vendos α = 0, nuk mbeti asnjë.
2. **Një lojë për çelës nuk mjaftonte. Duhej një lojë për çdo bllok.** Kur rirenditja nxirret vetëm nga çelësi, sulmi integral ka
   nevojë për mijëra mesazhe nën *të njëjtën* rirenditje. Kur çdo bllok merr çelësat e raundeve dhe rirenditjet e veta nga
   numri unik, dalluesit integralë zhduken plotësisht. E matur te BRI-410/4, rikthimi i çelësit në 5 raunde pati sukses 0 herë
   nga 3 (3 nga 3 më parë, dhe 3 nga 3 kur numri përsëritet). Te BRI-410/8, me numër unik për çdo bllok zhduket edhe dalluesi
   integral në 3 raunde. Vetë loja fsheh vetëm 1 bit për raund në nivel rreshti, sepse rreshti ku shkon kutia varet vetëm nga dr.
   Vlera e saj kryesore është se numri unik e bën çdo bllok një rirenditje të ndryshme.
3. **Kutitë 4-bitëshe u zëvendësuan me kuti 8-bitëshe.** BRI-410/4 (kuti 4-bitëshe, bllok 256-bitësh, 32 raunde) kishte një
   dallues integral në 4 raunde me vetëm 2^12 mesazhe të zgjedhura (3 kuti të rreshtuara nga π_1), një raund më shumë se
   AES-i me sasi të ngjashme të dhënash. Ekzekutuam një rikthim çelësi në 5 raunde për më pak se një sekondë. Shkaku i mundshëm
   është shkalla e ulët (3) e S-box-eve 4-bitëshe. Me kuti 8-bitëshe, dalluesi integral ndalet në 3 raunde: në 4 raunde
   vetëm 0–1 nga 64 bajte dalin të balancuara edhe me 2^16 mesazhe të rreshtuara, njësoj si te një funksion i rastësishëm.

### 5.3 Analiza diferenciale dhe lineare (kufijtë CP-SAT)

Modeli në nivel kutie: S nuk e ndryshon aktivitetin. Për θ vlen "kuti aktive në hyrje + kuti aktive në dalje të një rreshti
∈ {0} ∪ [9,16]". Për θ ka rëndësi vetëm rreshti ku π e çon kutinë, dhe **sulmuesit i lihet të zgjedhë dr-në në çdo raund**,
prandaj kufijtë vlejnë për çdo çelës dhe çdo numër. Të njëjtët kufij vlejnë për rrugët lineare, sepse transpozimi i një
matrice MDS është MDS.

| Raunde | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 16 |
|---|---|---|---|---|---|---|---|---|---|
| S-box aktive (min.) | 1 | 9 | 17 | **81** | 82 | 90 | 98 | 162 | 324 |
| prova | CP-SAT | CP-SAT | CP-SAT | CP-SAT | CP-SAT | 4+2 | 4+3 | 4+4 | 4×4 |
| log₂ e gjasës max | −6 | −54 | −102 | **−486** | −492 | **−540** | −588 | −972 | −1944 |

Për 6–8 raunde, CP-SAT gjeti edhe rrugë me saktësisht 90, 98 dhe 162 S-box aktive, prandaj këto vlera janë të sakta.

**Orari i numrit (numra të zgjedhur me ndryshime të qëllimshme).** Një diferencë e futur përmes numrit duhet të aktivizojë të
paktën 1, 9, 17, **81**, 107, 114 S-box në 1..6 hapa të orarit (të gjitha të provuara nga CP-SAT). Me 4 hapat që përdoren,
gjasa për të parashikuar diferencën e RK_0 është ≤ 2^-486.

### 5.4 Eksperimentet

| Eksperimenti | Rezultati |
|---|---|
| Integral, numër fiks, 1 bajt (2^8 mesazhe) | i balancuar pas 2 dhe 3 raundeve (10 nga 10), i rastësishëm pas 4 raundeve |
| Integral, numër fiks, 2 bajte të rreshtuara (2^16) | i rastësishëm pas 4 raundeve |
| Rikthimi i çelësit në 4 raunde (numër fiks) | 5 nga 5, RK_4 (512 bit) u rikthye me 512–768 mesazhe |
| Rikthimi i çelësit në 5 raunde (vlerësim) | ≈ 2^72 (merren me mend 8 + 1 bajte për çdo bajt objektiv) |
| Integral me numra të zgjedhur (1 / 2 bajte të numrit, 2^8 / 2^16 numra) | shkurtore vetëm me ≤ 1 hap përzierjeje dhe ≤ 2 raunde. Me 4 hapa dhe 16 raunde: rastësi |
| Efekti ortek i numrit (1 bit) | RK_0 ndryshon 49,9% pas 4 hapave; teksti i kriptuar 49,8% |
| AE | u refuzuan të 1 312 ndryshimet e një biti të vetëm në një paketë; 0 nga 2 000 falsifikime të rastësishme u pranuan |

### 5.5 Raundet

Rregulli ynë: R ≥ 2 × max(R₁, R₂, R₃), ku R₁ = raundet deri në përzierjen e plotë (2), R₂ = raundet deri sa rruga më e mirë të
jetë nën 2^-512 (6, e provuar), dhe R₃ = raundet e sulmuara (4 të ekzekutuara, 5 të vlerësuara). Kjo jep R ≥ 12.
Përdorim 16 raunde.

## 6. Shpejtësia

Implementimi reference në Python të pastër, në një bërthamë: rreth 150 KB/s për mesazhe të gjata me BRI-410 AE. AES-256 në
Python të pastër (kodi ynë i krahasimit) arrin rreth 356 KB/s. Meqë çelësat e raundeve rillogariten për çdo bllok
(seksioni 2.3), BRI-410 është më i ngadaltë se një projektim që e fut numrin në mënyrë më të lehtë (p.sh. TWEAKEY [JNP14]).
Një implementim në C në kohë konstante mbetet detyrë e hapur.

## 7. Pyetjet e hapura dhe sfidat

**Pyetjet e hapura.**
1. Sulmet integrale me "division property" [Tod15], për 4 raunde me ≥ 2^24 mesazhe dhe më tej.
2. Bashkimi i rrugëve diferenciale dhe "linear hull". Sulmet impossible-differential, boomerang dhe algjebrike.
3. Sulmet me numra të zgjedhur që kombinojnë një diferencë në numër me një diferencë në mesazh, përfshirë çiftet me rirenditje të ndryshme.
4. Një orar më i lehtë i numrit (si TWEAKEY) me të njëjtën siguri.
5. Një implementim në C në kohë konstante (bitsliced) dhe shpejtësia e tij.

**Sfidat** (autori do ta falënderojë publikisht çdo rezultat):

| Objektivi | Numër fiks | Numra të zgjedhur |
|---|---|---|
| dallues | 5, 6, 7, 8 raunde | 5, 6, 7, 8 raunde |
| rikthimi i një çelësi raundi | 6, 7, 8 raunde | 6, 7, 8 raunde |
| rikthimi i çelësit kryesor | çdo numër raundesh | çdo numër raundesh |

## 8. Implementimi reference dhe vektorët e testit

`reference/bri410.py` është një skedar i vetëm që përdor vetëm bibliotekën standarde të Python-it. Përmban shifrën e bllokut dhe
BRI-410 AE. `reference/test_vectors.json` ka 12 vektorë për shifrën e bllokut (përfshirë RK_0 dhe RK_16) dhe 6 vektorë për AE.
`reference/verify.py` i kontrollon. Vektorët u prodhuan nga një implementim tjetër i pavarur i të njëjtit specifikim, dhe të dy
implementimet përputhen. Kodi, vektorët e testit dhe të gjitha skriptet e analizës gjenden te
https://github.com/rinaldcobaj-cell/BRI-410.

## Pronësia intelektuale

BRI-410 nuk është i patentuar, dhe autori nuk ka ndër mend të kërkojë patentë për të. Specifikimi, implementimi reference,
vektorët e testit dhe skriptet e analizës i kushtohen domenit publik me licencën CC0 1.0 Universal.
Kushdo mund t'i përdorë, analizojë, implementojë dhe ndryshojë lirisht.

## Falënderime

Idetë dhe vendimet e projektimit janë të autorit: analogjia e shahut dhe çelësi 410-bitësh, "loja që luhet vetëm një herë"
për çdo bllok, zgjedhja e kutive 8-bitëshe dhe e 16 raundeve, dhe vula 416-bitëshe. Autori përdori një model AI (Claude, nga
Anthropic) si asistent për të shkruar implementimin dhe për të ekzekutuar eksperimentet dhe llogaritjet CP-SAT. Çdo rezultat
në këtë punim mund të riprodhohet me kodin e publikuar, dhe autori mban përgjegjësi për përmbajtjen.

## Referencat

- [All94] L. V. Allis. *Searching for Solutions in Games and Artificial Intelligence.* PhD thesis, University of Limburg, Maastricht, 1994.
- [BS91] E. Biham, A. Shamir. Differential cryptanalysis of DES-like cryptosystems. *Journal of Cryptology*, 1991.
- [DKR97] J. Daemen, L. Knudsen, V. Rijmen. The block cipher Square. *FSE 1997*.
- [DR02] J. Daemen, V. Rijmen. *The Design of Rijndael.* Springer, 2002.
- [JNP14] J. Jean, I. Nikolić, T. Peyrin. Tweaks and keys for block ciphers: the TWEAKEY framework. *ASIACRYPT 2014*.
- [KR11] T. Krovetz, P. Rogaway. The software performance of authenticated-encryption modes. *FSE 2011*.
- [LRW02] M. Liskov, R. Rivest, D. Wagner. Tweakable block ciphers. *CRYPTO 2002*.
- [Mat93] M. Matsui. Linear cryptanalysis method for DES cipher. *EUROCRYPT 1993*.
- [MWGP11] N. Mouha, Q. Wang, D. Gu, B. Preneel. Differential and linear cryptanalysis using mixed-integer linear programming. *Inscrypt 2011*.
- [Sha50] C. E. Shannon. Programming a computer for playing chess. *Philosophical Magazine*, 1950.
- [Tod15] Y. Todo. Structural evaluation by generalized integral property. *EUROCRYPT 2015*.
