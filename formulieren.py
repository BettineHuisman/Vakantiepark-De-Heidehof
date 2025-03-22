from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from datamodel import User

# Formulieren
# Sleutel niet vergeten! -> in de HTML

class BoekingsFormulier(FlaskForm):
    vakantiewoning = SelectField("Vakantiewoning", choices=[], validators=[DataRequired()])
    weeknummer = SelectField("Weeknummer", choices=[], validators=[DataRequired(message="Maak een keuze")])
    boeken = SubmitField('Boeken') 


class VakantiehuisFormulier(FlaskForm):
    vakantiehuis = RadioField("Vakantiewoning", coerce=int, validators=[DataRequired()])
    volgende = SubmitField("Volgende")

class WeekFormulier(FlaskForm):
    week = SelectField("Weeknummer", choices=[], validators=[DataRequired()])
    boeken = SubmitField("Boeken")

class ContactFormulier(FlaskForm):
    naam = StringField('Naam', validators=[DataRequired()], render_kw={"placeholder": "Vul je naam in"})
    email = StringField("E-mailadres", validators=[DataRequired(), Email(message="Voer een geldig e-mailadres in")], render_kw={"placeholder": "Vul je e-mailadres in"})
    bericht = TextAreaField("Bericht", validators=[DataRequired()], render_kw={"placeholder": "Schrijf hier je bericht"})
    verstuur = SubmitField("Versturen") 

class InlogFormulier(FlaskForm):
    email = StringField("E-mailadres", validators=[DataRequired(), Email(message="Voer een geldig e-mailadres in")])
    wachtwoord = PasswordField("Wachtwoord", validators=[DataRequired()])
    inloggen = SubmitField('Log in')

class RegistratieFormulier(FlaskForm):
    username = StringField("Gebruikersnaam", validators=[DataRequired()], render_kw={"placeholder": "Vul een (gebruikers)naam in"})
    email = StringField("E-mailadres", validators=[DataRequired(), Email(message="Voer een geldig e-mailadres in")], render_kw={"placeholder": "Vul je e-mailadres in"})
    wachtwoord = PasswordField("Wachtwoord", validators=[DataRequired()], render_kw={"placeholder": "Bedenk een wachtwoord"})
    bevestig_wachtwoord = PasswordField("Bevestig Wachtwoord", validators=[DataRequired(), EqualTo('wachtwoord', message="Deze invoer is niet gelijk aan het opgegeven wachtwoord.")], render_kw={"placeholder": "Herhaal je wachtwoord"})
    registreer = SubmitField('Registreren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Deze gebruikersnaam wordt al door iemand anders gebruikt.")
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Dit e-mailadres is al geregistreerd.")




