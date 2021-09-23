import sqlite3

fhandle = open('raw_data/validacijudati08_2021/ValidDati01_08_21.txt',encoding='Windows 1257')
# for line in fhandle:
#     line = line.rstrip()
#     print(line)
#     break
# print(fhandle)

conn = sqlite3.connect('raw_data/validacijas.sqlite')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Validacijas
    (id INTEGER UNIQUE, parks TEXT, veids TEXT, laiks TEXT)''')

i = 0
for line in fhandle:
    line = line.rstrip()
    if line.startswith('Ier_ID') : continue
    ride = line.split(',')
    id = ride[0]
    parks = ride[1]
    veids = ride[2]
    laiks = ride[-1]
    # print(ride)
    # break
    if len(ride[0]) > 0:
        cur.execute('INSERT OR IGNORE INTO Validacijas (id, parks, veids, laiks) VALUES (?, ?, ?, ?)', (id, parks, veids, laiks ))
    conn.commit()
    i = i + 1
    # if i > 5 : break # Read only first five lines
    if i == 100:
        conn.commit()
        i = 0