# -*- coding: utf-8 -*-
"""
Engendre les fichiers SVG de `assets/logos/` : la marque du cabinet et les
pictogrammes des neuf logiciels enseignés.

POURQUOI UN SCRIPT ET NON DES SVG ÉCRITS À LA MAIN
--------------------------------------------------
Les neuf pictogrammes partagent la MÊME géométrie (tuile arrondie de 96 px,
même rayon, même biseau, même ombre interne). Écrits un par un, ils
divergent : un rayon à 20 au lieu de 22, un dégradé oublié, et la planche
de logiciels de la brochure cesse de faire série. Ici la géométrie est
écrite une fois dans `tuile()` et seuls le fond et le glyphe changent.

    python outils/engendrer_logos.py

MENTION LÉGALE, à conserver dans tous les supports
--------------------------------------------------
Ces pictogrammes sont des REPRÉSENTATIONS maison, dessinées dans la couleur
dominante de chaque logiciel pour que la planche soit reconnaissable ; ce ne
sont pas les logos officiels et ils ne sont pas redistribués comme tels. Les
marques citées appartiennent à leurs propriétaires respectifs et leur
mention désigne les logiciels ENSEIGNÉS — elle n'implique aucun
partenariat, parrainage ni affiliation. La phrase correspondante figure au
pied de la brochure et de la page de vente : ne pas la retirer.
"""

import os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "assets", "logos")

# Couleurs de la charte, recopiées ici car un SVG ne lit pas osc.css.
# Toute retouche de la charte doit être reportée dans ces trois constantes.
MARINE = "#0B2545"
BLEU_ACTION = "#00689D"
BLEU_SIGNAL = "#009EDB"
OR = "#F4B942"
TURQUOISE = "#007C83"


def tuile(fond, contenu, degrade=None, id_suffixe=""):
    """Rend une tuile d'application de 96×96 avec son relief.

    Le relief est fait de deux choses, jamais d'une bordure : un dégradé
    très léger du haut vers le bas (la lumière vient d'en haut) et un
    liseré interne clair sur l'arête supérieure. C'est la traduction en SVG
    de la règle `--biseau` de osc.css.
    """
    fill = f"url(#g{id_suffixe})" if degrade else fond
    defs = ""
    if degrade:
        defs = (f'<linearGradient id="g{id_suffixe}" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{degrade[0]}"/>'
                f'<stop offset="1" stop-color="{degrade[1]}"/></linearGradient>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96" role="img">
<defs>{defs}
<linearGradient id="biseau{id_suffixe}" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#ffffff" stop-opacity=".28"/>
<stop offset=".5" stop-color="#ffffff" stop-opacity="0"/>
<stop offset="1" stop-color="#000000" stop-opacity=".14"/></linearGradient>
</defs>
<rect x="2" y="2" width="92" height="92" rx="22" fill="{fill}"/>
{contenu}
<rect x="2" y="2" width="92" height="92" rx="22" fill="url(#biseau{id_suffixe})"/>
</svg>'''


def mot(texte, taille=30, y=59, couleur="#ffffff", poids=700, espace="-.02em"):
    """Glyphe textuel centré. Les pictogrammes qui portent des initiales
    (SPSS, ODK, Stata) n'ont pas de forme propre reconnaissable : la lettre
    EST le signe, autant la traiter avec soin."""
    return (f'<text x="48" y="{y}" text-anchor="middle" fill="{couleur}" '
            f'font-family="Bahnschrift, Segoe UI Semibold, Arial, sans-serif" '
            f'font-size="{taille}" font-weight="{poids}" letter-spacing="{espace}">{texte}</text>')


# ---------------------------------------------------------------------------
# Les neuf logiciels. Chaque entrée porte : fichier, couleur dominante,
# dégradé de tuile, glyphe.
# ---------------------------------------------------------------------------
LOGICIELS = {}

# R — l'anneau gris et le R bleu sont le signe le plus reconnaissable du lot :
# on le reproduit fidèlement en géométrie, sur fond blanc comme l'original.
LOGICIELS["r"] = tuile(
    "#FFFFFF",
    '<ellipse cx="48" cy="46" rx="34" ry="24" fill="none" stroke="#9C9C9C" stroke-width="9"/>'
    '<ellipse cx="48" cy="46" rx="17" ry="11" fill="#FFFFFF"/>'
    '<path d="M40 30h15c8 0 13 4 13 10 0 5-3 8-8 9l11 19H60L51 51h-4v17H40z" fill="#276DC3"/>',
    id_suffixe="r")

# QGIS — le vert de l'application, un Q dont la queue file vers le bas droit.
LOGICIELS["qgis"] = tuile(
    "#589632",
    '<circle cx="46" cy="45" r="21" fill="none" stroke="#ffffff" stroke-width="8"/>'
    '<path d="M58 57l12 13" stroke="#ffffff" stroke-width="8" stroke-linecap="round"/>'
    '<circle cx="46" cy="45" r="6" fill="#ffffff"/>',
    degrade=("#6BAF3E", "#43761F"), id_suffixe="q")

# KoboToolbox — la tuile corail de l'écosystème Kobo, avec la grille de
# points d'un formulaire : c'est l'idée de « questionnaire » qu'on montre.
LOGICIELS["kobo"] = tuile(
    "#E35B4C",
    ''.join(f'<circle cx="{34 + c * 14}" cy="{32 + l * 14}" r="4" fill="#ffffff" '
            f'opacity="{0.45 if (c + l) % 2 else 1}"/>'
            for l in range(3) for c in range(3)) +
    '<path d="M26 70h44" stroke="#ffffff" stroke-width="5" stroke-linecap="round" opacity=".85"/>',
    degrade=("#EC6E5B", "#C9412F"), id_suffixe="k")

# ODK — le teal d'Open Data Kit et ses trois initiales.
LOGICIELS["odk"] = tuile(
    "#12A594",
    '<path d="M20 66l11-30 11 30" fill="none" stroke="#ffffff" stroke-width="0"/>' +
    mot("ODK", taille=25, y=57, espace=".01em"),
    degrade=("#19BCA8", "#0B8578"), id_suffixe="o")

# Google Forms — le violet et la feuille de formulaire à coche.
LOGICIELS["googleforms"] = tuile(
    "#7248B9",
    '<path d="M32 20h22l14 14v42a4 4 0 0 1-4 4H32a4 4 0 0 1-4-4V24a4 4 0 0 1 4-4z" fill="#ffffff"/>'
    '<path d="M54 20l14 14H54z" fill="#D7C6F0"/>'
    '<path d="M38 47h20M38 57h20M38 67h13" stroke="#7248B9" stroke-width="4" stroke-linecap="round"/>'
    '<circle cx="34" cy="47" r="3" fill="#7248B9"/><circle cx="34" cy="57" r="3" fill="#7248B9"/>'
    '<circle cx="34" cy="67" r="3" fill="#7248B9"/>',
    degrade=("#8055CC", "#5F3AA0"), id_suffixe="gf")

# Excel — le vert Office, la feuille et le X.
LOGICIELS["excel"] = tuile(
    "#217346",
    '<rect x="42" y="22" width="34" height="52" rx="3" fill="#ffffff"/>'
    '<path d="M42 38h34M42 54h34M59 22v52" stroke="#217346" stroke-width="3" opacity=".35"/>'
    '<rect x="18" y="28" width="34" height="40" rx="5" fill="#0F5132"/>' +
    '<text x="35" y="56" text-anchor="middle" fill="#ffffff" font-family="Bahnschrift, Arial, sans-serif" '
    'font-size="26" font-weight="700">X</text>',
    degrade=("#2A8A55", "#186139"), id_suffixe="x")

# IBM SPSS — le bleu IBM et les initiales.
LOGICIELS["spss"] = tuile(
    "#0F62FE",
    mot("SPSS", taille=21, y=56, espace=".02em"),
    degrade=("#2C77FF", "#0745C2"), id_suffixe="s")

# Stata — le bleu marine de l'éditeur et son nom en capitales.
LOGICIELS["stata"] = tuile(
    "#1A476F",
    mot("Stata", taille=23, y=57, espace="0"),
    degrade=("#255C8C", "#123452"), id_suffixe="st")

# Power BI — le jaune et les barres montantes du tableau de bord.
LOGICIELS["powerbi"] = tuile(
    "#F2C811",
    '<rect x="24" y="52" width="13" height="24" rx="3" fill="#4A3000"/>'
    '<rect x="42" y="38" width="13" height="38" rx="3" fill="#4A3000"/>'
    '<rect x="60" y="24" width="13" height="52" rx="3" fill="#4A3000"/>',
    degrade=("#FAD644", "#DEAF00"), id_suffixe="pb")


# ---------------------------------------------------------------------------
# La marque du cabinet
# ---------------------------------------------------------------------------
def marque(couleur_texte, couleur_sous_titre, couleur_points):
    """Bloc-marque horizontal : symbole + raison sociale.

    LE SYMBOLE. Un anneau ouvert traversé par une courbe qui remonte —
    l'anneau est le cycle du diagnostic (mesurer, analyser, décider,
    remesurer), la courbe est l'Oubangui et, en même temps, la série
    statistique qui progresse. Les quatre points posés dessus sont les
    relevés : c'est une COURBE DE DONNÉES avant d'être un fleuve, ce qui est
    exactement l'ordre de lecture voulu. Aucun emblème national ni
    international n'y figure — même règle que pour l'application ODC.

    `couleur_points` est un paramètre et non une constante : les relevés en
    marine disparaissent sur le fond marine du pied de page. Une seule
    couleur pour les deux versions ferait perdre trois points sur quatre.
    """
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 96" width="460" height="96" role="img">
<title>Oubangui Stat Consulting</title>
<defs>
<linearGradient id="anneau" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{BLEU_SIGNAL}"/><stop offset="1" stop-color="{BLEU_ACTION}"/>
</linearGradient>
</defs>
<!-- L'anneau est OUVERT en bas à droite : un cercle fermé dirait « boucle
     bouclée », or le cabinet vend une remesure annuelle. -->
<path d="M48 12a36 36 0 1 1-25 62" fill="none" stroke="url(#anneau)" stroke-width="9" stroke-linecap="round"/>
<!-- La série qui monte, tracée d'un seul geste. -->
<path d="M26 62l13-14 12 8 21-26" fill="none" stroke="{OR}" stroke-width="7"
      stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="26" cy="62" r="5.5" fill="{couleur_points}"/>
<circle cx="39" cy="48" r="5.5" fill="{couleur_points}"/>
<circle cx="51" cy="56" r="5.5" fill="{couleur_points}"/>
<circle cx="72" cy="30" r="6.5" fill="{TURQUOISE}"/>
<text x="106" y="46" fill="{couleur_texte}" font-family="Bahnschrift, Segoe UI Semibold, Arial, sans-serif"
      font-size="30" font-weight="700" letter-spacing=".01em">OUBANGUI STAT</text>
<text x="107" y="70" fill="{couleur_sous_titre}" font-family="Segoe UI, Arial, sans-serif"
      font-size="15" letter-spacing=".38em">CONSULTING</text>
</svg>'''


def main():
    os.makedirs(SORTIE, exist_ok=True)
    fichiers = dict(LOGICIELS)
    # Deux versions de la marque : sur fond clair et sur fond marine. Pas de
    # « logo noir et blanc » — le cabinet n'imprime rien en niveaux de gris.
    fichiers["logo-osc"] = marque(MARINE, BLEU_ACTION, MARINE)
    fichiers["logo-osc-blanc"] = marque("#FFFFFF", "#8FD3F0", "#FFFFFF")
    for nom, contenu in fichiers.items():
        with open(os.path.join(SORTIE, nom + ".svg"), "w", encoding="utf-8") as f:
            f.write(contenu)
    print(f"{len(fichiers)} fichiers SVG engendrés dans {SORTIE}")


if __name__ == "__main__":
    main()
