import sqlite3
import os
import time

# Create sqlite database to store the data from txt file
validations = sqlite3.connect('data/validacijas.sqlite')
validationsCur = validations.cursor()

# Create tables for data
validationsCur.executescript('''

CREATE TABLE IF NOT EXISTS Validacijas (
    id INTEGER UNIQUE PRIMARY KEY,
    parks_id INTEGER,
    tr_veids_id INTEGER,
    borta_nr_id INTEGER,
    marsruta_nos_id INTEGER,
    marsruts_id INTEGER,
    virziens_id INTEGER,
    eTalons_id INTEGER,
    laiks TEXT
);

CREATE TABLE IF NOT EXISTS Parks (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    parks TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Tr_veids (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    tr_veids TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Borta_nr (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    borta_nr TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Marsruta_nos (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    marsruta_nos TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Marsruts (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    marsruts TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Virziens (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    virziens TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS ETalons (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    eTalons TEXT UNIQUE
)
''')

while True:
    allFiles = sqlite3.connect('data/encoding.sqlite')
    allFilesCur = allFiles.cursor()
    allFilesCur.execute(
        'SELECT name, encoding, times_read FROM Files JOIN Encodings USING (encoding_id) WHERE times_read = 0')
    file = allFilesCur.fetchone()
    if file == None:
        print('All the files have been read')
        break
    name = file[0]
    encoding = file[1]
    times_read = int(file[2])

    # Opening individual files
    try:
        path = 'raw_data/' + name
        fhandle = open(path, encoding=encoding)

        i = 0
        for line in fhandle:  # Reading the file line for line and selecting necessary data
            line = line.rstrip()
            if line.startswith('Ier_ID'):
                continue  # Skipping the line with "Headers"
            ride = line.split(',')
            id = ride[0]
            parks = ride[1]
            tr_veids = ride[2]
            borta_nr = ride[3]
            marsr_nos = ride[4]
            marsr = ride[5]
            virziens = ride[6]
            eTalons = ride[7]
            laiks = ride[8]

            # Inserting selected data from txt file to sqlite database
            validationsCur.execute(
                'INSERT OR IGNORE INTO Parks (parks) VALUES ( ? )', (parks, ))
            validationsCur.execute(
                'SELECT id FROM Parks WHERE parks = ? ', (parks, ))
            parks_id = validationsCur.fetchone()[0]

            validationsCur.execute(
                'INSERT OR IGNORE INTO Tr_veids (tr_veids) VALUES ( ? )', (tr_veids, ))
            validationsCur.execute(
                'SELECT id FROM Tr_veids WHERE tr_veids = ? ', (tr_veids, ))
            tr_veids_id = validationsCur.fetchone()[0]

            validationsCur.execute(
                'INSERT OR IGNORE INTO Borta_nr (borta_nr) VALUES ( ? )', (borta_nr, ))
            validationsCur.execute(
                'SELECT id FROM Borta_nr WHERE borta_nr = ? ', (borta_nr, ))
            borta_nr_id = validationsCur.fetchone()[0]

            validationsCur.execute(
                'INSERT OR IGNORE INTO Marsruta_nos (marsruta_nos) VALUES ( ? )', (marsr_nos, ))
            validationsCur.execute(
                'SELECT id FROM Marsruta_nos WHERE marsruta_nos = ? ', (marsr_nos, ))
            marsr_nos_id = validationsCur.fetchone()[0]

            validationsCur.execute(
                'INSERT OR IGNORE INTO Marsruts (marsruts) VALUES ( ? )', (marsr, ))
            validationsCur.execute(
                'SELECT id FROM Marsruts WHERE marsruts = ? ', (marsr, ))
            marsrs_id = validationsCur.fetchone()[0]

            validationsCur.execute(
                'INSERT OR IGNORE INTO Virziens (virziens) VALUES ( ? )', (virziens, ))
            validationsCur.execute(
                'SELECT id FROM Virziens WHERE virziens = ? ', (virziens, ))
            virziens_id = validationsCur.fetchone()[0]

            validationsCur.execute(
                'INSERT OR IGNORE INTO ETalons (eTalons) VALUES ( ? )', (eTalons, ))
            validationsCur.execute(
                'SELECT id FROM ETalons WHERE eTalons = ? ', (eTalons, ))
            eTalons_id = validationsCur.fetchone()[0]

            validationsCur.execute('''INSERT OR IGNORE INTO Validacijas
            (id, parks_id, tr_veids_id, borta_nr_id, marsruta_nos_id, marsruts_id, virziens_id, etalons_id, laiks)
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (id, parks_id, tr_veids_id, borta_nr_id, marsr_nos_id, marsrs_id, virziens_id, eTalons_id, laiks))
            i = i + 1

            if i == 50000:
                validations.commit()
                print('commit')
                print('sleep for 5 seconds')
                time.sleep(5)
                i = 0
        allFilesCur.execute(
            'UPDATE Files SET times_read = ? WHERE name = ?', (times_read + 1, name,))
        allFiles.commit()

    except KeyboardInterrupt:
        print('\nstopped by user')
        break

validations.commit()
allFiles.commit()
