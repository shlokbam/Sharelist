# models.py - Add the SharedWorkspace model
from datetime import datetime
import string
import random
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

def generate_share_code(length=6):
    """Generate a random alphanumeric code for sharing"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    playlists = db.relationship('Playlist', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    links = db.relationship('Link', backref='playlist', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Playlist {self.title}>'

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(200))
    note = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    
    def __repr__(self):
        return f'<Link {self.title or self.url[:30]}>'

# New model for shared workspaces
class SharedWorkspace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    share_code = db.Column(db.String(10), unique=True, nullable=False, default=generate_share_code)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[creator_id], backref='created_workspaces')
    members = db.relationship('User', secondary='workspace_members', backref='joined_workspaces')
    shared_playlists = db.relationship('Playlist', secondary='workspace_playlists', backref='shared_in_workspaces')
    
    def __repr__(self):
        return f'<SharedWorkspace {self.name}>'

# Association tables for many-to-many relationships
workspace_members = db.Table('workspace_members',
    db.Column('workspace_id', db.Integer, db.ForeignKey('shared_workspace.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

workspace_playlists = db.Table('workspace_playlists',
    db.Column('workspace_id', db.Integer, db.ForeignKey('shared_workspace.id'), primary_key=True),
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
)