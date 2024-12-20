import os
from dotenv import load_dotenv
import requests
import lyricsgenius
from bs4 import BeautifulSoup

#loading the environment variables
load_dotenv()
api_token = os.getenv("api_token")
# api_token = "MjoClWGn4BevQD_AASJyl9y2y_Nejwrld5o9r09fZZkSM87JiMyksZqQrfgXy-DK"
# search_term = "Kanye West"
HEADERS = {'Authorization': f'Bearer {api_token}'}

def search_song(song_title, artist_name=None):
    search_url = 'https://api.genius.com/search'
    params = {'q': f'{song_title} {artist_name}'}
    response = requests.get(search_url, headers=HEADERS, params=params)
    response_data = response.json()
    hits = response_data['response']['hits']
    if hits:
        # 返回第一个匹配的 song_id
        return hits[0]['result']['id']
    return None

def get_song_url(song_id):
    song_url = f'https://api.genius.com/songs/{song_id}'
    response = requests.get(song_url, headers=HEADERS)
    response_data = response.json()
    return response_data['response']['song']['url']

def scrape_lyrics(song_url):
    response = requests.get(song_url)
    if(response.status_code != 200):
        print("Failed to scrape lyrics")
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    # Genius 的歌词通常位于 <div> 标签，类名为 'lyrics' 或 'Lyrics__Container'
    lyrics_divs = soup.find_all('div', {'data-lyrics-container': 'true'})
    lyrics_text = []
    if lyrics_divs:
        for lyrics_div in lyrics_divs:
            print("Scraping lyrics from divs")
            lyrics_text.append(lyrics_div.get_text(separator='<br>'))
        return {"blocks":len(lyrics_divs),'lyrics': lyrics_text}
    else:
        # 针对新版 Genius 页面结构
        lyrics = ''
        for div in soup.find_all('div', class_='Lyrics__Container'):
            lyrics += div.get_text(separator='\n')
        return lyrics

def get_genius_lyrics(song_title, artist_name=None):
    song_id = search_song(song_title, artist_name)
    if not song_id:
        print("Song not found")
        exit
    print(song_id)
    genius = lyricsgenius.Genius(api_token)
    song = genius.song(song_id)

    lyrics = scrape_lyrics(song['song']['url'])
    if lyrics:
        return lyrics
    else:
        return None
