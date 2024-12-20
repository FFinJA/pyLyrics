import sqlite3

conn = sqlite3.connect('Mylyrics.db')
if conn:
    print("Connected to database successfully")
else:
    print("Failed to connect to database")

cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS lyrics (track_name TEXT, artist_name TEXT, album_name TEXT, lyrics TEXT,searched_times int)")
conn.commit()

# cursor.execute("INSERT INTO lyrics (track_name, artist_name, album_name, lyrics,searched_times) VALUES ('track_name', 'artist_name', 'album_name', 'lyrics',1)")
# cursor.execute("INSERT INTO lyrics (track_name, artist_name, album_name, lyrics,searched_times) VALUES ('track_name2', 'artist_name2', 'album_name2', 'lyrics2',2)")

# cursor.execute('DELETE FROM lyrics WHERE track_name = "Piano Solo - Live"')
# conn.commit()

cursor.execute("SELECT * FROM lyrics")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()