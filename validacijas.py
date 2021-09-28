import sqlite3
import os
import time

# Prepare to open txt files with data from Rīgas Satiksme
allfiles = set()
for paths, dirs, files in os.walk('raw_data'):
    for file in files:
        if file.startswith('.') : continue
        allfiles.add(os.path.join(paths, file)) # Adds all files with their relative location to set allfiles

# Create sqlite database to store the data from txt file
conn = sqlite3.connect('data/validacijas.sqlite')
cur = conn.cursor()

# Create tables for data
cur.executescript('''

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

# Opening individual files
try:
    for file in allfiles:
        fhandle = open(file,encoding='Windows 1257')

        i = 0
        for line in fhandle: # Reading the file line for line and selecting necessary data
            line = line.rstrip()
            if line.startswith('Ier_ID') : continue # Skipping the line with "Headers"
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

            cur.execute('INSERT OR IGNORE INTO Parks (parks) VALUES ( ? )', ( parks, ) )
            cur.execute('SELECT id FROM Parks WHERE parks = ? ', (parks, ))
            parks_id = cur.fetchone()[0]

            cur.execute('INSERT OR IGNORE INTO Tr_veids (tr_veids) VALUES ( ? )', ( tr_veids, ) )
            cur.execute('SELECT id FROM Tr_veids WHERE tr_veids = ? ', (tr_veids, ))
            tr_veids_id = cur.fetchone()[0]

            cur.execute('INSERT OR IGNORE INTO Borta_nr (borta_nr) VALUES ( ? )', ( borta_nr, ) )
            cur.execute('SELECT id FROM Borta_nr WHERE borta_nr = ? ', (borta_nr, ))
            borta_nr_id = cur.fetchone()[0]

            cur.execute('INSERT OR IGNORE INTO Marsruta_nos (marsruta_nos) VALUES ( ? )', ( marsr_nos, ) )
            cur.execute('SELECT id FROM Marsruta_nos WHERE marsruta_nos = ? ', (marsr_nos, ))
            marsr_nos_id = cur.fetchone()[0]

            cur.execute('INSERT OR IGNORE INTO Marsruts (marsruts) VALUES ( ? )', ( marsr, ) )
            cur.execute('SELECT id FROM Marsruts WHERE marsruts = ? ', (marsr, ))
            marsrs_id = cur.fetchone()[0]

            cur.execute('INSERT OR IGNORE INTO Virziens (virziens) VALUES ( ? )', ( virziens, ) )
            cur.execute('SELECT id FROM Virziens WHERE virziens = ? ', (virziens, ))
            virziens_id = cur.fetchone()[0]

            cur.execute('INSERT OR IGNORE INTO ETalons (eTalons) VALUES ( ? )', ( eTalons, ) )
            cur.execute('SELECT id FROM ETalons WHERE eTalons = ? ', (eTalons, ))
            eTalons_id = cur.fetchone()[0]

            cur.execute('''INSERT OR IGNORE INTO Validacijas
            (id, parks_id, tr_veids_id, borta_nr_id, marsruta_nos_id, marsruts_id, virziens_id, etalons_id, laiks)
            VALUES
            (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (id, parks_id, tr_veids_id, borta_nr_id,marsr_nos_id, marsrs_id, virziens_id, eTalons_id, laiks ))
            i = i + 1
            if i == 50000:
                conn.commit()
                print('commit')
                # print('sleep for 5 seconds')
                # time.sleep(5)
                i = 0

except KeyboardInterrupt:
    print('\nstopped by user')

conn.commit()
