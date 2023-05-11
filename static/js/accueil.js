/**
 * Script pour l'accueil du site
 */

"use strict"


/**
 * Constantes globales
 * */
const formRecherche = document.getElementById("form-recherche")
const barRecherche = document.getElementById("recherche");
const chargement = document.getElementById("chargement");
const sectEncheres = document.getElementById("section-accueil");
const piedDePage = document.getElementById("sect-footer");
const alerteRecherche = document.getElementById("alerte-recherche");
const divSuggestions = document.getElementById("div-suggestions");
const nbEncheresDemandees = 15

/**
 * Variables globales
 * */
let controleur = null;
let indice = 0
let motCle
let caracteresMin = 3;

/**
 * Permets d'afficher une enchère reçue dans la section des enchères
 * @param enchere
 */
function afficherEncheres(enchere) {
    //Pour la card
    const card = document.createElement("div")
    card.classList.add("card")
    card.classList.add("card-enchere")

    //Pour le header de la Card
    const cardHeader = document.createElement("div")
    cardHeader.classList.add("card-header")
    const titre = document.createElement("h5")
    titre.append(enchere.titre)
    cardHeader.append(titre)
    if (enchere.est_supprimee === 1)
    {
        const texteSupprimee = document.createElement("p")
        texteSupprimee.append("Supprimée")
        cardHeader.append(texteSupprimee)
        cardHeader.classList.add("enchere-inactive")
    }
    else if (!enchere.est_active)
    {
        const texteInactive = document.createElement("p")
        texteInactive.append("Inactive")
        cardHeader.append(texteInactive)
        cardHeader.classList.add("enchere-inactive")
    }

    //Pour le body de la card
    const cardBody = document.createElement("div")
    cardBody.classList.add("card-body")
    const imgEnchere = document.createElement("img")
    imgEnchere.src = "https://picsum.photos/seed/"+ enchere.id_enchere+ "/300/300"
    imgEnchere.classList.add("card-img")
    imgEnchere.alt = "Image pour l'enchere" + enchere.titre
    const description = document.createElement("p")
    description.append(enchere.description)
    cardBody.append(imgEnchere, description)

    //Pour le Footer de la card
    const cardFooter = document.createElement("div")
    cardFooter.classList.add("card-footer")
    if (enchere.est_supprimee === 1 || !enchere.est_active)
    {
        cardFooter.classList.add("enchere-inactive")
    }
    const dateLimite = document.createElement("p")
    const date = new Date(enchere.date_limite)
    dateLimite.append("Date limite : " + date.getFullYear() + "-"+ date.getMonth() + "-" + date.getDate())
    const lienEnchere = document.createElement("a")
    lienEnchere.href = "/encheres/" + enchere.id_enchere
    lienEnchere.classList.add("card-link")
    lienEnchere.classList.add("stretched-link")
    lienEnchere.append("Voir cette enchère")
    cardFooter.append(dateLimite, lienEnchere)

    //Mise en place de la card
    card.append(cardHeader,cardBody,cardFooter)
    sectEncheres.append(card)
}

/**
 * Permets de chercher les encheres dans la BD
 * @returns {Promise<void>}
 */
async function ChercherEncheres() {
    if (barRecherche.value.length >= caracteresMin && motCle !== barRecherche.value)
    {
        sectEncheres.replaceChildren()
        indice = 0;
        motCle = barRecherche.value;
    }
    else if (barRecherche.value.length === 0)
    {
        motCle = "";
    }
    if (controleur != null) {
        //on attend que la dernière requète soit completé pour en envoyer une autre
        return;
    }

    const parametres = {
        "mot-cle": motCle,
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
        if (encheres.length < nbEncheresDemandees)
            piedDePage.classList.remove("d-none")
        else
            piedDePage.classList.add("d-none")
        if(Object.entries(encheres).length === 0 && barRecherche.value.length >= caracteresMin)
        {
            divSuggestions.replaceChildren();
            divSuggestions.classList.remove("afficher");
            alerteRecherche.classList.remove("d-none");
        }
        else
        {
            alerteRecherche.classList.add("d-none");
            divSuggestions.replaceChildren();
            const ul = document.createElement("ul");
            divSuggestions.append(ul);
            if (barRecherche.value.length >= 3) {
                divSuggestions.classList.add("afficher");
            }
            else {
                divSuggestions.classList.remove("afficher");
            }
            let i = 0;
            for (const enchere of encheres) {
                if (barRecherche.value.length >= caracteresMin && i < 5) {
                    const li = document.createElement("li");
                    li.innerHTML = "<a href='/encheres/" + enchere.id_enchere + "'>" + enchere.titre + "</a>";
                    //On pourrais ajouter un Streshed link ici
                    li.classList.add("p-1");
                    ul.append(li);
                }
                afficherEncheres(enchere);
                indice++
                i++;
            }
        }
        controleur = null;
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

/**
 * Permets de gerer les évenements lors d'un scroll down
 * @returns {Promise<void>}
 */
async function defilement() {
    if (VerifierBasPageVisible()) {
        await ChercherEncheres()
    }
}

function gererClicFenetre(evenement) {
    const clicDansDivision = divSuggestions.contains(evenement.target);

    if (!clicDansDivision) {
        divSuggestions.replaceChildren()
        divSuggestions.classList.remove("afficher")
        document.removeEventListener("click", gererClicFenetre)
    }
}

function CancellerRecherche(e)
{
    //Mène nul part quand on pèse sur enter
    e.preventDefault()
}

/**
 * Initialisation de la page
 */
async function initialisation() {

    window.addEventListener('scroll', defilement)
    piedDePage.classList.add("d-none")
    while (VerifierBasPageVisible()) {
        await defilement()
    }
    barRecherche.addEventListener("input", ChercherEncheres)
    formRecherche.addEventListener("submit", CancellerRecherche)
    //Pour fermer la liste de suggestions quand on clique ailleurs, je ne sais pas si window est le meilleur endroit
    window.addEventListener("click", gererClicFenetre)
}

window.addEventListener('load', initialisation)