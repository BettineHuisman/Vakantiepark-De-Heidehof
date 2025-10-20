from flask import render_template, url_for, flash, redirect, abort, request, session
from functools import wraps
from vakantiepark import app, db, bcrypt
from formulieren import ContactFormulier, InlogFormulier, RegistratieFormulier, VakantiehuisFormulier, WeekFormulier, DummyForm
from datamodel import User, Huistype, Vakantiehuis, Boeking
from flask_login import login_user, current_user, logout_user, login_required

# Admin required decorator maken
def admin_required(f):
    @wraps(f)
    def admin_decorator(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(403)
        if not current_user.admin == True:
            return abort(403)
        return f(*args, **kwargs)
    return admin_decorator


# Informatie/data
boeking = []

# Routes
# Homepage
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title='Home')

# Parkfaciliteiten
@app.route("/parkfaciliteiten")
def parkfaciliteiten():
    return render_template("parkfaciliteiten.html", title="Parkfaciliteiten")

@app.route("/parkfaciliteiten/restaurant")
def restaurant():
    return render_template("restaurant.html", title="De Gouden Koekenpan")

# Vakantiehuisjes
@app.route("/vakantiewoningen")
def vakantiehuisjes():
    return render_template("vakantiehuisjes.html", title="Vakantiewoningen")

@app.route("/vakantiewoningen/huisje_4p")
def huisje_4p():
    huistype = Huistype.query.filter_by(personen=4).first()
    weekprijs = str(huistype.weekprijs)
    return render_template("huisje_4p.html", weekprijs=weekprijs, title="4 Personen")

@app.route("/vakantiewoningen/huisje_6p")
def huisje_6p():
    huistype = Huistype.query.filter_by(personen=6).first()
    weekprijs = str(huistype.weekprijs)
    return render_template("huisje_6p.html", weekprijs=weekprijs, title="6 Personen")

@app.route("/vakantiewoningen/huisje_8p")
def huisje_8p():
    huistype = Huistype.query.filter_by(personen=8).first()
    weekprijs = str(huistype.weekprijs)
    return render_template("huisje_8p.html", weekprijs=weekprijs, title="8 Personen")

# Boeken
@app.route("/boeken", methods=['GET', 'POST'])
@login_required
def boeken():
    formulier = VakantiehuisFormulier()

    # Join om info over het type vakantiehuis te koppelen aan het vakantiehuis
    vakantiewoningen = db.session.query(
        Vakantiehuis.id,
        Vakantiehuis.naam,
        Huistype.personen,
        Huistype.weekprijs
    ).join(Huistype, Vakantiehuis.huistype_id == Huistype.id).all()

    # Alle info in een dictionary verzamelen om alle info in een keuzeblokje weer te geven op het formulier
    formulier.vakantiehuis.choices = [(huis.id, {"naam": huis.naam, "aantal_personen": huis.personen, "weekprijs": huis.weekprijs}) for huis in vakantiewoningen]

    # ID van de geselecteerde woning uit het formulier halen en doorgeven naar de volgende stap in het boekingsproces -> selecteren van een beschikbaar weeknummer
    if formulier.validate_on_submit():
        geselecteerde_woning = formulier.vakantiehuis.data
        return redirect(url_for("selecteer_week", vakantiehuis_id=geselecteerde_woning))
    return render_template("boeken.html", form=formulier, title="Boeken")

@app.route("/boeken/week", methods=['GET', 'POST'])
@login_required
def selecteer_week():
    # ID van de geselecteerde woning ophalen uit het vorige formulier
    vakantiehuis_id = request.args.get("vakantiehuis_id", type=int)
    if not vakantiehuis_id:
        return redirect(url_for("boeken"))

    # Alle nodige info over het geselecteerde huis verzamelen
    woning = Vakantiehuis.query.filter_by(id=vakantiehuis_id).first()
    woning_naam = woning.naam
    huistype = woning.huistype_id
    type = Huistype.query.filter_by(id=huistype).first()
    personen = type.personen
    
    formulier = WeekFormulier()

    # Bepalen welke weken beschikbaar zijn
    bezette_weken = [boeking.weeknummer for boeking in Boeking.query.filter_by(vakantiehuis_id=vakantiehuis_id).all()]
    weeknummers = list(range(1, 53))
    weeknummer_choices = [week for week in weeknummers if week not in bezette_weken]
    formulier.week.choices = weeknummer_choices

    if formulier.validate_on_submit():
        # Data verzamelen om te tonen op de bedankt pagina
        if boeking:
            boeking.pop()
        boeking_data = {
            "typehuisje": f"{personen} personen",
            "vakantiewoning": woning_naam,
            "weeknummer": formulier.week.data
        }
        boeking.append(boeking_data)

        # Data verzamelen om in de database te stoppen
        nieuwe_boeking = Boeking(
            user_id=current_user.id,
            vakantiehuis_id=vakantiehuis_id,
            weeknummer=formulier.week.data
        )
        db.session.add(nieuwe_boeking)
        db.session.commit()         

        return redirect(url_for("bedankt"))
    return render_template("week.html", form=formulier, woning_naam=woning_naam, title="Weeknummer")

@app.route("/boeken/bedankt")
@login_required
def bedankt():
    return render_template("bedankt.html", boeking=boeking, title="Bedankt!")

# Fotogalerij
@app.route("/fotogalerij")
def fotogalerij():
    return render_template("fotogalerij.html", title="Fotogalerij")

# Contact
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    formulier = ContactFormulier()
    if formulier.validate_on_submit():
        naam = formulier.naam.data
        email = formulier.email.data
        bericht = formulier.bericht.data
        flash('Bedankt voor uw bericht!', 'success')
        return redirect(url_for('contact'))
    return render_template("contact.html", form=formulier, title="Contact")
    
# Login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    formulier = InlogFormulier()
    if formulier.validate_on_submit():
        user = User.query.filter_by(email=formulier.email.data).first()
        if user and bcrypt.check_password_hash(user.wachtwoord, formulier.wachtwoord.data):
            login_user(user, remember=True)
            flash("Succesvol ingelogd!", "success") 
            if user.admin == True:
                return redirect(url_for("beheer_admin"))
            else:          
                return redirect(url_for("mijn_boeking"))
        else:
            flash("Inloggen mislukt. Controleer je email en wachtwoord.", "danger")
    return render_template("login.html", form=formulier, title="Login")

# Logout
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# Registreren
@app.route("/registreren", methods=['GET', 'POST'])
def registreren():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    formulier = RegistratieFormulier()
    if formulier.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(formulier.wachtwoord.data).decode('utf-8')
        user = User(
            username=formulier.username.data, 
            email=formulier.email.data, 
            wachtwoord=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash("Succesvol geregistreerd! Je kunt nu inloggen", "success")
        return redirect(url_for("login"))
    return render_template("registreren.html", form=formulier, title="Registreren")


# Beheer boekingen -> klant 
@app.route("/mijn_boeking")
@login_required
def mijn_boeking():
    formulier = DummyForm()
    # mijn_boekingen = Boeking.query.filter_by(user_id=current_user.id).all()
    mijn_boekingen = db.session.query(
        Boeking.id,
        Boeking.user_id,
        Boeking.vakantiehuis_id,
        Boeking.weeknummer,
        Vakantiehuis.naam,
        Huistype.personen,
        Huistype.weekprijs
    ).join(Vakantiehuis, Boeking.vakantiehuis_id == Vakantiehuis.id
    ).join(Huistype, Vakantiehuis.huistype_id == Huistype.id
    ).filter(Boeking.user_id == current_user.id
    ).order_by(Boeking.weeknummer.asc()
    ).all()

    return render_template("mijn_boeking.html", form=formulier, mijn_boekingen=mijn_boekingen, title="Mijn Boeking")

@app.route("/mijn_boeking/wijzig_huisje/<int:boeking_id>", methods=['GET', 'POST'])
@login_required
def wijzig_huisje(boeking_id):
    boeking = Boeking.query.get_or_404(boeking_id)
    formulier = VakantiehuisFormulier(obj=boeking)

    # Beschikbare huisjes voor de al gekozen week selecteren + het al gekozen huisje boven aan de lijst zetten
    boekingen_in_zelfde_week = Boeking.query.filter_by(weeknummer=boeking.weeknummer).all()
    bezette_huisjes = [huisje.vakantiehuis_id for huisje in boekingen_in_zelfde_week]
    alle_huisjes = Vakantiehuis.query.all()
    alle_huisjes_ID = [huisje.id for huisje in alle_huisjes]
    beschikbare_huisjes = [huisje for huisje in alle_huisjes_ID if huisje not in bezette_huisjes]
    beschikbare_huisjes = [boeking.vakantiehuis_id] + beschikbare_huisjes

    # Alle gegevens verzamelen om weer te geven op het formulier
    vakantiehuis_choices = []
    for huisje in beschikbare_huisjes:
        vakantiewoning = db.session.query(
            Vakantiehuis.id,
            Vakantiehuis.naam,
            Huistype.personen,
            Huistype.weekprijs
        ).join(Huistype, Vakantiehuis.huistype_id == Huistype.id
        ).filter(Vakantiehuis.id == huisje
        ).first()
        vakantiehuis_choices.append(vakantiewoning)

    formulier.vakantiehuis.choices = [(huis.id, {"naam": huis.naam, "aantal_personen": huis.personen, "weekprijs": huis.weekprijs}) for huis in vakantiehuis_choices]

    if formulier.validate_on_submit():
        boeking.vakantiehuis_id = formulier.vakantiehuis.data
        db.session.commit()
        flash('Je boeking is gewijzigd', 'success')
        return redirect(url_for("mijn_boeking"))
    return render_template("wijzig_huisje.html", form=formulier, boeking=boeking, title="Boeking Wijzigen")


@app.route("/mijn_boeking/wijzig_week/<int:boeking_id>", methods=['GET', 'POST'])
@login_required
def wijzig_week(boeking_id):
    # Boekeing + naam van de vakantiewoning ophalen uit de database
    boeking = Boeking.query.get_or_404(boeking_id)
    woning = Vakantiehuis.query.filter_by(id=boeking.vakantiehuis_id).first()
    woning_naam = woning.naam

    # Formulier specifiek voor de bijbehorende boeking
    formulier = WeekFormulier(obj=boeking)

    # Beschikbare weken uit de database halen + de al geboekte week bovenaan de keuzelijst zetten
    bezette_weken = [boeking.weeknummer for boeking in Boeking.query.filter_by(vakantiehuis_id=boeking.vakantiehuis_id).all()]
    weeknummers = list(range(1, 53))
    weeknummer_choices = [week for week in weeknummers if week not in bezette_weken]
    weeknummer_choices = [boeking.weeknummer] + weeknummer_choices
    formulier.week.choices = weeknummer_choices

    # Week aanpassen in de database
    if formulier.validate_on_submit():
        boeking.weeknummer = formulier.week.data
        db.session.commit()
        flash('Je boeking is gewijzigd', 'success')
        return redirect(url_for("mijn_boeking"))
    return render_template("wijzig_week.html", form=formulier, boeking=boeking, woning_naam=woning_naam, title="Boeking Wijzigen")

@app.route("/mijn_boeking/annuleren/<int:boeking_id>", methods=['POST'])
@login_required
def annuleer_boeking(boeking_id):
    boeking = Boeking.query.get_or_404(boeking_id)
    db.session.delete(boeking)
    db.session.commit()
    flash('Je hebt je boeking geannuleerd', 'warning')
    return redirect(url_for('mijn_boeking'))

# Beheer boekingen -> admin
@app.route("/beheer_admin")
@login_required
@admin_required
def beheer_admin():
    formulier = DummyForm()
    boekingen = db.session.query(
        Boeking.id,
        Boeking.user_id,
        Boeking.vakantiehuis_id,
        Boeking.weeknummer,
        Vakantiehuis.naam,
        Huistype.personen,
        Huistype.weekprijs,
        User.username,
        User.email
    ).join(Vakantiehuis, Boeking.vakantiehuis_id == Vakantiehuis.id
    ).join(Huistype, Vakantiehuis.huistype_id == Huistype.id
    ).join(User, Boeking.user_id == User.id
    ).order_by(Boeking.weeknummer.asc()
    ).all()

    return render_template("admin.html", form=formulier, boekingen=boekingen, title="Beheer Boekingen")
    
@app.route("/beheer_admin/vrijgeven/<int:boeking_id>", methods=['POST'])
@login_required
@admin_required
def woning_vrijgeven(boeking_id):
    boeking = Boeking.query.get_or_404(boeking_id)
    db.session.delete(boeking)
    db.session.commit()
    flash('Woning is vrijgegeven', 'primary')
    return redirect(url_for('beheer_admin'))   

@app.route("/beheer_admin/wijzig_huisje/<int:boeking_id>", methods=['GET', 'POST'])
@login_required
@admin_required
def wijzig_huisje_admin(boeking_id):
    boeking = Boeking.query.get_or_404(boeking_id)
    formulier = VakantiehuisFormulier(obj=boeking)

    # Beschikbare huisjes voor de al gekozen week selecteren + het al gekozen huisje boven aan de lijst zetten
    boekingen_in_zelfde_week = Boeking.query.filter_by(weeknummer=boeking.weeknummer).all()
    bezette_huisjes = [huisje.vakantiehuis_id for huisje in boekingen_in_zelfde_week]
    alle_huisjes = Vakantiehuis.query.all()
    alle_huisjes_ID = [huisje.id for huisje in alle_huisjes]
    beschikbare_huisjes = [huisje for huisje in alle_huisjes_ID if huisje not in bezette_huisjes]
    beschikbare_huisjes = [boeking.vakantiehuis_id] + beschikbare_huisjes

    # Alle gegevens verzamelen om weer te geven op het formulier
    vakantiehuis_choices = []
    for huisje in beschikbare_huisjes:
        vakantiewoning = db.session.query(
            Vakantiehuis.id,
            Vakantiehuis.naam,
            Huistype.personen,
            Huistype.weekprijs
        ).join(Huistype, Vakantiehuis.huistype_id == Huistype.id
        ).filter(Vakantiehuis.id == huisje
        ).first()
        vakantiehuis_choices.append(vakantiewoning)

    formulier.vakantiehuis.choices = [(huis.id, {"naam": huis.naam, "aantal_personen": huis.personen, "weekprijs": huis.weekprijs}) for huis in vakantiehuis_choices]

    if formulier.validate_on_submit():
        boeking.vakantiehuis_id = formulier.vakantiehuis.data
        db.session.commit()
        flash('Boeking is gewijzigd', 'success')
        return redirect(url_for("beheer_admin"))
    return render_template("wijzig_huisje.html", form=formulier, boeking=boeking, title="Boeking Wijzigen")

@app.route("/beheer_admin/wijzig_week/<int:boeking_id>", methods=['GET', 'POST'])
@login_required
@admin_required
def wijzig_week_admin(boeking_id):
    # Boekeing + naam van de vakantiewoning ophalen uit de database
    boeking = Boeking.query.get_or_404(boeking_id)
    woning = Vakantiehuis.query.filter_by(id=boeking.vakantiehuis_id).first()
    woning_naam = woning.naam

    # Formulier specifiek voor de bijbehorende boeking
    formulier = WeekFormulier(obj=boeking)

    # Beschikbare weken uit de database halen + de al geboekte week bovenaan de keuzelijst zetten
    bezette_weken = [boeking.weeknummer for boeking in Boeking.query.filter_by(vakantiehuis_id=boeking.vakantiehuis_id).all()]
    weeknummers = list(range(1, 53))
    weeknummer_choices = [week for week in weeknummers if week not in bezette_weken]
    weeknummer_choices = [boeking.weeknummer] + weeknummer_choices
    formulier.week.choices = weeknummer_choices

    # Week aanpassen in de database
    if formulier.validate_on_submit():
        boeking.weeknummer = formulier.week.data
        db.session.commit()
        flash('Boeking is gewijzigd', 'success')
        return redirect(url_for("beheer_admin"))
    return render_template("wijzig_week.html", form=formulier, boeking=boeking, woning_naam=woning_naam, title="Boeking Wijzigen")

# 403
@app.errorhandler(403)
def verboden(e):
    return render_template("403.html", title="Error 403"), 403

# 404
@app.errorhandler(404)
def pagina_niet_gevonden(e):
    return render_template("404.html", title="Error 404"), 404