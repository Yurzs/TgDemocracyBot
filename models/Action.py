from config import db


class Action(db.Model):
    __tablename__ = 'action'

    id = db.Column(db.Integer(), primary_key=True)
    poll = db.Column(db.ForeignKey('poll.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    action = db.Column(db.Integer(), nullable=False)
    action_time = db.Column(db.Integer(), nullable=False)
