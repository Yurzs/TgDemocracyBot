from config import db
from sqlalchemy import UniqueConstraint
class InviteLink(db.Model):
    __tablename__ = 'invitelink'
    __table_args__ = (
        UniqueConstraint('chat_id', 'username'),
    )

    id = db.Column(db.Integer(), primary_key=True)
    internal_link = db.Column(db.Unicode(), nullable=False)
    chat_id = db.Column(db.BigInteger(), nullable=False)
    username = db.Column(db.Unicode(), nullable=False)
