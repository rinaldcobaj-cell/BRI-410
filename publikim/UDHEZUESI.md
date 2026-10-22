# Udhëzuesi i publikimit të BRI-410

Ky udhëzues është për ty. Dosja `publikim/` përmban gjithçka që u duhet të tjerëve, **në anglisht**:

| Skedari | Çfarë është |
|---|---|
| `paper/BRI-410.md` / `.pdf` | **Punimi** (anglisht, për publikim): specifikimi, arsyetimi, analiza, deklarata e sigurisë, pyetjet e hapura, sfidat |
| `paper/BRI-410_shqip.md` / `.pdf` | **I njëjti punim në shqip**, vetëm për ty, që ta lexosh dhe ta kontrollosh. Nuk publikohet. |
| `reference/bri410.py` | Kodi reference: një skedar, vetëm Python standard, shifra + mënyra me vulë |
| `reference/test_vectors.json` | 12 + 6 vektorë testi |
| `reference/verify.py` | Kontrolli: `python verify.py` duhet të shkruajë `ALL PASSED` |

Kodi reference u shkrua nga e para dhe përputhet bit për bit me implementimin e projektit. Testi `teste/test_publikim.py` e mban këtë përputhje.

**Publikimin e bën ti, me emrin tënd.** Unë nuk publikoj asgjë.

## Hapat, një nga një

### 1. Lexo punimin dhe plotëso të dhënat e tua
- Te rreshti i dytë: `[Author name]`, `[affiliation / independent researcher]`, `[contact]`.
  "Independent researcher" është plotësisht në rregull nëse nuk ke institucion.
- Lexoje të gjithë. Nëse diçka nuk të duket e qartë ose e saktë, më thuaj dhe e rregullojmë.
- Nëse njeh dikë me njohuri kriptografie ose matematike, është shumë e dobishme që ta lexojë para publikimit.

### 2. Vendos për deklaratën e ndihmës së AI-së
Në fund të punimit ("Acknowledgements") është një fjali që thotë se implementimi dhe analiza u bënë me ndihmën e një modeli AI.
**Rekomandimi im: mbaje.** Shumë vende publikimi e kërkojnë këtë transparencë, dhe fshehja e saj mund të dëmtojë besueshmërinë.
Mund ta riformulosh si të duash, por vendimi është yti.

### 3. Zgjidh licencën e kodit
Që të tjerët ta përdorin dhe ta testojnë lirshëm, kodi duhet të ketë licencë. Dy zgjedhje të zakonshme:
- **CC0 / public domain**: kushdo e përdor pa kushte (shumë algoritme kriptografike publikohen kështu)
- **MIT**: e lirë, por me përmendjen e emrit tënd

Më thuaj cilën do, dhe e shtoj.

### 4. Ktheje punimin në PDF
IACR ePrint pranon vetëm PDF. Mund ta bëj unë nga `BRI-410.md`, ose mund ta kopjosh në Word / Google Docs dhe ta ruash si PDF.

### 5. Vendose kodin online në GitHub (rekomandohet)
Dosja e pastër, gati për ngarkim: **`C:\Users\vlora\BRI-410_per_GitHub`** (73 skedarë, pa `.venv` dhe `__pycache__`).
`README.md` (anglisht) del si faqja kryesore e projektit. `README_sq.md` është versioni shqip.

1. Hap https://github.com dhe krijo një llogari ("Sign up"), nëse nuk ke.
2. Lart djathtas: **"+" → "New repository"**.
3. Emri: `BRI-410` · zgjidh **Public** · **MOS** shëno "Add a README" (e kemi tonën) · **"Create repository"**.
4. Në faqen që hapet, kliko lidhjen **"uploading an existing file"**.
5. Hap dosjen `BRI-410_per_GitHub` në kompjuter, **zgjidh gjithë përmbajtjen e saj** (Ctrl+A) dhe tërhiqe me maus në faqen e GitHub-it.
   Dosjet ruajnë strukturën e tyre.
6. Poshtë, te "Commit changes", shkruaj `BRI-410: initial publication` dhe kliko **"Commit changes"**.
7. Kopjo adresën e depos (p.sh. `https://github.com/emri-yt/BRI-410`) dhe ma dërgo, që ta shtoj te punimi dhe te formulari i ePrint-it.

Raportet në `docs/` janë në shqip. Kjo nuk është problem, sepse punimi në anglisht përmbledh gjithçka.
Kujdes: dosja e pastër është kopje e gjendjes së sotme. Nëse ndryshojmë diçka më vonë, e rikrijoj.

### 6. Publikimi në IACR ePrint (https://eprint.iacr.org)
Të gjitha tekstet e formularit (titulli, abstrakti, fjalët kyçe, kategoria) janë gati te **`publikim/EPRINT_FORMULARI.md`**.

1. Krijo një llogari.
2. "Submit a paper": ngarko PDF-në, titullin, emrin, abstraktin (merre nga punimi) dhe fjalët kyçe, p.sh.
   `block cipher, tweakable block cipher, authenticated encryption, SPN, MILP, design`.
3. Kategoria: **secret-key cryptography**.
4. Redaktorët bëjnë një kontroll të shkurtër (nuk është vlerësim i plotë shkencor). Zakonisht punimi del brenda pak ditësh.
5. Vendos lidhjen e GitHub-it te punimi.

### 7. Pas publikimit
- **Përgjigju analizave.** Nëse dikush gjen një sulm, falënderoje publikisht dhe vlerëso nëse duhet një version i ri (v2).
- **Sfidat** (seksioni 7 i punimit) janë ftesë konkrete për kriptanalistët.
- Mundësi për më vonë: prezantim i shkurtër në "rump session" të një konference (p.sh. FSE). Kjo tërheq vëmendjen e specialistëve.

## Lista e kontrollit

- [x] Emri i autorit: **Rinald Cobaj**, "Independent researcher" (ndryshohet nëse ke afiliacion)
- [x] Kontakti te punimi: vlorarino@gmail.com
- [ ] Punimi i lexuar, pyetjet e mia të sqaruara
- [x] Fjalia e AI-së: e mbajtur, me ndarjen e qartë të roleve (idetë dhe vendimet = autori; AI = asistent)
- [x] Licenca: **CC0 1.0** (`LICENSE` në rrënjë dhe te `publikim/reference/`), me deklaratën "nuk është i patentuar"
- [x] PDF: `paper/BRI-410.pdf` (5 faqe). Nëse ndryshon `BRI-410.md`, rindërtoje me `python ndertoj_pdf.py` brenda `paper/`
- [ ] (opsionale) depo në GitHub (`.gitignore` gati: përjashton `.venv/` dhe `__pycache__/`)
- [ ] Dërgimi në IACR ePrint
