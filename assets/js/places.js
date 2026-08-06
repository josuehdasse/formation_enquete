/* ==========================================================================
   SOURCE UNIQUE du compteur de places de la campagne.

   C'EST LE SEUL FICHIER À MODIFIER quand une inscription est confirmée.
   Il est lu par la page de vente ET par le formulaire d'inscription : les
   deux affichent donc toujours le même nombre. Deux compteurs qui se
   contredisent sur deux pages du même site détruisent la crédibilité de la
   rareté — et la rareté est le moteur de conversion de cette campagne.

   POURQUOI UN FICHIER JS ET NON UN JSON. Les supports doivent fonctionner
   ouverts DEPUIS UN DISQUE (file://), envoyés par WhatsApp ou copiés sur
   une clé — un commercial en tournée à Bangui n'a pas toujours de réseau.
   Or `fetch()` sur un fichier local est refusé par la politique d'origine
   du navigateur, alors qu'une balise <script> passe toujours.

   QUAND LE SITE SERA HÉBERGÉ : remplacer le contenu de ce fichier par un
   appel à l'API d'inscription, en conservant EXACTEMENT le même nom et la
   même forme d'objet — rien d'autre n'aura à changer dans les pages.

   RÈGLE DÉONTOLOGIQUE, à ne pas contourner : ces nombres doivent être les
   nombres RÉELS d'inscriptions confirmées. Un compteur gonflé se voit — les
   gens se parlent, à Bangui plus qu'ailleurs — et coûte plus cher qu'il ne
   rapporte.
   ========================================================================== */

window.OSC_PLACES = {

  /* La limite de 30 places est celle du COURS DU SOIR : c'est la seule des
     deux formules pour laquelle un plafond strict a été arrêté. Le compteur
     public porte donc sur elle, et c'est aussi la formule au tarif le plus
     élevé — celle dont la rareté pèse le plus dans la décision. */
  total: 30,

  // Inscriptions CONFIRMÉES au Cours du soir (règlement reçu).
  confirmees: 7,

  /* Le BootCamp n'a pas de plafond chiffré arrêté : on annonce un effectif
     limité sans inventer de nombre. Passer ce champ à un entier fait
     apparaître un second compteur partout où il est prévu. */
  bootcamp_total: null,
  bootcamp_confirmees: 12,

  // Date du dernier pointage, affichée sous le compteur. Sans elle, un
  // visiteur ne sait pas si le chiffre date d'hier ou du mois dernier.
  mise_a_jour: "6 août 2026",

  // Clôture des inscriptions, au format ISO pour le décompte des jours.
  cloture: "2026-08-18T23:59:59",
  cloture_libelle: "18 août 2026",

  // Seuil au-delà duquel l'affichage passe en alerte (or, ton pressant).
  // Fixé à 70 % : en dessous, insister sur l'urgence sonne faux ; au-delà,
  // c'est la vérité et elle suffit.
  seuil_alerte: 0.70
};
