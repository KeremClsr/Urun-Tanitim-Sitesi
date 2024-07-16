from app import db, giris_yoneticisi
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.sql import func

class Kullanici(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_adi = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    parola_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    incelemeler = db.relationship('Inceleme', back_populates='yazar', lazy='dynamic')
    
    def parola_ayarla(self, parola):
        self.parola_hash = generate_password_hash(parola)

    def parola_kontrol(self, parola):
        return check_password_hash(self.parola_hash, parola)

@giris_yoneticisi.user_loader
def kullanici_yukle(id):
    return Kullanici.query.get(int(id))

class Urun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), index=True)
    aciklama = db.Column(db.String(500))
    fotograf = db.Column(db.String(200))
    incelemeler = db.relationship('Inceleme', back_populates='urun', lazy='dynamic', cascade='all, delete-orphan')

    def ortalama_puan(self):
        result = db.session.query(func.avg(Inceleme.puan)).filter(Inceleme.urun_id == self.id).scalar()
        return round(result, 2) if result else None
    
class Inceleme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    icerik = db.Column(db.String(500))
    puan = db.Column(db.Integer)
    tarih = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    kullanici_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'))
    urun_id = db.Column(db.Integer, db.ForeignKey('urun.id'))
    
    yazar = db.relationship('Kullanici', back_populates='incelemeler')
    urun = db.relationship('Urun', back_populates='incelemeler')