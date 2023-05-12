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
const spanMeilleurMiseur = document.getElementById("span-meilleur-miseur")
const chargement = document.getElementById("chargement");
const confirmation = document.getElementById("confirmation");

/**
 * Variables gloabales
 */
let controleurMise = null;
let miseMaxActuel

/**
 * Permets d'obtenir la meilleure mise sur une enchère
 * @returns {Promise<Record<string, *>>} La meilleure mise
 */
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

/**
 * Permets d'ajuster le span qui indique à l'utilisateur s'il a la meilleure mise
 */
function ajusterTexteMeilleureMiseur() {
    if (miseMaxActuel.fk_miseur === Number(spanMeilleurMiseur.dataset.idUtilisateur)) {
        spanMeilleurMiseur.innerText = "Vous avez la meilleure mise"
    } else {
        spanMeilleurMiseur.innerText = "Vous n'avez pas la meilleure mise"
    }
}

/**
 * Permets d'ajuster l'affichage de la meilleure mise
 * @returns {Promise<void>}
 */
async function ajusterMiseMax() {
    let miseMax = await getMiseMax()
    if (miseMax === null) {
        return
    }
    if (miseMax.montant === miseMaxActuel.montant) {
        if (spanMeilleurMiseur.innerText === "")
            ajusterTexteMeilleureMiseur()
        return
    }
    miseMaxActuel = miseMax
    champMise.min = miseMaxActuel.montant
    spanMiseMax.innerText = miseMaxActuel.montant + "$"
    ajusterTexteMeilleureMiseur()
}

/**
 * Permets de valider si une mise est valide
 * @returns {Promise<boolean>} True si la mise est valide, False sinon
 */
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
    //On ne devrait jamais rentrer ici, car le input est en type number, mais là pour être certain
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

/**
 * Permets de miser sur une enchère
 * @param e sender de l'événement
 * @returns {Promise<void>}
 */
async function miserSurEnchere(e) {
    e.preventDefault()
    if (await validerMise()) {
        chargement.classList.remove("d-none");
        if (controleurMise != null) {
            //on attend que la dernière requète soit completé pour en envoyer une autre
            champMise.classList.add("is-invalid")
            divFeedback.innerHTML = "<p>Veuillez attendre que votre mise dernière mise soit completée</p>"
            return;
        }
        const parametres = {
            "txt_mise": champMise.value
        }
        controleurMise = new AbortController()
        //attendre 2 secondes avant de faire la requète
        await new Promise(r => setTimeout(r, 2000));
        try {
            const miseMax = await envoyerRequeteAjax(
                "/api/miser/" + formMise.dataset.idEnchere,
                "POST",
                parametres,
                controleurMise
            );
            champMise.value = "";
            await ajusterMiseMax();
            controleurMise = null;
            chargement.classList.add("d-none");
            CreeConfirmation();
        } catch (err) {
            console.error("Erreur lors d'une mise");
            console.error(err);
            champMise.classList.add("is-invalid")
            divFeedback.innerHTML = "<p>Erreur lors de votre mise</p>"
            chargement.classList.add("d-none");
        }
    }
}
function CreeConfirmation(prix, nom) {
    confirmation.innerHTML = "";
    const div = document.createElement("div");
    div.classList.add("alert", "alert-success", "alert-dismissible");
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute("data-bs-dismiss", "alert");
    button.classList.add("btn-close");
    const p = document.createElement("p");
    p.classList.add("mb-0");
    p.innerHTML = "<strong>Bien joué!</strong> Votre mise a bien été effectuée.";
    div.append(button, p);
    confirmation.append(div);
}
/**
 * Initialisation de la page
 * @returns {Promise<void>}
 */
async function initialisation() {
    //Quand l'utilisateur ne peut pas miser le formulaire n'existe pas
    if (formMise !== null) {
        formMise.addEventListener("submit", miserSurEnchere)
    }
    miseMaxActuel = await getMiseMax()
    setInterval(ajusterMiseMax, 1000);
}

window.addEventListener("load", initialisation)
