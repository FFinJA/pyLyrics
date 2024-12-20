import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import requests
import base64
import chineseName
import json
# import sqlite3
import requests
import json
import base64
from sqlalchemy.orm import Session
import crudTest0, modelTest0, pgTest0
from pgTest0 import SessionLocal, engine
import lyricsGenius

def get_gecimi_lyrics(track_name, artist_name,collection_name,headers):
    # clean track_name
    if "feat." in track_name:
        track_name = track_name.split("feat.")[0].strip()
    if "(" in track_name:
        track_name = track_name.split("(")[0].strip()
    if "・" in track_name:
        track_name = track_name.split("・")[0].strip()
    if "&" in track_name:
        track_name = track_name.replace("&", "and").strip()
    
    # clean artist_name
    artist_chineseName = chineseName.get_chinese(artist_name)
    if artist_chineseName:
        artist_name = artist_chineseName
    if "(" in artist_name:
        artist_name = artist_name.split("(")[0].strip()
    
    try:
        response = requests.get(
            f"https://api.lrc.cx/api/v1/lyrics/advance?title={track_name}&album={collection_name}&artist={artist_name}",
            headers=headers,
        )
        if response.status_code == 200:
            lyrics = json.loads(response.text)
            if lyrics:
                if len(lyrics) > 0:
                    # only return the first result
                    print(lyrics[0].get("title"),lyrics[0].get("ratio"))
                    return f"<h3>Lyric of {track_name} ({lyrics[0].get("artist")}) :</h3><p>{lyrics[0].get("lyrics").replace(lyrics[0].get("lyrics").split('[00:0')[0],'').replace('[', '<br>[')}</p>"
                
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

    return None


def get_kugou_lyrics(track_name, album_name, artist_name, headers):
    contents = []
    
    # clean track_name
    if "feat." in track_name:
        track_name = track_name.split("feat.")[0].strip()
    if "(" in track_name:
        track_name = track_name.split("(")[0].strip()
    if "・" in track_name:
        track_name = track_name.split("・")[0].strip()
    if "&" in track_name:
        track_name = track_name.replace("&", "and").strip()
    
    # clean artist_name
    artist_chineseName = chineseName.get_chinese(artist_name)
    if artist_chineseName:
        artist_name = artist_chineseName
    if "(" in artist_name:
        artist_name = artist_name.split("(")[0].strip()
    
    print(f"Cleaned track_name: {track_name}, artist_name: {artist_name}")

    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        # 1st step request
        response0 = requests.get(
            f"http://mobileservice.kugou.com/api/v3/lyric/search?version=9108&highlight=1&keyword={track_name}+{artist_name}&plat=0&pagesize=20&area_code=1&page=1&with_res_tag=1",
            headers=headers,
        )
        print(f"Response0 Status: {response0.status_code}")
        if not response0.ok:
            return None

        res0_str = response0.text.replace("<!--KG_TAG_RES_START-->", "").replace("<!--KG_TAG_RES_END-->", "")
        info_data = json.loads(res0_str).get("data", {}).get("info", [])
        if not info_data:
            print("No info data found.")
            return None

        # get hashes
        hashes = []
        if len(info_data) > 0:
            # get no1 and no2 320hash in 320hash tag if existing
            if len(info_data) > 0:
                hashes.append(info_data[0].get("320hash", ""))
            if len(info_data) > 1:
                hashes.append(info_data[1].get("320hash", ""))
            if len(info_data) > 2:
                hashes.append(info_data[2].get("hash", ""))
            

        # 2nd step request
        for hash_value in hashes:
            response1 = requests.get(
                f"http://krcs.kugou.com/search?ver=1&man=yes&client=mobi&keyword=&duration=&hash={hash_value}&album_audio_id=",
                headers=headers,
            )
            if response1.status_code != 200:
                continue

            candidates = response1.json().get("candidates", [])
            for candidate in candidates[:2]:  # 最多尝试 3 个候选项
                id1 = candidate.get("id")
                access1 = candidate.get("accesskey")
                response2 = requests.get(
                    f"http://lyrics.kugou.com/download?ver=1&client=pc&id={id1}&accesskey={access1}&fmt=lrc",
                    headers=headers,
                )
                if response2.status_code == 200:
                    content = response2.json().get("content")
                    if content:
                        contents.append(content)

        # decode the lyrics
        if contents:
            decoded_contents = []
            for content_encoded in contents:
                decoded_bytes = base64.urlsafe_b64decode(content_encoded)
                lyrics_option = decoded_bytes.decode(errors="ignore")
                decoded_contents.append(lyrics_option)

            # match the lyrics according to the poriority
            for lyrics in decoded_contents:
                if track_name in lyrics and album_name in lyrics and artist_name in lyrics:
                    return f"<h3>Lyric of {track_name} :</h3><p>{lyrics.replace(lyrics.split('[00:0')[0],'').replace('[', '<br>[')}</p>"
            for lyrics in decoded_contents:
                if track_name in lyrics and album_name in lyrics:
                    return f"<h3>Lyric of {track_name} :</h3><p>{lyrics.replace(lyrics.split('[00:0')[0],'').replace('[', '<br>[')}</p>"
            for lyrics in decoded_contents:
                if track_name in lyrics and artist_name in lyrics:
                    return f"<h3>Lyric of {track_name} :</h3><p>{lyrics.replace(lyrics.split('[00:0')[0],'').replace('[', '<br>[')}</p>"
            for lyrics in decoded_contents:
                if track_name in lyrics:
                    return f"<h3>Lyric of {track_name} :</h3><p>{lyrics.replace(lyrics.split('[00:0')[0],'').replace('[', '<br>[')}</p>"

            # reutrn the longest content if no match
            longest_content = max(decoded_contents, key=len)
            return f"<h3>Lyric of {track_name} :</h3><p>{longest_content.replace(longest_content.split('[00:0')[0],'').replace('[', '<br>[')}</p>"

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

    return None


def get_itunes_lyrics(track_name,track_album,track_explicit,artist,headers):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        if(" - " in track_name or " - " in track_name):
                track_name = track_name.split("-")[0].trim()
                iTunes_results = requests.get("https://itunes.apple.com/search", params={
                    "term": " ".join((track_name, track_album)), # TODO: make this lookup one artist instead of the album name, so that it doesn't look up names of singles twice
                    "entity": "song",
                    "explicit": "No" if (track_explicit == False) else "Yes"
                    }).json()
                iTunes_track = iTunes_results["results"][0]
                iTunes_track = iTunes_track["trackViewUrl"].split("=")[-2].split("&")[0]
                print("iTunresTrack: ",iTunes_track)
                response_gh_itune = requests.get(f"https://raw.githubusercontent.com/Steve-xmh/amll-ttml-db/refs/heads/main/am-lyrics/{iTunes_track}.lrc", headers=headers)
                if(response_gh_itune.text not in ["404: Not Found", ""] ):
                    print("returning iTunes lyrics")
                    return "<h3>Lyric of " + track_name + " :</h3><p>"+response_gh_itune.text
    except:
        print("NO iTunes lyrics found")

    return None

def get_github_results(track_id,track_name,track_album,track_explicit,artist,headers):
    try:
        response_gh = requests.get(f"https://raw.githubusercontent.com/Steve-xmh/amll-ttml-db/refs/heads/main/spotify-lyrics/{track_id}.lrc", headers=headers)
        if(response_gh.text != "404: Not Found"): 
            print("returning Spotify lyrics")           
            return "<h3>Lyric of " + track_name + " :</h3><p>"+response_gh.text.replace("[","<br>[")+"</p>"
    except:
        print("NO Github lyrics found")
        
    return None

    

def get_lyrics_from_apis(track_id,track_name,track_album,track_explicit,artist):
    print("beginning get_lyrics")
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
    }
    try:
        github_lyrics = get_github_results(track_id,track_name,track_album,track_explicit,artist,headers)
        if(github_lyrics and github_lyrics is not None):
            return tranlate_lyrics(github_lyrics)
    except:
        print("NO Github lyrics found")             
    
    try:
        gecimi_lyrics = get_gecimi_lyrics(track_name,artist,track_album,headers)
        print("returning gecimi lyrics")
        if(gecimi_lyrics and gecimi_lyrics is not None):
            return tranlate_lyrics(gecimi_lyrics)
    except:
        print("NO gecimi lyrics found")

    try:
        genius_lyrics = lyricsGenius.get_genius_lyrics(track_name,artist)
        print("returning genius lyrics")
        genius_lyrics_str = f"<h3>Lyric of {track_name} ({artist}):</h3>"
        if(genius_lyrics and genius_lyrics is not None):
            lyrics_list =  genius_lyrics['lyrics']            
            for lyrrics_block in lyrics_list:
                genius_lyrics_str += f"<p>{lyrrics_block}</p>"
            return genius_lyrics_str
    except:
        print("NO genius lyrics found")
                    
    try:
        kugou_lyrics = get_kugou_lyrics(track_name,track_album,artist,headers)
        print("returning kugou lyrics")
        if(kugou_lyrics and kugou_lyrics is not None):
            return tranlate_lyrics(kugou_lyrics)
    except:
        print("NO kugou lyrics found")

    try:
        iTunes_lyrics = get_itunes_lyrics(track_name,track_album,track_explicit,artist,headers)
        print("returning iTunes lyrics")
        if(iTunes_lyrics and iTunes_lyrics is not None):
            return tranlate_lyrics(iTunes_lyrics)
    except:
        print("NO iTunes lyrics found")
        return None      
    
    return None

def get_played_datas(sp):    
    # get data from spotipy api and return it directly
    listPlayed = sp.current_user_recently_played(limit=50)
    return listPlayed

def get_saved_datas(sp):
    listSaved = sp.current_user_saved_tracks(limit=20,offset=0)
    return listSaved

def get_liked_datas(sp):    
    listLiked = sp.current_user_saved_albums(limit=20,offset=0)
    return listLiked


def get_lyrics(spotify_results,track_name,track_name_short,stroage_path,connection): 
    if(" - " in track_name):
        track_name_trimmed = track_name.split("-")[0].rstrip()
    else:
        track_name_trimmed = ""      
    
    for item in spotify_results['items']:
        track = item['track']
        # print(track['name'])
        # print(f"{track['name']} by {track['artists'][0]['name']} twa: {track['external_ids']} id: {track['id']} ")

        if(track_name == track['name']):
            print(f"{track['name']} by {track['artists'][0]['name']} twa: {track['external_ids']} id: {track['id']} ")
            # for sqlite :
            # cursor = connection.cursor()
            # cursor.execute("SELECT * FROM lyrics WHERE track_name = ? AND artist_name = ?", (track['name'], track['artists'][0]['name']))
            # lyrics_sqlite = cursor.fetchone()
            # for ORM sqlalchemy.orm :
            mylyrics_pg = crudTest0.get_lyrics_by_track_name(connection, track_name)
            # if(lyrics_sqlite):
            if(mylyrics_pg):
                # cursor.execute("UPDATE lyrics SET searched_times = ? WHERE track_name = ? AND artist_name = ?", (lyrics_sqlite[4]+1,track['name'], track['artists'][0]['name']))
                # connection.commit()
                # cursor.close()
                # for ORM sqlalchemy.orm , update searched_times field
                crudTest0.add_searched_times_by_track_name_and_artist_name(connection, track['name'], track['artists'][0]['name'])
                connection.close()
                # return{"result": "Lyrics found in database", "lyrics": lyrics_sqlite[3]}
                # return a dict with the result and the lyrics, for json serialization
                return{"result": "Lyrics found in database", "lyrics": mylyrics_pg.lyrics}
            
            if(track_name != track_name_short):
                lyrics = get_lyrics_from_apis(track['id'],track_name_short,track['album']['name'],track['explicit'],track['artists'][0]['name'])
            else:
                lyrics = get_lyrics_from_apis(track['id'],track['name'],track['album']['name'],track['explicit'],track['artists'][0]['name'])
            if(lyrics):
                # cursor = connection.cursor()
                # cursor.execute("INSERT INTO lyrics (track_name, artist_name,album_name, lyrics,searched_times) VALUES (?, ?,?,?,?)", (track['name'], track['artists'][0]['name'],track['album']['name'], lyrics,1))
                # connection.commit()
                # cursor.close()

                new_lyrics = modelTest0.Mylirics(track_name=track['name'], artist_name=track['artists'][0]['name'], album_name=track['album']['name'], lyrics=lyrics, searched_times=1)
                new_lyrics_pg = crudTest0.create_mylrics(connection, new_lyrics)
                
                file_name = f"{track['name']} - {track['artists'][0]['name']}.md"
                print("stroage_path: ",stroage_path)
                with open(f"../{stroage_path}/{file_name}", "w",encoding="utf-8") as f:
                    f.write(lyrics)
                return{"result": "Lyrics found in api and saved", "lyrics": lyrics}

        elif(track_name_trimmed != "" and track_name_trimmed == track['name']):
                print(f"{track_name_trimmed} by {track['artists'][0]['name']} twa: {track['external_ids']} id: {track['id']} ")
                # get data from 1 github repository and 3 apis
                lyrics = get_lyrics_from_apis(track['id'],track_name_trimmed,track['album']['name'],track['explicit'],track['artists'][0]['name'])
                if(lyrics):
                    # save the lyric as a markdown file
                    file_name = f"{track_name_trimmed} - {track['artists'][0]['name']}.md"
                    print("stroage_path: ",stroage_path)
                    with open(f"../{stroage_path}/{file_name}", "w",encoding="utf-8") as f:
                        f.write(lyrics)
                    return{"result": "Lyrics found and saved", "lyrics": lyrics}
                
    return{"result": "Lyrics not found", "lyrics": None}

def get_lyrics_search(track_name,artist_name,stroage_path,db):    
    return_lyrics = []
    mylyrics_pg = crudTest0.get_lyrics_by_track_name(db, track_name)
    db.close()
    
    if(mylyrics_pg):
        return_lyrics.append(mylyrics_pg.lyrics)
    
    print("beginning get_lyrics")
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
    }
    lyrics_gecimi = get_gecimi_lyrics(track_name, artist_name,"",headers)
    # all apis return 1st result
    if(lyrics_gecimi):
        return_lyrics.append(lyrics_gecimi)
    
    genius_lyrics_str = f"<h3>Lyric of {track_name} ({artist_name}):</h3>"
    lyrics_genius = lyricsGenius.get_genius_lyrics(track_name,artist_name)
    if(lyrics_genius):
        lyrics_list =  lyrics_genius['lyrics']            
        for lyrrics_block in lyrics_list:
            for lyrrics_block in lyrics_list:
                genius_lyrics_str += f"<p>{lyrrics_block}</p>"
        return_lyrics.append(genius_lyrics_str)

    if(len(return_lyrics) == 0):
        return{"result": "Lyrics not found", "lyrics": None}
    # return 3lyrics most
    return{"result": "Lyrics found", "lyrics": return_lyrics}



def tranlate_lyrics(lyrics):
    tranlated_lyrics = lyrics.replace("作词", "Lyrics").replace("作曲", "Composer").replace("编曲", "Arranger").replace("制作人", "Producer").replace("混音", "Mixing").replace("母带", "Mastering").replace("录音", "Recording").replace("和声", "Backing Vocals").replace("吉他", "Guitar").replace("贝斯", "Bass").replace("键盘", "Keyboard").replace("鼓", "Drums").replace("词:","Lyrics:").replace("曲:","Composer:").replace("监制","Produser")
    return tranlated_lyrics


