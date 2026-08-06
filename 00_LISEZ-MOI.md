# Kit de campagne — « Conduire une enquête statistique de A à Z »
### Seconde édition · rentrée du 20 août 2026 · OUBANGUI STAT CONSULTING

Huit livrables, prêts à diffuser. Ce document dit **où est quoi**, **ce qu'il
reste à faire avant diffusion**, et **comment régénérer** ce qui s'engendre.

---

## Les huit livrables

| # | Livrable | Où | Format |
|---|---|---|---|
| 1 | **Affiche premium** | `01_Affiche/Affiche_A3.html` + `.pdf` | A3 portrait, prêt imprimeur |
| 2 | **Page de vente** | `02_Page_de_vente/index.html` | Web, structure PAS + AIDA |
| 3 | **Brochure** | `03_Brochure/Brochure.html` + `Brochure_Formation_2026.pdf` | A4, 12 pages |
| 4 | **Publications réseaux** | `04_Reseaux_sociaux/Publications.md` + `visuels/` | 13 textes + 13 visuels 1080×1080 |
| 5 | **Vidéo promotionnelle** | `05_Video/Script_video.md` + `Storyboard.html` + `.pdf` | Script minuté 75 s + storyboard 11 plans |
| 6 | **Formulaire d'inscription** | `06_Inscription/inscription.html` | Web, compteur de places + envoi WhatsApp |
| 7 | **Séquence WhatsApp** | `07_WhatsApp/Sequence_WhatsApp.md` | 9 étapes de relance |
| 8 | **Lettres administratives** | `08_Courriers/` (3 modèles) + `.pdf` | A4, 2 pages : lettre + fiche technique annexée |

**Point d'entrée :** `index.html`, à la racine — une **copie engendrée** de la
page de vente, avec ses chemins remontés d'un niveau. C'est le fichier qui
s'ouvre quand on double-clique sur le dossier, et celui que servira un
hébergeur si le kit est mis en ligne tel quel.

> **Ne jamais le modifier directement.** La source reste
> `02_Page_de_vente/index.html` ; après correction, relancer
> `python outils/copier_page_vente.py`. Le script remonte les chemins et
> s'interrompt si l'un d'eux resterait cassé.

**Support commun :** `assets/` — la feuille de style `css/osc.css`, les
photographies étalonnées `img/`, les logos `logos/`, les codes QR `qr/`, les
scripts `js/`.

**Les courriers en deux feuillets.** Chaque lettre fait exactement deux pages :
la **lettre** (sobre, signable, classable) puis la **fiche technique annexée**
(chiffres, tableau comparatif, modules, logiciels, intervenants, preuve).
Un courrier qui s'ouvre sur des aplats de couleur se lit comme un prospectus
et finit à la corbeille d'un secrétariat ; un courrier sobre suivi d'une annexe
documentée se lit comme un dossier. Ne jamais faire remonter l'infographie en
page 1.

---

## À faire avant diffusion

Trois points, et trois seulement.

1. **Tester les codes QR avec un vrai téléphone.** Ils pointent vers
   `wa.me/23672728442` avec un message pré-rédigé. Un numéro mal formé produit
   un code valide qui ouvre une conversation **vide** — panne silencieuse, et
   il sera trop tard une fois l'affiche tirée à 200 exemplaires.

2. **Tenir le compteur de places à jour** dans `assets/js/places.js`. C'est le
   **seul** fichier à modifier : la page de vente et le formulaire le lisent
   tous les deux. Le nombre affiché doit être le nombre réel d'inscriptions
   réglées.

3. **Remplacer les `[X]`** dans `04_Reseaux_sociaux/Publications.md` et
   `07_WhatsApp/Sequence_WhatsApp.md` par le nombre de places restantes au
   moment de publier ou d'écrire.

Dans les trois lettres du livrable 8, les passages **surlignés en bleu** sont
les champs à compléter (destinataire, date, signataire). Le surlignage
disparaît à l'impression.

---

## Ce qui s'engendre, et comment

Ces fichiers **ne se retouchent pas à la main** : on modifie la source, on
relance le script.

```bash
cd "Campagne_2026"
python outils/traiter_images.py       # photographies étalonnées -> assets/img/
python outils/engendrer_marque.py     # logo du cabinet -> assets/logos/
python outils/engendrer_logos.py      # pictogrammes des 9 logiciels
python outils/engendrer_qr.py         # codes QR -> assets/qr/
python outils/engendrer_visuels.py    # visuels réseaux -> 04_Reseaux_sociaux/visuels/
python outils/copier_page_vente.py    # page de vente -> index.html à la racine
python outils/exporter_pdf.py         # tous les PDF imprimables
```

**Source unique des informations opérationnelles :** `parametres.json`.
Dates, tarifs, horaires, contacts, intervenants y figurent une fois. Après
modification, répercuter dans les fichiers HTML puis relancer
`engendrer_qr.py` et `exporter_pdf.py`.

**Source unique du style :** `assets/css/osc.css`. Aucune couleur ne doit être
écrite en dur ailleurs.

---

## Les paramètres de la campagne

| | BootCamp intensif | Cours du soir approfondi |
|---|---|---|
| **Public** | Étudiants et doctorants | Professionnels et institutions |
| **Dates** | 20 août → 5 septembre 2026 | 20 août → 28 octobre 2026 |
| **Volume** | 15 journées · 105 heures | 60 séances · 300 heures |
| **Rythme** | Lundi au samedi, 09 h – 17 h | Lundi au samedi, 16 h – 21 h |
| **Dimanches** | exclus | exclus |
| **Lieu** | Université de Bangui + Zoom | Siège du cabinet + Zoom |
| **Places** | effectif limité | **30, strictes** |
| **Tarif** | **100 000 FCFA** (au lieu de 250 000) | **200 000 FCFA** (au lieu de 300 000) |
| **Règlement** | paiement unique au démarrage | paiement unique au démarrage |

**Clôture des inscriptions :** mardi 18 août 2026.
**Obligatoire :** ordinateur portable personnel.

**Calendrier :** 18 août — clôture et rencontre des personnes intéressées ·
19 août — rencontre des inscrits, remise des fichiers, installation des
logiciels · 20 août — ouverture.

> **Le volume horaire est la contrainte, la date de fin en découle.**
> 300 heures ÷ 5 h par séance = 60 séances ; départ le 20 août, tous les jours
> sauf le dimanche ⇒ 60ᵉ séance le mercredi 28 octobre 2026. Ne jamais
> déplacer la date de fin sans refaire ce calcul.

---

## Intervenants

- **DASSE TE NGBOKOTA Josué Honoré** — ingénieur statisticien, spécialiste
  MEAL, analyste quantitatif, développeur de systèmes d'informations
  décisionnelles.
- **ZIA KOYANGBO Arsène** — ingénieur statisticien économiste, directeur des
  statistiques d'entreprise et de la conjoncture économique à l'ICASEES.
  Directeur technique de l'EHCVM 2021, contributeur au PND 2024-2028.
  Seize ans d'expérience.
- **DAVY MAKOSSO** — ingénieur statisticien, spécialiste du traitement et de
  l'analyse des données.

> **L'argument le plus fort du kit :** M. ZIA a produit l'EHCVM 2021, d'où
> vient le chiffre de 68,8 % cité dans la page de vente et la brochure.
> Le formateur a produit la donnée que la campagne invoque. Ne pas retirer ce
> rapprochement des supports.

---

## Sources des données citées

Toutes les données de contexte national sont sourcées et vérifiables :

- **Plan national de développement de la RCA 2024-2028** (MEPCI) — les cinq
  axes stratégiques et leurs intitulés exacts, le décompte des 66 cibles ODD
  (section 2.10.1), le coût de 7 040 milliards FCFA, la matrice des risques
  (« insuffisance de données fiables… »), l'action prioritaire H 63, l'objectif
  stratégique 2.1.1 sur le RGPH-4, le taux de chômage urbain et les taux de
  scolarisation par sexe.
- **EHCVM 2021, ICASEES** — le taux de pauvreté chronique de 68,8 %.
- **Agenda 2030** — les cibles ODD 17.18 et 17.19.
- **Objectifs du Millénaire** — 8 objectifs, 21 cibles, 60 indicateurs.

**Aucun témoignage n'a été inventé, aucun taux de satisfaction ni de placement
n'est avancé.** Si le cabinet dispose de retours réels de la première
promotion, les ajouter augmentera nettement la conversion — mais ils doivent
être authentiques et attribuables.

---

## Choix graphiques à ne pas défaire

- **Aucune bordure sur les cartes.** Le relief vient d'une ombre portée et
  d'un biseau interne. C'est une demande explicite du commanditaire.
- **L'or ne sert qu'à l'urgence** (places, échéances) et jamais à décorer :
  s'il décore, il n'alerte plus.
- **Le bleu signal `#009EDB` ne porte jamais de texte** (2,6:1 sur blanc).
  Tout texte bleu emploie `#00689D`.
- **Les deux formules ont le même poids visuel** partout : elles ne s'adressent
  pas au même public, il n'y a pas d'offre « recommandée ».
- **Les photographies sont réelles** — ateliers du cabinet (Bangui, mai 2026)
  et remise des attestations de la première promotion (janvier et avril 2026).
  Les clichés portant le logo d'un tiers ont été écartés ou recadrés :
  faire figurer l'emblème d'une organisation sur un support commercial
  laisserait entendre un partenariat qui n'existe pas.
- **Les noms des lauréats sont floutés** sur toutes les photographies
  d'attestations. Diffuser l'identité de personnes privées dans une campagne
  commerciale suppose leur accord écrit, un par un. Le floutage se pilote par
  `FLOUTER_NOMS` dans `outils/traiter_images.py` : ne le désactiver qu'une fois
  les autorisations réunies.
- **Les photographies se désignent par NOM DE FICHIER**, jamais par rang.
  Le dossier source est passé de 30 à 54 clichés en cours de projet ; la
  sélection par rang avait alors silencieusement étalonné les mauvaises images
  en leur donnant les bons noms de sortie.
- **Les pictogrammes de logiciels** sont des représentations maison. La mention
  légale correspondante figure au pied de la brochure et de la page de vente —
  ne pas la retirer.

---

## Points signalés au commanditaire

1. **Le BootCamp n'a pas de plafond de places chiffré.** Les supports
   annoncent un « effectif limité » sans inventer de nombre ; le compteur
   public porte sur les 30 places du Cours du soir, seule limite arrêtée.
   Si un plafond existe, le renseigner dans `assets/js/places.js`
   (`bootcamp_total`) le fera apparaître partout où il est prévu.
2. **Les lettres du livrable 8 tiennent sur deux pages**, signature comprise.
   C'est un format admis pour une correspondance institutionnelle portant un
   tableau de synthèse ; pour les ramener à une page, retirer le tableau.
3. **Le lieu et l'heure précis** de la rencontre du 19 août restent à fixer :
   ils sont signalés `[Lieu et heure à préciser]` à l'étape 7 de la séquence
   WhatsApp.
4. **Les autorisations des lauréats photographiés** ne sont pas réunies à ce
   jour : c'est pourquoi les noms sont floutés. Si le cabinet les obtient, les
   attestations pourront être montrées en clair — ce qui renforcerait encore la
   preuve.
5. **Vingt-quatre nouvelles photographies** ont été ajoutées au dossier
   `Pictures\QGIS` en cours de projet (février 2026). Elles n'ont pas été
   examinées : la sélection actuelle porte sur les clichés de mai 2026.
   Elles méritent un tri si l'on veut enrichir le fonds.

---

**OUBANGUI STAT CONSULTING** — cabinet d'études statistiques et de conseil
« Faciliter la prise de décision par les données »
Kangala, Avenue B. Boganda, 3ᵉ arrondissement, Bangui, République centrafricaine
Téléphone · WhatsApp · Telegram : **00 236 72 72 84 42**
oubanguistatc@gmail.com · www.oubanguistatc.io
