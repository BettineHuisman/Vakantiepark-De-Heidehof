from vakantiepark import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    wachtwoord = db.Column(db.String(60), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'User({self.username}, {self.email})'


class Huistype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    personen = db.Column(db.Integer, nullable=False)
    weekprijs = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Huistype({self.id}, aantal personen: {self.personen}, weekprijs: {self.weekprijs})'
    

class Vakantiehuis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(25), nullable=False, unique=True)
    huistype_id = db.Column(db.Integer, db.ForeignKey('huistype.id'), nullable=False)

    huistype = db.relationship('Huistype', backref=db.backref('vakantiehuizen', lazy=True))

    def __repr__(self):
        return f'Vakantiehuis({self.id}, naam: {self.naam}, type: {self.huistype_id})'


class Boeking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vakantiehuis_id = db.Column(db.Integer, db.ForeignKey('vakantiehuis.id'), nullable=False)
    weeknummer = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref=db.backref('boekingen', lazy=True))
    vakantiehuis = db.relationship('Vakantiehuis', backref=db.backref('boekingen', lazy=True))