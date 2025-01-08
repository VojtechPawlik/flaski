# Standard Library imports

# Core Flask imports
from flask import Blueprint, render_template

# Third-party imports

# App imports
from app import db_manager
from app import login_manager
from .views import (
    error_views,
    account_management_views,
    static_views,
)
from .models import User,Uzivatele,Kniha,SPZ

bp = Blueprint('routes', __name__)

# alias
db = db_manager.session
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField,DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length,InputRequired

class FormFormular(FlaskForm):
    name = StringField('Name', validators=[ InputRequired(message="You can't leave this empty")])
    surename = StringField('Surename', validators=[ InputRequired(message="You can't leave this empty")])

@bp.route("/formular", methods=["GET", "POST"])
def formular():
    form=FormFormular()
    if form.validate_on_submit():
        print(form.name.data)
        new_user = Uzivatele(name=form.name.data, surename=form.surename.data)
        db.add(new_user)
        db.commit()
        return "Formular submitted"
    return render_template("formular.html",form=form)
# Request management
class KnihaForm(FlaskForm):
    nazev = StringField('nazev', validators=[InputRequired(message="Title is required"), Length(max=255)])
    iban = StringField('iban', validators=[InputRequired(message="Author is required"), Length(max=255)])
    popisek = StringField('popisek', validators=[InputRequired(message="Published date is required")])

@bp.route("/add_kniha", methods=["GET", "POST"])
def kniha():
    form = KnihaForm()
    if form.validate_on_submit():
        new_kniha = Kniha(nazev=form.nazev.data, iban=form.iban.data, popisek=form.popisek.data)
        db.add(new_kniha)
        db.commit()
        return "Kniha submitted"
    return render_template("kniha.html", form=form)

@bp.route("/list_knih", methods=["GET"])
def list_knih():
    knihy = Kniha.query.all()
    return render_template("list_knih.html", knihy=knihy)

@bp.route("/del_kniha/<int:id>", methods=["GET", "POST"])
def smaz_knihu(id):
    kniha = Kniha.query.get(id)
    if kniha:
        db.delete(kniha)
        db.commit()
        return f"Kniha with id {id} has been deleted"
    return f"Kniha with id {id} not found", 404

class EditaceSPZForm(FlaskForm):
    spz = StringField('SPZ', validators=[InputRequired(message="SPZ is required"), Length(max=10)])
    typ_vozidla = StringField('Typ Vozidla', validators=[InputRequired(message="Typ Vozidla is required"), Length(max=50)])
    datum_zarazeni = DateField('Datum Zarazeni', validators=[InputRequired(message="Datum Zarazeni is required")])

@bp.route("/editace_spz/<int:id>", methods=["GET", "POST"])
def editace_spz(id):
    spz_record = Spz.query.get(id)
    if not spz_record:
        return f"Record with id {id} not found", 404

    form = EditaceSPZForm(obj=spz_record)
    if form.validate_on_submit():
        spz_record.spz = form.spz.data
        spz_record.typ_vozidla = form.typ_vozidla.data
        spz_record.datum_zarazeni = form.datum_zarazeni.data
        db.commit()
        return f"Record with id {id} has been updated"
    
    return render_template("spz.html", form=form, spz_record=spz_record)

class AddSPZForm(FlaskForm):
    spz = StringField('SPZ', validators=[InputRequired(message="SPZ is required"), Length(max=10)])
    typ_vozidla = StringField('Typ Vozidla', validators=[InputRequired(message="Typ Vozidla is required"), Length(max=50)])
    datum_zarazeni = DateField('Datum Zarazeni', validators=[InputRequired(message="Datum Zarazeni is required")])

@bp.route("/add_spz", methods=["GET", "POST"])
def add_spz():
    form = AddSPZForm()
    if form.validate_on_submit():
        new_spz = Spz(spz=form.spz.data, typ_vozidla=form.typ_vozidla.data, datum_zarazeni=form.datum_zarazeni.data)
        db.add(new_spz)
        db.commit()
        return "SPZ submitted"
    return render_template("spz.html", form=form)

@bp.before_app_request
def before_request():
    db()

@bp.teardown_app_request
def shutdown_session(response_or_exc):
    db.remove()

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    if user_id and user_id != "None":
        return User.query.filter_by(user_id=user_id).first()

# Error views
bp.register_error_handler(404, error_views.not_found_error)

bp.register_error_handler(500, error_views.internal_error)

# Public views
bp.add_url_rule("/", view_func=static_views.index)

bp.add_url_rule("/register", view_func=static_views.register)

bp.add_url_rule("/login", view_func=static_views.login)

# Login required views
bp.add_url_rule("/settings", view_func=static_views.settings)

# Public API
bp.add_url_rule(
   "/api/login", view_func=account_management_views.login_account, methods=["POST"]
)

bp.add_url_rule("/logout", view_func=account_management_views.logout_account)

bp.add_url_rule(
   "/api/register",
   view_func=account_management_views.register_account,
   methods=["POST"],
)

# Login Required API
bp.add_url_rule("/api/user", view_func=account_management_views.user)

bp.add_url_rule(
   "/api/email", view_func=account_management_views.email, methods=["POST"]
)

# Admin required
bp.add_url_rule("/admin", view_func=static_views.admin)
