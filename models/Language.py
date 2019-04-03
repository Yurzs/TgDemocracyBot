from config import db

class Language(db.Model):
    __tablename__ = 'language'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode(), unique=True)
