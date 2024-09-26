'''
Flask app for eTalons validation data display.
Creates CLI commands for
- DB Table creation (flask create-tables) and
- data loading (flask load-data <data_path> <encoding>).
'''
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# pylint: disable=wrong-import-position
import click
import pandas as pd
from app import create_app
from app.models import sqlite_db, Parks, Transports, GarNr, Marsruts, Talons, Validacijas
# pylint: enable=wrong-import-position

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    '''Add object to flask shell context.'''
    return {'db': sqlite_db,
            'Validacijas': Validacijas,
            'Parks': Parks,
            'Transports': Transports,
            'GarNr': GarNr,
            'Marsruts': Marsruts,
            'Talons': Talons}


@app.cli.command(name='create-tables')
def create_tables():
    '''Create database tables.'''
    sqlite_db.connect(reuse_if_open=True)
    sqlite_db.create_tables(
        [Parks, Transports, GarNr, Marsruts, Talons, Validacijas])
    sqlite_db.close()


@app.cli.command('load-data')
@click.argument('data_path', type=click.Path(exists=True))
@click.argument('encoding')
def load_data(data_path: str, encoding: str):
    '''Load data from a CSV file into the database.'''
    # pylint: disable=import-outside-toplevel
    from datetime import datetime
    import glob
    from peewee import chunked, DoesNotExist
    from tqdm import tqdm
    # pylint: enable=import-outside-toplevel
    sqlite_db.connect(reuse_if_open=True)
    col_names: list[str] = ['id', 'parks', 'transports', 'gar',
                            'mars_nos', 'marsruts', 'virziens', 'talons', 'laiks']
    datetime_format = '%d.%m.%Y %H:%M:%S'
    if os.path.isfile(data_path):
        df = pd.read_csv(data_path, encoding=encoding,
                         header=0, names=col_names)
    else:
        files = glob.glob(os.path.join(data_path, "ValidDati*"))
        if not files:
            return
        df = pd.DataFrame()
        for file in files:
            df = pd.concat(
                [df, pd.read_csv(file, encoding=encoding, header=0, names=col_names)])
    df_parks = df['parks'].to_frame().drop_duplicates()
    df_parks_dict = df_parks.to_dict(orient='records')
    df_transports = df['transports'].to_frame().drop_duplicates()
    df_transports_dict = df_transports.to_dict(orient='records')
    df_gar = df['gar'].to_frame().drop_duplicates()
    df_gar_dict = df_gar.to_dict(orient='records')
    df_marsruts = df[['mars_nos', 'marsruts']].drop_duplicates()
    df_marsruts_dict = df_marsruts.to_dict(orient='records')
    df_talons = df['talons'].to_frame().drop_duplicates().fillna(value=0)
    df_talons_dict = df_talons.to_dict(orient='records')

    with sqlite_db.atomic():
        for batch in chunked(df_parks_dict, 100):
            Parks.insert_many(batch).on_conflict_ignore().execute()
        for batch in chunked(df_transports_dict, 100):
            Transports.insert_many(batch).on_conflict_ignore().execute()
        for batch in chunked(df_gar_dict, 100):
            GarNr.insert_many(batch).on_conflict_ignore().execute()
        for batch in chunked(df_marsruts_dict, 100):
            Marsruts.insert_many(batch).on_conflict_ignore().execute()
        for batch in chunked(df_talons_dict, 100):
            Talons.insert_many(batch).on_conflict_ignore().execute()

    parks_cache = {p.parks: p.id for p in Parks.select()}
    transports_cache = {t.transports: t.id for t in Transports.select()}
    gar_nr_cache = {g.gar: g.id for g in GarNr.select()}
    marsruts_cache = {(m.mars_nos, m.marsruts): m.id for m in Marsruts.select()}
    talons_cache = {tal.talons: tal.id for tal in Talons.select()}

    validacijas: list[dict] = []
    for row in tqdm(df.itertuples(), total=len(df), desc='Processing rows'):
        def virziens(a, b):
            return a == b
        parks_id = parks_cache.get(row.parks)
        transports_id = transports_cache.get(row.transports)
        gar_nr_id = gar_nr_cache.get(row.gar)
        marsruts_id = marsruts_cache.get((row.mars_nos, row.marsruts))
        talons_id = talons_cache.get(row.talons, 0)
        validacija = {
            'parks_id': parks_id,
            'transp_id': transports_id,
            'gar_nr_id': gar_nr_id,
            'marsruts_id': marsruts_id,
            'talona_id': talons_id,
            'virziens': virziens(row.virziens, 'Forth'),
            'laiks': datetime.strptime(str(row.laiks), datetime_format)
        }
        try:
            Validacijas.get((Validacijas.parks_id == validacija['parks_id']) &
                            (Validacijas.transp_id == validacija['transp_id']) &
                            (Validacijas.gar_nr_id == validacija['gar_nr_id']) &
                            (Validacijas.marsruts_id == validacija['marsruts_id']) &
                            (Validacijas.virziens == validacija['virziens']) &
                            (Validacijas.talona_id == validacija['talona_id']) &
                            (Validacijas.laiks == validacija['laiks']))
        except DoesNotExist:
            validacijas.append(validacija)
    with sqlite_db.atomic():
        for batch in chunked(validacijas, 100):
            Validacijas.insert_many(batch).on_conflict_ignore().execute()

    sqlite_db.close()


@app.cli.command('test-read')
def test_read():
    from peewee import fn, JOIN
    sqlite_db.connect(reuse_if_open=True)
    validations = [(hour, 0) for hour in range(24)]
    print(validations)

    query = (Validacijas.
             select(
                 Validacijas.laiks.hour.alias('hour'),
                 fn.COUNT(Validacijas.id).alias('count')).
             group_by(
                 Validacijas.laiks.hour))

    for hour, count in query.tuples().iterator():
        validations[hour] = count
        print(hour, ' -> ', count)
    print(validations)


@app.cli.command('execute-sql')
def execute_sql():
    sqlite_db.connect(reuse_if_open=True)

    sqlite_db.execute_sql("PRAGMA synchronous = NORMAL;")
    sqlite_db.execute_sql("PRAGMA journal_mode = WAL;")
    sqlite_db.execute_sql("PRAGMA cache_size = -40000;")
    sqlite_db.execute_sql("PRAGMA temp_store = MEMORY;")
    sqlite_db.execute_sql("PRAGMA mmap_size = 268435456;")
    sqlite_db.execute_sql("PRAGMA locking_mode = EXCLUSIVE;")
    sqlite_db.execute_sql("PRAGMA auto_vacuum = NONE;")
    sqlite_db.execute_sql("PRAGMA optimize;")
    sqlite_db.execute_sql("VACUUM;")

    sqlite_db.close()
