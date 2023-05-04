/**
 * Script pour l'accueil du site
 */

"use strict"


/**
 * Constantes globales
 * */
const sectEnchere = document.getElementById("section-accueil")
const piedDePage = document.getElementById("sect-footer")


/**
 * Variables globales
 * */
let indice = 0

function afficherEncheres()
{

}

function defilement()
{
    while ((innerHeight + scrollY) >= 0.9 * document.body.offsetHeight)
    {
        afficherEncheres()
    }
}

/**
 * Initialisation de la page
 */
function initialisation()
{
    window.addEventListener('scroll', defilement)
    piedDePage.className = "d-none"
    defilement()
}