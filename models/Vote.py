from config import db
from sqlalchemy import UniqueConstraint

class Vote(db.Model):
    __tablename__ = 'vote'
    __table_args__ = (
        UniqueConstraint('poll_id', 'user_id'),
    )

    id = db.Column(db.Integer(), primary_key=True)
    poll_id = db.Column(db.ForeignKey('poll.id',  deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    user_id = db.Column(db.BigInteger(), nullable=False)
    result = db.Column(db.BigInteger(), nullable=False)
