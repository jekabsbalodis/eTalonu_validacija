'''
Database models for eTalonu validācijas app
'''
import peewee as pw

sqlite_db = pw.Proxy()


class BaseModel(pw.Model):
    '''Base model class'''
    class Meta:
        '''Specify database for all models'''
        database = sqlite_db


class Parks(BaseModel):
    '''Model for table containing transportation depot information'''
    id = pw.AutoField()
    parks = pw.CharField(max_length=10, unique=True)


class Transports(BaseModel):
    '''Model for table containg transportation type information'''
    id = pw.AutoField()
    transports = pw.CharField(max_length=32, unique=True)


class GarNr(BaseModel):
    '''Model for table containing transportation vehicle numbers'''
    id = pw.AutoField()
    gar = pw.IntegerField(unique=True)


class Marsruts(BaseModel):
    '''Model for table containing route names and identification numbers'''
    id = pw.AutoField()
    mars_nos = pw.CharField()
    marsruts = pw.CharField(max_length=10, unique=True)


class Talons(BaseModel):
    '''Model for table containing ticket ID number'''
    id = pw.AutoField()
    talons = pw.IntegerField(unique=True)


class Validacijas(BaseModel):
    '''Model for table containg eTalons validation information'''
    id = pw.AutoField()
    parks_id = pw.ForeignKeyField(Parks)
    transp_id = pw.ForeignKeyField(Transports)
    gar_nr_id = pw.ForeignKeyField(GarNr)
    marsruts_id = pw.ForeignKeyField(Marsruts)
    virziens = pw.BooleanField()
    talona_id = pw.ForeignKeyField(Talons)
    laiks = pw.DateTimeField()

    class Meta:
        indexes = (
            (('laiks',), False)
        )
