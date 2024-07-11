import peewee as pw

sqlite_db = pw.Proxy()


class BaseModel(pw.Model):
    class Meta:
        database = sqlite_db


class Parks(BaseModel):
    id = pw.AutoField()
    parks = pw.CharField(max_length=10, unique=True)


class Transports(BaseModel):
    id = pw.AutoField()
    transports = pw.CharField(max_length=32, unique=True)


class GarNr(BaseModel):
    id = pw.AutoField()
    gar = pw.IntegerField(unique=True)


class Marsruts(BaseModel):
    id = pw.AutoField()
    mars_nos = pw.CharField()
    marsruts = pw.CharField(max_length=10, unique=True)


class Talons(BaseModel):
    id = pw.AutoField()
    talons = pw.IntegerField(unique=True)


class Validacijas(BaseModel):
    id = pw.AutoField()
    parks_id = pw.ForeignKeyField(Parks)
    transp_id = pw.ForeignKeyField(Transports)
    gar_nr_id = pw.ForeignKeyField(GarNr)
    marsruts_id = pw.ForeignKeyField(Marsruts)
    virziens = pw.BooleanField()
    talona_id = pw.ForeignKeyField(Talons)
    laiks = pw.DateTimeField()
