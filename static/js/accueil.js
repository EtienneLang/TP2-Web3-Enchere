/**
 * Script pour l'accueil du site
 */

"use strict"


/**
 * Constantes globales
 * */
const sectEncheres = document.getElementById("section-accueil")
const piedDePage = document.getElementById("sect-footer")
const listeEncheres = document.getElementById("section-encheres")
const nbEncheresDemandees = 15

/**
 * Variables globales
 * */
let controleur = null;
let indice = 0
let motCle


function afficherEncheres(enchere) {
    let li = document.createElement("li")
    let p = document.createElement("p")
    p.append(indice + enchere.titre)
    li.append(p)
    listeEncheres.append(li)
}


async function ChercherEncheres() {
    let motCle = ""
    if (controleur != null) {
        // Annuler la requête précédente, car on lancera une nouvelle requête
        // à chaque input et on ne veut plus le résultat de la requête précédente.
        return;
    }

    const parametres = {
        "mots-cles": motCle,
        "indice": indice.toString()
    }

    controleur = new AbortController()
    try {
        const encheres = await envoyerRequeteAjax(
            "/api/recherche",
            "GET",
            parametres,
            controleur
        );
        for (const enchere of encheres) {
            afficherEncheres(enchere)
            indice++
        }
        controleur = null


    } catch (err) {
        if (err.name === "AbortError") {
            console.log("Une requête Ajax a été annulée")
        } else {
            console.error("Erreur lors d'une requête Ajax");
            console.error(err);
            //erreur.textContent = "Erreur lors de la requête. Veuillez réessayer."
            //chargement.classList.add("masquer")
        }
    }
}

/**
 * Permets de vérifier si le bas de la page est visible
 * @returns {boolean} True si le bas de la page est visible, False sinon
 */
function VerifierBasPageVisible()
{
    return (innerHeight + scrollY) >= 0.9 * document.body.offsetHeight
}


async function defilement() {
    if (VerifierBasPageVisible()) {
        await ChercherEncheres()
    }
}


/**
 * Initialisation de la page
 */
async function initialisation() {

    window.addEventListener('scroll', defilement)
    piedDePage.className = "d-none"
    while (VerifierBasPageVisible()) {
        await defilement()
    }

}

window.addEventListener('load', initialisation)