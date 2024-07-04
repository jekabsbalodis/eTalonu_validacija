from . import db

class Validacijas(db.Model):
    __tablename__ = 'validacijas'
    Ier_ID = db.Column(db.Integer, primary_key=True)
    Parks = db.Column(db.String(64))
    TranspVeids = db.Column(db.String(64))
    GarNr = db.Column(db.Integer)
    MarsrNos = db.Column(db.String(64))
    TMarsruts = db.Column(db.String(64))
    Virziens = db.Column(db.String(64))
    ValidTalonaId = db.Column(db.Integer)
    Laiks = db.Column(db.String(64))
