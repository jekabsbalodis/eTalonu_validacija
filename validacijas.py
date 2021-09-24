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

# cur.execute('''CREATE TABLE IF NOT EXISTS Validacijas
#     (id INTEGER UNIQUE, parks TEXT, veids TEXT, laiks TEXT)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Validacijas
    (id INTEGER UNIQUE, laiks TEXT)''')

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
            # parks = ride[1]
            # veids = ride[2]
            laiks = ride[-1]
            # Inserting selected data from txt file to sqlite database
            # cur.execute('INSERT OR IGNORE INTO Validacijas (id, parks, veids, laiks) VALUES (?, ?, ?, ?)', (id, parks, veids, laiks ))
            cur.execute('INSERT OR IGNORE INTO Validacijas (id, laiks) VALUES (?, ?)', (id, laiks ))
            i = i + 1
            if i == 500:
                conn.commit()
                print('commit')
                print('sleep for 5 seconds')
                time.sleep(5)
                print('continue')
                i = 0
                
except KeyboardInterrupt:
    print('\nstopped by user')