/* ==========================================================================
   Compteur de places — rendu partagé par la page de vente et le formulaire.

   Dépend de `places.js`, qui doit être chargé AVANT lui.

   PRINCIPE DE DÉGRADATION. Le HTML des pages contient déjà un compteur
   ÉCRIT EN DUR, avec les mêmes chiffres. Ce script ne fait que le remplacer.
   Conséquence voulue : si le JavaScript est coupé, si le fichier manque, ou
   si la page est imprimée, le visiteur voit quand même un compteur juste au
   lieu d'un trou. Ne jamais vider le HTML de secours en pensant « le script
   s'en charge ».
   ========================================================================== */

(function () {
  "use strict";

  var P = window.OSC_PLACES;
  if (!P) { return; }   // pas de données : on laisse le HTML de secours

  var restantes = Math.max(0, P.total - P.confirmees);
  var taux = P.confirmees / P.total;
  var alerte = taux >= P.seuil_alerte;

  /* Nombre de jours pleins avant la clôture. Math.ceil et non round : à
     douze heures de l'échéance, afficher « 0 jour » alors qu'on peut encore
     s'inscrire ferait perdre des candidats. */
  function joursRestants() {
    var reste = new Date(P.cloture) - new Date();
    return Math.max(0, Math.ceil(reste / 86400000));
  }

  function accord(n, singulier, pluriel) {
    return n <= 1 ? singulier : pluriel;
  }

  /* Rend un compteur dans chaque élément portant [data-compteur].
     L'attribut vaut "complet" (barre + phrases) ou "compact" (une ligne),
     ce qui évite d'écrire deux scripts pour deux mises en page. */
  function rendre(hote) {
    var compact = hote.getAttribute("data-compteur") === "compact";
    var jours = joursRestants();
    var pourcent = Math.round(taux * 100);

    var etat = alerte ? "compteur--alerte" : "";
    var phrase = restantes === 0
      ? "Session complète — inscrivez-vous sur la liste d’attente"
      : "<strong>" + restantes + "</strong> " + accord(restantes, "place", "places") +
        " " + accord(restantes, "restante", "restantes") + " sur " + P.total;

    if (compact) {
      hote.className = "compteur compteur--compact " + etat;
      hote.innerHTML =
        '<span class="compteur__pastille">' + phrase + "</span>" +
        '<span class="compteur__delai">Clôture dans ' + jours + " " +
          accord(jours, "jour", "jours") + "</span>";
      return;
    }

    hote.className = "compteur " + etat;
    hote.innerHTML =
      '<div class="compteur__tete">' +
        '<span class="compteur__phrase">' + phrase + "</span>" +
        '<span class="compteur__pourcent">' + pourcent + "&nbsp;% pourvues</span>" +
      "</div>" +
      /* La barre est en aria-hidden et doublée d'un texte : un lecteur
         d'écran doit entendre « 19 places restantes », pas « 63 % ». */
      '<div class="compteur__barre" aria-hidden="true">' +
        '<span style="width:' + pourcent + '%"></span>' +
      "</div>" +
      '<div class="compteur__pied">' +
        "<span>Clôture le " + P.cloture_libelle + " — dans <strong>" + jours + " " +
          accord(jours, "jour", "jours") + "</strong></span>" +
        "<span>Pointage du " + P.mise_a_jour + "</span>" +
      "</div>";
  }

  function initialiser() {
    var hotes = document.querySelectorAll("[data-compteur]");
    for (var i = 0; i < hotes.length; i++) { rendre(hotes[i]); }
  }

  /* Le script est chargé en fin de corps, mais on garde la garde sur
     readyState : le formulaire d'inscription le charge dans <head> pour que
     le compteur soit prêt avant la première peinture. */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialiser);
  } else {
    initialiser();
  }

  /* Exposé pour le formulaire, qui doit connaître le nombre restant afin de
     basculer en mode « liste d'attente » quand il tombe à zéro. */
  window.OSC_COMPTEUR = { restantes: restantes, complet: restantes === 0 };
})();
