# -*- coding: utf-8 -*-
"""
Engendre les codes QR de la campagne (`assets/qr/`).

POURQUOI DES CODES QR, ET POURQUOI CEUX-LÀ
-------------------------------------------
À Bangui, le canal de conversion n'est ni le courriel ni le formulaire web :
c'est WhatsApp. Une affiche collée dans un couloir de l'Université doit donc
mener en UN GESTE à une conversation, sans que l'étudiant ait à recopier un
numéro à huit chiffres. D'où trois codes distincts, et non un seul :

  qr-whatsapp   ouvre une discussion avec un message PRÉ-RÉDIGÉ. Le message
                compte autant que le lien : il qualifie le contact tout seul
                (« je suis étudiant / professionnel ») et évite les
                « bonjour » sans suite auxquels personne ne sait répondre.
  qr-inscription pointe vers le formulaire en ligne, pour les supports lus
                sur écran.
  qr-brochure   pointe vers la brochure PDF, pour les partenaires
                institutionnels qui demandent « un document ».

Le niveau de correction d'erreur est volontairement élevé (H) : ces codes
sont imprimés sur des affiches qui vont vivre dehors, se salir et se plier.
Un code en correction L devient illisible au premier coin corné.

    python outils/engendrer_qr.py
"""

import json
import os
import urllib.parse

import segno

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "assets", "qr")

with open(os.path.join(RACINE, "parametres.json"), encoding="utf-8") as f:
    P = json.load(f)

# Messages pré-rédigés des liens WhatsApp. Écrits à la première personne du
# CANDIDAT, pas du cabinet : c'est lui qui écrit, le texte doit sonner comme
# lui. Chacun nomme sa formule, ce qui qualifie le contact dès le premier
# message et évite les « bonjour » sans suite auxquels personne ne sait
# répondre. Sans accent : un caractère non ASCII mal encodé dans une URL
# casse le message sur certains téléphones.
MESSAGES = {
    "qr-whatsapp": ("Bonjour, je souhaite des informations sur vos formations "
                    "\"Conduire une enquete statistique de A a Z\" "
                    "(rentree du 20 aout 2026). Voici mon profil : "),
    "qr-bootcamp": ("Bonjour, je souhaite m'inscrire au BootCamp intensif "
                    "(20 aout - 5 septembre 2026, 100 000 FCFA). "
                    "Je suis etudiant/doctorant en : "),
    "qr-cours-du-soir": ("Bonjour, je souhaite m'inscrire au Cours du soir approfondi "
                         "(20 aout - 28 octobre 2026, 200 000 FCFA). "
                         "Ma structure et ma fonction : "),
}


def lien_whatsapp(cle):
    """Construit un lien wa.me avec message pré-rempli.

    wa.me est le format officiel des liens WhatsApp : numéro international
    SANS « + » ni espace. Un numéro mal formé produit un code QR valide qui
    ouvre une conversation VIDE — panne silencieuse classique, à vérifier
    avec un vrai téléphone avant tout tirage papier.
    """
    return "https://wa.me/{}?text={}".format(
        P["contact"]["whatsapp_lien"],
        urllib.parse.quote(MESSAGES[cle], safe=""))


CODES = {
    "qr-whatsapp": lien_whatsapp("qr-whatsapp"),
    "qr-bootcamp": lien_whatsapp("qr-bootcamp"),
    "qr-cours-du-soir": lien_whatsapp("qr-cours-du-soir"),
    # Le site du cabinet porte déjà le « www » dans parametres.json : on ne
    # le rajoute pas, sinon on obtient « https://www.www... ».
    "qr-site": "https://{}".format(P["contact"]["site"]),
}

# Couleurs de la charte. Le code est tracé en marine et non en noir : posé
# sur un aplat blanc à côté du bloc-marque, un carré noir pur crée un point
# de contraste plus fort que le titre et attire l'œil en premier.
MARINE = "#0B2545"


def main():
    os.makedirs(SORTIE, exist_ok=True)
    for nom, url in CODES.items():
        qr = segno.make(url, error="h")
        # scale n'a pas d'effet sur la définition d'un SVG (c'est du
        # vectoriel) mais fixe l'unité de la grille : à 1, les coordonnées
        # sont entières et le fichier reste petit et net.
        qr.save(os.path.join(SORTIE, nom + ".svg"), scale=1,
                dark=MARINE, light=None, border=2)
        print(f"  {nom:<16} {url[:78]}")
    print(f"\n{len(CODES)} codes QR engendrés dans {SORTIE}")
    print("VÉRIFIER avec un vrai téléphone avant tout tirage papier.")


if __name__ == "__main__":
    main()
