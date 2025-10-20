from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import secrets 

# App maken
app = Flask(__name__) 
# app.config['SECRET_KEY'] = "geheime_sleutel"
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///vakantiepark.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Deze regel staat hier zodat ik de boel kan hacken:
app.config['WTF_CSRF_ENABLED'] = True

# Sessie cookies toevoegen
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@app.before_request
def create_tables():
    db.create_all()

# Veilige headers toevoegen
@app.after_request
def set_veilige_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera-()'
    response.headers['Strict-Transport-Security'] =  'max-age=31536000; inculdeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
    )
    return response

from routes import *

# Runnen van de app
if __name__ == '__main__':
    app.run(debug=True)
