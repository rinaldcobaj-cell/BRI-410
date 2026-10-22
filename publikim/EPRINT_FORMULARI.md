# Formulari i IACR ePrint: tekstet gati për kopjim

Faqja: https://eprint.iacr.org → "Submit". Llogarinë e krijon **ti** me emailin tënd.
Më poshtë është çfarë të shkruash në secilën fushë. Tekstet në kuti janë në anglisht: kopjoji ashtu siç janë.

## Titulli (Title)

```
BRI-410: A Chess-Inspired Tweakable Block Cipher with a 410-bit Key, Designed by Measurement
```

## Autori (Authors)

```
Rinald Cobaj
```
Afiliacioni (Affiliation): `Independent researcher` · Emaili: `vlorarino@gmail.com`

## Abstrakti (Abstract)

```
We present BRI-410, a tweakable block cipher with a 512-bit block, a 410-bit key, a 128-bit tweak and 16 rounds, together with BRI-410 AE, an authenticated-encryption mode based on ThetaCB3 with a 416-bit tag. The design started from an analogy with chess: the rules of the game are public while every game played is unique. The game-tree complexity of chess, about 10^123 = 2^410, fixes the key length. The 8x8 board fixes the state, and the knight's move gives a key- and tweak-dependent cell permutation. The idea that every game is played only once led to deriving all round keys and the permutation from the key and a per-block tweak. The cipher is a key-alternating SPN with an AES-like 8-bit S-box and an 8x8 Cauchy MDS matrix over GF(2^8).

The design was driven by measurements. An earlier version with 4-bit cells had a 4-round integral distinguisher with 2^12 chosen plaintexts and a practical 5-round key-recovery attack, and was replaced. For the final version we prove with a CP-SAT model that, for every choice of the key-dependent permutations, any 4-round differential or linear trail has at least 81 active S-boxes (probability at most 2^-486) and any 6-round trail at least 90 (at most 2^-540). The best attacks we found reach 4 of 16 rounds in practice, with an estimated 5-round attack at about 2^72. We state explicit security claims, list open problems and propose reduced-round challenges. A reference implementation and test vectors are public under CC0 at https://github.com/rinaldcobaj-cell/BRI-410.
```

## Fjalët kyçe (Keywords)

```
block cipher, tweakable block cipher, authenticated encryption, SPN, MILP, CP-SAT, cryptanalysis, design
```

## Kategoria (Category)

`Secret-key cryptography`

## Skedari (PDF)

`publikim/paper/BRI-410.pdf`

## Licenca e punimit (nëse formulari pyet)

ePrint mund të të kërkojë të zgjedhësh një licencë për punimin. Zgjidh **CC0**, nëse ekziston si opsion, që të përputhet me kodin.
Përndryshe zgjidh **CC BY**, që lejon gjithçka me kusht përmendjen e emrit tënd.

## Lidhja e kodit (nëse ka fushë për shënime ose "note")

```
Reference implementation, test vectors and all analysis scripts: https://github.com/rinaldcobaj-cell/BRI-410
```

## Pas dërgimit

- Redaktorët e ePrint-it bëjnë një kontroll të shkurtër. Zakonisht punimi del brenda pak ditësh.
- Do të marrësh një email me numrin e punimit, p.sh. `2026/1234`. Ruaje: me të e citojnë të tjerët.
- Shto këtë numër te README në GitHub. Mund ta shtoj unë, mjafton të ma thuash.
