# -*- coding: utf-8 -*-
"""
Convertit en PDF les livrables destinés à l'impression.

POURQUOI EDGE SANS INTERFACE PLUTÔT QUE QUARTO OU LATEX
--------------------------------------------------------
Les supports de cette campagne sont d'abord des OBJETS GRAPHIQUES : photos
en fond perdu, dégradés, ombres portées, grilles à colonnes inégales. LaTeX
les rend mal et Quarto n'est pas installé sur le poste. Le moteur de rendu
de Chromium, lui, produit exactement ce que montre le navigateur — donc ce
qui a été validé à l'écran — et respecte `@page { size: A3 }`.

Trois options ne sont PAS facultatives :
  --headless=new      l'ancien mode sans interface ignore certains dégradés ;
  --no-pdf-header-footer  sans elle, Chromium imprime l'URL du fichier et la
                      date en marge, ce qui ruine une affiche ;
  --print-to-pdf-no-header  même effet, nom retenu selon les versions.

PIÈGE CONNU, à ne pas réintroduire : ne JAMAIS ajouter
`--virtual-time-budget`. Sur une page qui charge des images locales, il rend
la main avant la fin du décodage et produit des pages BLANCHES par
intermittence — panne non déterministe, très coûteuse à diagnostiquer.
On laisse plutôt Chromium finir de lui-même.

    python outils/exporter_pdf.py            # tout
    python outils/exporter_pdf.py affiche    # un seul, par mot-clé
"""

import os
import subprocess
import sys
import time
import urllib.parse

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Edge est présent d'origine sur le poste ; Chrome sert de repli si le
# cabinet change de machine. On teste l'existence plutôt que de coder un
# chemin en dur, sinon le script casse au premier poste différent.
NAVIGATEURS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

# Les documents à convertir : (source HTML, PDF produit).
# Les pages purement écran — page de vente, formulaire d'inscription — n'y
# figurent pas : les figer en PDF perdrait leur compteur et leurs liens.
DOCUMENTS = [
    ("01_Affiche/Affiche_A3.html", "01_Affiche/Affiche_A3.pdf"),
    ("03_Brochure/Brochure.html", "03_Brochure/Brochure_Formation_2026.pdf"),
    ("05_Video/Storyboard.html", "05_Video/Storyboard.pdf"),
    ("08_Courriers/Lettre_universite_de_bangui.html", "08_Courriers/Lettre_universite_de_bangui.pdf"),
    ("08_Courriers/Lettre_etablissements_professionnels.html", "08_Courriers/Lettre_etablissements_professionnels.pdf"),
    ("08_Courriers/Lettre_administrations_publiques.html", "08_Courriers/Lettre_administrations_publiques.pdf"),
]


def navigateur():
    for chemin in NAVIGATEURS:
        if os.path.exists(chemin):
            return chemin
    raise SystemExit("Aucun navigateur Chromium trouvé — voir la liste NAVIGATEURS.")


def convertir(exe, source, cible):
    src = os.path.join(RACINE, source)
    dst = os.path.join(RACINE, cible)
    if not os.path.exists(src):
        print(f"  -- {source} : absent, ignore")
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    # Le chemin doit être encodé : « Formations 2026 » contient une espace,
    # que Chromium tronque silencieusement dans une URL file:// brute.
    url = "file:///" + urllib.parse.quote(src.replace("\\", "/"), safe="/:")
    subprocess.run([
        exe, "--headless=new", "--disable-gpu",
        "--no-pdf-header-footer",
        "--allow-file-access-from-files",
        f"--print-to-pdf={dst}",
        url,
    ], check=True, capture_output=True)
    taille = os.path.getsize(dst) / 1024
    print(f"  ok  {cible}  ({taille:.0f} Ko)")
    return True


def main():
    exe = navigateur()
    filtre = sys.argv[1].lower() if len(sys.argv) > 1 else None
    faits = 0
    for source, cible in DOCUMENTS:
        if filtre and filtre not in source.lower():
            continue
        if convertir(exe, source, cible):
            faits += 1
        # Une pause d'un dixième de seconde entre deux lancements : sans
        # elle, deux instances d'Edge se disputent le même profil temporaire
        # et l'une des deux sort un PDF vide.
        time.sleep(0.4)
    print(f"\n{faits} PDF produits.")


if __name__ == "__main__":
    main()
