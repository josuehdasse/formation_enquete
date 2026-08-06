# -*- coding: utf-8 -*-
"""
Chaîne de traitement photographique de la campagne « Formations 2026 ».

POURQUOI CE SCRIPT PLUTÔT QU'UNE RETOUCHE MANUELLE
--------------------------------------------------
Les 30 photographies sources viennent d'un même atelier, mais de trois
appareils et de conditions d'éclairage très différentes (salle informatique
au néon, projection dans le noir, plein soleil de la latérite). Utilisées
telles quelles côte à côte dans une brochure, elles ne font pas famille :
l'affiche paraît être un collage. L'étalonnage ci-dessous les ramène toutes
au MÊME rendu — ombres bleu marine, hautes lumières légèrement chaudes,
micro-contraste appuyé — qui est le vocabulaire visuel des rapports de
données. C'est cet accord, pas un filtre spectaculaire, qui donne le fini
professionnel demandé.

Les fichiers engendrés vivent dans `assets/img/` et NE SONT PAS à retoucher
à la main : on modifie la table SELECTION puis on relance le script.

    python outils/traiter_images.py

DÉCISION DE CADRAGE À NE PAS DÉFAIRE
------------------------------------
Les photographies de groupe qui montrent la banderole de l'atelier d'origine
(logos d'une organisation internationale) et les gilets siglés sont ÉCARTÉES
ou recadrées pour les exclure. Faire figurer l'emblème d'un tiers sur un
support commercial laisserait entendre un partenariat qui n'existe pas —
c'est la même règle que celle appliquée à l'application ODC.
"""

import os
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

# Les photographies de la remise des attestations sont au format HEIC (photos
# de téléphone Samsung). Pillow ne le lit pas nativement : l'extension
# pillow-heif enregistre le décodeur. Sans elle, la moitié du fonds
# photographique du cabinet est inexploitable.
#     python -m pip install pillow-heif
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:                      # pragma: no cover
    print("ATTENTION : pillow-heif absent, les fichiers .heic seront ignorés.")

# Répertoires des photographies d'origine, laissés intacts : le script ne
# fait que lire ici, jamais écrire.
SOURCE = r"C:\Users\josue\Pictures\QGIS"
# Remise des attestations de la PREMIÈRE ÉDITION (janvier et avril 2026).
SOURCE_DIPLOMES = r"C:\Users\josue\Pictures\Diplomes"

# Sortie relative à la racine de la campagne (le script est dans outils/).
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "assets", "img")

# ---------------------------------------------------------------------------
# 1. Étalonnage — les constantes de la charte
# ---------------------------------------------------------------------------

# Teinte poussée dans les ombres : c'est le marine de la charte OSC. On ne
# l'applique pas en aplat mais comme un décalage progressif, d'autant plus
# fort que le pixel est sombre — les noirs des salles mal éclairées cessent
# d'être « sales » et deviennent une couleur assumée.
OMBRE = (10, 28, 56)

# Teinte des hautes lumières : un blanc très légèrement ambré. Sans elle, le
# marine des ombres fait virer toute l'image au bleu et les peaux deviennent
# cadavériques — le split-toning n'a de sens que par paires.
LUMIERE = (255, 246, 232)

# Intensité du virage, en fraction du canal. 0,16 est le maximum au-delà
# duquel les carnations des participants perdent leur naturel (essayé à 0,25 :
# rejeté, les visages tiraient sur le gris-bleu).
FORCE_OMBRE = 0.155
FORCE_LUMIERE = 0.085

# Contraste en S : relève les hautes lumières et creuse les basses sans
# toucher aux tons moyens, là où vivent les visages.
CONTRASTE_S = 0.20

# Saturation : +10 % seulement. Les pagnes centrafricains sont déjà très
# saturés ; les pousser davantage fait « carte postale » et non « rapport ».
SATURATION = 1.10

# Vignetage : assombrissement des bords, en fraction de luminosité perdue au
# coin. Il ne décore pas — il ramène l'œil au centre de l'action quand la
# photo est utilisée en fond derrière du texte.
VIGNETAGE = 0.28

# Interrupteur du floutage des noms sur les attestations. Voir
# brouiller_zones() pour la raison. Ne passer à False que lorsque le cabinet
# détient l'autorisation écrite de chaque lauréat photographié.
FLOUTER_NOMS = True


def lut_etalonnage():
    """Construit les trois tables de correspondance (une par canal) qui
    portent d'un seul coup le contraste en S et le split-toning.

    Une LUT plutôt qu'une suite d'opérations d'image : un seul passage sur
    les pixels, résultat strictement reproductible, et surtout aucun
    arrondi intermédiaire — sur des JPEG de 8000 px, enchaîner quatre
    filtres laisse des marches visibles dans les dégradés de ciel.
    """
    tables = []
    for canal in range(3):
        table = []
        for i in range(256):
            v = i / 255.0
            # Courbe en S : smoothstep mélangé à l'identité. Le paramètre
            # CONTRASTE_S dose le mélange, ce qui garde la courbe monotone
            # (donc sans postérisation) quelle que soit sa valeur.
            s = v * v * (3 - 2 * v)
            v = v + (s - v) * CONTRASTE_S
            # Split-toning : le poids de l'ombre décroît avec la luminosité,
            # celui de la lumière croît. Les tons moyens ne reçoivent presque
            # rien, ce qui est exactement le but.
            poids_ombre = (1 - v) ** 2
            poids_lum = v ** 2
            v = v + FORCE_OMBRE * poids_ombre * (OMBRE[canal] / 255.0 - v)
            v = v + FORCE_LUMIERE * poids_lum * (LUMIERE[canal] / 255.0 - v)
            table.append(max(0, min(255, int(round(v * 255)))))
        tables.append(table)
    return tables[0] + tables[1] + tables[2]


LUT = lut_etalonnage()


def masque_vignette(taille):
    """Masque de vignetage, dessiné une fois par dimension puis réutilisé.

    Fabriqué en basse définition (128 px) puis agrandi : un dégradé radial
    n'a aucun détail fin, le calculer à pleine taille coûterait des secondes
    pour un résultat identique après flou.
    """
    petit = Image.new("L", (128, 128), 0)
    dessin = ImageDraw.Draw(petit)
    # L'ellipse déborde volontairement du cadre : sans ce débord, le
    # vignetage attaque dès le bord de l'image et se voit.
    dessin.ellipse((-26, -26, 154, 154), fill=255)
    petit = petit.filter(ImageFilter.GaussianBlur(28))
    return petit.resize(taille, Image.LANCZOS)


def etalonner(im):
    """Applique la totalité du rendu maison à une image RVB déjà recadrée."""
    im = im.convert("RGB")
    # 1. LUT (contraste + virage) — voir lut_etalonnage().
    im = im.point(LUT)
    # 2. Saturation, APRÈS la LUT : appliquée avant, le virage des ombres la
    #    reprendrait en partie et le réglage deviendrait imprévisible.
    im = ImageEnhance.Color(im).enhance(SATURATION)
    # 3. Micro-contraste. Rayon large et taux modéré = « clarté » (le relief
    #    des visages et des écrans ressort) et non « accentuation » (qui
    #    ferait apparaître le bruit des photos prises dans le noir).
    im = im.filter(ImageFilter.UnsharpMask(radius=2.4, percent=62, threshold=3))
    # 4. Vignetage par multiplication du masque.
    masque = masque_vignette(im.size)
    noir = Image.new("RGB", im.size, (4, 12, 26))
    im = Image.composite(im, Image.blend(im, noir, VIGNETAGE), masque)
    return im


def duotone(im):
    """Variante bichrome marine → bleu signal, pour les fonds portant du texte.

    Une photographie couleur derrière un titre le rend illisible quel que
    soit le voile appliqué : trop de valeurs différentes sous les lettres.
    La réduire à une seule rampe de couleur règle le problème à la source et
    donne au passage la signature graphique de la campagne.
    """
    gris = ImageOps.grayscale(im)
    # Rampe en trois points : marine profond → bleu ONU → écume très claire.
    # Le point intermédiaire est ce qui empêche le résultat de ressembler à
    # un simple « bleu délavé ».
    rampe = []
    jalons = [(0.0, (8, 26, 48)), (0.55, (0, 104, 157)), (1.0, (196, 227, 242))]
    for i in range(256):
        v = i / 255.0
        for k in range(len(jalons) - 1):
            a, b = jalons[k], jalons[k + 1]
            if a[0] <= v <= b[0]:
                t = (v - a[0]) / (b[0] - a[0])
                rampe.append(tuple(int(a[1][c] + (b[1][c] - a[1][c]) * t) for c in range(3)))
                break
    plat = []
    for c in range(3):
        plat += [couleur[c] for couleur in rampe]
    return gris.convert("RGB").point(plat)


def brouiller_zones(im, zones):
    """Rend illisibles les zones de texte nominatif d'une photographie.

    POURQUOI C'EST OBLIGATOIRE ICI. Les attestations de la première édition
    portent, en toutes lettres et parfaitement lisibles, le NOM ET LES
    PRÉNOMS de chaque lauréat. Ces photographies partent sur une affiche
    publique, une page web et des réseaux sociaux : diffuser l'identité de
    personnes privées dans une campagne commerciale suppose leur accord
    écrit, un par un. Tant que cet accord n'est pas réuni, on floute.

    Ce qui est flouté : la ligne du nom et le corps de texte.
    Ce qui reste NET, et doit le rester : le sceau du cabinet, le grand « R »
    en filigrane, la signature et la forme générale du document. C'est cela
    qui dit « attestation remise » — le nom n'y contribue en rien.

    `zones` : liste de (x1, y1, x2, y2) en FRACTIONS de l'image, relevées à
    la grille sur chaque cliché. Le flou est appliqué AVANT recadrage et
    redimensionnement, donc les coordonnées se lisent sur l'original.

    Si le cabinet obtient les autorisations, passer FLOUTER_NOMS à False.
    """
    if not zones or not FLOUTER_NOMS:
        return im
    l, h = im.size
    for x1, y1, x2, y2 in zones:
        boite = (int(x1 * l), int(y1 * h), int(x2 * l), int(y2 * h))
        morceau = im.crop(boite)
        largeur = boite[2] - boite[0]
        # Rayon proportionnel à la largeur de la zone : un rayon fixe laisse
        # le texte devinable sur un cliché en 4000 px et fait de la bouillie
        # sur un cliché en 1200 px.
        rayon = max(6, largeur // 22)
        flou = morceau.filter(ImageFilter.GaussianBlur(rayon))

        # BORDS ADOUCIS. Un flou collé au rectangle net se lit comme une
        # BARRE DE CENSURE : l'œil voit d'abord qu'on cache quelque chose, et
        # la photographie perd sa spontanéité — exactement le contraire de
        # l'effet recherché sur un support commercial. On fond donc le flou
        # dans l'image par un masque aux bords estompés : le nom reste
        # parfaitement illisible, mais rien ne signale l'intervention.
        marge = max(4, largeur // 30)
        masque = Image.new("L", morceau.size, 0)
        ImageDraw.Draw(masque).rectangle(
            (marge, marge, morceau.size[0] - marge, morceau.size[1] - marge),
            fill=255)
        masque = masque.filter(ImageFilter.GaussianBlur(marge))
        im.paste(Image.composite(flou, morceau, masque), boite)
    return im


def recadrer(im, ratio, focal, zoom=1.0):
    """Recadre au rapport demandé autour d'un point d'intérêt.

    `focal` est (x, y) en fraction de l'image : c'est ce qui évite les
    recadrages centrés qui coupent les visages en deux. La fenêtre est
    ensuite ramenée de force dans le cadre, donc un point focal excentré ne
    peut pas produire de bande vide.

    `zoom` resserre la fenêtre (0,7 = on ne garde que 70 % de la largeur
    disponible). C'est le seul moyen d'EXCLURE un détail parasite — un
    « HDMI NO SIGNAL » projeté au mur, une pancarte, un logo de tiers —
    sans retoucher le pixel : on cadre plus serré, comme au tirage.
    """
    l, h = im.size
    if l / h > ratio:
        nl, nh = int(h * ratio), h
    else:
        nl, nh = l, int(l / ratio)
    nl, nh = int(nl * zoom), int(nh * zoom)
    x = int(focal[0] * l - nl / 2)
    y = int(focal[1] * h - nh / 2)
    x = max(0, min(l - nl, x))
    y = max(0, min(h - nh, y))
    return im.crop((x, y, x + nl, y + nh))


# ---------------------------------------------------------------------------
# 2. Les formats produits
# ---------------------------------------------------------------------------
# Chaque déclinaison porte son usage : le nom du fichier doit dire à quoi il
# sert, sinon on se retrouve à ouvrir les images pour choisir.
FORMATS = {
    "16x9": (16 / 9, 2400),   # bandeaux héros (affiche, page de vente)
    "3x2": (3 / 2, 1600),     # illustrations pleine largeur de la brochure
    "4x3": (4 / 3, 1100),     # vignettes de cartes
    "1x1": (1.0, 1200),       # publications Facebook / LinkedIn
    "3x4": (3 / 4, 1000),     # colonnes portrait et stories
}

# ---------------------------------------------------------------------------
# 3. La sélection — quelle photo, cadrée où, dans quels formats
# ---------------------------------------------------------------------------
# fichier : NOM EXACT du cliché dans le dossier source — jamais son rang,
#           voir le piège documenté dans traiter().
# focal : point d'intérêt (x, y) en fraction — ajusté à l'œil, image par image.
# duo   : engendre en plus la variante bichrome (fonds de titre).
SELECTION = [
    # Salle informatique en pleine session : le plan qui porte toute la
    # promesse de la formation (des gens qui PRATIQUENT), donc décliné partout.
    dict(nom="salle", fichier="IMG_20260513_130341_615@-727537998.jpg", focal=(0.50, 0.52),
         formats=["16x9", "3x2", "4x3", "1x1"], duo=True),
    # Un écran d'ordinateur montrant la carte de la Centrafrique : la preuve
    # visuelle que le travail porte sur des données nationales.
    # zoom 0,55 : le plan large laissait lire « HDMI NO SIGNAL » projeté au
    # fond de la salle. Serrer sur l'écran garde le sujet et supprime le
    # parasite — ne pas réélargir ce cadrage.
    dict(nom="carte-ecran", fichier="IMG_20260518_143024_676@1642819688.jpg", focal=(0.30, 0.72), zoom=0.55,
         formats=["16x9", "3x2", "4x3", "1x1"], duo=True),
    # Collecte de terrain sur la latérite : l'autre moitié du métier, celle
    # qu'aucune formation « en salle » ne montre jamais.
    dict(nom="terrain", fichier="1779284683608.jpg", focal=(0.52, 0.62), zoom=0.88,
         formats=["3x2", "4x3", "3x4", "1x1"], duo=True),
    # Visage concentré devant un tableur : sert de vignette « analyse ».
    dict(nom="analyse", fichier="IMG_20260518_162102_544@-2132289940.jpg", focal=(0.42, 0.50),
         formats=["4x3", "3x4", "1x1"], duo=False),
    # Travail à plusieurs sur un même poste : illustre l'encadrement.
    dict(nom="encadrement", fichier="IMG_20260514_161658_108@1077679483.jpg", focal=(0.45, 0.55),
         formats=["3x2", "4x3", "1x1"], duo=False),
    # Rangées d'apprenants vues de face : plan large « promotion ».
    dict(nom="promotion", fichier="IMG_20260513_130025_874@-227616016.jpg", focal=(0.60, 0.52),
         formats=["16x9", "3x2", "4x3"], duo=True),
    # Approche des ménages dans un quartier : le geste exact de la collecte
    # CAPI, celui que la formation apprend à organiser et à superviser.
    dict(nom="collecte", fichier="IMG_20260520_131230_112@1647087308.jpg", focal=(0.46, 0.55), zoom=0.92,
         formats=["3x2", "4x3", "1x1"], duo=False),
    # Projection dans la pénombre : image de « lecture des résultats ».
    dict(nom="projection", fichier="1779208762651.jpg", focal=(0.42, 0.45),
         formats=["16x9", "3x2"], duo=True),
    # Rue de Bangui : ancre la campagne dans la ville, sans quoi les visuels
    # pourraient venir de n'importe quel pays.
    dict(nom="bangui", fichier="IMG_20260520_131618_835@-449870302.jpg", focal=(0.50, 0.55),
         formats=["16x9", "3x2", "1x1"], duo=True),
    # La promotion au complet, en extérieur : l'image de fin de parcours,
    # celle qui sert de preuve sociale sans qu'on ait à écrire un témoignage.
    dict(nom="groupe", fichier="IMG_20260520_124635_206@-149868777.jpg", focal=(0.52, 0.55), zoom=0.94,
         formats=["3x2", "4x3", "1x1", "16x9"], duo=True),
    # Restitution debout devant l'assemblée : illustre la journée 10, la
    # soutenance des travaux devant un « décideur ».
    dict(nom="restitution", fichier="IMG_20260526_155436_526@542017459.jpg", focal=(0.50, 0.52), zoom=0.95,
         formats=["3x2", "4x3", "1x1"], duo=False),
]

# ---------------------------------------------------------------------------
# 3 bis. La PREMIÈRE ÉDITION — remise des attestations
# ---------------------------------------------------------------------------
# POURQUOI CES CLICHÉS CHANGENT TOUT. Les photographies d'atelier prouvent
# qu'on travaille ; celles-ci prouvent qu'on TERMINE. C'est la seule preuve
# sociale dont dispose la campagne, et la seule réponse possible à la
# question que se pose tout candidat : « est-ce que ça marche vraiment ? ».
# Elles justifient à elles seules la mention « seconde édition ».
#
# `flou` : zones de texte nominatif à rendre illisibles — voir
# brouiller_zones(). Coordonnées relevées à la grille, cliché par cliché.
# Ne pas les modifier sans revérifier à l'écran que plus aucun nom ne se lit.
SELECTION_DIPLOMES = [
    # LA photographie de la campagne : quatre lauréats, attestations en main,
    # la carte de la Centrafrique projetée derrière eux. Preuve sociale et
    # ancrage national dans un seul cadre.
    dict(nom="promotion-1re", fichier="20260119_150227.heic", focal=(0.47, 0.46), zoom=0.96,
         formats=["16x9", "3x2", "4x3", "1x1"], duo=True,
         flou=[(0.148, 0.383, 0.297, 0.478),
               (0.288, 0.413, 0.437, 0.508),
               (0.398, 0.493, 0.572, 0.592),
               (0.633, 0.478, 0.817, 0.582)]),

    # Remise en tête-à-tête : le geste, les deux sourires, l'attestation
    # lisible comme objet. Sert de vignette « certificat » partout.
    dict(nom="remise", fichier="20260119_150057.heic", focal=(0.44, 0.50), zoom=0.94,
         formats=["3x2", "4x3", "1x1"], duo=False,
         flou=[(0.325, 0.660, 0.540, 0.785)]),

    # Même geste, avec la carte nationale bien visible à l'écran : c'est le
    # cliché qui relie la formation aux données du pays.
    dict(nom="remise-carte", fichier="20260119_150038.heic", focal=(0.42, 0.52), zoom=0.96,
         formats=["3x2", "4x3", "1x1"], duo=True,
         flou=[(0.275, 0.655, 0.505, 0.785)]),

    # Une lauréate. INDISPENSABLE : sans elle, toute la preuve sociale de la
    # campagne serait exclusivement masculine, ce qui contredirait le
    # discours sur les données désagrégées par sexe tenu deux pages plus tôt.
    dict(nom="remise-laureate", fichier="IMG_20260415_113502_341.jpg", focal=(0.50, 0.55), zoom=0.92,
         formats=["3x2", "4x3", "1x1", "16x9"], duo=False,
         flou=[(0.410, 0.600, 0.620, 0.790)]),

    # Poings levés : la seule image joyeuse du fonds. Réservée aux réseaux
    # sociaux, où l'émotion porte plus loin que l'argument.
    dict(nom="celebration", fichier="20260119_150158.heic", focal=(0.47, 0.45), zoom=0.97,
         formats=["3x2", "1x1"], duo=False,
         flou=[(0.178, 0.373, 0.332, 0.458),
               (0.353, 0.488, 0.517, 0.582),
               (0.623, 0.483, 0.792, 0.578)]),

    # Salle de travail de la première édition : aucune attestation, donc
    # aucun floutage. Sert de plan de coupe.
    dict(nom="travaux-1re", fichier="IMG_20250819_154658_467.jpg", focal=(0.52, 0.55), zoom=0.95,
         formats=["3x2", "4x3"], duo=False),
]


def traiter(selection, dossier):
    """Traite une table de sélection et renvoie le nombre de fichiers écrits.

    PIÈGE RENCONTRÉ, à ne JAMAIS réintroduire : cette fonction désignait
    autrefois les clichés par leur RANG dans le dossier trié. Le jour où
    vingt-quatre photographies ont été ajoutées à la source, tous les rangs
    se sont décalés — le script a réétalonné les mauvaises images sans lever
    la moindre erreur, en leur donnant les bons noms de sortie. Une panne
    parfaitement silencieuse, et la plus coûteuse du projet.

    On désigne donc par NOM DE FICHIER, et l'absence d'un fichier arrête le
    script au lieu de produire une image fausse.
    """
    produits = 0
    for entree in selection:
        chemin = os.path.join(dossier, entree["fichier"])
        if not os.path.exists(chemin):
            raise SystemExit(
                f"Introuvable : {entree['fichier']} (pour « {entree['nom']} ») "
                f"dans {dossier}.\nLa photographie a ete renommee ou deplacee ; "
                f"corriger la table de selection.")
        # exif_transpose : les photos de téléphone portent leur orientation
        # en métadonnée. Sans cette ligne, un cliché sur quatre sort couché.
        origine = ImageOps.exif_transpose(Image.open(chemin)).convert("RGB")
        # Le floutage se fait UNE FOIS sur l'original, avant tout recadrage :
        # les coordonnées se lisent ainsi sur le cliché de départ, et un
        # format oublié ne peut pas ressortir avec les noms en clair.
        origine = brouiller_zones(origine, entree.get("flou"))
        for cle in entree["formats"]:
            ratio, largeur = FORMATS[cle]
            im = recadrer(origine, ratio, entree["focal"], entree.get("zoom", 1.0))
            im = im.resize((largeur, int(largeur / ratio)), Image.LANCZOS)
            im = etalonner(im)
            nom = f"{entree['nom']}-{cle}.jpg"
            # optimize + progressive : le poids compte, la page de vente
            # sera consultée depuis Bangui sur des connexions mobiles.
            im.save(os.path.join(SORTIE, nom), "JPEG", quality=86,
                    optimize=True, progressive=True)
            produits += 1
            if entree["duo"] and cle in ("16x9", "3x2"):
                duo = duotone(im)
                duo.save(os.path.join(SORTIE, f"{entree['nom']}-duo-{cle}.jpg"),
                         "JPEG", quality=84, optimize=True, progressive=True)
                produits += 1
        marque = "  [noms floutes]" if entree.get("flou") else ""
        print(f"  {entree['nom']:<16} <- {entree['fichier']}{marque}")
    return produits


def main():
    os.makedirs(SORTIE, exist_ok=True)
    print("Ateliers de formation (mai 2026)")
    produits = traiter(SELECTION, SOURCE)
    print("\nRemise des attestations, premiere edition (janvier et avril 2026)")
    produits += traiter(SELECTION_DIPLOMES, SOURCE_DIPLOMES)
    print(f"\n{produits} fichiers engendres dans {SORTIE}")
    if FLOUTER_NOMS:
        print("Les noms des laureats sont floutes. Voir FLOUTER_NOMS.")


if __name__ == "__main__":
    main()
