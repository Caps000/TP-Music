from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# ==========================================
# FORMULAIRES D'ACCÈS (AUTHENTIFICATION)
# ==========================================

class InscriptionForm(FlaskForm):
    nom = StringField("Nom complet", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email professionnel/personnel", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirmez votre mot de passe", 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Créer mon compte")

class ConnexionForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember = BooleanField("Se souvenir de moi")
    submit = SubmitField("Me connecter")

# ======================================
# FORMULAIRES D'ADMINISTRATION (CRUD)
# ======================================

class CategorieForm(FlaskForm):
    nom = StringField("Nom du genre musical (ex: Rap, Jazz)", validators=[DataRequired()])
    submit = SubmitField("Enregistrer la catégorie")

class ActualiteForm(FlaskForm):
    titre = StringField("Titre de l'article", validators=[DataRequired()])
    contenu = TextAreaField("Contenu de la news", validators=[DataRequired()])
    categorie_id = SelectField("Associer à une catégorie", coerce=int)
    submit = SubmitField("Publier maintenant")

class ConcertForm(FlaskForm):
    nom = StringField("Nom de l'événement / Artiste", validators=[DataRequired()])
    lieu = StringField("Salle ou Festival", validators=[DataRequired()])
    date_concert = DateTimeLocalField("Date et heure du show", format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    type_musique = StringField("Genre musical", validators=[DataRequired()])
    places_totales = IntegerField("Capacité maximum", validators=[DataRequired()])
    submit = SubmitField("Ajouter au calendrier")
    prix = IntegerField("Prix du billet (€)", validators=[DataRequired()])

# =================================
# FORMULAIRES D'INTERACTION
# =================================

class CommentaireForm(FlaskForm):
    # Le nom de l'auteur sera récupéré via la session en Python
    contenu = TextAreaField("Votre message", validators=[DataRequired(), Length(max=500)])
    submit = SubmitField("Poster mon avis")

