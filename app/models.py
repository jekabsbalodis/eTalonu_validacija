from sqlalchemy import ForeignKey
from . import db


class Validacijas(db.Model):
    __tablename__: str = 'validacijas'
    id: int = db.Column(db.Integer, primary_key=True)
    parks_id: int = db.Column(db.Integer, ForeignKey('parks.id'))
    transp_id: int = db.Column(db.Integer, ForeignKey('transports.id'))
    gar_nr_id: int = db.Column(db.Integer, ForeignKey('gar.id'))
    marsruts_id: str = db.Column(db.Integer, ForeignKey('marsruts.id'))
    virziens: bool = db.Column(db.Boolean)
    talona_id: int = db.Column(db.Integer)
    laiks: str = db.Column(db.String(32))


class Parks(db.Model):
    __tablename__: str = 'parks'
    id: int = db.Column(db.Integer, primary_key=True)
    parks: str = db.Column(db.String(10), unique=True)

    def __init__(self, **kwargs: str) -> None:
        if kwargs.get('parks') is None:
            return super().__init__()
        self.parks = kwargs.get('parks')


class Transport(db.Model):
    __tablename__: str = 'transports'
    id: int = db.Column(db.Integer, primary_key=True)
    transports: str = db.Column(db.String(32), unique=True)


class Gar(db.Model):
    __tablename__: str = 'gar'
    id: int = db.Column(db.Integer, primary_key=True)
    gar: str = db.Column(db.Integer, unique=True)


class Marsruts(db.Model):
    __tablename__ = 'marsruts'
    id: int = db.Column(db.Integer, primary_key=True)
    mars_nos: str = db.Column(db.Text, unique=True)
    marsruts: str = db.Column(db.String(10), unique=True)

    # def __init__(self,
    #              ier_id: int,
    #              parks: str,
    #              transp_veids: str,
    #              gar_nr: int,
    #              mars_nos: str,
    #              marsruts: str,
    #              virziens: str,
    #              talona_id: int,
    #              laiks: str) -> None:
    #     self.id = ier_id
    #     self.parks = parks
    #     self.transp_veids = transp_veids
    #     self.gar_nr = gar_nr
    #     self.mars_nos = mars_nos
    #     self.mars_nos = mars_nos
    #     self.marsruts = marsruts
    #     self.virziens = virziens
    #     self.talona_id = talona_id
    #     self.laiks = laiks

    # @staticmethod
    # def add_entry(ier_id, parks, transp_veids, gar_nr, marsr_nos, marsruts, virziens, talona_id, laiks) -> None:
    #     new_entry: Validacijas = Validacijas(
    #         ier_id=ier_id,
    #         parks=parks,
    #         transp_veids=transp_veids,
    #         gar_nr=gar_nr,
    #         mars_nos=marsr_nos,
    #         marsruts=marsruts,
    #         virziens=virziens,
    #         talona_id=talona_id,
    #         laiks=laiks
    #     )
    #     db.session.add(new_entry)
    #     db.session.commit()

    # @staticmethod
    # def bulk_add(folder_name: str, encoding: str) -> None:
    #     col_names: list[str] = ['id', 'parks', 'transp_veids', 'gar_nr',
    #                             'mars_nos', 'marsruts', 'virziens', 'talona_id', 'laiks']
    #     for paths, dirs, files in os.walk(folder_name):
    #         for file in files:
    #             df: pd.DataFrame = pd.read_csv(filepath_or_buffer=(
    #                 folder_name + '/' + file), encoding=encoding, header=0, names=col_names)
    #             database_url: str | None = 'sqlite:///data-dev.sqlite'
    #             if database_url is None:
    #                 print('database url is none')
    #                 return None
    #             engine: Engine = create_engine(
    #                 url=database_url)
    #             df.to_sql('validacijas', index=False,
    #                       con=engine, if_exists='append')
