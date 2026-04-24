from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False, unique=True)
    actualites = db.relationship('Actualite', backref='categorie', lazy=True)

class Actualite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(150), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'), nullable=False)
    commentaires = db.relationship('Commentaire', backref='actualite', lazy=True)

class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    est_admin = db.Column(db.Boolean, default=False)
    reservations = db.relationship('Reservation', backref='utilisateur', lazy=True)

class Concert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(150), nullable=False)
    date_concert = db.Column(db.DateTime, nullable=False)
    lieu = db.Column(db.String(150), nullable=False)
    type_musique = db.Column(db.String(50), nullable=False)
    places_totales = db.Column(db.Integer, nullable=False)
    avis_redacteur = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(255), nullable=True)
    commentaires = db.relationship('Commentaire', backref='concert', lazy=True)
    prix = db.Column(db.Float, nullable=False, default=0.0)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nb_places = db.Column(db.Integer, nullable=False)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=False)
    concert_id = db.Column(db.Integer, db.ForeignKey('concert.id'), nullable=False)

class Commentaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_auteur = db.Column(db.String(100), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    concert_id = db.Column(db.Integer, db.ForeignKey('concert.id'), nullable=True)
    actualite_id = db.Column(db.Integer, db.ForeignKey('actualite.id'), nullable=True)