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

@app.route("/")
def accueil():
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lemon Kiss</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
      :root {
        --bg: #1C1A17;
        --ink: #F6F3EA;
        --ink-soft: #B9B2A5;
        --lemon: #E8C547;
        --line: #383430;
      }
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body {
        background: var(--bg);
        color: var(--ink);
        font-family: 'Jost', sans-serif;
        -webkit-font-smoothing: antialiased;
      }
      .wrap { max-width: 760px; margin: 0 auto; padding: 0 28px 140px; }
      .hero { padding: 110px 0 90px; text-align: center; }
      .hero .mark {
        font-family: 'Playfair Display', serif;
        font-weight: 500;
        font-size: clamp(50px, 9vw, 84px);
        color: var(--ink);
        line-height: 1;
      }
      .hero .tagline { margin-top: 18px; font-size: 16px; color: var(--lemon); letter-spacing: 0.02em; }
      .scenario { text-align: center; padding: 0 0 90px; }
      .scenario .quote {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-weight: 500;
        font-size: 24px;
        line-height: 1.5;
        color: var(--ink);
        max-width: 36ch;
        margin: 0 auto;
      }
      .scenario .sub { margin-top: 14px; font-size: 15px; color: var(--ink-soft); }
      .scenario .steps {
        margin-top: 34px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 14px;
        font-size: 13px;
        letter-spacing: 0.05em;
        color: var(--ink-soft);
        text-transform: uppercase;
      }
      .scenario .steps span.arrow { color: var(--lemon); }
      .how .kicker { font-size: 13px; letter-spacing: 0.05em; color: var(--lemon); text-transform: uppercase; text-align: center; }
      .how h2 {
        font-family: 'Playfair Display', serif;
        font-weight: 500;
        font-size: 32px;
        color: var(--ink);
        text-align: center;
        margin-top: 14px;
      }
      .how-grid {
        margin-top: 50px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
      }
      @media (max-width: 640px) {
        .how-grid { grid-template-columns: 1fr; }
        .how-col.left { border-right: none; border-bottom: 1px solid var(--line); }
      }
      .how-col { padding: 40px 40px; }
      .how-col.left { border-right: 1px solid var(--line); }
      .how-col .label {
        font-family: 'Jost', sans-serif;
        font-weight: 600;
        font-size: 12px;
        letter-spacing: 0.05em;
        color: var(--lemon);
        text-transform: uppercase;
      }
      .how-col ol { margin-top: 22px; padding-left: 20px; }
      .how-col ol li { font-size: 15px; line-height: 2.1; color: var(--ink); }
      .how-col ol li::marker { font-family: 'Playfair Display', serif; font-weight: 600; color: var(--lemon); }
      .how-col ul { margin-top: 22px; list-style: none; }
      .how-col ul li { font-size: 15px; line-height: 2.1; color: var(--ink); display: flex; gap: 10px; }
      .how-col ul li .arrow { color: var(--lemon); flex-shrink: 0; }
      .insight { margin-top: 80px; text-align: center; }
      .insight p {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 23px;
        line-height: 1.65;
        color: var(--ink-soft);
        max-width: 42ch;
        margin: 0 auto;
      }
      .insight p b { font-style: normal; font-weight: 600; color: var(--ink); }
      .cta { margin-top: 90px; text-align: center; }
      .cta a {
        display: inline-block;
        padding: 16px 40px;
        background: var(--lemon);
        color: var(--bg);
        text-decoration: none;
        font-family: 'Jost', sans-serif;
        font-weight: 500;
        font-size: 15px;
        letter-spacing: 0.02em;
      }
      .cta .note { margin-top: 16px; font-size: 13px; color: var(--ink-soft); }
      .cta.inline { margin-top: 40px; }
      .cta.inline a { padding: 14px 34px; font-size: 14px; }
      .divider { height: 1px; background: var(--line); margin: 90px 0; }
    </style>
    </head>
    <body>
      <div class="wrap">
        <div class="hero">
          <div class="mark">Lemon Kiss</div>
          <div class="tagline">Ta recette signature. Un lien pour la partager.</div>
        </div>
        <div class="scenario">
          <p class="quote">On te demande souvent la même recette&nbsp;?</p>
          <p class="sub">Crée ta recette une fois → puis partage-la régulièrement.</p>
          <div class="steps">
            <span>Créer</span><span class="arrow">→</span><span>Partager</span><span class="arrow">→</span><span>Terminé</span>
          </div>
          <div class="cta inline">
            <a href="/creer">Créer ma recette</a>
          </div>
        </div>
        <div class="divider"></div>
        <div class="how">
          <div class="kicker">Comment ça fonctionne</div>
          <h2>Tu crées ta recette en 5 minutes, ils la reçoivent en un clic.</h2>
          <div class="how-grid">
            <div class="how-col left">
              <div class="label">Pour toi</div>
              <ol>
                <li>Tu crées ta recette une fois.</li>
                <li>Tu ajoutes l'essentiel : ingrédients, préparation, ton petit secret.</li>
                <li>Tu obtiens ton lien personnel.</li>
                <li>Si on te demande TA recette, tu ouvres ton lien.</li>
                <li>Tu partages sur WhatsApp et c'est terminé, recette reçue&nbsp;!</li>
              </ol>
            </div>
            <div class="how-col right">
              <div class="label">Pour la personne qui reçoit</div>
              <ul>
                <li><span class="arrow">→</span> Elle clique sur le lien.</li>
                <li><span class="arrow">→</span> Elle voit la recette.</li>
                <li><span class="arrow">→</span> Pas besoin de télécharger une application.</li>
                <li><span class="arrow">→</span> Pas besoin de créer un compte.</li>
              </ul>
            </div>
          </div>
        </div>
        <div class="insight">
          <p>Les recettes signatures ne sont pas forcément celles qu'on cuisine le plus. <b>Ce sont celles qu'on ose refaire, parce qu'on sait qu'elles vont fonctionner.</b></p>
        </div>
        <div class="cta">
          <a href="/creer">Créer ma recette</a>
          <div class="note">Créer une fois, partager encore et encore. Aucune inscription pour la recevoir.</div>
        </div>
      </div>
    </body>
    </html>
    """
    return html

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


@app.route("/ping")  # Crée l'adresse /ping, que UptimeRobot appellera toutes les 5 minutes
def ping():  # Fonction exécutée à chaque visite de /ping
    # Lit UNE seule ligne dans Supabase : une vraie requête, donc de l'activité aux yeux de Supabase
    supabase.table("recettes").select("id").limit(1).execute()  # limit(1) garde la requête légère
    return "ok"  # Réponse minimale : UptimeRobot vérifie juste que le site répond


@app.route("/<utilisateur>/<slug>")  # Adresse d'une recette partagée, ex. /nancy/lemon-kiss-cake
def voir_recette(utilisateur, slug):  # Flask passe le prénom et le slug de l'adresse à la fonction
    # Si le prénom OU la recette n'existe pas, on renvoie une erreur 404 propre (au lieu d'un plantage)
    if utilisateur not in utilisateurs or slug not in utilisateurs[utilisateur]:
        return "Recette introuvable", 404

    recette = utilisateurs[utilisateur][slug]

    # On construit la liste des ingrédients en HTML
    html_ingredients = ""
    for ingredient in recette["ingredients"]:
        html_ingredients += f"<li>{ingredient}</li>"

    # On construit la liste des étapes de préparation en HTML
    html_preparation = ""
    for etape in recette["preparation"]:
        html_preparation += f"<li>{etape}</li>"

    # On construit le bloc photo, seulement si une photo existe
    html_photo = ""
    if recette.get("photo"):
        html_photo = f'<div class="photo-wrap"><img src="{recette["photo"]}" alt="{recette["titre"]}"></div>'

    # On construit le message de partage WhatsApp
    lien_recette = f"https://recette-app-3zbn.onrender.com/{utilisateur}/{slug}"
    message_whatsapp = f"Voici ma recette : {recette['titre']} 🍋 {lien_recette}"

    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{recette['titre']} — Lemon Kiss</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
      :root {{
        --bg: #1C1A17;
        --bg-secret: #211F1B;
        --ink: #F6F3EA;
        --ink-soft: #B9B2A5;
        --lemon: #E8C547;
        --line: #383430;
      }}
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{
        background: var(--bg);
        color: var(--ink);
        font-family: 'Jost', sans-serif;
        -webkit-font-smoothing: antialiased;
      }}
      .wrap {{ max-width: 680px; margin: 0 auto; padding: 60px 28px 120px; }}
      .brandbar {{ text-align: center; padding-bottom: 50px; }}
      .brandbar a {{
        font-family: 'Playfair Display', serif;
        font-weight: 500;
        font-size: 20px;
        color: var(--lemon);
        text-decoration: none;
      }}
      .photo-wrap {{
        width: 100%;
        border: 1px solid var(--line);
        overflow: hidden;
      }}
      .photo-wrap img {{ width: 100%; display: block; }}
      .head {{ margin-top: 40px; }}
      .head .crumb {{
        font-size: 13px;
        letter-spacing: 0.05em;
        color: var(--lemon);
        text-transform: uppercase;
      }}
      .head h1 {{
        font-family: 'Playfair Display', serif;
        font-weight: 500;
        font-size: 42px;
        line-height: 1.15;
        color: var(--ink);
        margin-top: 14px;
      }}
      .head .by {{ margin-top: 14px; font-size: 14px; color: var(--ink-soft); }}
      .head .desc {{
        margin-top: 22px;
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 19px;
        line-height: 1.6;
        color: var(--ink-soft);
      }}
      .share {{
        display: inline-flex;
        align-items: center;
        gap: 10px;
        margin-top: 30px;
        padding: 14px 26px;
        background: var(--lemon);
        color: var(--bg);
        font-family: 'Jost', sans-serif;
        font-weight: 500;
        font-size: 14px;
        text-decoration: none;
      }}
      .section {{ margin-top: 56px; }}
      .section h2 {{
        font-family: 'Jost', sans-serif;
        font-weight: 600;
        font-size: 13px;
        letter-spacing: 0.06em;
        color: var(--lemon);
        text-transform: uppercase;
        padding-bottom: 14px;
        border-bottom: 1px solid var(--line);
      }}
      .section ul, .section ol {{ margin-top: 20px; padding-left: 22px; }}
      .section li {{ font-size: 16px; line-height: 2; color: var(--ink); }}
      .section ol li::marker {{
        font-family: 'Playfair Display', serif;
        font-weight: 600;
        color: var(--lemon);
      }}
      .secret {{
        margin-top: 56px;
        padding: 28px 30px;
        background: var(--bg-secret);
        border-left: 2px solid var(--lemon);
      }}
      .secret .label {{
        font-family: 'Jost', sans-serif;
        font-weight: 600;
        font-size: 12px;
        letter-spacing: 0.06em;
        color: var(--lemon);
        text-transform: uppercase;
      }}
      .secret p {{
        margin-top: 12px;
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 18px;
        line-height: 1.6;
        color: var(--ink);
      }}
      .bottom {{
        margin-top: 70px;
        text-align: center;
        padding-top: 44px;
        border-top: 1px solid var(--line);
      }}
      .bottom p {{ font-size: 14px; color: var(--ink-soft); margin-bottom: 20px; }}
      .footer {{ margin-top: 60px; text-align: center; font-size: 12px; color: #6B6558; }}
    </style>
    </head>
    <body>
      <div class="wrap">
        <div class="brandbar">
          <a href="/">Lemon Kiss</a>
        </div>

        {html_photo}

        <div class="head">
          <div class="crumb">Recette de {utilisateur.capitalize()}</div>
          <h1>{recette['titre']}</h1>
          <div class="by">Recette partagée par {utilisateur.capitalize()}</div>
          <p class="desc">{recette['description']}</p>
          <a class="share" href="https://wa.me/?text={message_whatsapp}" target="_blank">📤 Partager sur WhatsApp</a>
        </div>

        <div class="section">
          <h2>Ingrédients</h2>
          <ul>{html_ingredients}</ul>
        </div>

        <div class="section">
          <h2>Préparation</h2>
          <ol>{html_preparation}</ol>
        </div>

        <div class="secret">
          <div class="label">✨ Le petit secret</div>
          <p>{recette['secret']}</p>
        </div>

        <div class="bottom">
          <p>Envie de la garder sous la main&nbsp;? Repartage ce lien.</p>
          <a class="share" href="https://wa.me/?text={message_whatsapp}" target="_blank">📤 Partager sur WhatsApp</a>
        </div>

        <div class="footer">Créée avec Lemon Kiss</div>
      </div>
    </body>
    </html>
    """

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
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Créer ma recette — Lemon Kiss</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=Jost:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
      :root {{
        --bg: #1C1A17;
        --bg-card: #26231F;
        --ink: #F6F3EA;
        --ink-soft: #B9B2A5;
        --lemon: #E8C547;
        --line: #383430;
      }}
      * {{ box-sizing: border-box; margin: 0; padding: 0; }}
      body {{
        background: var(--bg);
        color: var(--ink);
        font-family: 'Jost', sans-serif;
        -webkit-font-smoothing: antialiased;
      }}
      .wrap {{ max-width: 560px; margin: 0 auto; padding: 60px 28px 120px; }}
      .brandbar {{ text-align: center; padding-bottom: 40px; }}
      .brandbar a {{
        font-family: 'Playfair Display', serif;
        font-weight: 500;
        font-size: 20px;
        color: var(--lemon);
        text-decoration: none;
      }}
      h1 {{
        font-family: 'Playfair Display', serif;
        font-weight: 500;
        font-size: 36px;
        color: var(--ink);
        text-align: center;
      }}
      .sub {{
        margin-top: 12px;
        font-size: 14px;
        color: var(--ink-soft);
        text-align: center;
      }}
      form {{ margin-top: 46px; }}
      .field {{ margin-top: 26px; }}
      .field label {{
        display: block;
        font-size: 13px;
        font-weight: 500;
        color: var(--ink);
        margin-bottom: 10px;
      }}
      .field .hint {{
        display: block;
        font-size: 12px;
        color: var(--ink-soft);
        margin-top: 4px;
        font-weight: 400;
      }}
      input[type="text"], textarea, input[type="file"] {{
        width: 100%;
        background: var(--bg-card);
        border: 1px solid var(--line);
        color: var(--ink);
        font-family: 'Jost', sans-serif;
        font-size: 14px;
        padding: 13px 16px;
        border-radius: 2px;
      }}
      input[type="text"]:focus, textarea:focus {{
        outline: none;
        border-color: var(--lemon);
      }}
      textarea {{ resize: vertical; }}
      input[type="file"] {{ padding: 10px 16px; font-size: 13px; }}
      button {{
        display: block;
        width: 100%;
        margin-top: 40px;
        padding: 16px;
        background: var(--lemon);
        color: var(--bg);
        border: none;
        font-family: 'Jost', sans-serif;
        font-weight: 600;
        font-size: 15px;
        letter-spacing: 0.02em;
        cursor: pointer;
      }}
    </style>
    </head>
    <body>
      <div class="wrap">
        <div class="brandbar">
          <a href="/">Lemon Kiss</a>
        </div>

        <h1>Crée ta recette signature</h1>
        <p class="sub">Trois minutes suffisent. Garde ce que tu tapes simple, le lien fait le reste.</p>

        <form method="POST" action="/creer" enctype="multipart/form-data">
          <div class="field">
            <label>Ton prénom</label>
            <input type="text" name="prenom" required>
          </div>
          <div class="field">
            <label>Titre de ta recette</label>
            <input type="text" name="titre" required>
          </div>
          <div class="field">
            <label>Une petite phrase sur ta recette
              <span class="hint">Facultatif</span>
            </label>
            <textarea name="description" rows="2"></textarea>
          </div>
          <div class="field">
            <label>Ingrédients
              <span class="hint">Un par ligne</span>
            </label>
            <textarea name="ingredients" rows="6" required></textarea>
          </div>
          <div class="field">
            <label>Préparation
              <span class="hint">Une étape par ligne</span>
            </label>
            <textarea name="preparation" rows="6" required></textarea>
          </div>
          <div class="field">
            <label>Ton petit secret
              <span class="hint">Facultatif</span>
            </label>
            <textarea name="secret" rows="2"></textarea>
          </div>
          <div class="field">
            <label>📸 Photo de ta recette
              <span class="hint">Facultatif</span>
            </label>
            <input type="file" name="photo" accept="image/*">
          </div>
          <button type="submit">Créer mon lien</button>
        </form>
      </div>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    app.run(debug=True, port=5001)
