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

import duckdb  # pylint: disable=wrong-import-position
import click  # pylint: disable=wrong-import-position
from app import create_app  # pylint: disable=wrong-import-position

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
db_file: str = app.config['DATABASE']


@app.cli.command('create-tables')
def create_tables():
    '''Create duckdb database file and create table to store data into it.'''
    with duckdb.connect(db_file) as con:
        con.sql('''
                CREATE TABLE IF NOT EXISTS validacijas(
                Ier_ID UINTEGER,
                Parks VARCHAR,
                TranspVeids VARCHAR,
                GarNr UINTEGER,
                MarsrNos VARCHAR,
                TMarsruts VARCHAR,
                Virziens VARCHAR,
                ValidTalonaId UINTEGER,
                Laiks TIMESTAMP);
                ''')


@app.cli.command('load-data')
@click.argument('data_folder', type=click.Path(exists=True))
def load_data(data_folder: str):
    '''Load data from a CSV files into the database.'''
    with duckdb.connect(db_file) as con:
        con.sql(f'''
                COPY validacijas FROM "{data_folder}\\ValidDati*.txt";
                ''')
