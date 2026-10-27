# Kriteret e IACR ePrint dhe versioni 2 i punimit

Dokument pune për autorin, për shqyrtimin para apelimit. Burimi i kritereve: https://eprint.iacr.org/operations.html
(teksti i sjellë nga autori më 2026-10-27). Punimi: `paper/BRI-410_v2.pdf` (anglisht), `paper/BRI-410_v2_shqip.pdf` (shqip).

**Kujdes:** redaktorët **nuk dhanë arsye specifike** për refuzimin. Ata cituan kriteret e pranimit dhe ofruan mundësinë
e apelimit me "PDF-në e dorëzimit dhe një arsyetim pse i plotëson të gjitha kriteret". Kolona e dytë më poshtë është
**vlerësimi ynë** për dobësitë e v1, jo arsye e deklaruar nga IACR. Në apelim nuk duhet t'u atribuojmë redaktorëve
kërkesa që nuk i kanë shprehur.

**Pyetje e hapur para apelimit:** a pranojnë redaktorët në apelim një **PDF të rishikuar** (v2), apo vetëm PDF-në
origjinale? Përgjigjja e Matthias-it ("including your submission PDF") nuk e thotë qartë. Duhet pyetur ose shkruar
qartë në letër që PDF-ja e bashkangjitur është version i rishikuar.

| Kriteri zyrtar | Vlerësimi ynë për v1 (i refuzuar) | Si i përgjigjet v2 | Ku |
|---|---|---|---|
| Kërkim në kriptologji | ✅ | ✅ | i gjithë punimi |
| **I qartë, i lexueshëm, i pavarur** (i plotë në vetvete) | ❌ 5 faqe; konstantet, provat dhe detajet vetëm në GitHub dhe në raporte shqip | specifikim i plotë; tabela e S-box-it, M, M^-1, konstantja e mbushjes, vektorë testi dhe modeli CP-SAT brenda punimit; 12 faqe | §3, §4, shtojcat A–C |
| **Disi i ri dhe interesant** | ❌ pa krahasim me të tjerët | krahasim me Threefish-512, Kalyna-512, SKINNY/Deoxys-BC, AES-256, Blowfish/Twofish, rikeying; kontributet e thëna qartë, pa pretendim avantazhi praktik | §1, §2 |
| **Prova ose argumente bindëse për çdo pretendim** | ❌ pretendim sigurie 2^410 pa mbështetje; asnjë provë e shkruar | lemat 1–4 dhe teoremat 1–2 me prova; etiketa [Provë]/[Llogaritje]/[Eksperiment]/[Vlerësim]/[Hamendje]/[E hapur] për çdo pohim; objektivi i sigurisë si hamendje (2^256), me kufijtë e shkruar | §5, §8, §9 |
| Jo anonim; titulli, autori, kontakti në faqen e parë | ✅ | ✅ | faqja 1 |

## Rezultatet negative, të ruajtura në v2 (kërkesa 7 e autorit)

α i padobishëm · loja që fsheh 1 bit për raund · BRI-410/4 i thyer në 5 raunde · dobësia integrale e kutive 4-bitëshe ·
**orari i kthyeshëm i v1.0 (gjetja K)** · testi linear i projektuar keq · gabimet e versionit 1 të punimit. Shih §6.2, §7, §10.

## Para apelimit duhet të vendosë autori

1. **Leximi i versionit shqip** dhe miratimi i përmbajtjes.
2. **Përditësimi i GitHub-it** me v1.1. Punimi i drejton lexuesit te depoja, e cila tani ka ende v1.0. Duhet `git commit` + `push`, me miratimin e autorit.
3. **Hamendja 1 (objektivi 2^256):** është zgjedhje e projektimit të punimit, jo e algoritmit. Mund të ndryshohet nëse autori dëshiron.
4. **Letra e apelimit** te eprint-editor@iacr.org: PDF-ja e re + arsyetimi pikë për pikë sipas tabelës së mësipërme. E përgatisim pas miratimit.
5. Opsionale: një lexues me njohuri kriptografie para dërgimit.

## Kufizime që mbeten edhe pas v2

- Kriteri "disi i ri dhe interesant" mbetet në gjykimin e redaktorëve. v2 e argumenton, por nuk e garanton.
- CP-SAT nuk u rillogarit pas 22.10 (bllokohet nga Windows). Provat matematike nuk varen prej tij.
- Rezistenca "preimage" e F(X) ⊕ X (hamendja 2) dhe shumë klasa sulmesh mbeten të hapura, dhe kjo thuhet hapur në punim.
