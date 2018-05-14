from app import app, db
from app.models import User, Post, Film

@app.shell_context_processor
def make_shell_contexr():
    return {'db':db, 'User': User, 'Post': Post, 'Film': Film}