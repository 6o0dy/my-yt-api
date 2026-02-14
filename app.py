from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
# السماح لبلوجر بالاتصال بهذا السيرفر
CORS(app) 

@app.route('/', methods=['GET'])
def home():
    return "السيرفر يعمل بنجاح!"

@app.route('/api/download', methods=['GET'])
def get_download_link():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "لم يتم إرسال رابط"}), 400

    # إعدادات مكتبة yt-dlp لاستخراج الرابط المباشر فقط بدون تحميل الفيديو على السيرفر
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "status": "success",
                "title": info.get('title', 'فيديو'),
                "thumbnail": info.get('thumbnail', ''),
                "direct_url": info.get('url', '')
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
