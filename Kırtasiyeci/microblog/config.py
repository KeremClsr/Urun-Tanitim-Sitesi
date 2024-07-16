import os
temel_dizin = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tahmin-edemezsin'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(temel_dizin, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False