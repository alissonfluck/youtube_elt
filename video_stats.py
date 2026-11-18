import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
CHAVE_API = os.getenv("API_KEY")
IDENTIFICADOR_CANAL = "IShowSpeed"

def get_playlist_id():
    try:
        url_canal = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={IDENTIFICADOR_CANAL}&key={CHAVE_API}'

        response = requests.get(url_canal)
        response.raise_for_status()
        data = response.json()
        # print(json.dumps(data, indent=4))

        info_canal = data["items"][0]
        playlistId = info_canal["contentDetails"]["relatedPlaylists"]
        # print(playlistId)
        return playlistId
    except requests.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    get_playlist_id()  
        
