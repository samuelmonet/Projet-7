// Chargement des id clients disponibles
// Chargement des articles de presse
var request = new XMLHttpRequest();
request.open("GET", "/client/ids");
request.send();

function validateForm() {
	var erreur;
	var client=document.getElementById("client_id");
	var liste=JSON.parse(request.response)
	console.log(liste)
	console.log(Number(client.value))
	console.log(liste.includes(Number(client.value)))
	if (!client.value) {
	erreur="Veuillez renseigner une ID client";
	} else if (!client.value.match(/^[0-9]{6}$/)) {
	erreur="Veuillez renseigner une ID à 6 chiffres";
	} else if (!(liste.includes(Number(client.value)))) {
	erreur="L'ID est inconnue";
	} 
	
	if (erreur) {
		document.getElementById("erreur").innerHTML=erreur;
		return false;
		} else {
		return true;
		}
	};
