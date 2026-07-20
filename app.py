import os
import requests
from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def search_itunes_music(query):
    try:
        # Официальный открытый эндпоинт Apple iTunes (не требует ключей и авторизаций)
        url = "https://apple.com"
        params = {
            "term": query,
            "media": "music",
            "limit": 5,
            "lang": "ru_ru"
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {"error": "Музыкальная база временно недоступна"}

        data = response.json()
        results = data.get('results', [])

        if not results:
            return {"error": "По вашему запросу ничего не найдено"}

        tracks = []
        for item in results:
            # Делаем обложку более качественной (из 100х100 в 300х300)
            artwork = item.get('artworkUrl100', 'https://placeholder.com')
            artwork_high = artwork.replace('100x100bb', '300x300bb')

            tracks.append({
                'title': item.get('trackName', 'Неизвестный трек'),
                'artist': item.get('artistName', 'Неизвестный исполнитель'),
                'thumbnail': artwork_high,
                # Прямая вечная MP3-ссылка на 30-секундный оригинальный превью-поток
                'stream_url': item.get('previewUrl', '')
            })

        return {"tracks": tracks}
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

    result = search_itunes_music(query)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
