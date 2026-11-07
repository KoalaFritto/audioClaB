#!/usr/bin/env python3
"""Conta i voti dei commenti Instagram per un episodio "decidete voi".

Input: file di testo, una riga per commento, nel formato "utente: testo"
(oppure solo "testo", senza deduplica per utente).

Uso:
    python3 conta_voti.py commenti.txt --opzioni 1 2
    python3 conta_voti.py commenti.txt --opzioni A B C
    python3 conta_voti.py commenti.txt --opzioni 🚪 🪟
"""
import argparse
import re
import sys
from collections import Counter


def trova_opzioni(testo, opzioni):
    """Restituisce l'insieme delle opzioni citate nel testo."""
    trovate = set()
    for op in opzioni:
        if op.isalnum():
            # numero o lettera isolati: "1", "opzione 1", "la 2!" ma non "12" o "ABC"
            if re.search(r"(?<![0-9A-Za-zÀ-ÿ])" + re.escape(op) + r"(?![0-9A-Za-zÀ-ÿ])",
                         testo, re.IGNORECASE):
                trovate.add(op)
        elif op in testo:  # emoji o simboli
            trovate.add(op)
    return trovate


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", help="file con i commenti ('-' per stdin)")
    p.add_argument("--opzioni", nargs="+", default=["1", "2"], help="etichette di voto (default: 1 2)")
    p.add_argument("--tutti", action="store_true", help="conta tutti i commenti, anche più di uno per utente")
    a = p.parse_args()

    righe = (sys.stdin if a.file == "-" else open(a.file, encoding="utf-8")).read().splitlines()

    voti = Counter()
    gia_votato = set()
    ambigui, nulli, doppi = [], 0, 0
    for riga in righe:
        riga = riga.strip()
        if not riga:
            continue
        utente, testo = None, riga
        m = re.match(r"^@?([\w.]{1,30})\s*:\s*(.*)$", riga)
        if m:
            utente, testo = m.group(1).lower(), m.group(2)
        scelte = trova_opzioni(testo, a.opzioni)
        if not scelte:
            nulli += 1
            continue
        if len(scelte) > 1:
            ambigui.append(riga)
            continue
        if utente and not a.tutti:
            if utente in gia_votato:
                doppi += 1
                continue
            gia_votato.add(utente)
        voti[scelte.pop()] += 1

    totale = sum(voti.values())
    print(f"Voti validi: {totale}")
    for op in a.opzioni:
        n = voti.get(op, 0)
        perc = (100 * n / totale) if totale else 0
        print(f"  {op}: {n:>5}  ({perc:5.1f}%)  " + "█" * round(perc / 2))
    print(f"Commenti senza voto: {nulli} · ambigui (più opzioni): {len(ambigui)} · voti doppi scartati: {doppi}")

    if totale:
        massimo = max(voti.values())
        vincitori = [op for op in a.opzioni if voti.get(op, 0) == massimo]
        if len(vincitori) == 1:
            print(f"VINCE: {vincitori[0]}")
        else:
            print("PAREGGIO tra: " + ", ".join(vincitori) + " → applica la regola di pareggio del commento fissato")


if __name__ == "__main__":
    main()
