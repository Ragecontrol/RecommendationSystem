from app import app, db
from app.models import User, Film, User_Film

@app.shell_context_processor
def make_shell_contexr():
    return {'db':db, 'User': User, 'Film': Film, 'User_Film': User_Film}