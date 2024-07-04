from . import db


class Validacijas(db.Model):
    __tablename__ = 'validacijas'
    id: int = db.Column(db.Integer, primary_key=True)
    parks: str = db.Column(db.String(10))
    transp_veids: str = db.Column(db.String(32))
    gar_nr: int = db.Column(db.Integer)
    mars_nos: str = db.Column(db.Text)
    marsruts: str = db.Column(db.String(10))
    virziens: str = db.Column(db.String(10))
    talona_id: int = db.Column(db.Integer)
    laiks: str = db.Column(db.String(32))

    def __init__(self,
                 ier_id: int,
                 parks: str,
                 transp_veids: str,
                 gar_nr: int,
                 mars_nos: str,
                 marsruts: str,
                 virziens: str,
                 talona_id: int,
                 laiks: str) -> None:
        self.id = ier_id
        self.parks = parks
        self.transp_veids = transp_veids
        self.gar_nr = gar_nr
        self.mars_nos = mars_nos
        self.mars_nos = mars_nos
        self.marsruts = marsruts
        self.virziens = virziens
        self.talona_id = talona_id
        self.laiks = laiks

    @staticmethod
    def add_entry(ier_id, parks, transp_veids, gar_nr, marsr_nos, marsruts, virziens, talona_id, laiks):
        new_entry: Validacijas = Validacijas(
            ier_id=ier_id,
            parks=parks,
            transp_veids=transp_veids,
            gar_nr=gar_nr,
            mars_nos=marsr_nos,
            marsruts=marsruts,
            virziens=virziens,
            talona_id=talona_id,
            laiks=laiks
        )
        db.session.add(new_entry)
        db.session.commit()
        return new_entry
