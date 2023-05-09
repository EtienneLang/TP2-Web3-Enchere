/**
 * Pour les mises sur une enchère
 */

"use strict"

/**
 * Constantes gloabales
 */
const formMise = document.getElementById("form-mise")
const champMise = document.getElementById("txt_mise")
const divFeedback = document.getElementById("feedback-mise")
const spanMiseMax = document.getElementById("span-mise-max")

/**
 * Variables gloabales
 */
let controleurMise = null;


async function getMiseMax() {
    try {
        return await envoyerRequeteAjax("/api/" + formMise.dataset.idEnchere + "/misemax")
    } catch (err) {
        if (err.name === "AbortError") {
            console.log("Une requête Ajax a été annulée")
        } else {
            console.error("Erreur lors de la demande de la mise max");
            console.error(err);
        }
    }
}

async function validerMise() {
    champMise.className = ""
    divFeedback.innerHTML = ""
    let miseUtilisateur = champMise.value
    if (miseUtilisateur.length === 0) {
        champMise.classList.add("is-invalid")
        divFeedback.innerHTML = "<p>Veuillez entrer une mise</p>"
        return false
    }
    miseUtilisateur = Number(miseUtilisateur)
    //On ne devrait jamais rentrer ici car le input est en type number, mais là pour être certain
    if (isNaN(miseUtilisateur)) {
        champMise.classList.add("is-invalid")
        divFeedback.innerHTML = "<p>La mise doit être une valeur numérique entière</p>"
        return false
    }
    //Pourrais utiliser le champ ou la mise max est indiqué, mais peut-être pas à jour
    const miseMax = await getMiseMax()
    let montantMin
    if (miseMax === null) {
        montantMin = 0
    } else {
        montantMin = miseMax.montant
    }
    if (miseUtilisateur <= montantMin) {
        champMise.classList.add("is-invalid")
        divFeedback.innerHTML = "<p>La mise ne peut pas être inférieure à la meilleure mise</p>"
        return false
    }
    return true
}

async function miserSurEnchere(e) {
    e.preventDefault()
    if (await validerMise()) {
        if (controleurMise != null) {
            //on attend que la dernière requète soit completé pour en envoyer une autre
            return;
        }
        const parametres = {
            "txt_mise": champMise.value
        }
        controleurMise = new AbortController()
        try {
             const miseMax = await envoyerRequeteAjax(
                "/api/miser/" + formMise.dataset.idEnchere,
                "POST",
                parametres,
                controleurMise
             );
             champMise.value = ""
             spanMiseMax.innerText = miseMax.montant + "$"
             controleurMise = null;
        } catch (err) {
            console.error("Erreur lors d'une mise");
            console.error(err);
            champMise.classList.add("is-invalid")
            divFeedback.innerHTML = "<p>Erreur lors de votre mise</p>"
        }
    }
}

function initialisation() {
    if (formMise !== null) {
        formMise.addEventListener("submit", miserSurEnchere)
    }

}

window.addEventListener("load", initialisation)
