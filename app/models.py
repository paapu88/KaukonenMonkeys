""" models of the database.
"""

from app import db

class Monkey(db.Model):
    """model for monkeys"""
    __tablename__ = 'monkey'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    age = db.Column(db.Integer)
    email = db.Column(db.String(80))
    friends = db.relationship('Friend', backref='monkey')
    #best_friend = db.relationship('Friend', uselist=False)
    best_friend_name=db.Column(db.String(180))
    lenfriends = db.Column(db.Integer)

    def __repr__(self):
        return '<Name %r>' % self.name

class Friend(db.Model):
    """model for friends"""
    __tablename__ = 'friend'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    monkey_id = db.Column(db.Integer, db.ForeignKey('monkey.id'))

    to_monkey = db.relationship('Monkey', foreign_keys='Friend.monkey_id')
    #to_monkey_name = db.Column(db.String(80))
    def __repr__(self):
        return 'Friend: <Name %r>' % self.name



