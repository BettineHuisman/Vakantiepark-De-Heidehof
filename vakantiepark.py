from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# App maken
app = Flask(__name__) 
app.config['SECRET_KEY'] = "geheime_sleutel"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///vakantiepark.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@app.before_request
def create_tables():
    db.create_all()

from routes import *

# Runnen van de app
if __name__ == '__main__':
    app.run(debug=True)
