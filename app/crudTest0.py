from sqlalchemy.orm import Session
import modelTest0

def get_lyrics_by_track_name(db: Session, track_name: str):
    return db.query(modelTest0.Mylirics).filter(modelTest0.Mylirics.track_name == track_name).first()

def create_mylrics(db: Session, mylyrics: modelTest0.Mylirics):
    db.add(mylyrics)
    db.commit()
    db.refresh(mylyrics)
    return mylyrics

def add_searched_times_by_track_name_and_artist_name(db: Session, track_name: str, artist_name: str):
    db.query(modelTest0.Mylirics).filter(modelTest0.Mylirics.track_name == track_name).filter(modelTest0.Mylirics.artist_name == artist_name).update({modelTest0.Mylirics.searched_times: modelTest0.Mylirics.searched_times + 1})
    db.commit()
    return db.query(modelTest0.Mylirics).filter(modelTest0.Mylirics.track_name == track_name).filter(modelTest0.Mylirics.artist_name == artist_name).first()

