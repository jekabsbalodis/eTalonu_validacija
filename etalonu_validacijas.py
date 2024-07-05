import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# pylint: disable=wrong-import-position
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import Validacijas, Parks, Transport, Gar, Marsruts
# pylint: enable=wrong-import-position

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db, render_as_batch=True)


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'Validacijas': Validacijas,
            'Parks': Parks,
            'Transport': Transport,
            'Gar': Gar,
            'Marsruts': Marsruts}


# @app.cli.command()
# @click.argument('folder_name', type=click.Path(exists=True))
# @click.argument('encoding')
# def add(folder_name: str, encoding: str):
#     Validacijas.bulk_add(folder_name, encoding=encoding)

def insert_data(data):
    # Insert data in bulk (optimized for large datasets)
    parks_data = []
    transports_data = []
    gar_data = []
    marsruts_data = []
    validations_data = []

    for row in data:
        # Extract data from each dictionary
        park_name = row["parks"]
        transport = row["transp_veids"]
        gar_nr = row["gar_nr"]
        marsrut = row["marsruts"]
        # Assuming "Back" is False and "Forth" is True
        virziens = row["virziens"] == "Back"
        talona_id = int(row["talona_id"])
        laiks = row["laiks"]

        # Prepare data for bulk inserts (avoiding redundant queries)
        parks_data.append({"parks": park_name})
        transports_data.append({"transp_veids": transport})
        gar_data.append({"gar_nr": gar_nr})
        marsruts_data.append({"marsruts": marsrut})
        validations_data.append({
            "parks_id": None,  # Will be filled later
            "transp_id": None,
            "gar_nr_id": None,
            "marsruts_id": None,
            "virziens": virziens,
            "talona_id": talona_id,
            "laiks": laiks
        })

    # Insert Parks (assuming unique constraint allows duplicates for now)
    db.session.execute(Parks.__table__.insert(), parks_data)

    # Insert others similarly (assuming non-unique for now)
    db.session.execute(Transport.__table__.insert(), transports_data)
    db.session.execute(Gar.__table__.insert(), gar_data)
    db.session.execute(Marsruts.__table__.insert(), marsruts_data)
    db.session.commit()

    # Get IDs for foreign keys after bulk insert
    park_id_map = {park["parks"]: park["id"]
                   for park in db.session.query(Parks).all()}
    transport_id_map = {transport["transp_veids"]: transport["id"]
                        for transport in db.session.query(Transport).all()}
    gar_id_map = {gar["gar"]: gar["id"] for gar in db.session.query(Gar).all()}
    marsrut_id_map = {marsrut["marsruts"]: marsrut["id"]
                      for marsrut in db.session.query(Marsruts).all()}

    # Update Validacijas with foreign key IDs
    for validation in validations_data:
        validation["parks_id"] = park_id_map.get(validation["parks"])
        validation["transp_id"] = transport_id_map.get(
            validation["transpVeids"])
        validation["gar_nr_id"] = gar_id_map.get(validation["garNr"])
        validation["marsruts_id"] = marsrut_id_map.get(validation["marsruts"])

    # Insert Validacijas
    db.session.execute(Validacijas.__table__.insert(), validations_data)
    db.session.commit()
    db.session.close()


@app.cli.command()
@click.argument('folder_name', type=click.Path(exists=True))
@click.argument('encoding')
def add(folder_name: str, encoding: str):
    import pandas as pd
    col_names: list[str] = ['id', 'parks', 'transp_veids', 'gar_nr',
                            'mars_nos', 'marsruts', 'virziens', 'talona_id', 'laiks']
    for paths, dirs, files in os.walk(folder_name):
        for file in files:
            df: pd.DataFrame = pd.read_csv(filepath_or_buffer=(
                folder_name + '/' + file), encoding=encoding, header=0, names=col_names)
            entries = df.to_dict(orient='records')
            insert_data(entries)
