from config import db
from sqlalchemy import UniqueConstraint

class LangText(db.Model):
    __tablename__ = 'text'
    __table_args__ = (
        UniqueConstraint('language_id', 'name'),
    )
    id = db.Column(db.Integer(), primary_key=True)
    language_id = db.Column(db.ForeignKey('language.id', deferrable=True, initially='DEFERRED'), nullable=False)
    name = db.Column(db.Unicode(), nullable=False)
    text = db.Column(db.Unicode(), nullable=False)
