import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime, timezone
from pathlib import Path

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


def batch_list(video_id_list, batch_size):
        for inicio in range(0, len(video_id_list), batch_size):
            yield video_id_list[inicio: inicio + batch_size]

def extract_video_data(video_ids):
    extracted_data = []
    url_base = "https://youtube.googleapis.com/youtube/v3/videos"
    try:
        for batch in batch_list(video_ids, maxResults):
            video_ids_str = ",".join(batch)

            params={
                    "part": "contentDetails, snippet, statistics", 
                    "id": video_ids_str,
                    "key": CHAVE_API
                }
           
            response = requests.get(url_base, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for item in data.get('items', []):
                video_id = item.get("id")
                snippet = item.get("snippet", {})
                contentDetails = item.get("contentDetails", {})
                statistics = item.get("statistics", {})

                video_data = {
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "publishedAt": snippet.get("publishedAt"),
                    "duration": contentDetails.get("duration"),
                    "viewCount": statistics.get("viewCount"),
                    "likeCount": statistics.get("likeCount"),
                    "commentCount": statistics.get("commentCount"),
                }

                extracted_data.append(video_data)

        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e

def save_to_json(extracted_data, output_dir="data"):
    if not extracted_data:
        raise ValueError("Nenhum dado extraído para salvar.")

    data_dir = Path(output_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    file_path = data_dir / f"youtube_data_{today_utc}.json"
    temp_path = file_path.with_suffix(".tmp")

    with open(temp_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False)

    temp_path.replace(file_path)
    return file_path


if __name__ == "__main__":
    playlistId = get_playlist_id()
    video_ids = get_video_id(playlistId)
    video_data = extract_video_data(video_ids)
    save_to_json(video_data)
        
