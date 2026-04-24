from flask import Blueprint, render_template, flash, redirect, url_for, session, abort, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func
from models import db, Utilisateur, Categorie, Actualite, Concert, Reservation, Commentaire
from controllers.forms import InscriptionForm, ConnexionForm, CategorieForm, ActualiteForm, ConcertForm, CommentaireForm

main_bp = Blueprint('main', __name__)

# =========================
# ROUTES PUBLIQUES
# =========================

@main_bp.route('/')
def accueil():
    maintenant = datetime.now()
    actus = Actualite.query.order_by(Actualite.date_creation.desc()).limit(3).all()
    prochains = Concert.query.filter(Concert.date_concert >= maintenant).order_by(Concert.date_concert.asc()).limit(4).all()
    return render_template('index.html', actualites=actus, concerts=prochains)

@main_bp.route('/actualites')
def actualites():
    actus = Actualite.query.order_by(Actualite.date_creation.desc()).all()
    return render_template('actualites.html', actualites=actus)

@main_bp.route('/actualite/<int:id>')
def detail_actualite(id):
    actu = Actualite.query.get_or_404(id)
    return render_template('actualite_detail.html', actu=actu)

@main_bp.route('/concerts')
def concerts():
    maintenant = datetime.now()
    f_genre = request.args.get('genre', '')
    f_lieu = request.args.get('lieu', '')
    f_date = request.args.get('date', '')
    f_prix_max = request.args.get('prix_max', '')

    query = Concert.query.filter(Concert.date_concert >= maintenant)
    if f_genre: query = query.filter(Concert.type_musique.ilike(f"%{f_genre}%"))
    if f_lieu: query = query.filter(Concert.lieu.ilike(f"%{f_lieu}%"))
    if f_date: query = query.filter(func.date(Concert.date_concert) == f_date)
    if f_prix_max:
        try: query = query.filter(Concert.prix <= float(f_prix_max))
        except ValueError: pass

    a_venir = query.order_by(Concert.date_concert.asc()).all()
    passes = Concert.query.filter(Concert.date_concert < maintenant).order_by(Concert.date_concert.desc()).limit(6).all()
    return render_template('concerts.html', concerts=a_venir, concerts_passes=passes, f_genre=f_genre, f_lieu=f_lieu, f_date=f_date, f_prix_max=f_prix_max)

@main_bp.route('/concert/<int:id>', methods=['GET', 'POST'])
def detail_concert(id):
    concert = Concert.query.get_or_404(id)
    maintenant = datetime.now()
    places_prises = db.session.query(func.sum(Reservation.nb_places)).filter(Reservation.concert_id == id).scalar() or 0
    restantes = concert.places_totales - places_prises

    if request.method == 'POST':
        if not session.get('utilisateur_id'): return redirect(url_for('main.connexion'))
        nb = int(request.form.get('nb_places', 0))
        if 0 < nb <= restantes:
            db.session.add(Reservation(nb_places=nb, utilisateur_id=session['utilisateur_id'], concert_id=id))
            db.session.commit()
            flash(f"Réservation confirmée !", "success")
            return redirect(url_for('main.detail_concert', id=id))
    return render_template('concert_detail.html', concert=concert, maintenant=maintenant, places_restantes=restantes)

@main_bp.route('/genre/<string:nom>')
def filtrer_genre(nom):
    maintenant = datetime.now()
    cat = Categorie.query.filter(Categorie.nom.ilike(nom)).first()
    actus = Actualite.query.filter_by(categorie_id=cat.id).all() if cat else []
    cons = Concert.query.filter((Concert.type_musique.ilike(nom)) & (Concert.date_concert >= maintenant)).all()
    return render_template('genre.html', genre=nom, actualites=actus, concerts=cons)

# ==================================
# ACTIONS & AUTHENTIFICATION
# ==================================

@main_bp.route('/poster_commentaire/<string:type_objet>/<int:id_objet>', methods=['POST'])
def poster_commentaire(type_objet, id_objet):
    if not session.get('utilisateur_id'): return redirect(url_for('main.connexion'))
    contenu = request.form.get('contenu')
    if contenu:
        c = Commentaire(nom_auteur=session.get('utilisateur_nom'), contenu=contenu)
        if type_objet == 'actualite':
            c.actualite_id = id_objet
            dest = url_for('main.detail_actualite', id=id_objet)
        else:
            c.concert_id = id_objet
            dest = url_for('main.detail_concert', id=id_objet)
        db.session.add(c)
        db.session.commit()
    return redirect(dest)

@main_bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    form = InscriptionForm()
    if form.validate_on_submit():
        h_pass = generate_password_hash(form.password.data)
        db.session.add(Utilisateur(nom=form.nom.data, email=form.email.data, mot_de_passe=h_pass))
        db.session.commit()
        return redirect(url_for('main.connexion'))
    return render_template('inscription.html', form=form)

@main_bp.route('/connexion', methods=['GET', 'POST'])
def connexion():
    form = ConnexionForm()
    if form.validate_on_submit():
        u = Utilisateur.query.filter_by(email=form.email.data).first()
        if u and check_password_hash(u.mot_de_passe, form.password.data):
            session.update({'utilisateur_id': u.id, 'utilisateur_nom': u.nom, 'est_admin': u.est_admin})
            return redirect(url_for('main.accueil'))
    return render_template('connexion.html', form=form)

@main_bp.route('/deconnexion')
def deconnexion():
    session.clear()
    return redirect(url_for('main.accueil'))

# ================================
# ADMINISTRATION (CRUD COMPLET)
# ================================
@main_bp.route('/admin')
def admin_dashboard():
    if not session.get('est_admin'): abort(403)
    return render_template('admin/dashboard.html')

# --- Catégories ---
@main_bp.route('/admin/categories')
def admin_categories():
    if not session.get('est_admin'): abort(403)
    return render_template('admin/categories.html', categories=Categorie.query.all())

@main_bp.route('/admin/categorie/ajouter', methods=['GET', 'POST'])
def ajouter_categorie():
    if not session.get('est_admin'): abort(403)
    form = CategorieForm()
    if form.validate_on_submit():
        db.session.add(Categorie(nom=form.nom.data))
        db.session.commit()
        return redirect(url_for('main.admin_categories'))
    return render_template('admin/form_generique.html', form=form, titre="Ajouter Catégorie")

@main_bp.route('/admin/categorie/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_categorie(id):
    if not session.get('est_admin'): abort(403)
    cat = Categorie.query.get_or_404(id)
    form = CategorieForm(obj=cat)
    if form.validate_on_submit():
        cat.nom = form.nom.data
        db.session.commit()
        return redirect(url_for('main.admin_categories'))
    return render_template('admin/form_generique.html', form=form, titre="Modifier Catégorie")

@main_bp.route('/admin/categorie/supprimer/<int:id>')
def supprimer_categorie(id):
    if not session.get('est_admin'): abort(403)
    cat = Categorie.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    return redirect(url_for('main.admin_categories'))

# --- Actualités ---
@main_bp.route('/admin/actualites')
def admin_actualites():
    if not session.get('est_admin'): abort(403)
    return render_template('admin/actualites.html', actualites=Actualite.query.all())

@main_bp.route('/admin/actualite/ajouter', methods=['GET', 'POST'])
def ajouter_actualite():
    if not session.get('est_admin'): abort(403)
    form = ActualiteForm()
    form.categorie_id.choices = [(c.id, c.nom) for c in Categorie.query.all()]
    if form.validate_on_submit():
        db.session.add(Actualite(titre=form.titre.data, contenu=form.contenu.data, categorie_id=form.categorie_id.data))
        db.session.commit()
        return redirect(url_for('main.admin_actualites'))
    return render_template('admin/form_generique.html', form=form, titre="Ajouter News")

@main_bp.route('/admin/actualite/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_actualite(id):
    if not session.get('est_admin'): abort(403)
    actu = Actualite.query.get_or_404(id)
    form = ActualiteForm(obj=actu)
    form.categorie_id.choices = [(c.id, c.nom) for c in Categorie.query.all()]
    if form.validate_on_submit():
        actu.titre, actu.contenu, actu.categorie_id = form.titre.data, form.contenu.data, form.categorie_id.data
        db.session.commit()
        return redirect(url_for('main.admin_actualites'))
    return render_template('admin/form_generique.html', form=form, titre="Modifier News")

@main_bp.route('/admin/actualite/supprimer/<int:id>')
def supprimer_actualite(id):
    if not session.get('est_admin'): abort(403)
    db.session.delete(Actualite.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('main.admin_actualites'))

# --- Concerts ---
@main_bp.route('/admin/concerts')
def admin_concerts():
    if not session.get('est_admin'): abort(403)
    return render_template('admin/concerts.html', concerts=Concert.query.all())

@main_bp.route('/admin/concert/ajouter', methods=['GET', 'POST'])
def ajouter_concert():
    if not session.get('est_admin'): abort(403)
    form = ConcertForm()
    if form.validate_on_submit():
        new_c = Concert(nom=form.nom.data, lieu=form.lieu.data, date_concert=form.date_concert.data, 
                        type_musique=form.type_musique.data, places_totales=form.places_totales.data,
                        prix=form.prix.data)
        db.session.add(new_c)
        db.session.commit()
        return redirect(url_for('main.admin_concerts'))
    return render_template('admin/form_generique.html', form=form, titre="Ajouter Concert")

@main_bp.route('/admin/concert/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_concert(id):
    if not session.get('est_admin'): abort(403)
    con = Concert.query.get_or_404(id)
    form = ConcertForm(obj=con)
    if form.validate_on_submit():
        form.populate_obj(con)
        db.session.commit()
        return redirect(url_for('main.admin_concerts'))
    return render_template('admin/form_generique.html', form=form, titre="Modifier Concert")

@main_bp.route('/admin/concert/supprimer/<int:id>')
def supprimer_concert(id):
    if not session.get('est_admin'): abort(403)
    db.session.delete(Concert.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('main.admin_concerts'))