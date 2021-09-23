import sqlite3

# Open txt file with data from Rīgas Satiksme
fhandle = open('raw_data/validacijudati08_2021/ValidDati01_08_21.txt',encoding='Windows 1257')

# Create sqlite database to store the data from txt file
conn = sqlite3.connect('data/validacijas.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Validacijas
    (id INTEGER UNIQUE, parks TEXT, veids TEXT, laiks TEXT)''')

i = 0
for line in fhandle: # Reading the file line for line and selecting necessary data
    line = line.rstrip()
    if line.startswith('Ier_ID') : continue # Skipping the line with "Headers"
    ride = line.split(',')
    id = ride[0]
    parks = ride[1]
    veids = ride[2]
    laiks = ride[-1]
    # Inserting selected data from txt file to sqlite database
    cur.execute('INSERT OR IGNORE INTO Validacijas (id, parks, veids, laiks) VALUES (?, ?, ?, ?)', (id, parks, veids, laiks ))
    i = i + 1
    if i == 100:
        conn.commit()
        i = 0