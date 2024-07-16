from flask_wtf import FlaskForm
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app import app, db
from app.forms import KayitFormu, GirisFormu, UrunEkleFormu, IncelemeEkleFormu, AramaFormu, ProfilGuncellemeFormu
from app.models import Kullanici, Urun, Inceleme

@app.route('/')
@app.route('/index')
def index():
    urunler = Urun.query.all()
    return render_template('anasayfa.html', title='Ana Sayfa', urunler=urunler)

@app.route('/urun/<int:urun_id>')
def urun_detay(urun_id):
    urun = Urun.query.get_or_404(urun_id)
    form = FlaskForm()
    return render_template('urun_detay.html', title=urun.isim, urun=urun, form=form)

@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = KayitFormu()
    if form.validate_on_submit():
        kullanici = Kullanici(kullanici_adi=form.kullanici_adi.data, email=form.email.data)
        kullanici.parola_ayarla(form.parola.data)
        db.session.add(kullanici)
        db.session.commit()
        flash('Tebrikler, kayıt oldunuz!', 'success')
        return redirect(url_for('giris'))
    return render_template('kayit.html', title='Kayıt Ol', form=form)

@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = GirisFormu()
    if form.validate_on_submit():
        kullanici = Kullanici.query.filter_by(email=form.email.data).first()
        if kullanici is None or not kullanici.parola_kontrol(form.parola.data):
            flash('Geçersiz email veya parola', 'danger')
            return redirect(url_for('giris'))
        login_user(kullanici, remember=form.beni_hatirla.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('giris.html', title='Giriş Yap', form=form)

@app.route('/cikis')
def cikis():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'info')
    return redirect(url_for('index'))

@app.route('/urun_ekle', methods=['GET', 'POST'])
@login_required
def urun_ekle():
    if not current_user.is_admin:
        flash('Bu işlem için yönetici yetkisi gerekiyor.', 'danger')
        return redirect(url_for('index'))
    
    form = UrunEkleFormu()
    if form.validate_on_submit():
        urun = Urun(isim=form.isim.data, aciklama=form.aciklama.data, fotograf=form.fotograf.data)
        db.session.add(urun)
        db.session.commit()
        flash('Ürün başarıyla eklendi!', 'success')
        return redirect(url_for('index'))
    return render_template('urun_ekle.html', title='Ürün Ekle', form=form)

@app.route('/inceleme_ekle/<int:urun_id>', methods=['GET', 'POST'])
@login_required
def inceleme_ekle(urun_id):
    urun = Urun.query.get_or_404(urun_id)

    mevcut_inceleme = Inceleme.query.filter_by(kullanici_id=current_user.id, urun_id=urun.id).first()
    if mevcut_inceleme:
        flash('Bir ürüne birden fazla yorum / puanlama yapamazsınız.', 'warning')
        return redirect(url_for('urun_detay', urun_id=urun.id))

    form = IncelemeEkleFormu()
    if form.validate_on_submit():
        inceleme = Inceleme(icerik=form.icerik.data, 
                            puan=form.puan.data,
                            kullanici_id=current_user.id, 
                            urun_id=urun.id)
        db.session.add(inceleme)
        db.session.commit()
        flash('İncelemeniz başarıyla eklendi!', 'success')
        return redirect(url_for('urun_detay', urun_id=urun.id))
    return render_template('inceleme_ekle.html', title='İnceleme Ekle', form=form, urun=urun)

from flask_wtf import FlaskForm

@app.route('/yonetici')
@login_required
def yonetici_paneli():
    if not current_user.is_admin:
        abort(403)
    urunler = Urun.query.all()
    incelemeler = Inceleme.query.all()
    kullanicilar = Kullanici.query.all()
    form = FlaskForm()
    return render_template('yonetici_paneli.html', title='Yönetici Paneli', 
                           urunler=urunler, incelemeler=incelemeler, kullanicilar=kullanicilar, form=form)

@app.route('/urun_sil/<int:urun_id>', methods=['POST'])
@login_required
def urun_sil(urun_id):
    if not current_user.is_admin:
        flash('Bu işlemi yapmaya yetkiniz yok.', 'danger')
        return redirect(url_for('index'))
    
    urun = Urun.query.get_or_404(urun_id)
    db.session.delete(urun)
    db.session.commit()
    flash(f'{urun.isim} adlı ürün ve ona ait tüm incelemeler başarıyla silindi.', 'success')
    return redirect(url_for('yonetici_paneli'))

@app.route('/inceleme_sil/<int:inceleme_id>', methods=['POST'])
@login_required
def inceleme_sil(inceleme_id):
    inceleme = Inceleme.query.get_or_404(inceleme_id)
    if not current_user.is_admin and inceleme.yazar != current_user:
        flash('Bu incelemeyi silme yetkiniz yok.', 'danger')
        return redirect(url_for('yonetici_paneli'))
    
    urun_ismi = inceleme.urun.isim
    db.session.delete(inceleme)
    db.session.commit()
    flash(f'"{urun_ismi}" ürününe ait inceleme başarıyla silindi.', 'success')
    return redirect(url_for('yonetici_paneli'))

@app.route('/kullanici_yonetici_yap/<int:kullanici_id>', methods=['POST'])
@login_required
def kullanici_yonetici_yap(kullanici_id):
    if not current_user.is_admin:
        abort(403)
    kullanici = Kullanici.query.get_or_404(kullanici_id)
    kullanici.is_admin = True
    db.session.commit()
    flash(f'{kullanici.kullanici_adi} artık bir yönetici.', 'success')
    return redirect(url_for('yonetici_paneli'))

@app.route('/ara', methods=['GET', 'POST'])
def ara():
    form = AramaFormu()
    if form.validate_on_submit():
        arama_terimi = form.arama.data
        sonuclar = Urun.query.filter(Urun.isim.like(f'%{arama_terimi}%')).all()
        return render_template('arama_sonuclari.html', title='Arama Sonuçları', sonuclar=sonuclar)
    return render_template('ara.html', title='Ürün Ara', form=form)

@app.route('/profil')
@login_required
def profil():
    incelemeler = current_user.incelemeler.order_by(Inceleme.tarih.desc()).all()
    form = FlaskForm()
    return render_template('profil.html', title='Profil', incelemeler=incelemeler, form=form)

@app.route('/404')
def test_404():
    abort(404)

@app.route('/500')
def test_500():
    abort(500)

@app.route('/kullanici_yoneticilikten_cikar/<int:kullanici_id>', methods=['POST'])
@login_required
def kullanici_yoneticilikten_cikar(kullanici_id):
    if not current_user.is_admin:
        abort(403)
    kullanici = Kullanici.query.get_or_404(kullanici_id)
    if kullanici == current_user:
        flash('Yüce efendi... Bu zaten sizsiniz..?', 'danger')
    else:
        kullanici.is_admin = False
        db.session.commit()
        flash(f'{kullanici.kullanici_adi} artık yönetici değil.', 'success')
    return redirect(url_for('yonetici_paneli'))

@app.route('/profil_guncelle', methods=['GET', 'POST'])
@login_required
def profil_guncelle():
    form = ProfilGuncellemeFormu(current_user.email)
    if form.validate_on_submit():
        if current_user.parola_kontrol(form.eski_parola.data):
            current_user.email = form.email.data
            current_user.parola_ayarla(form.yeni_parola.data)
            db.session.commit()
            flash('Profiliniz başarıyla güncellendi.', 'success')
            return redirect(url_for('profil'))
        else:
            flash('Mevcut parolanız yanlış.', 'danger')
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('profil_guncelle.html', title='Profil Güncelle', form=form)