from app import create_app, db
from app.models import Kullanici, Urun, Inceleme

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Kullanici': Kullanici, 'Urun': Urun, 'Inceleme': Inceleme}