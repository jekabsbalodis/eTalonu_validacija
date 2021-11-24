import sqlite3
import os
import time
from chardet.universaldetector import UniversalDetector

detector = UniversalDetector()

# Create database for storing information about file encodings
conn = sqlite3.connect('data/encoding.sqlite')
cur = conn.cursor()

# Create tables for data
cur.executescript('''
CREATE TABLE IF NOT EXISTS Files (
    name TEXT UNIQUE,
    encoding_id INTEGER,
    times_read INTEGER
);

CREATE TABLE IF NOT EXISTS Encodings (
    encoding_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    encoding TEXT UNIQUE
)
''')

i = 0
# Writing information to database
for paths, dirs, files in os.walk('raw_data'):
    for file in files:
        if file.startswith('.'):
            continue
        cur.execute('SELECT name FROM Files WHERE name = ?', (file,))
        check = cur.fetchone()
        if check:
            print('File info already stored')
            continue
        else:
            filePath = os.path.join(paths, file)
            detector.reset()
            with open(filePath, 'rb') as openFile:
                for line in openFile:
                    detector.feed(line)
                    if detector.done:
                        break
                detector.close()
                encoding = detector.result['encoding']
            print(encoding)
            cur.execute(
                'INSERT OR IGNORE INTO Encodings (encoding) VALUES (?)', (encoding,))
            cur.execute(
                'SELECT encoding_id FROM Encodings WHERE encoding = ?', (encoding,))
            encodingId = cur.fetchone()[0]

            cur.execute('''INSERT OR IGNORE INTO Files
            (name, encoding_id, times_read) VALUES (?, ?, ?)''', (file, encodingId, 0))
        i = i + 1
        conn.commit()
        print('commit')
        print('Read file ', i)
conn.commit()
conn.close()
