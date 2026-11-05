"""Shkruan shtojcat A–B të BRI-410_v2.1.tex (S-box, M, M^-1, mbushja, vektorët) nga kodi i v1.1.

Përdorimi (nga rrënja e projektit): python publikim/paper/gjenero_shtojcat_tex.py
Çdo pjesë ndodhet midis "% BEGIN X" dhe "% END X", ndaj skripti mund të rinisë sa herë të duhet.
"""

import re
import sys
from pathlib import Path

RRENJA = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RRENJA))

from shahu import bri8, mds8, sbox8  # noqa: E402

PUNIMI = Path(__file__).resolve().parent / "BRI-410_v2.1.tex"


def _hex(v: int) -> str:
    return r"\texttt{%02x}" % v


def _koka(v: int) -> str:
    return r"\textbf{\texttt{%x}}" % v


def tabela_sbox() -> list[str]:
    rreshta = [r"\begin{center}\small\setlength{\tabcolsep}{3.2pt}",
               r"\begin{tabular}{@{}c|" + "c" * 16 + "@{}}",
               " & " + " & ".join(_koka(j) for j in range(16)) + r"\\",
               r"\hline"]
    for i in range(16):
        rreshta.append(_koka(i) + " & " + " & ".join(_hex(sbox8.SBOX[16 * i + j]) for j in range(16)) + r"\\")
    return rreshta + [r"\end{tabular}", r"\end{center}"]


def _matrica(m: list[list[int]], emri: str) -> list[str]:
    rreshta = [r"\begin{tabular}{@{}" + "c" * 8 + "@{}}", r"\multicolumn{8}{c}{%s}\\[2pt]" % emri]
    rreshta += [" & ".join(_hex(v) for v in r) + r"\\" for r in m]
    return rreshta + [r"\end{tabular}"]


def tabelat_mds() -> list[str]:
    return ([r"\begin{center}\small\setlength{\tabcolsep}{4pt}"] + _matrica(mds8.M, "$M$") + [r"\qquad"]
            + _matrica(mds8.M_INV, "$M^{-1}$") + [r"\end{center}"])


def vektoret() -> list[str]:
    celesi2, numri2, mesazhi2 = bytes(range(51)) + b"\x02", bytes(range(16)), bytes(range(64))
    c1 = bri8.BRI410_8(bytes(52), 16, bytes(16)).kripto(bytes(64)).hex()
    c2 = bri8.BRI410_8(celesi2, 16, numri2).kripto(mesazhi2).hex()

    def kriptuar(c: str) -> str:
        return r"Ciphertext & \texttt{%s}\\ & \texttt{%s}\\" % (c[:64], c[64:])

    return [r"\begin{center}\small", r"\begin{tabular}{@{}ll@{}}", r"\toprule",
            r"\multicolumn{2}{@{}l}{\emph{Vector 1}}\\",
            r"Key & $\hx{00}^{52}$ (52 zero bytes)\\",
            r"Tweak & $\hx{00}^{16}$\\",
            r"Plaintext & $\hx{00}^{64}$\\",
            kriptuar(c1), r"\midrule",
            r"\multicolumn{2}{@{}l}{\emph{Vector 2}}\\",
            r"Key & bytes $0..50$ equal to $0,1,\dots,50$ ($\hx{00}\,\hx{01}\cdots\hx{32}$), byte $51 = \hx{02}$\\",
            r"Tweak & \texttt{%s}\\" % numri2.hex(),
            r"Plaintext & bytes $0..63$ equal to $0,1,\dots,63$ ($\hx{00}\,\hx{01}\cdots\hx{3f}$)\\",
            kriptuar(c2), r"\bottomrule", r"\end{tabular}", r"\end{center}"]


def main() -> None:
    teksti = PUNIMI.read_text(encoding="utf-8")
    for emri, rreshtat in (("SBOX", tabela_sbox()), ("MDS", tabelat_mds()), ("VECTORS", vektoret())):
        blloku = "\n".join([f"% BEGIN {emri}"] + rreshtat + [f"% END {emri}"])
        modeli = re.compile(rf"%%{emri}%%|% BEGIN {emri}\n.*?% END {emri}", re.S)
        teksti, n = modeli.subn(lambda _: blloku, teksti)
        assert n == 1, emri
    teksti, n = re.subn(r"\\mathit\{pad\} = \\texttt\{[^}]*\}",
                        lambda _: r"\mathit{pad} = \texttt{%s}" % hex(bri8._MBUSHJA), teksti)
    assert n == 1, "PAD"
    assert not re.search(r"[\x00-\x08\x0b-\x1f]", teksti), "shenja kontrolli"
    PUNIMI.write_text(teksti, encoding="utf-8", newline="\n")
    print("ok", PUNIMI.name)


if __name__ == "__main__":
    main()
