from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crudTest0, modelTest0, pgTest0
from pgTest0 import SessionLocal, engine

# initialize the database
pgTest0.Base.metadata.create_all(bind=engine)

def get_db():
    db = pgTest0.SessionLocal()
    try:
        yield db  #using generator to return db
    finally:
        db.close()

if __name__ == "__main__":
    db = next(get_db())
    try:
        track_name = "track_name"
        mylyrics = crudTest0.get_lyrics_by_track_name(db, track_name)
        if mylyrics:
            print(mylyrics.id)
    finally:
        db.close()

    db1 = next(get_db())
    try:
        id = 5
        track_name = "track_name"
        artist_name = "artist_name"
        album_name = "album_name"
        lyrics = "lyrics"
        searched_time = 1
        mylyrics = modelTest0.Mylirics(id=id, track_name=track_name, artist_name=artist_name, album_name=album_name, lyrics=lyrics, searched_time=searched_time)
        new_lyrics = crudTest0.create_mylrics(db1, mylyrics)
        print(new_lyrics)
    finally:
        db1.close()
        

    