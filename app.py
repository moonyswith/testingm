import os
import requests
from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def search_youtube_via_invidious(query):
    try:
        # Используем одно из самых стабильных и быстрых зеркал Invidious API
        url = "https://perennialte.ch"
        params = {
            "q": query,
            "type": "video"
        }

        # Отправляем безопасный запрос от лица браузера
        response = requests.get(url, params=params, timeout=10, headers={"User-Agent": "Mozilla/5.0"})

        if response.status_code != 200:
            return {"error": f"Зеркало перегружено, код ответа: {response.status_code}"}

        data = response.json()

        if not data or len(data) == 0:
            return {"error": "Ничего не найдено на YouTube по этому запросу"}

        results = []
        # Берем топ-5 результатов, как и планировали
        for video in data[:5]:
            video_id = video.get('videoId')
            if video_id:
                results.append({
                    'title': video.get('title', 'Неизвестный трек'),
                    'artist': video.get('author', 'Неизвестный исполнитель'),
                    'thumbnail': f"https://perennialte.ch{video_id}/mqdefault.jpg",
                    # Генерируем вечную прямую ссылку на аудиопоток (itag=140 — это чистый звук M4A/AAC)
                    'stream_url': f"https://perennialte.ch{video_id}&itag=140"
                })

        return {"tracks": results}
    except Exception as e:
        return {"error": f"Ошибка сети бэкенда: {str(e)}"}

@app.route('/')
def home():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Пустой запрос"}), 400

    result = search_youtube_via_invidious(query)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
