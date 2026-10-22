# BRI-410 — Raporti F3: loja kundrejt lëvizjes fikse, dhe krahasimi me AES (2026-10-22)

Riprodhimi (nga `C:\Users\vlora\Shahu_Kripto`):

```
python -m unittest discover -s teste -t .          # 22/22 OK (përfshirë AES-in me vektorin FIPS-197 C.3)
python -m matje.f3_matjet                           # → matje/f3_rezultatet.json (~30 s)
python -m matje.f3_zgjerimi dalluesi                # → matje/f3_zgjerimi_dalluesi.json (~3 min)
python -m matje.f3_zgjerimi sulmi 5                 # → matje/f3_zgjerimi_sulmi.json (~6 s)
```

AES-i i krahasimit (`matje/aes_studim.py`) është i shkruar për matje, sepse lejon raunde të shkurtuara.
Ai kalon vektorin zyrtar FIPS-197 C.3 për AES-256. Opsioni B (bllok 512 bit) **nuk** u mat: nuk u kërkua.

## Përmbledhja

| Pyetja | Përgjigjja e matur |
|---|---|
| A e vështirëson loja (V-L) sulmet që provuam? | **Pak:** ≈ 1 bit për raund të sulmuar (sulmuesi provon 2 mundësi në vend të 1) |
| Sa fsheh loja realisht? | 5 bit për pozicionin e saktë, por **vetëm 1 bit** për "cili rresht", që është ajo që u intereson sulmeve |
| Sa raunde u thyen? | **5 raunde**: rikthimi i plotë i çelësit të raundit 5 (256 bit) me ~12 000 tekste, < 1 s, te V-F dhe V-L |
| BRI-410 kundrejt AES-it, raund për raund | Përzierja: njësoj ose më mirë. **Sulmi integral: BRI-410 është 1 raund më i dobët** |
| Shpejtësia (Python) | BRI-410/16 ≈ 1,9× më i ngadaltë se AES-256 për bajt; BRI-410/32 ≈ 3,7× |

## 1. Sa informacion fsheh loja

32 variante për raund, të gjitha të ndryshme. Por sulmet nuk kanë nevojë gjithmonë për pozicionin e saktë:

| Çfarë i duhet sulmuesit | Mundësi të ndryshme mes 32 varianteve | Bit të fshehur për raund |
|---|---|---|
| Pozicioni i saktë i çdo kutie | 32 | 5,0 |
| Në cilin rresht shkon çdo kuti | **2** | **1,0** |
| Cilat kuti përfundojnë bashkë në një rresht | **2** | **1,0** |

**Arsyeja:** rreshti i ri është `r + k·dr` dhe varet vetëm nga `dr = ±1`. β dhe `dk` lëvizin kutitë vetëm brenda rreshtit.
Meqë θ përzien vetëm brenda rreshtave, shumica e sulmeve (integral, diferencial i shkurtuar) shohin vetëm këtë 1 bit.

## 2. Dalluesi integral ("Square")

Grup tekstesh ku disa nibble marrin të gjitha vlerat dhe pjesa tjetër mbetet fikse. Pastaj numërojmë sa nibble dalin
me shumë XOR = 0. Një funksion i rastësishëm jep mesatarisht **4 nga 64** (AES-i: 0,06 nga 16).

| Grupi | Tekste | Raunde | V-F | V-L | |
|---|---|---|---|---|---|
| 1 nibble | 16 | 3 | 64/64 (20/20) | 64/64 (20/20) | dallues |
| 1 nibble | 16 | 4 | 3,7 | 4,0 | rastësi |
| 2 nibble në të njëjtin rresht hyrës | 256 | 4 | 3,9 | 3,2 | rastësi |
| 2 nibble të **rreshtuara** pas π₁ | 256 | 4 | 2–4 | 2–5 | rastësi |
| **3 nibble të rreshtuara pas π₁** | **4 096** | **4** | **64/64 (5/5)** | **64/64 (5/5)** | **dallues** |
| 4 nibble të rreshtuara | 65 536 | 4 | 64/64 (3/3) | 64/64 (3/3) | dallues |
| 4 nibble të rreshtuara | 65 536 | 5 | 1–2 | 2–8 | rastësi |
| 4 nibble të rreshtuara | 65 536 | 6 | 2–3 | 3–4 | rastësi |
| **AES:** 1 bajt | 256 | 3 | 16/16 (20/20) | | dallues |
| **AES:** 1 bajt | 256 | 4 | 0,1 | | rastësi |

"Të rreshtuara" do të thotë kuti që π₁ i çon në të njëjtin rresht. Te V-L kjo varet vetëm nga 1 bit (dr), kështu që sulmuesi provon të dyja.

**Gjetja kryesore:** BRI-410 ka dallues integral në **4 raunde me vetëm 2^12 tekste**. AES-i ka dallues në 3 raunde me 2^8 tekste,
dhe për 4 raunde i duhen 2^32. Arsyeja më e mundshme është S-box-i 4-bitësh me shkallë algjebrike 3: shkalla rritet ngadalë,
ndaj shumat mbi grupe të vogla dalin zero për më gjatë. **Raund për raund, BRI-410 është më i dobët se AES-i kundër këtij sulmi.**

## 3. Sulme reale: rikthimi i çelësit

Dalluesi në r raunde, plus deshifrimi i pjesshëm i 1 raundi, rikthen çelësin e raundit r + 1.
θ-ja e fundit nuk ka çelës dhe kthehet plotësisht, kështu që çdo nibble i çelësit (4 bit) gjendet veç.

| Objektivi | Konfigurimi | Sukses | Tekste (mesatarja) | Koha | Rikthehen |
|---|---|---|---|---|---|
| 4 raunde | V-F | 10/10 | 48 | < 0,1 s | RK₄, 256 bit |
| 4 raunde | V-L | 10/10 | 56 | < 0,1 s | RK₄, 256 bit |
| 4 raunde | AES-256 | 10/10 | 538 | 0,05 s | RK₄, 128 bit |
| **5 raunde** | **V-F** | **3/3** | 12 288 | 0,8 s | **RK₅, 256 bit** |
| **5 raunde** | **V-L** | **3/3** | 12 288 – 16 384 | 0,8–1,0 s | **RK₅, 256 bit** |

Te V-L, sulmuesi nuk e di `dr`-në. Provon `dr = +1`, dhe nëse grupi i parë jep kontradiktë, kalon te `dr = −1`.
Kostoja shtesë ishte 4 096 tekste në 1 nga 3 prova. Kjo është ≈ 1 bit, siç parashikon §1.

**Kujdes:** këto sulme rikthejnë **çelësin e raundit**, jo çelësin 410-bitësh. Për çelësin kryesor, sulmuesit i duhen
edhe 40 nibble (160 bit) të gjendjes së orarit. Kjo kërkon punë shtesë, që nuk u provua.

### Sa larg mund të shkojë sulmi (vlerësim, i pa ekzekutuar)

- **6 raunde:** shtohet 1 raund në fund. Sulmuesi merr me mend 8 nibble të raundit të fundit + 1 të parafundit (36 bit) për çdo nibble,
  me 2^12 tekste, pra ≈ 2^48 operacione. Është e pamundur në Python, por **e arritshme për një sulmues real**.
- **7+ raunde:** kërkon dallues më të gjatë (p.sh. me 8 nibble të rreshtuara = 2^32 tekste) ose analizë me
  "division property". Kjo matet në F4 me mjete MILP/SAT.

## 4. Krahasimi me AES-256

| | BRI-410 | AES-256 |
|---|---|---|
| Blloku / çelësi | 256 / 410 bit | 128 / 256 bit |
| Raunde deri në përzierje të plotë (efekti ortek ≈ 50%) | 3 (F2) | 3 (raundi 2: 12,6%, raundi 3: 50,2%) |
| Dallues integral | 4 raunde, 2^12 tekste | 3 raunde, 2^8 (4 raunde: 2^32) |
| Sulm real i ekzekutuar këtu | 5 raunde | 4 raunde |
| Raunde gjithsej | 16 ose 32 | 14 |
| Shpejtësia në Python | 16 r: 186–188 KB/s; 32 r: 95–97 KB/s | 356 KB/s |
| Vite analize publike | ~0 (disa orë) | 25 |

Shpejtësia vlen vetëm për krahasim mes tyre. AES-i real përdor udhëzime të procesorit (AES-NI) dhe arrin GB/s.

## 5. Përfundimet

1. **V-L kundrejt V-F:** loja nuk dobëson asgjë. Të 32 variantet janë të verifikuara dhe shpejtësia është e njëjtë.
   Fitimi është i vogël: ≈ 1 bit për raund të sulmuar kundër sulmeve që provuam (deri në 5 bit kur sulmuesit i duhet pozicioni i saktë),
   plus përhapje pak më e shpejtë e çelësit në raundet 1–2 (F2).
   Kostoja vjen në implementimin real, ku zbatimi në kohë konstante është më i vështirë.
2. **R₃ ≥ 5** (i ekzekutuar), me gjasë 6 (≈ 2^48 punë), ndoshta më shumë (F4).
3. **Rregulli i raundeve me njohuritë e sotme:** R = 2 × max(R₁ = 3, R₂ ≈ 8, R₃ = 5–6) = **16**.
   Por marzhi është më i ngushtë sesa dukej: nëse F4 gjen një sulm mbi 8 raunde, rregulli jep **32**.
4. **Ndershmëria:** AES-i ka 25 vjet sulme pa u thyer. BRI-410 ka disa orë analizë nga një burim i vetëm.

## Vendimet që presin pronarin

1. **Varianti zyrtar:**
   - **(a) Rekomandim: V-L, por siguria llogaritet sikur të ishte V-F.** Ruhet ideja e lojës, që nuk kushton shpejtësi dhe nuk dëmton,
     por numri i raundeve nuk mbështetet te fitimi i saj i vogël.
   - (b) V-F: më i thjeshtë për analizë dhe për kohë konstante.
   - (c) Lojë më e pasur, që fsheh edhe rreshtat (p.sh. `r + m·k` me `m` tek sipas çelësit, 2 bit "rreshti" për raund). Kërkon F1 të ri.
2. **Raundet:** mbajmë 16 dhe 32 të hapura deri në F4, apo fiksojmë **32 tani** për siguri, duke ditur që BRI-410 është 1 raund më i dobët se AES-i kundër sulmit integral?
3. **F4:** analiza me MILP/SAT (division property, gjurmë diferenciale/lineare) dhe përpjekja për 6 raunde.
