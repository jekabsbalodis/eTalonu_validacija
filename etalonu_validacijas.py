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
    return {'db': sqlite_db,
            'Validacijas': Validacijas,
            'Parks': Parks,
            'Transports': Transports,
            'GarNr': GarNr,
            'Marsruts': Marsruts,
            'Talons': Talons}


@app.cli.command(name='createTables')
def createTables():
    sqlite_db.connect(reuse_if_open=True)
    sqlite_db.create_tables(
        [Parks, Transports, GarNr, Marsruts, Talons, Validacijas])


@app.cli.command('load-data')
@click.argument('csv_file')
@click.argument('encoding')
def load_data(csv_file, encoding):
    '''Load data from a CSV file into the database.'''
    # pylint: disable=wrong-import-position
    from peewee import chunked
    # pylint: enable=wrong-import-position
    sqlite_db.connect(reuse_if_open=True)
    col_names: list[str] = ['id', 'parks', 'transports', 'gar',
                            'mars_nos', 'marsruts', 'virziens', 'talons', 'laiks']
    df = pd.read_csv(csv_file, encoding=encoding, header=0, names=col_names)
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
        Parks.insert_many(df_parks_dict).on_conflict_ignore().execute()
    with sqlite_db.atomic():
        Transports.insert_many(
            df_transports_dict).on_conflict_ignore().execute()
    with sqlite_db.atomic():
        GarNr.insert_many(df_gar_dict).on_conflict_ignore().execute()
    with sqlite_db.atomic():
        Marsruts.insert_many(df_marsruts_dict).on_conflict_ignore().execute()
    with sqlite_db.atomic():
        Talons.insert_many(df_talons_dict).on_conflict_ignore().execute()
    validacijas = []
    for row in df.itertuples():
        def virziens(a, b): return a == b
        parks_obj = Parks.select(Parks.id).where(
            Parks.parks == row.parks).first()
        transports_obj = Transports.select(Transports.id).where(
            Transports.transports == row.transports).first()
        gar_nr_obj = GarNr.select(GarNr.id).where(
            GarNr.gar == row.gar).first()
        marsruts_obj = Marsruts.select(Marsruts.id).where(
            Marsruts.marsruts == row.marsruts).first()
        talons_obj = Talons.select(Talons.id).where(
            Talons.talons == row.talons).first()
        if talons_obj:
            validacija = {
                'parks_id': parks_obj.id,
                'transp_id': transports_obj.id,
                'gar_nr_id': gar_nr_obj.id,
                'marsruts_id': marsruts_obj.id,
                'talona_id': talons_obj.id,
                'virziens': virziens(row.virziens, 'Forth'),
                'laiks': row.laiks,
            }
        else:
            validacija = {
                'parks_id': parks_obj.id,
                'transp_id': transports_obj.id,
                'gar_nr_id': gar_nr_obj.id,
                'marsruts_id': marsruts_obj.id,
                'talona_id': 0,
                'virziens': virziens(row.virziens, 'Forth'),
                'laiks': row.laiks,
            }
        validacijas.append(validacija)
    with sqlite_db.atomic():
        for batch in chunked(validacijas, 100):
            Validacijas.insert_many(batch).on_conflict_ignore().execute()

    sqlite_db.close()


@app.cli.command('batch-load-data')
@click.argument('folder')
@click.argument('encoding')
def batch_load_data(folder, encoding):
    # pylint: disable=wrong-import-position
    from peewee import chunked
    # pylint: enable=wrong-import-position
    sqlite_db.connect(reuse_if_open=True)
    col_names: list[str] = ['id', 'parks', 'transports', 'gar',
                            'mars_nos', 'marsruts', 'virziens', 'talons', 'laiks']
    for paths, dirs, files in os.walk(folder):
        for file in files:
            df = pd.read_csv((folder + '/' + file), encoding=encoding, header=0, names=col_names)
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
                Parks.insert_many(df_parks_dict).on_conflict_ignore().execute()
            with sqlite_db.atomic():
                Transports.insert_many(
                    df_transports_dict).on_conflict_ignore().execute()
            with sqlite_db.atomic():
                GarNr.insert_many(df_gar_dict).on_conflict_ignore().execute()
            with sqlite_db.atomic():
                Marsruts.insert_many(df_marsruts_dict).on_conflict_ignore().execute()
            with sqlite_db.atomic():
                Talons.insert_many(df_talons_dict).on_conflict_ignore().execute()
            validacijas = []
            for row in df.itertuples():
                def virziens(a, b): return a == b
                parks_obj = Parks.select(Parks.id).where(
                    Parks.parks == row.parks).first()
                transports_obj = Transports.select(Transports.id).where(
                    Transports.transports == row.transports).first()
                gar_nr_obj = GarNr.select(GarNr.id).where(
                    GarNr.gar == row.gar).first()
                marsruts_obj = Marsruts.select(Marsruts.id).where(
                    Marsruts.marsruts == row.marsruts).first()
                talons_obj = Talons.select(Talons.id).where(
                    Talons.talons == row.talons).first()
                if talons_obj:
                    validacija = {
                        'parks_id': parks_obj.id,
                        'transp_id': transports_obj.id,
                        'gar_nr_id': gar_nr_obj.id,
                        'marsruts_id': marsruts_obj.id,
                        'talona_id': talons_obj.id,
                        'virziens': virziens(row.virziens, 'Forth'),
                        'laiks': row.laiks,
                    }
                else:
                    validacija = {
                        'parks_id': parks_obj.id,
                        'transp_id': transports_obj.id,
                        'gar_nr_id': gar_nr_obj.id,
                        'marsruts_id': marsruts_obj.id,
                        'talona_id': 0,
                        'virziens': virziens(row.virziens, 'Forth'),
                        'laiks': row.laiks,
                    }
                validacijas.append(validacija)
            with sqlite_db.atomic():
                for batch in chunked(validacijas, 100):
                    Validacijas.insert_many(batch).on_conflict_ignore().execute()

    sqlite_db.close()
