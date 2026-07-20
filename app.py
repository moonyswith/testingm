import os
import requests
from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__)

# Путь к текущей папке проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def search_soundcloud_multiple(query):
    try:
        # Официальный открытый клиентский ID SoundCloud для веб-плееров
        client_id = "v3E6Ad9O4r77A016930O59A4101E694a"
        url = "https://soundcloud.com"
        
        params = {
            "q": query,
            "client_id": client_id,
            "limit": 5 # Запрашиваем 5 вариантов
        }
        
        response = requests.get(url, params=params, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        
        if response.status_code != 200:
            return {"error": f"База данных перегружена (Код {response.status_code})"}
            
        data = response.json()
        collection = data.get('collection', [])
        
        if not collection:
            return {"error": "Ничего не найдено"}
            
        results = []
        for track in collection:
            # Ищем прямую ссылку на аудиопоток внутри метаданных трека
            transcodings = track.get('media', {}).get('transcodings', [])
            stream_url = ""
            
            # Пытаемся вытащить стандартный прогрессивный mp3-поток
            for t in transcodings:
                if t.get('format', {}).get('protocol') == 'progressive':
                    unauth_url = t.get('url')
                    # Получаем финальный рабочий URL для плеера
                    stream_resp = requests.get(f"{unauth_url}?client_id={client_id}", timeout=3)
                    if stream_resp.status_code == 200:
                        stream_url = stream_resp.json().get('url', '')
                    break
            
            # Если прогрессивный формат не найден, берем первый доступный HLS-поток
            if not stream_url and transcodings:
                unauth_url = transcodings[0].get('url')
                stream_resp = requests.get(f"{unauth_url}?client_id={client_id}", timeout=3)
                if stream_resp.status_code == 200:
                    stream_url = stream_resp.json().get('url', '')

            if stream_url:
                # Настраиваем обложку
                artwork = track.get('artwork_url') or track.get('user', {}).get('avatar_url') or 'https://placeholder.com'
                artwork = artwork.replace('-large.', '-t200x200.') # делаем качество лучше
                
                results.append({
                    'title': track.get('title', 'Неизвестный трек'),
                    'artist': track.get('user', {}).get('username', 'Неизвестный исполнитель'),
                    'thumbnail': artwork,
                    'stream_url': stream_url
                })
                
        return {"tracks": results}
    except Exception as e:
        return {"error": f"Ошибка сети сервера: {str(e)}"}

@app.route('/')
def home():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Пустой запрос"}), 400
        
    result = search_soundcloud_multiple(query)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
