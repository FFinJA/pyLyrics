from enum import Enum
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Union
import os
import get_data
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import spotipy
from spotipy.oauth2 import SpotifyOAuth
# import sqlite3
import atexit
from sqlalchemy.orm import Session
import crudTest0, modelTest0, pgTest0
from pgTest0 import SessionLocal, engine

pgTest0.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = pgTest0.SessionLocal()
    try:
        yield db  #using generator to return db
    finally:
        db.close()

#enabling CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#loading the environment variables
# load_dotenv()
# client_id = os.getenv("CLIENT_ID")
# client_secret = os.getenv("CLIENT_SECRET")
# your_redirect_uri = os.getenv("YOUR_APP_REDIRECT_URI")
stroage_path = os.getenv("STORAGE_PATH", "lyrics")

client_id = None
client_secret = None
your_redirect_uri = None

#instantiating the Spotify object
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
#                                                 client_secret=client_secret,
#                                                 redirect_uri=your_redirect_uri,
#                                                 scope="user-read-recently-played user-library-read"))
# #defining the TrackItem class
class TrackItem(BaseModel):
    track_name: str
    artist_name: str
    album_name: str

class EnvVars(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str

# simple config the store service
class ConfigService:
    # using a dict to store the user info {user_id: (client_id, client_secret, redirect_uri)}
    user_configs = {}

    def save_user_config(self, user_id: str, client_id: str, client_secret: str, redirect_uri: str):
        self.user_configs[user_id] = (client_id, client_secret, redirect_uri)

    def get_user_config(self, user_id: str):
        return self.user_configs.get(user_id, None)
    
config_service = ConfigService()  # instantiate the service for global

# played_items = []
# saved_items = []
# played_datas = get_data.get_played_datas(sp)

# for item in played_datas['items']:
#     track = item['track']
#     played_item = TrackItem(track_name=track['name'], artist_name=track['artists'][0]['name'], album_name=track['album']['name'])
#     played_items.append(played_item)

# saved_datas = get_data.get_saved_datas(sp)
# for item in saved_datas['items']:
#     track = item['track']
#     saved_item = TrackItem(track_name=track['name'], artist_name=track['artists'][0]['name'], album_name=track['album']['name'])
#     saved_items.append(saved_item)

def storage_file_exits(file_name: str) -> bool:
    file_path = os.path.abspath(os.path.join(f'{stroage_path}', f'{file_name}'))
    return os.path.isfile(file_path)

#the function to close the connection
# def close_connection():
#     if conn:
#         conn.close()
#         print("Database connection closed")
# atexit.register(close_connection)

def clean_track_name(track_name: str) -> str:
   
    if " - Live" in track_name:        
        return track_name.split(" - Live")[0].strip()
    if "・" in track_name:
        return track_name.replace("・", " ").strip()
    return track_name

def get_sp_for_user(user_id: str):
    config = config_service.get_user_config(user_id)
    if not config:
        raise HTTPException(status_code=400, detail="No config found for this user. Please call /config/save first.")
    client_id, client_secret, your_redirect_uri = config
    sp_instance = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=your_redirect_uri,
        scope="user-read-recently-played user-library-read"
    ))
    return sp_instance


@app.get("/played")
def get_played(user_id: str = "testuser"):
    sp_instance = get_sp_for_user(user_id)
    played_datas = get_data.get_played_datas(sp_instance)
    played_items = []
    for item in played_datas['items']:
        track = item['track']
        played_item = TrackItem(track_name=track['name'], artist_name=track['artists'][0]['name'], album_name=track['album']['name'])
        played_items.append(played_item)
    serialized_data = jsonable_encoder(played_items)
    return JSONResponse(content=serialized_data)

@app.get("/saved")
def get_saved(user_id: str = "testuser"):
    sp_instance = get_sp_for_user(user_id)
    saved_datas = get_data.get_saved_datas(sp_instance)
    saved_items = []
    for item in saved_datas['items']:
        track = item['track']
        saved_item = TrackItem(track_name=track['name'], artist_name=track['artists'][0]['name'], album_name=track['album']['name'])
        saved_items.append(saved_item)
    serialized_data = jsonable_encoder(saved_items)
    return JSONResponse(content=serialized_data)

@app.get("/lyrics/saved/{track_name}")
def get_specific_lyric(track_name: str, user_id: str = "testuser", db: Session = Depends(get_db)):
    sp_instance = get_sp_for_user(user_id)
    saved_datas = get_data.get_saved_datas(sp_instance)
    print("/lyrics track_name: " + track_name)
    track_name_short = clean_track_name(track_name)
    
    lyric_result = get_data.get_lyrics(saved_datas,track_name,track_name_short,stroage_path,db)
    serialized_data = jsonable_encoder(lyric_result)
    return JSONResponse(content=serialized_data)


@app.get("/lyrics/played/{track_name}")
def get_specific_lyric(track_name: str, user_id: str = "testuser", db: Session = Depends(get_db)):
    sp_instance = get_sp_for_user(user_id)
    played_datas = get_data.get_played_datas(sp_instance)
    print("/lyrics track_name: " + track_name)
    track_name_short = clean_track_name(track_name)
    
    lyric_result = get_data.get_lyrics(played_datas,track_name,track_name_short,stroage_path,db)
    serialized_data = jsonable_encoder(lyric_result)
    return JSONResponse(content=serialized_data)

@app.get("/lyrics/search/{track_name}/{artist_name}")
def get_specific_lyric(track_name: str, user_id: str = "testuser", db: Session = Depends(get_db), artist_name: str = None):
    print("/lyrics search track_name: " + track_name)
    sp_instance = get_sp_for_user(user_id)
    
    track_name_short = clean_track_name(track_name)
    lyric_results = get_data.get_lyrics_search(track_name,artist_name,stroage_path,db)

        
    return JSONResponse(content=lyric_results)


@app.post("/config/save")
def save_env_vars(vars: EnvVars, user_id: str = "testuser"):
    
    # global client_id, client_secret, your_redirect_uri
    # client_id = vars.client_id
    # client_secret = vars.client_secret
    # your_redirect_uri = vars.redirect_uri
    if(vars.client_id == "" or vars.client_secret == "" or vars.redirect_uri == "" or len(vars.client_id) != 32 or len(vars.client_secret) != 32):
        return JSONResponse(
            status_code=400,
            content={"message": "Env vars are not complete"}
        )

    config_service.save_user_config(user_id, vars.client_id, vars.client_secret, vars.redirect_uri)
    print(f"Received new env vars: {vars.client_id}, {vars.client_secret}, {vars.redirect_uri}. And assigned to user: {user_id}")
    return {"message": "Env vars updated"}
        