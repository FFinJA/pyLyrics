from sqlalchemy import Column, Integer, String
import pgTest0

class Mylirics(pgTest0.Base):
    __tablename__ = "Mylyrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    track_name = Column(String, index=True)
    artist_name = Column(String, index=True)
    album_name = Column(String)
    lyrics = Column(String)
    searched_times = Column(Integer)
