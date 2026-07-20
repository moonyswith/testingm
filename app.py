import os
import requests
from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ваш проверенный рабочий ключ Google API
YOUTUBE_API_KEY = "AIzaSyDQAy5AyvG8p6FJq90I7fP42qzfq0QJ8oU"

def search_youtube_direct(query):
    try:
        # Прямой официальный эндпоинт поиска самого YouTube
        url = "https://googleapis.com"
        params = {
            "part": "snippet",
            "q": query,
            "maxResults": 5,
            "type": "video",
            "key": YOUTUBE_API_KEY
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {"error": f"Ошибка YouTube API. Код: {response.status_code}. Проверьте, включен ли YouTube Data API v3 в консоли Google."}

        data = response.json()
        items = data.get('items', [])

        if not items:
            return {"error": "По вашему запросу ничего не найдено на YouTube"}

        results = []
        for item in items:
            video_id = item.get('id', {}).get('videoId')
            snippet = item.get('snippet', {})

            if video_id:
                results.append({
                    'title': snippet.get('title', 'Неизвестный трек'),
                    'artist': snippet.get('channelTitle', 'YouTube Content'),
                    'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                    'stream_url': f"https://youtube.com{video_id}?autoplay=1"
                })

        return {"tracks": results}
    except Exception as e:
        return {"error": f"Внутренняя ошибка сервера: {str(e)}"}

@app.route('/')
def home():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Пустой запрос"}), 400

    result = search_youtube_direct(query)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
