# -*- coding: utf-8 -*-
"""
Engendre les visuels carrés des publications LinkedIn et Facebook
(`04_Reseaux_sociaux/visuels/`).

POURQUOI ENGENDRER PLUTÔT QUE DESSINER
---------------------------------------
Douze visuels doivent partager exactement le même bandeau de marque, le même
filet de couleurs, la même famille de titres et le même pied. Dessinés un par
un dans un éditeur, ils divergent au troisième — et un fil de campagne dont
les visuels ne font pas famille ressemble à trois campagnes différentes.
Ici, le gabarit est écrit une fois et seul le CONTENU change.

Format : 1080 × 1080, le carré. C'est le seul format qui s'affiche sans
recadrage sur le fil Facebook comme sur LinkedIn ; le 1080 × 1350 gagne en
surface mais se fait rogner sur LinkedIn, et l'on perd alors le pied de page
qui porte le numéro de téléphone.

    python outils/engendrer_visuels.py

Régénérer après toute modification de `parametres.json` ou de la charte.
"""

import os
import subprocess
import urllib.parse

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "04_Reseaux_sociaux", "visuels")
TEMPO = os.path.join(SORTIE, "_gabarit.html")

NAVIGATEURS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]

# Le gabarit est un carré de 1080 px de côté. Les tailles sont en pixels et
# non en millimètres : ces images ne s'impriment jamais, elles se regardent
# sur un téléphone de 6 pouces — c'est ce qui dicte les corps de texte.
GABARIT = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<link rel="stylesheet" href="../../assets/css/osc.css">
<style>
  body {{ margin: 0; background: #DDE5EC; }}
  .v {{
    width: 1080px; height: 1080px; position: relative; overflow: hidden;
    background: var(--marine-900); color: #D3E3EF;
    display: flex; flex-direction: column;
  }}
  .v__fond {{ position: absolute; inset: 0; z-index: 0; }}
  .v__fond img {{ width: 100%; height: 100%; object-fit: cover; }}
  /* Voile oblique : il laisse vivre le coin haut droit de la photographie,
     là où l'on distingue encore les visages — c'est ce qui prouve que la
     scène est réelle et non une image de banque. */
  .v__fond::after {{
    content: ""; position: absolute; inset: 0;
    background: linear-gradient(118deg, rgba(7,26,47,.97) 0%, rgba(7,26,47,.90) 50%, rgba(11,37,69,.60) 100%);
  }}
  .v__int {{ position: relative; z-index: 1; flex: 1; display: flex; flex-direction: column; padding: 62px 68px; }}
  .v__tete {{ display: flex; align-items: center; justify-content: space-between; gap: 30px; }}
  .v__tete img {{ height: 74px; }}
  .v__edition {{
    font-family: var(--titre); font-size: 20px; letter-spacing: .18em; text-transform: uppercase;
    color: #08243D; background: var(--or); padding: 10px 22px; border-radius: 99px; white-space: nowrap;
  }}
  .v__corps {{ flex: 1; display: flex; flex-direction: column; justify-content: center; }}
  .v__sur {{
    font-family: var(--titre); font-size: 25px; letter-spacing: .17em; text-transform: uppercase;
    color: #7FD0F2; margin: 0 0 26px; display: flex; align-items: center; gap: 18px;
  }}
  .v__sur::before {{ content: ""; width: 46px; height: 4px; background: var(--bleu-signal); border-radius: 2px; flex: none; }}
  .v__t {{
    font-family: var(--titre); font-variation-settings: "wght" 700, "wdth" 80;
    font-size: {taille}px; line-height: .98; color: #fff; margin: 0 0 30px;
    text-shadow: 0 10px 26px rgba(0,0,0,.4);
  }}
  .v__t em {{ font-style: normal; color: var(--or); }}
  .v__c {{ font-size: 31px; line-height: 1.42; margin: 0; color: #C7DAE9; }}
  .v__c strong {{ color: #fff; }}
  .v__pied {{
    display: flex; align-items: center; justify-content: space-between; gap: 26px;
    padding-top: 26px; box-shadow: inset 0 1px 0 rgba(255,255,255,.18);
    font-size: 23px; color: #94AEC4;
  }}
  .v__pied b {{ color: var(--or); font-variant-numeric: tabular-nums; }}
  /* Bandeau de chiffres, employé par les visuels qui comparent. */
  .v__faits {{ display: flex; gap: 46px; margin-top: 12px; }}
  .v__faits div b {{
    display: block; font-family: var(--titre); font-size: 62px; color: var(--or); line-height: 1;
    font-variation-settings: "wght" 700, "wdth" 84; font-variant-numeric: tabular-nums;
  }}
  .v__faits div span {{ font-size: 21px; letter-spacing: .1em; text-transform: uppercase; color: #94AEC4; }}
  /* Planche de logiciels. */
  .v__logos {{ display: flex; flex-wrap: wrap; gap: 22px; margin-top: 18px; }}
  .v__logos img {{ width: 104px; height: 104px; border-radius: 26px; box-shadow: 0 12px 26px rgba(0,0,0,.42); }}
  {extra}
</style></head><body>
<div class="v">
  <div class="v__fond"><img src="../../assets/img/{photo}" alt=""></div>
  <div class="osc-filet" style="position:relative;z-index:2"><span></span><span></span><span></span><span></span><span></span></div>
  <div class="v__int">
    <div class="v__tete">
      <img src="../../assets/logos/logo-osc-blanc.svg" alt="Oubangui Stat Consulting">
      <span class="v__edition">2<sup>e</sup> édition</span>
    </div>
    <div class="v__corps">
      <p class="v__sur">{surtitre}</p>
      <h1 class="v__t">{titre}</h1>
      {corps}
    </div>
    <div class="v__pied">
      <span>Rentrée le <b>20 août 2026</b> · clôture le <b>18 août</b></span>
      <span><b>00 236 72 72 84 42</b></span>
    </div>
  </div>
</div>
</body></html>
"""

LOGOS = ["kobo", "odk", "googleforms", "excel", "spss", "stata", "r", "qgis", "powerbi"]
PLANCHE = "".join(f'<img src="../../assets/logos/{n}.svg" alt="">' for n in LOGOS)

# Les douze visuels, dans l'ordre du calendrier de Publications.md.
# `taille` : corps du titre. On le baisse quand le titre est long — c'est le
# seul réglage manuel, et il vaut mieux le voir ici que de laisser un titre
# déborder silencieusement du carré.
VISUELS = [
    dict(nom="01-annonce", photo="salle-1x1.jpg", taille=96,
         surtitre="Rentrée du 20 août 2026",
         titre="CONDUIRE UNE<br>ENQUÊTE <em>DE A À Z</em>",
         corps='<p class="v__c">Deux formules, dix modules, neuf logiciels.<br>'
               'À Bangui <strong>et en ligne sur Zoom</strong>.</p>'
               '<div class="v__faits">'
               '<div><b>2</b><span>formules</span></div>'
               '<div><b>10</b><span>modules</span></div>'
               '<div><b>9</b><span>logiciels</span></div>'
               '<div><b>30</b><span>places</span></div></div>'),

    dict(nom="02-chiffre", photo="carte-ecran-1x1.jpg", taille=190,
         surtitre="Le déficit statistique",
         titre="<em>2003</em>",
         corps='<p class="v__c">L’année du dernier recensement général achevé en '
               'République centrafricaine.<br><br>'
               '<strong>Le RGPH-4 est en cours — vingt-deux ans plus tard.</strong></p>'),

    dict(nom="03-memoire", photo="analyse-1x1.jpg", taille=84,
         surtitre="Étudiants et doctorants",
         titre="TON MÉMOIRE BLOQUE ?<br><em>CE N’EST PAS LE SUJET.</em>",
         corps='<p class="v__c">C’est la méthode. Un jury n’attaque presque jamais le thème — '
               'il attaque <strong>l’échantillon, le questionnaire, le taux de non-réponse</strong>.</p>'),

    dict(nom="04-formules", photo="promotion-1x1.jpg", taille=88,
         surtitre="Deux formules, un seul programme",
         titre="CHOISISSEZ<br><em>VOTRE RYTHME</em>",
         corps='<p class="v__c"><strong>BootCamp</strong> — étudiants · 20 août → 5 septembre<br>'
               '15 journées · 105 h · <strong>100 000 F</strong> au lieu de 250 000<br><br>'
               '<strong>Cours du soir</strong> — professionnels · 20 août → 28 octobre<br>'
               '60 séances · 300 h · <strong>200 000 F</strong> au lieu de 300 000</p>'),

    dict(nom="05-logiciels", photo="encadrement-1x1.jpg", taille=88,
         surtitre="Les outils du parcours",
         titre="NEUF LOGICIELS,<br><em>UN MÉTIER</em>",
         corps='<div class="v__logos">' + PLANCHE + '</div>'
               '<p class="v__c" style="margin-top:26px;font-size:27px">'
               'Et surtout : savoir <strong>lequel ouvrir devant quel problème</strong>.</p>'),

    dict(nom="06-intervenant", photo="remise-1x1.jpg", taille=74,
         surtitre="Qui vous forme",
         titre="IL A PRODUIT<br>LES CHIFFRES QUE<br><em>TOUT LE MONDE CITE</em>",
         corps='<p class="v__c"><strong>ZIA KOYANGBO Arsène</strong>, ingénieur statisticien '
               'économiste, directeur à l’ICASEES.<br>'
               'Directeur technique de l’<strong>EHCVM 2021</strong>, contributeur au '
               '<strong>PND 2024-2028</strong>. Seize ans de métier.</p>'),

    dict(nom="07-terrain", photo="collecte-1x1.jpg", taille=88,
         surtitre="Module 5 · la sortie de terrain",
         titre="CE JOUR-LÀ,<br><em>ON SORT DE LA SALLE</em>",
         corps='<p class="v__c">Le ménage qui refuse. L’adresse introuvable. La tablette '
               'déchargée à 11 h.<br><strong>Ça ne s’apprend pas dans un cours.</strong></p>'),

    dict(nom="08-echeance", photo="salle-1x1.jpg", taille=96,
         surtitre="Plus que cinq jours",
         titre="CLÔTURE LE<br><em>18 AOÛT</em>",
         corps='<p class="v__c">30 places strictes au Cours du soir approfondi.<br>'
               '<strong>Après cette date, prochaine session l’an prochain.</strong></p>'),

    dict(nom="09-ancrage", photo="projection-16x9.jpg", taille=80,
         surtitre="Ancrage national",
         titre="TROIS AGENDAS,<br><em>UNE COMPÉTENCE</em>",
         corps='<p class="v__c">Les cibles <strong>ODD 17.18 et 17.19</strong> appellent des données '
               'désagrégées et des capacités statistiques. Le <strong>PND-RCA 2024-2028</strong> '
               'couvre 66 cibles ODD sur cinq axes.<br><br>'
               'Aucun indicateur ne se renseigne tout seul.</p>'),

    dict(nom="10-modules", photo="atelier-1x1.jpg", taille=88,
         surtitre="Le parcours",
         titre="DIX MODULES,<br><em>DIX LIVRABLES</em>",
         corps='<p class="v__c" style="font-size:27px">'
               'Cadrer · Questionner · Échantillonner · Numériser · Collecter<br>'
               'Apurer · Analyser · Modéliser · Cartographier · Soutenir<br><br>'
               '<strong>Chaque module produit une pièce corrigée.</strong> '
               'À la fin, elles forment votre dossier de travaux.</p>'),

    dict(nom="11-dernier-jour", photo="celebration-1x1.jpg", taille=110,
         surtitre="Dernier jour",
         titre="C’EST<br><em>DEMAIN</em>",
         corps='<p class="v__c">Les inscriptions à la 2<sup>e</sup> édition ferment '
               '<strong>mardi 18 août</strong>.<br>Un message suffit.</p>'),

    dict(nom="13-promotion", photo="promotion-1re-1x1.jpg", taille=76,
         surtitre="La première promotion",
         titre="ILS L’ONT FAIT<br><em>AVANT VOUS</em>",
         corps='<p class="v__c">Étude complète, soutenance devant un jury, puis remise des '
               '<strong>attestations de réussite</strong>.<br>'
               'Bangui, janvier 2026.<br><br>'
               '<strong>La 2<sup>e</sup> édition reprend le même parcours.</strong></p>'),

    dict(nom="12-coulisses", photo="encadrement-1x1.jpg", taille=88,
         surtitre="19 août · veille de l’ouverture",
         titre="AUJOURD’HUI,<br><em>ON INSTALLE</em>",
         corps='<p class="v__c">Remise des fichiers de travail et installation des '
               '<strong>neuf logiciels</strong> sur chaque machine.<br>'
               'Demain, 20 août : on ouvre. 🚀</p>'),
]


def navigateur():
    for chemin in NAVIGATEURS:
        if os.path.exists(chemin):
            return chemin
    raise SystemExit("Aucun navigateur Chromium trouvé.")


def main():
    os.makedirs(SORTIE, exist_ok=True)
    exe = navigateur()
    for v in VISUELS:
        html = GABARIT.format(photo=v["photo"], surtitre=v["surtitre"],
                              titre=v["titre"], corps=v["corps"],
                              taille=v["taille"], extra=v.get("extra", ""))
        with open(TEMPO, "w", encoding="utf-8") as f:
            f.write(html)
        url = "file:///" + urllib.parse.quote(TEMPO.replace("\\", "/"), safe="/:")
        cible = os.path.join(SORTIE, v["nom"] + ".png")
        subprocess.run([exe, "--headless=new", "--disable-gpu",
                        "--allow-file-access-from-files",
                        "--screenshot=" + cible, "--window-size=1080,1080", url],
                       capture_output=True)
        print(f"  ok  {v['nom']}.png")
    os.remove(TEMPO)   # le gabarit ne reste pas dans le dossier livré
    print(f"\n{len(VISUELS)} visuels engendrés dans {SORTIE}")


if __name__ == "__main__":
    main()
