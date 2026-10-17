"""Typeset PYTHON_DEVELOPER_GUIDE.md as a LaTeX book and compile it with tectonic.

Usage, from the repository root (needs tectonic: https://tectonic-typesetting.github.io):

    python tools/build_guide_pdf.py

writes docs/geant4-python-developer-guide.pdf. The intermediate LaTeX goes to
build/guide-latex/.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    Path(sys.argv[1]).resolve()
    if len(sys.argv) > 1
    else ROOT / "PYTHON_DEVELOPER_GUIDE.md"
)
OUTPUT = (
    Path(sys.argv[2]).resolve()
    if len(sys.argv) > 2
    else ROOT / "docs" / "geant4-python-developer-guide.pdf"
)
WORK = ROOT / "build" / "guide-latex"

PREAMBLE = r"""
\documentclass[11pt,a4paper,openany]{book}
\usepackage[a4paper,top=25mm,bottom=25mm,left=25mm,right=22mm,headheight=14pt]{geometry}
\usepackage{fontspec}
\setmainfont{texgyrepagella}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,
  ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\setsansfont{texgyreheros}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,
  ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\setmonofont{DejaVuSansMono}[Extension=.ttf,BoldFont=*-Bold,Scale=0.82]
\usepackage{amsmath,amssymb}
\usepackage{newunicodechar}
\newunicodechar{√}{\ensuremath{\surd}}
\usepackage{microtype}
\usepackage[dvipsnames,table]{xcolor}
\definecolor{navy}{HTML}{123B5D}
\definecolor{accent}{HTML}{1D5B83}
\definecolor{codebg}{HTML}{F5F7FA}
\definecolor{rule}{HTML}{D0D5DD}
\usepackage{graphicx}
\usepackage{float}
\usepackage{caption}
\captionsetup{font=small,labelfont={bf,color=navy},labelsep=period}
\usepackage{booktabs,xltabular,array}
\renewcommand{\arraystretch}{1.25}
\usepackage{enumitem}
\setlist{itemsep=2pt,topsep=4pt,parsep=0pt}
\usepackage{listings}
\lstdefinestyle{guide}{
  basicstyle=\ttfamily\small,
  backgroundcolor=\color{codebg},
  frame=single, rulecolor=\color{rule}, framesep=4pt, xleftmargin=6pt, xrightmargin=6pt,
  breaklines=true, breakatwhitespace=false, columns=fullflexible, keepspaces=true,
  showstringspaces=false, upquote=true, tabsize=4,
  postbreak=\mbox{\textcolor{gray}{$\hookrightarrow$}\space},
  aboveskip=6pt, belowskip=8pt,
}
\lstdefinestyle{python}{style=guide, language=Python,
  keywordstyle=\color{accent}\bfseries, commentstyle=\color{gray}\itshape,
  stringstyle=\color{BrickRed}, morekeywords={with,as,None,True,False,assert,yield,lambda}}
\lstdefinestyle{plain}{style=guide}
\lstset{style=plain}
\usepackage{titlesec}
\titleformat{\part}[display]{\sffamily\bfseries\color{navy}\centering}{\LARGE\partname~\thepart}{14pt}{\Huge}
\titleformat{\chapter}[display]{\sffamily\bfseries\huge\color{navy}}{}{0pt}{}
\titleformat{\section}{\sffamily\bfseries\Large\color{navy}}{}{0pt}{}
\titleformat{\subsection}{\sffamily\bfseries\large\color{accent}}{}{0pt}{}
\titlespacing*{\section}{0pt}{16pt}{6pt}
\titlespacing*{\subsection}{0pt}{12pt}{4pt}
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\sffamily\color{gray}\nouppercase{\rightmark}}
\fancyhead[R]{\small\sffamily\color{gray}Geant4 with Python}
\fancyfoot[C]{\small\sffamily\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\small\sffamily\thepage}\renewcommand{\headrulewidth}{0pt}}
\usepackage{tocloft}
\setlength{\cftsecnumwidth}{2.4em}
\setlength{\cftsubsecnumwidth}{3em}
\renewcommand{\cftpartfont}{\sffamily\bfseries\color{navy}}
\renewcommand{\cftsecfont}{\normalfont}
\setcounter{tocdepth}{2}
\usepackage[hidelinks,bookmarksnumbered,pdfusetitle]{hyperref}
\hypersetup{pdftitle={Geant4 with Python: a developer guide},
  pdfauthor={Luis Antonio Obis Aparicio and Kavya Wadhwa}}
\usepackage{bookmark}
\newcommand{\code}[1]{\texttt{\textcolor{accent}{#1}}}
\setlength{\parskip}{4pt}
\setlength{\parindent}{0pt}
\emergencystretch=4em
\begin{document}
\frontmatter
\begin{titlepage}
\centering
\vspace*{45mm}
{\sffamily\bfseries\fontsize{34}{40}\selectfont\color{navy} Geant4 with Python\par}
\vspace{6mm}
{\sffamily\Large\color{accent} A developer guide to geant4-python-application\par}
\vspace{14mm}
\begin{minipage}{0.75\linewidth}\centering\large
Install the package, build detectors with GDML, run and analyse simulations,
understand how the package works, and contribute to it.
\end{minipage}
\vfill
{\large Luis Antonio Obis Aparicio \quad\textperiodcentered\quad Kavya Wadhwa\par}
\vspace{4mm}
{\small Package 0.2.0 \quad\textperiodcentered\quad Geant4 11.4.3 \quad\textperiodcentered\quad \today\par}
\vspace*{15mm}
\end{titlepage}
\tableofcontents
\chapter*{About this guide}
\markboth{About this guide}{About this guide}
\addcontentsline{toc}{chapter}{About this guide}
"""

SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "<": r"\textless{}",
    ">": r"\textgreater{}",
    "|": r"\textbar{}",
}


def esc(text):
    return "".join(SPECIALS.get(ch, ch) for ch in text)


def esc_code(text):
    """Escape inline code and allow line breaks after separators."""
    out = esc(text)
    for sep in (r"\_", ".", "/", ",", "(", "="):
        out = out.replace(sep, sep + r"\allowbreak{}")
    if len(text) > 14:  # long CamelCase identifiers may break between words
        out = re.sub(r"(?<=[a-z])(?=[A-Z])", r"\\allowbreak{}", out)
    return out


def inline(text):
    """Markdown inline markup to LaTeX. Math ($...$) passes through unchanged."""
    stash = []

    def keep(s):
        stash.append(s)
        return f"\x00{len(stash) - 1}\x01"

    text = re.sub(
        r"`([^`]+)`", lambda m: keep(r"\code{" + esc_code(m.group(1)) + "}"), text
    )
    text = re.sub(r"\$([^$]+)\$", lambda m: keep("$" + m.group(1) + "$"), text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: keep(
            r"\href{"
            + m.group(2).replace("%", r"\%").replace("#", r"\#")
            + "}{"
            + esc(m.group(1))
            + "}"
        ),
        text,
    )
    text = re.sub(
        r"https?://[^\s)]+", lambda m: keep(r"\url{" + m.group(0) + "}"), text
    )
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"\\emph{\1}", text)
    text = (
        text.replace("“", "``")
        .replace("”", "''")
        .replace(' "', " ``")
        .replace('" ', "'' ")
    )
    text = re.sub(r"^\"", "``", text)
    text = re.sub(r"\"([.,;:)])", r"''\1", text)
    while "\x00" in text:  # stashed pieces can contain other stashed pieces
        text = re.sub("\x00(\\d+)\x01", lambda m: stash[int(m.group(1))], text)
    return text


def table(rows):
    rows = [
        [c.strip() for c in re.split(r"(?<!\\)\|", r.strip().strip("|"))] for r in rows
    ]
    rows = [r for r in rows if not all(re.fullmatch(r":?-+:?", c) for c in r)]
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    lengths = [max(len(r[i]) for r in rows) for i in range(ncol)]
    spec = []
    for i, length in enumerate(lengths):
        cells = [r[i] for r in rows[1:] if r[i]]
        if cells and all(c.startswith("`") and c.endswith("`") for c in cells):
            # monospace column: as wide as its longest entry, up to 45% of the line
            spec.append(
                r">{\raggedright\arraybackslash}p{%.3f\linewidth}"
                % min(0.45, 0.0118 * (length - 2) + 0.02)
            )
        elif length <= 12:
            spec.append(
                r">{\raggedright\arraybackslash}p{%.3f\linewidth}"
                % max(0.07, 0.012 * length)
            )
        else:
            spec.append(r">{\raggedright\arraybackslash}X")
    out = [
        r"{\small",
        r"\begin{xltabular}{\linewidth}{" + "".join(spec) + "}",
        r"\toprule",
    ]
    out.append(" & ".join(r"\textbf{" + inline(c) + "}" for c in rows[0]) + r" \\")
    out += [r"\midrule", r"\endhead"]
    for r in rows[1:]:
        out.append(" & ".join(inline(c) for c in r) + r" \\")
    out += [r"\bottomrule", r"\end{xltabular}}", ""]
    return out


def heading(level, text):
    m = re.match(r"^(\d+(?:\.\d+)?)\.?\s+(.*)$", text)
    number, title = (m.group(1), m.group(2)) if m else (None, text)
    title_tex = inline(title)
    if level == 1:
        m = re.match(r"^Part ([IVX]+) - (.*)$", text)
        roman, name = m.groups()
        value = sum({"I": 1, "V": 5, "X": 10}[c] for c in roman)
        value -= 2 * sum(1 for a, b in zip(roman, roman[1:]) if a == "I" and b in "VX")
        front = [r"\mainmatter"] if value == 1 else []
        return front + [
            r"\setcounter{part}{%d}" % (value - 1),
            r"\part{%s}" % inline(name),
            r"\markright{%s}" % inline(name),
        ]
    cmd = "section" if level == 2 else "subsection"
    if number:
        return [
            r"\%s*{\texorpdfstring{%s\quad %s}{%s %s}}"
            % (cmd, number, title_tex, number, esc(title)),
            r"\addcontentsline{toc}{%s}{\protect\numberline{%s}%s}"
            % (cmd, number, title_tex),
        ]
    return [r"\%s*{%s}" % (cmd, title_tex)]


def code_block(lang, lines):
    style = "python" if lang == "python" else "plain"
    body = "\n".join(lines)
    return [r"\begin{lstlisting}[style=%s]" % style, body, r"\end{lstlisting}"]


def convert(md):
    lines = md.splitlines()
    out, para, i = [], [], 0
    list_env = None
    first_h1 = True

    def flush():
        if para:
            out.append(inline(" ".join(para)))
            out.append("")
            para.clear()

    def close_list():
        nonlocal list_env
        if list_env:
            out.append(r"\end{%s}" % list_env)
            out.append("")
            list_env = None

    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith("```"):
            flush()
            indent = len(line) - len(stripped)
            lang = stripped[3:].strip()
            j = i + 1
            while not lines[j].lstrip().startswith("```"):
                j += 1
            block = [l[indent:] for l in lines[i + 1 : j]]
            if indent == 0:
                close_list()
            out += code_block(lang, block)
            i = j + 1
            continue
        if line.startswith("|"):
            flush()
            close_list()
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            out += table(lines[i:j])
            i = j
            continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
        if m:
            flush()
            close_list()
            path = (SOURCE.parent / m.group(2)).resolve()
            out += [
                r"\begin{figure}[H]\centering",
                r"\includegraphics[width=0.86\linewidth]{%s}" % path.as_posix(),
                r"\caption{%s}" % inline(m.group(1)),
                r"\end{figure}",
                "",
            ]
            i += 1
            continue
        m = re.match(r"^(#{1,3}) (.*)", line)
        if m:
            flush()
            close_list()
            level = len(m.group(1))
            if level == 1 and first_h1:  # the document title is on the title page
                first_h1 = False
            else:
                out += heading(level, m.group(2))
            i += 1
            continue
        m = re.match(r"^(- |\d+\. )(.*)", line)
        if m:
            flush()
            env = "itemize" if m.group(1) == "- " else "enumerate"
            if list_env != env:
                close_list()
                out.append(r"\begin{%s}" % env)
                list_env = env
            item = [m.group(2)]
            i += 1
            while (
                i < len(lines)
                and lines[i].startswith("  ")
                and lines[i].strip()
                and not lines[i].lstrip().startswith("```")
            ):
                item.append(lines[i].strip())
                i += 1
            out.append(r"\item " + inline(" ".join(item)))
            continue
        if not line.strip():
            flush()
            # a list continues across blank lines only if the next line is an item or indented code
            k = i + 1
            while k < len(lines) and not lines[k].strip():
                k += 1
            if (
                list_env
                and k < len(lines)
                and not (
                    re.match(r"^(- |\d+\. )", lines[k]) or lines[k].startswith("   ")
                )
            ):
                close_list()
            i += 1
            continue
        if list_env and line.startswith("  "):
            out[-1] += " " + inline(line.strip())
            i += 1
            continue
        close_list()
        para.append(line.strip())
        i += 1
    flush()
    close_list()
    return "\n".join(out)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    tex = PREAMBLE + convert(SOURCE.read_text()) + "\n\\end{document}\n"
    (WORK / "guide.tex").write_text(tex)
    subprocess.run(["tectonic", "--keep-logs", "guide.tex"], cwd=WORK, check=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(WORK / "guide.pdf", OUTPUT)
    print("wrote", OUTPUT)


if __name__ == "__main__":
    main()
