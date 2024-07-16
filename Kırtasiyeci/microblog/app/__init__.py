from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
giris_yoneticisi = LoginManager(app)
giris_yoneticisi.login_view = 'giris'
giris_yoneticisi.login_message = 'Sizi tanımıyorum, lütfen bu sayfayı görüntülemek için giriş yapın.'

from app import routes, models

def create_app():
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    return app

from app import db
from app.models import Kullanici
from app import errors

csrf = CSRFProtect(app)