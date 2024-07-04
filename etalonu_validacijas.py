import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# pylint: disable=wrong-import-position
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import Validacijas
# pylint: enable=wrong-import-position

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Validacijas': Validacijas}


@app.cli.command()
@click.argument('file_name')
def add(file_name):
    # pylint: disable=import-outside-toplevel
    import pandas as pd
    from sqlalchemy import create_engine
    # pylint: enable=import-outside-toplevel

    df = pd.read_csv(file_name, encoding='cp1257')
    name_dict = {
        'Ier_ID': 'id',
        'Parks': 'parks',
        'TranspVeids': 'transp_veids',
        'GarNr': 'gar_nr',
        'MarsrNos': 'mars_nos',
        'TMarsruts': 'marsruts',
        'Virziens': 'virziens',
        'ValidTalonaId': 'talona_id',
        'Laiks': 'laiks'
    }
    df = df.rename(columns=name_dict)
    engine = create_engine('sqlite:///data-dev.sqlite')
    df.to_sql('validacijas', engine, index=False, if_exists='append')
