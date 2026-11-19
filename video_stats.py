import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()
CHAVE_API = os.getenv("API_KEY")
IDENTIFICADOR_CANAL = "IShowSpeed"
maxResults = 50

def get_playlist_id():
    url_canal = f"https://youtube.googleapis.com/youtube/v3/channels"
    params={
        "part": "contentDetails",
        "forHandle": IDENTIFICADOR_CANAL,
        "key": CHAVE_API
    }
    try:
        response = requests.get(url_canal, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        # print(json.dumps(data, indent=4))

        items = data.get("items", [])
        if not items:
            raise ValueError(f"Canal não encontrado para o identificador de canal: {IDENTIFICADOR_CANAL}")
        playlistId = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        print(playlistId)
        return playlistId
    except requests.exceptions.RequestException as e:
        raise e

def get_video_id(playlistId):
    video_ids = []
    pageToken = None
    url_base = f"https://youtube.googleapis.com/youtube/v3/playlistItems"
    params={
        "part": "contentDetails",
        "maxResults": maxResults,
        "playlistId": playlistId,
        "key": CHAVE_API
    }
    try:
        while True:
            response = requests.get(url_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            page_token = data.get('nextPageToken')

            if not pageToken:
                break

            params['pageToken'] = page_token

        return video_ids

    except requests.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    playlistId = get_playlist_id()
    print(get_video_id(playlistId))
        
