# BRI-410 — Raporti F3-bis: "çdo lojë luhet vetëm një herë" (2026-10-22)

Riprodhimi (nga `C:\Users\vlora\Shahu_Kripto`):

```
python -m unittest discover -s teste -t .     # 26/26 OK (4 teste të reja për V-N)
python -m matje.f3bis_matjet                  # → matje/f3bis_rezultatet.json (~35 s)
```

## Ideja e pronarit

> Çdo lojë është unike dhe luhet vetëm një herë.

Në F0–F3, BRI-410 kishte **një lojë për çdo çelës**: i njëjti çelës luante të njëjtën lojë për çdo mesazh.
Sulmi integral i F3 e shfrytëzoi pikërisht këtë, me 4 096 mesazhe që kaluan nëpër të njëjtën lojë.
F3-bis ndërton idenë siç ishte menduar: **një lojë e re për çdo bllok**.

## Ndërtimi: varianti V-N ("loja sipas bllokut")

```
çelësi 410 bit (gjenerohet NJË herë, sekret)
      │  4 hapa përzierjeje (vetëm çelësi)
      ▼
      ⊕  numri unik 128 bit (publik, i ndryshëm për ÇDO bllok, nuk përsëritet kurrë)
      │  4 hapa përzierjeje
      ▼
loja + të gjithë çelësat e raundeve për këtë bllok
```

- Numri nuk futet direkt mbi çelësin. Po të futej, sulmuesi që zgjedh numrin do të zgjidhte në fakt një "çelës të lidhur".
- Marrësi ka çelësin dhe numrin, ndaj e riprodhon lojën dhe dekripton.
- Kod: `BRI410(celesi, raunde, "VN", numri)`. Testet: kthim 100%, përputhje me një version reference, numra të ndryshëm japin kriptime të ndryshme.

## Rezultatet: i njëjti sulm kundër tri mënyrave

### 1. Dalluesi integral (sa nga 64 nibble dalin të balancuara; rastësia jep ≈ 4)

| Mënyra | 1 nibble, 3 raunde (10 prova) | 3 nibble të rreshtuara, 4 raunde (5 prova) |
|---|---|---|
| VL: loja sipas çelësit | 64 ×10 ❌ dallohet | 64 ×5 ❌ dallohet |
| **VN: lojë e re për çdo bllok** | **1–7** ✅ rastësi | **2–6** ✅ rastësi |
| VN me numër të përsëritur (keqpërdorim) | 64 ×10 ❌ dallohet | 64 ×5 ❌ dallohet |

Me V-N zhduket edhe dalluesi më i thjeshtë, ai në 3 raunde, jo vetëm ai në 4.

### 2. Sulmi real mbi 5 raunde

| Mënyra | Rezultati | Tekste | Koha |
|---|---|---|---|
| VL | **3/3**: çelësi i raundit 5 u rikthye | 12 288 – 20 480 | 0,8–1,3 s |
| **VN** | **0/3: "kontradiktë: asnjë çelës nuk përputhet"**, me të dy supozimet për lojën | 8 192 | 2,5 s |
| VN me numër të përsëritur | **3/3**: çelësi i raundit 5 u rikthye | 12 288 – 16 384 | 0,8–1,0 s |

Rreshti i tretë provon kushtin: **numri nuk duhet të përsëritet kurrë.** Nëse përsëritet, rikthehet dobësia e vjetër.

### 3. A mund sulmuesi të gjejë rastësisht blloqe me "të njëjtën lojë"?

Nga 20 000 blloqe me të njëjtin çelës, **187 çifte** kishin lojë identike në 4 raundet e para (pritej 190,7 për 20 bit lojë).
Por edhe në këto çifte, **çelësat e raundeve ndryshonin 50%** (minimumi 42%), sepse edhe ata nxirren nga numri.
Pra përputhja e lojës nuk i jep sulmuesit të njëjtin funksion. ✅

Ndryshimi i 1 biti në numër ndryshon 49,6% të tekstit të kriptuar (16 raunde), siç pritet nga rastësia. ✅

### 4. Kostoja

| | Blloqe/s (Python) | Ngadalësimi |
|---|---|---|
| VL, 16 raunde | 5 840 | — |
| **VN, 16 raunde** | **1 603** | **3,6×** |
| VL, 32 raunde | 3 026 | — |
| **VN, 32 raunde** | **928** | **3,3×** |

Shkaku: loja dhe çelësat e raundeve llogariten nga e para për çdo bllok (8 hapa përzierjeje + R hapa).

## Interpretimi i ndershëm

1. **Pse funksionon:** pothuajse të gjitha sulmet klasike (integral, diferencial, linear) kanë nevojë për **shumë tekste
   të kriptuara me të njëjtin funksion**. Me V-N, çdo bllok ka funksionin e vet, kështu që sulmuesi merr vetëm 1 tekst për funksion.
2. **Ideja ekziston në kriptografi**, me emra si "tweakable block cipher", ndërrimi i çelësit për çdo mesazh, apo XChaCha20.
   Pronari arriti në të në mënyrë të pavarur, nga analogjia e shahut. Kjo është shenjë e mirë: ideja është e shëndoshë.
3. **Siguria tani mbështetet në dy gjëra:**
   - **rregulli i numrit:** nuk përsëritet kurrë me të njëjtin çelës. Ky është i njëjti rregull si te AES-GCM, ku përsëritja është gjithashtu katastrofë.
   - **forca e përzierjes çelës + numër.** Sulmuesi tani mund të zgjedhë numra me ndryshime të qëllimshme
     (sulme "related-tweak"). Kjo është **sipërfaqja e re e sulmit** që duhet analizuar në F4.
4. **Nuk vërteton siguri të plotë.** Vërteton se sulmi që theu 5 raunde **bllokohet plotësisht** kur rregulli respektohet.

## Vendimet që presin pronarin

1. **A bëhet V-N varianti zyrtar i BRI-410?** Rekomandim: **po**. Është ideja jote origjinale, bllokon sulmin kryesor, dhe kostoja (~3,5× në Python) është e pranueshme për algoritëm studimi.
2. **Raundet:** edhe me V-N, rekomandoj **32**. Nëse dikush e përsërit numrin gabimisht, BRI-410 bie në nivelin e VL, dhe atje 32 raunde japin marzhin e duhur.
3. **F4:** përveç planit të mëparshëm, analizë e sulmeve me numra të zgjedhur (related-tweak) mbi përzierjen çelës + numër.
