# -*- coding: utf-8 -*-
"""
Recopie la page de vente à la RACINE du kit, sous le nom `index.html`.

POURQUOI UNE COPIE À LA RACINE
-------------------------------
Un dossier de campagne se transmet tel quel — clé USB, archive ZIP, dépôt
partagé. Celui qui le reçoit ouvre le dossier et cherche par quoi commencer.
Un `index.html` posé à la racine est la réponse universelle : c'est le nom
que tout navigateur et tout hébergeur ouvrent par défaut. Mis en ligne, le
dossier devient un site sans aucune configuration.

POURQUOI ENGENDRER PLUTÔT QUE DUPLIQUER À LA MAIN
--------------------------------------------------
Deux copies d'une même page divergent toujours : on corrige un prix dans
l'une, on oublie l'autre, et deux versions du même argumentaire circulent
avec des tarifs différents. Ici la copie est REFABRIQUÉE à chaque
exécution — la seule source reste `02_Page_de_vente/index.html`.

La seule transformation appliquée est la REMONTÉE D'UN NIVEAU des chemins
relatifs : la page d'origine vit dans un sous-dossier et pointe vers
`../assets/…` ; à la racine, ce doit être `assets/…`. Sans cela, la copie
s'ouvre sans aucune image, sans feuille de style et sans compteur — panne
d'autant plus vicieuse que la page reste « à peu près » lisible.

    python outils/copier_page_vente.py

À RELANCER après toute modification de la page de vente.
"""

import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(RACINE, "02_Page_de_vente", "index.html")
COPIE = os.path.join(RACINE, "index.html")

# Bandeau inséré en tête du fichier produit. Il tient en deux lignes et sert
# une seule chose : qu'un collègue qui ouvre ce fichier dans un éditeur
# comprenne en trois secondes qu'il ne doit PAS le modifier.
BANDEAU = """<!--
  ============================================================================
  FICHIER ENGENDRÉ — NE PAS MODIFIER À LA MAIN.

  Copie de 02_Page_de_vente/index.html, ramenée à la racine du kit pour
  servir de point d'entrée (index.html s'ouvre par défaut dans un navigateur
  comme sur un hébergement).

  Toute correction se fait dans 02_Page_de_vente/index.html, puis :
      python outils/copier_page_vente.py

  Seuls les chemins relatifs ont été remontés d'un niveau (../assets -> assets).
  ============================================================================
-->
"""


def main():
    if not os.path.exists(SOURCE):
        raise SystemExit(f"Source introuvable : {SOURCE}")

    html = open(SOURCE, encoding="utf-8").read()

    # On ne remplace que dans les attributs href/src : un « ../ » qui
    # apparaîtrait dans du texte rédigé ou un commentaire ne doit pas bouger.
    html, n = re.subn(r'((?:href|src)=")\.\./', r"\1", html)

    # Garde-fou : s'il reste un « ../ » dans un attribut, la copie serait
    # cassée en silence. Mieux vaut s'arrêter que livrer une page muette.
    restants = re.findall(r'(?:href|src)="\.\./[^"]*', html)
    if restants:
        raise SystemExit("Chemins non traités, copie abandonnée :\n  "
                         + "\n  ".join(restants))

    # Le <title> gagne le nom du cabinet : c'est le libellé de l'onglet du
    # navigateur et celui de l'aperçu quand le lien est collé dans WhatsApp.
    html = html.replace(
        "<title>Conduire une enquête statistique de A à Z",
        "<title>OUBANGUI STAT CONSULTING — Conduire une enquête statistique de A à Z",
        1)

    html = BANDEAU + html
    open(COPIE, "w", encoding="utf-8").write(html)

    poids = os.path.getsize(COPIE) / 1024
    print(f"  ok  index.html a la racine  ({poids:.0f} Ko, {n} chemins remontes)")
    print("      source : 02_Page_de_vente/index.html")


if __name__ == "__main__":
    main()
