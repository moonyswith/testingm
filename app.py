import os
from flask import Flask, send_from_directory, request, jsonify
from yt_dlp import YoutubeDL

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def search_youtube_audio_multiple(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        # Запрашиваем 5 результатов вместо 1
        'default_search': 'ytsearch5:',
        'skip_download': True,
        'quiet': True,
        'nocheckcertificate': True,
        'source_address': '0.0.0.0',
        'extractor_args': {
            'youtube': {
                'player_client': ['android'],
                'skip': ['webpage', 'hls']
            }
        }
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if not info or 'entries' not in info or not info['entries']:
                return {"error": "Ничего не найдено"}

            results = []
            # Пробегаемся по всем 5 найденным элементам
            for entry in info['entries']:
                if entry:
                    results.append({
                        'title': entry.get('title', 'Неизвестный трек'),
                        'artist': entry.get('uploader', 'Неизвестный исполнитель'),
                        'duration': entry.get('duration', 0),
                        'thumbnail': entry.get('thumbnail', ''),
                        'stream_url': entry.get('url', '')
                    })

            return {"tracks": results}
        except Exception as e:
            return {"error": f"Ошибка YouTube: {str(e)}"}

@app.route('/')
def home():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"error": "Пустой запрос"}), 400

    result = search_youtube_audio_multiple(query)
    return jsonify(result)

if __name__ == '__main__':
    # Render сам передаст нужный порт через переменные окружения
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
