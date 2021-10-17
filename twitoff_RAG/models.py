from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Creates a 'user' table
class User(db.Model):
    id = db.Column(
        db.BigInteger,
        primary_key=True
        ) # unique id from API as primary key
    screen_name = db.Column(
        db.String,
        nullable=False
        ) # user screen name from API
    last_updated = db.Column(
        db.Date,
        nullable=False
        )
    tweet_vectors = db.Column(
        db.PickleType,
        nullable=False
        )

    def __repr__(self):
        return "<User: {}>".format(self.screen_name)

class Tweet(db.Model):
    id = db.Column(
        db.BigInteger,
        primary_key=True) # tweet id from API as primary key
    body = db.Column(
        db.String(280), # tweet max length of 280 characters
        nullable=False) # tweet text
    tweet_vect = db.Column(
        db.PickleType,
        nullable=False
        ) # vectorized tweet
    last_updated = db.Column(
        db.Date,
        nullable=False
        )
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(
        "User",
        backref=db.backref(
            'tweets',
            cascade="all, delete-orphan",
            lazy=True
            )
        )

    def __repr__(self):
        return "<User: {}>".format(self.body)

class Data_Hold(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_1 = db.Column(db.BigInteger, nullable=True)
    id_2 = db.Column(db.BigInteger, nullable=True)
    hypo_tweet = db.Column(db.String(280), nullable=True)