import peewee as pw

sqlite_db = pw.Proxy()


class BaseModel(pw.Model):
    class Meta:
        database = sqlite_db


class Parks(BaseModel):
    id = pw.IntegerField(unique=True, primary_key=True)
    parks = pw.CharField(max_length=10, unique=True)


class Transports(BaseModel):
    id = pw.IntegerField(unique=True, primary_key=True)
    transports = pw.CharField(max_length=32, unique=True)


class GarNr(BaseModel):
    id = pw.IntegerField(unique=True, primary_key=True)
    gar = pw.IntegerField(unique=True)


class Marsruts(BaseModel):
    id = pw.IntegerField(unique=True, primary_key=True)
    mars_nos = pw.CharField()
    marsruts = pw.CharField(max_length=10, unique=True)


class Talons(BaseModel):
    id = pw.IntegerField(unique=True, primary_key=True)
    talons = pw.IntegerField(unique=True)


class Validacijas(BaseModel):
    id = pw.IntegerField(unique=True, primary_key=True)
    parks_id = pw.ForeignKeyField(Parks, backref='validacijas')
    transp_id = pw.ForeignKeyField(Transports, backref='validacijas')
    gar_nr_id = pw.ForeignKeyField(GarNr, backref='validacijas')
    marsruts_id = pw.ForeignKeyField(Marsruts, backref='validacijas')
    virziens = pw.BooleanField()
    talona_id = pw.ForeignKeyField(Talons, backref='validacijas')
    laiks = pw.CharField(max_length=32)
