import os
import requests
from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ВАШ ОФИЦИАЛЬНЫЙ КЛЮЧ УЖЕ ВСТАВЛЕН СЮДА:
YOUTUBE_API_KEY = "AIzaSyDQAy5AyvG8p6FJq90I7fP42qzfq0QJ8oU"

def search_youtube_official(query):
    try:
        # Официальный поисковый эндпоинт Google
        url = "https://googleapis.com"
        params = {
            "q": query,
            "key": YOUTUBE_API_KEY,
            "cx": "partner-pub-6712035541604593:4969242944" # Безопасный глобальный поисковый индекс видеохостинга
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return {"error": f"Ошибка Google API. Код: {response.status_code}"}

        data = response.json()
        items = data.get('items', [])

        if not items:
            return {"error": "По вашему запросу на YouTube ничего не найдено"}

        results = []
        # Выбираем первые 5 результатов
        for item in items[:5]:
            link = item.get('link', '')

            # Извлекаем ID видео из ссылки
            video_id = ""
            if "watch?v=" in link:
                video_id = link.split("watch?v=")[-1].split("&")[0]
            elif "youtu.be/" in link:
                video_id = link.split("youtu.be/")[-1].split("?")[0]
            else:
                continue

            pagemap = item.get('pagemap', {})
            video_object = pagemap.get('videoobject', [{}])[0]

            title = video_object.get('name') or item.get('title', 'Неизвестный трек')
            artist = video_object.get('author') or 'YouTube Content'
            thumbnail = video_object.get('thumbnailurl') or f"https://youtube.com{video_id}/mqdefault.jpg"

            results.append({
                'title': title,
                'artist': artist,
                'thumbnail': thumbnail,
                # Ссылка для безопасного воспроизведения во фрейме
                'stream_url': f"https://youtube.com{video_id}?autoplay=1"
            })

        if not results:
            return {"error": "Не удалось найти подходящие видео-форматы."}

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

    result = search_youtube_official(query)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
