from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from app.models import Kullanici

class KayitFormu(FlaskForm):
    kullanici_adi = StringField('Kullanıcı Adı', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    parola = PasswordField('Parola', validators=[DataRequired()])
    parola2 = PasswordField('Parolayı Tekrar Girin', validators=[DataRequired(), EqualTo('parola')])
    gonder = SubmitField('Kayıt Ol')

    def validate_kullanici_adi(self, kullanici_adi):
        kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi.data).first()
        if kullanici is not None:
            raise ValidationError('Lütfen farklı bir kullanıcı adı deneyin.')

    def validate_email(self, email):
        kullanici = Kullanici.query.filter_by(email=email.data).first()
        if kullanici is not None:
            raise ValidationError('Lütfen farklı bir email adresi deneyin.')

class GirisFormu(FlaskForm):
    kullanici_adi = StringField('Kullanıcı Adı', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    parola = PasswordField('Parola', validators=[DataRequired()])
    beni_hatirla = BooleanField('Beni Hatırla')
    gonder = SubmitField('Giriş Yap')

class UrunEkleFormu(FlaskForm):
    isim = StringField('Ürün Adı', validators=[DataRequired()])
    aciklama = TextAreaField('Açıklama', validators=[DataRequired()])
    fotograf = StringField('Fotoğraf URL', validators=[DataRequired()])
    gonder = SubmitField('Ürün Ekle')
    
class IncelemeEkleFormu(FlaskForm):
    icerik = TextAreaField('İnceleme', validators=[DataRequired(), Length(min=10, max=500)])
    puan = IntegerField('Puan (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    gonder = SubmitField('İnceleme Ekle')

class AramaFormu(FlaskForm):
    arama = StringField('Ürün Ara', validators=[DataRequired()])
    gonder = SubmitField('Ara')

class ProfilGuncellemeFormu(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    eski_parola = PasswordField('Mevcut Parola', validators=[DataRequired()])
    yeni_parola = PasswordField('Yeni Parola', validators=[DataRequired()])
    yeni_parola2 = PasswordField('Yeni Parola (Tekrar)', validators=[DataRequired(), EqualTo('yeni_parola')])
    gonder = SubmitField('Güncelle')

    def __init__(self, original_email, *args, **kwargs):
        super(ProfilGuncellemeFormu, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            kullanici = Kullanici.query.filter_by(email=email.data).first()
            if kullanici:
                raise ValidationError('Bu e-posta adresini zaten başkası kullanıyor. Lütfen biraz özgün olun.')