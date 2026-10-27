"""Kthen BRI-410.md në BRI-410.pdf (reportlab, fontet e Windows-it). Përdorimi: python ndertoj_pdf.py

Mbështet vetëm atë që përdor punimi: titujt (#, ##, ###), paragrafët, **të trasha**, *të pjerrëta*, `kod`,
tabelat |…|, blloqet ``` dhe listat (- dhe 1.).
"""

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle, XPreformatted)

DOSJA = Path(__file__).resolve().parent
FONTET = Path(r"C:\Windows\Fonts")
pdfmetrics.registerFont(TTFont("Body", str(FONTET / "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("Body-B", str(FONTET / "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("Body-I", str(FONTET / "segoeuii.ttf")))
pdfmetrics.registerFont(TTFont("Mono", str(FONTET / "consola.ttf")))
pdfmetrics.registerFont(TTFont("Sym", str(FONTET / "seguisym.ttf")))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I", boldItalic="Body-B")

SIMBOLET = "∈∪⊕⌊⌋∎"  # mungojnë te Segoe UI dhe Consolas → Segoe UI Symbol

BAZA = ParagraphStyle("baza", fontName="Body", fontSize=10, leading=14, spaceAfter=6)
STILET = {
    "titulli": ParagraphStyle("titulli", parent=BAZA, fontName="Body-B", fontSize=17, leading=22, alignment=TA_CENTER,
                              spaceAfter=10),
    "autori": ParagraphStyle("autori", parent=BAZA, alignment=TA_CENTER, spaceAfter=2),
    "shenim": ParagraphStyle("shenim", parent=BAZA, fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor("#444444"),
                             spaceAfter=14),
    "h2": ParagraphStyle("h2", parent=BAZA, fontName="Body-B", fontSize=13, leading=17, spaceBefore=12, spaceAfter=6,
                         keepWithNext=1),
    "h3": ParagraphStyle("h3", parent=BAZA, fontName="Body-B", fontSize=11, leading=15, spaceBefore=8, spaceAfter=4,
                         keepWithNext=1),
    "liste": ParagraphStyle("liste", parent=BAZA, spaceAfter=2.5),
    "para_listes": ParagraphStyle("para_listes", parent=BAZA, keepWithNext=1),  # paragrafi që mbaron me ":"
    "referenca": ParagraphStyle("referenca", parent=BAZA, fontSize=8.8, leading=11.5, spaceAfter=1.5),
    "qeliza": ParagraphStyle("qeliza", parent=BAZA, fontSize=8.5, leading=11, spaceAfter=0),
    "kodi": ParagraphStyle("kodi", fontName="Mono", fontSize=7.6, leading=10, leftIndent=8, backColor=colors.HexColor("#f4f4f4"),
                           borderPadding=5, spaceBefore=4, spaceAfter=10),
}


def _simbolet(t: str) -> str:
    return "".join(f'<font name="Sym">{c}</font>' if c in SIMBOLET else c for c in t)


def _rresht(t: str) -> str:
    """Markdown brenda rreshtit → markup i reportlab-it."""
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    kodet = []

    def _ruaj_kodin(m):
        kodet.append(m.group(1))
        return f"\x00{len(kodet) - 1}\x00"

    t = re.sub(r"`([^`]+)`", _ruaj_kodin, t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
    t = _simbolet(t)
    return re.sub(r"\x00(\d+)\x00", lambda m: f'<font name="Mono" size="8.6">{_simbolet(kodet[int(m.group(1))])}</font>', t)


def _tabela(rreshtat: list[str], gjeresia: float) -> Table:
    qelizat = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rreshtat
               if not re.fullmatch(r"\|?[\s:|-]+\|?", r.strip())]
    n = max(len(r) for r in qelizat)
    qelizat = [r + [""] * (n - len(r)) for r in qelizat]
    # Gjerësia minimale e kolonës: fjala më e gjatë nuk duhet të pritet. Pjesa tjetër ndahet sipas gjatësisë së tekstit.
    def _pastro(c):
        return c.replace("**", "").replace("`", "").replace("*", "")

    minimumi = [max(pdfmetrics.stringWidth(f, "Body-B" if i == 0 else "Body", 8.5)
                    for i, r in enumerate(qelizat) for f in (_pastro(r[j]).split() or [""])) + 8 for j in range(n)]
    gjatesite = [max(len(_pastro(r[j])) for r in qelizat) + 2 for j in range(n)]
    teprica = max(gjeresia - sum(minimumi), 0)
    kolonat = [m + teprica * g / sum(gjatesite) for m, g in zip(minimumi, gjatesite)]
    kolonat = [k * gjeresia / sum(kolonat) for k in kolonat]
    te_dhena = [[Paragraph(("<b>%s</b>" if i == 0 else "%s") % _rresht(c), STILET["qeliza"]) for c in r]
                for i, r in enumerate(qelizat)]
    t = Table(te_dhena, colWidths=kolonat, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def _lista(elementet: list[str], e_numeruar: bool) -> ListFlowable:
    stili = STILET["referenca"] if all(e.startswith("[") for e in elementet) else STILET["liste"]
    return ListFlowable([ListItem(Paragraph(_rresht(e), stili), leftIndent=16) for e in elementet],
                        bulletType="1" if e_numeruar else "bullet", start="1" if e_numeruar else None,
                        bulletFormat="%s." if e_numeruar else None,
                        bulletFontName="Body", bulletFontSize=9, leftIndent=16, spaceAfter=6)


def ndertoj(md: Path, pdf: Path, fundi: str = "BRI-410 — draft — study cipher, not for real use") -> None:
    rreshtat = md.read_text(encoding="utf-8").splitlines()
    gjeresia = A4[0] - 4.4 * cm
    historia = []
    i = 0
    paragrafi: list[str] = []
    titulli_u_vu = False

    def mbyll_paragrafin():
        if paragrafi:
            teksti = " ".join(paragrafi)
            stili = STILET["para_listes"] if teksti.rstrip("*").endswith(":") else BAZA
            historia.append(Paragraph(_rresht(teksti), stili))
            paragrafi.clear()

    while i < len(rreshtat):
        r = rreshtat[i]
        if r.startswith("```"):
            mbyll_paragrafin()
            j = i + 1
            while not rreshtat[j].startswith("```"):
                j += 1
            kodi = "\n".join(rreshtat[i + 1:j]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            historia.append(XPreformatted(_simbolet(kodi), STILET["kodi"]))
            i = j + 1
        elif r.startswith("|"):
            mbyll_paragrafin()
            j = i
            while j < len(rreshtat) and rreshtat[j].startswith("|"):
                j += 1
            historia += [_tabela(rreshtat[i:j], gjeresia), Spacer(1, 8)]
            i = j
        elif re.match(r"^(\s*)([-]|\d+\.) ", r):
            mbyll_paragrafin()
            e_numeruar = bool(re.match(r"^\s*\d+\.", r))
            elementet = []
            while i < len(rreshtat) and rreshtat[i].strip():
                m = re.match(r"^\s*(?:-|\d+\.) (.*)", rreshtat[i])
                if m:
                    elementet.append(m.group(1))
                else:
                    elementet[-1] += " " + rreshtat[i].strip()
                i += 1
            # titulli dhe/ose fjalia me ":" që i paraprijnë listës nuk ndahen prej saj
            bashke = [_lista(elementet, e_numeruar)]
            while (historia and isinstance(historia[-1], Paragraph)
                   and historia[-1].style.name in ("para_listes", "h2", "h3")):
                bashke.insert(0, historia.pop())
            historia.append(KeepTogether(bashke) if len(bashke) > 1 else bashke[0])
        elif r.startswith("# "):
            mbyll_paragrafin()
            historia.append(Paragraph(_rresht(r[2:]), STILET["titulli"]))
            titulli_u_vu = True
            i += 1
        elif r.startswith("## "):
            mbyll_paragrafin()
            historia.append(Paragraph(_rresht(r[3:]), STILET["h2"]))
            i += 1
        elif r.startswith("### "):
            mbyll_paragrafin()
            historia.append(Paragraph(_rresht(r[4:]), STILET["h3"]))
            i += 1
        elif not r.strip():
            mbyll_paragrafin()
            i += 1
        elif titulli_u_vu and len(historia) == 1:      # rreshti i autorit
            historia.append(Paragraph(_rresht(r), STILET["autori"]))
            i += 1
        elif titulli_u_vu and len(historia) == 2 and r.startswith("*"):   # shënimi i draftit
            historia.append(Paragraph(_rresht(r), STILET["shenim"]))
            i += 1
        else:
            paragrafi.append(r.strip())
            i += 1
    mbyll_paragrafin()

    def faqja(kanavaca, dok):
        kanavaca.saveState()
        kanavaca.setFont("Body", 8)
        kanavaca.setFillColor(colors.HexColor("#666666"))
        kanavaca.drawString(2.2 * cm, 1.2 * cm, fundi)
        kanavaca.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, str(dok.page))
        kanavaca.restoreState()

    SimpleDocTemplate(str(pdf), pagesize=A4, leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2 * cm,
                      bottomMargin=2 * cm, title="BRI-410", author="Rinald Cobaj",
                      subject="A chess-inspired tweakable block cipher with a 410-bit key").build(
        historia, onFirstPage=faqja, onLaterPages=faqja)


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["v1"]:  # versioni 1 (i dërguar në IACR më 2026-10-22); mos e rindërto pa nevojë
        ndertoj(DOSJA / "BRI-410.md", DOSJA / "BRI-410.pdf")
        ndertoj(DOSJA / "BRI-410_shqip.md", DOSJA / "BRI-410_shqip.pdf",
                "BRI-410 — përkthim në shqip për autorin (versioni për publikim: anglisht)")
        print("v1: BRI-410.pdf dhe BRI-410_shqip.pdf u ndërtuan")
    else:
        ndertoj(DOSJA / "BRI-410_v2.md", DOSJA / "BRI-410_v2.pdf",
                "BRI-410 v1.1 — paper version 2 — study cipher, not for real use")
        ndertoj(DOSJA / "BRI-410_v2_shqip.md", DOSJA / "BRI-410_v2_shqip.pdf",
                "BRI-410 v1.1 — versioni 2 në shqip, për autorin (për publikim: anglisht)")
        print("v2: BRI-410_v2.pdf dhe BRI-410_v2_shqip.pdf u ndërtuan")
