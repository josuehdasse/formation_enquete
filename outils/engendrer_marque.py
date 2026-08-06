# -*- coding: utf-8 -*-
"""
Prépare les déclinaisons du VRAI logo du cabinet et les blocs-marque de la
campagne (`assets/logos/`).

SOURCE OFFICIELLE : C:\\Users\\josue\\Pictures\\logo_osc.png — sceau circulaire
bleu portant « OUBANGUI STAT CONSULTING · CABINET D'ÉTUDES STATISTIQUES ET DE
CONSEIL » autour d'un histogramme fléché. Ce fichier n'est jamais modifié :
on le lit, on en dérive.

POURQUOI DÉRIVER PLUTÔT QUE POSER LE PNG TEL QUEL
--------------------------------------------------
1. Le sceau est bleu foncé. Posé sur le bandeau marine de l'affiche ou de la
   brochure, il devient une tache illisible. Il faut donc une version blanche,
   obtenue en ne gardant que la couche alpha — pas en « éclaircissant », ce
   qui laisserait un halo gris autour des lettres du pourtour.
2. Le sceau seul ne dit pas le nom du cabinet à moins de vingt centimètres :
   les lettres du pourtour font moins d'un millimètre à l'impression. Le
   bloc-marque associe donc le sceau à un logotype composé, exactement comme
   le fait le Catalogue des formations 2026-2027 du cabinet.
3. Le PNG source mesure 266 px. Recadré au plus juste (le fichier porte
   quinze pixels de marge transparente), il en reste 236 — assez pour un
   tirage à 300 dpi jusqu'à 20 mm, ce qui couvre tous les emplois de la
   campagne. Ne pas l'agrandir au-delà.

    python outils/engendrer_marque.py
"""

import base64
import io
import os

from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "assets", "logos")
SOURCE = r"C:\Users\josue\Pictures\logo_osc.png"

# Couleurs relevées AU PIXEL sur le logo et sur la couverture du catalogue
# 2026-2027 : ce sont les valeurs de la maison, pas des approximations.
BLEU_SCEAU = "#175A85"     # le bleu du sceau lui-même
MARINE = "#0B2545"         # marine de la charte de campagne (osc.css)
BLEU_ACTION = "#00689D"


def sceau_png():
    """Recadre le sceau au plus juste et renvoie ses octets PNG.

    `getbbox()` sur une image RVBA borne la zone NON TRANSPARENTE : c'est ce
    qui supprime la marge morte du fichier d'origine. Sans ce recadrage, le
    sceau paraît trop petit dans chaque bloc où on le pose, et on est tenté
    de compenser en l'agrandissant — donc en le pixellisant.
    """
    im = Image.open(SOURCE).convert("RGBA")
    im = im.crop(im.getbbox())
    tampon = io.BytesIO()
    im.save(tampon, "PNG", optimize=True)
    return tampon.getvalue(), im.size


def sceau_blanc_png():
    """Version blanche du sceau, pour les fonds marine.

    PIÈGE RENCONTRÉ, à ne pas refaire : la première version se contentait de
    peindre en blanc tous les pixels en CONSERVANT leur alpha. Or le sceau
    n'est pas un tracé sur fond transparent — son disque intérieur est un
    aplat BLANC OPAQUE. Repeindre en blanc à alpha constant donnait donc, sur
    fond marine, une pastille blanche pleine : le logo avait disparu.

    La bonne transformation est une INVERSION EN NÉGATIF : l'alpha de sortie
    se déduit de la densité d'encre (255 − luminance), si bien que le bleu du
    tracé devient blanc opaque et que le fond clair devient transparent. Le
    dégradé d'anticrénelage est conservé, donc les lettres minuscules du
    pourtour restent lisibles.
    """
    im = Image.open(SOURCE).convert("RGBA")
    im = im.crop(im.getbbox())
    # Luminance perçue puis inversion : ImageOps.invert refuse le mode RVBA,
    # d'où le passage explicite par la couche « L ».
    from PIL import ImageChops, ImageOps
    encre = ImageOps.invert(im.convert("L"))
    # On multiplie par l'alpha d'origine pour que la marge extérieure, qui
    # est transparente ET noire une fois convertie en L, ne redevienne pas
    # un carré blanc opaque.
    alpha = ImageChops.multiply(encre, im.getchannel("A"))
    blanc = Image.new("RGBA", im.size, (255, 255, 255, 255))
    blanc.putalpha(alpha)
    tampon = io.BytesIO()
    blanc.save(tampon, "PNG", optimize=True)
    return tampon.getvalue(), im.size


def en_data_uri(octets):
    """Encode le PNG dans le SVG lui-même.

    Un <image href="...png"> lierait un fichier voisin : le SVG cesserait de
    fonctionner dès qu'on le déplace, et surtout Chromium REFUSE de charger
    une image liée depuis un SVG chargé en <img> (règle d'origine). Le data
    URI règle les deux d'un coup, au prix de quelques kilo-octets.
    """
    return "data:image/png;base64," + base64.b64encode(octets).decode("ascii")


def bloc_marque(uri, couleur_nom, couleur_ligne, largeur=520):
    """Bloc-marque horizontal : sceau + raison sociale + signature.

    La signature reprend mot pour mot celle du catalogue du cabinet
    (« Cabinet d'études statistiques et de conseil »), pour que les supports
    de formation et le catalogue se lisent comme une seule maison.
    """
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largeur} 96" width="{largeur}" height="96" role="img">
<title>Oubangui Stat Consulting</title>
<image href="{uri}" x="0" y="4" width="88" height="88"/>
<text x="106" y="45" fill="{couleur_nom}" font-family="Bahnschrift, Segoe UI Semibold, Arial, sans-serif"
      font-size="29" font-weight="700" letter-spacing=".005em">OUBANGUI STAT CONSULTING</text>
<text x="107" y="70" fill="{couleur_ligne}" font-family="Segoe UI, Arial, sans-serif"
      font-size="14.5" letter-spacing=".05em">Cabinet d’études statistiques et de conseil · Bangui, RCA</text>
</svg>'''


def sceau_seul(uri):
    """Sceau isolé, pour les emplois où le nom est déjà écrit à côté
    (en-têtes de lettres, filigranes, coin de vignette de réseau social)."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96" role="img">
<title>Oubangui Stat Consulting</title>
<image href="{uri}" x="0" y="0" width="96" height="96"/>
</svg>'''


def main():
    os.makedirs(SORTIE, exist_ok=True)

    bleu, taille = sceau_png()
    blanc, _ = sceau_blanc_png()
    uri_bleu, uri_blanc = en_data_uri(bleu), en_data_uri(blanc)

    # Les PNG bruts servent aux supports qui n'acceptent pas le SVG
    # (publication Facebook engendrée par Pillow, pièce jointe de courriel).
    with open(os.path.join(SORTIE, "sceau-osc.png"), "wb") as f:
        f.write(bleu)
    with open(os.path.join(SORTIE, "sceau-osc-blanc.png"), "wb") as f:
        f.write(blanc)

    fichiers = {
        "logo-osc": bloc_marque(uri_bleu, MARINE, BLEU_ACTION),
        "logo-osc-blanc": bloc_marque(uri_blanc, "#FFFFFF", "#8FD3F0"),
        "sceau-osc": sceau_seul(uri_bleu),
        "sceau-osc-blanc": sceau_seul(uri_blanc),
    }
    for nom, contenu in fichiers.items():
        with open(os.path.join(SORTIE, nom + ".svg"), "w", encoding="utf-8") as f:
            f.write(contenu)

    print(f"Sceau source recadré : {taille[0]}×{taille[1]} px")
    print(f"{len(fichiers)} SVG + 2 PNG engendrés dans {SORTIE}")


if __name__ == "__main__":
    main()
