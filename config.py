import os
import secrets

class Config:
    # Generate a random secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    
    # SQLite database
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'Sharelist.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False