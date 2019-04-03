from config import db
from sqlalchemy import UniqueConstraint

class Poll(db.Model):
    __tablename__ = 'poll'
    # __table_args__ = (
    #     UniqueConstraint('chat_id'),
    # )

    id = db.Column(db.Integer(), primary_key=True)
    chat_id = db.Column(db.BigInteger(), nullable=False)
    text_id = db.Column(db.ForeignKey('text.id', deferrable=True, initially='DEFERRED', ondelete='CASCADE'), nullable=False)
