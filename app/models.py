from __init__ import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(105))
    emailConfirm = db.Column(db.Boolean)
    username = db.Column(db.String(50))
    aws_secret = db.Column(db.String(128))
    aws_access = db.Column(db.String(128))
    profile_picture = db.Column(db.String(256))
    password_reset = db.Column(db.String(100))