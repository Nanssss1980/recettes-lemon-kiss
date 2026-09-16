# app.py

from flask import Flask, request, redirect
import os
import json
import re
import unicodedata
from dotenv import load_dotenv
from supabase import create_client

# On charge les variables du fichier .env (SUPABASE_URL et SUPABASE_KEY)
load_dotenv()

# On récupère ces valeurs pour les utiliser
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# On crée la connexion à Supabase, qu'on pourra utiliser partout dans le code
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
import cloudinary
import cloudinary.uploader

# On configure Cloudinary avec nos clés (récupérées depuis le fichier .env)
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True,
)

app = Flask(__name__)


def sauvegarder_recette(utilisateur, slug, donnees):
    # On enregistre UNE recette à la fois dans Supabase.
    # "upsert" veut dire : si cette combinaison utilisateur+slug existe déjà, on la met à jour,
    # sinon on l'insère comme nouvelle ligne.
    supabase.table("recettes").upsert({
        "utilisateur": utilisateur,
        "slug": slug,
        "titre": donnees["titre"],
        "description": donnees.get("description", ""),
        "ingredients": donnees["ingredients"],
        "preparation": donnees["preparation"],
        "secret": donnees.get("secret", ""),
        "photo": donnees.get("photo"),
    }, on_conflict="utilisateur,slug").execute()


def charger_toutes_les_recettes():
    # On récupère TOUTES les recettes stockées dans Supabase,
    # et on les remet dans la même structure que notre dictionnaire "utilisateurs"
    # (utilisateur -> slug -> données), pour ne rien casser dans le reste du code.
    reponse = supabase.table("recettes").select("*").execute()
    resultat = {}
    for ligne in reponse.data:
        utilisateur = ligne["utilisateur"]
        slug = ligne["slug"]
        if utilisateur not in resultat:
            resultat[utilisateur] = {}
        resultat[utilisateur][slug] = {
            "titre": ligne["titre"],
            "description": ligne["description"],
            "ingredients": ligne["ingredients"],
            "preparation": ligne["preparation"],
            "secret": ligne["secret"],
            "photo": ligne["photo"],
        }
    return resultat


# Au démarrage de l'app, on charge toutes les recettes depuis Supabase.
utilisateurs = charger_toutes_les_recettes()


@app.route("/<utilisateur>/<slug>")
def voir_recette(utilisateur, slug):
    if utilisateur not in utilisateurs:
        return "Utilisateur introuvable", 404

    if slug not in utilisateurs[utilisateur]:
        return "Recette introuvable", 404

    recette = utilisateurs[utilisateur][slug]

    html = f"<h1>{recette['titre']}</h1>"
    if recette.get("photo"):
        html += f'<p><img src="{recette["photo"]}" width="400"></p>'
    html += f"<p><em>{recette['description']}</em></p>"
    html += f"<p>Recette partagée par {utilisateur.capitalize()}</p>"

    html += "<h2>🥘 Ingrédients</h2><ul>"
    for ingredient in recette["ingredients"]:
        html += f"<li>{ingredient}</li>"
    html += "</ul>"

    html += "<h2>👩‍🍳 Préparation</h2><ol>"
    for etape in recette["preparation"]:
        html += f"<li>{etape}</li>"
    html += "</ol>"

    html += "<h2>✨ Le petit secret</h2>"
    html += f"<p>{recette['secret']}</p>"

    lien_recette = f"http://127.0.0.1:5001/{utilisateur}/{slug}"
    message = f"Voici ma recette : {recette['titre']} 🍋 {lien_recette}"
    html += f'<p><a href="https://wa.me/?text={message}" target="_blank">📤 Partager sur WhatsApp</a></p>'

    return html


# "methods=['GET', 'POST']" veut dire : cette route accepte deux types de visite :
# GET = juste regarder la page (afficher le formulaire vide)
# POST = envoyer des données (quand on clique sur "Valider")
@app.route("/creer", methods=["GET", "POST"])
def formulaire_creation():
    # Si la méthode est POST, ça veut dire que quelqu'un vient de valider le formulaire
    if request.method == "POST":
        # request.form permet de récupérer ce que la personne a tapé,
        # en utilisant le "name" de chaque champ du formulaire (ex: name="prenom")
        prenom = request.form["prenom"].strip().lower()
        titre = request.form["titre"].strip()
        description = request.form.get("description", "").strip()
        secret = request.form.get("secret", "").strip()

        # Les ingrédients et la préparation ont été tapés "un par ligne" dans le formulaire.
        # .splitlines() découpe le texte à chaque retour à la ligne, et donne une liste.
        # On ignore aussi les lignes vides avec cette petite vérification.
        ingredients = [ligne.strip() for ligne in request.form["ingredients"].splitlines() if ligne.strip()]
        preparation = [ligne.strip() for ligne in request.form["preparation"].splitlines() if ligne.strip()]

        # On transforme le titre en "slug" : tout en minuscules, espaces remplacés par des tirets.
        # C'est ce qui apparaîtra dans le lien final.
        slug = titre.lower().strip().replace(" ", "-")
        # On enlève aussi les accents et emojis les plus courants pour un lien plus propre.
        slug = unicodedata.normalize("NFKD", slug).encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-z0-9\-]", "", slug)

        # On récupère le fichier photo envoyé, s'il y en a un.
        photo = request.files.get("photo")
        nom_photo = None  # Par défaut, pas de photo

        # On vérifie que la personne a bien choisi un fichier (le champ n'est pas vide)
        if photo and photo.filename:
            # On envoie la photo directement vers Cloudinary, avec un identifiant unique.
            resultat_upload = cloudinary.uploader.upload(
                photo,
                public_id=f"{prenom}-{slug}",
                folder="recettes",
            )
            # Cloudinary nous renvoie l'URL complète de l'image hébergée.
            nom_photo = resultat_upload["secure_url"]

        # Si ce prénom n'existe pas encore dans notre "base de données", on lui crée son espace.
        if prenom not in utilisateurs:
            utilisateurs[prenom] = {}

        # On enregistre la nouvelle recette.
        utilisateurs[prenom][slug] = {
            "titre": titre,
            "description": description,
            "ingredients": ingredients,
            "preparation": preparation,
            "secret": secret,
            "photo": nom_photo,
        }

        # On sauvegarde immédiatement dans Supabase, pour ne jamais perdre cette recette.
        sauvegarder_recette(prenom, slug, utilisateurs[prenom][slug])

        # On redirige automatiquement vers la page de la recette qu'on vient de créer.
        return redirect(f"/{prenom}/{slug}")

    # Si la méthode est GET, on affiche simplement le formulaire vide, comme avant.
    html = """
    <h1>🍋 Crée ta recette signature</h1>
    <form method="POST" action="/creer" enctype="multipart/form-data">
        <p>
            <label>Ton prénom :</label><br>
            <input type="text" name="prenom" required>
        </p>
        <p>
            <label>Titre de ta recette :</label><br>
            <input type="text" name="titre" required>
        </p>
        <p>
            <label>Une petite phrase sur ta recette (facultatif) :</label><br>
            <textarea name="description" rows="2"></textarea>
        </p>
        <p>
            <label>Ingrédients (un par ligne) :</label><br>
            <textarea name="ingredients" rows="6" required></textarea>
        </p>
        <p>
            <label>Préparation (une étape par ligne) :</label><br>
            <textarea name="preparation" rows="6" required></textarea>
        </p>
        <p>
            <label>Ton petit secret (facultatif) :</label><br>
            <textarea name="secret" rows="2"></textarea>
        </p>
        <p>
            <label>📸 Photo de ta recette (facultatif) :</label><br>
            <input type="file" name="photo" accept="image/*">
        </p>
        <button type="submit">Valider</button>
    </form>
    """
    return html


if __name__ == "__main__":
    app.run(debug=True, port=5001)
