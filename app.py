from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import urllib.request
import json
import re

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "السيرفر يعمل بنجاح!"

# دالة لاستخراج صورة الفيديو
def extract_video_id(url):
    match = re.search(r'(?:youtu\.be/|v=|/v/|/embed/|/shorts/)([^&?]+)', url)
    return match.group(1) if match else "default"

# المحرك الاحتياطي: يعمل تلقائياً إذا قام يوتيوب بحظر السيرفر الأساسي
def fallback_api(url):
    servers = [
        "https://cobalt-api.ayo.tf/",
        "https://api.cobalt.tacohitbox.com/",
        "https://api.seventyhost.net/"
    ]
    
    payload = json.dumps({"url": url}).encode('utf-8')
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    
    for server in servers:
        try:
            req = urllib.request.Request(server + "api/json", data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if "url" in res_data:
                    video_id = extract_video_id(url)
                    return jsonify({
                        "status": "success",
                        "title": "فيديو يوتيوب جاهز للتحميل",
                        "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                        "direct_url": res_data["url"]
                    })
        except Exception as e:
            continue # إذا فشل سيرفر، ينتقل للذي يليه بصمت
            
    return jsonify({"status": "error", "message": "المعذرة، الفيديو محمي جداً أو جميع الخوادم مشغولة حالياً. جرب فيديو آخر."})

@app.route('/api/download', methods=['GET'])
def get_download_link():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "لم يتم إرسال رابط"}), 400

    # المحرك الأول: استخدام yt-dlp مع التخفي كجهاز آيفون (iOS)
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'skip_download': True,
        'nocheckcertificate': True,
        'extractor_args': {'youtube': {'player_client': ['ios', 'android']}}
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
        error_msg = str(e)
        # إذا اكتشف يوتيوب السيرفر وطلب تسجيل دخول (bot)، يتم تشغيل المحرك الاحتياطي فوراً
        if "Sign in" in error_msg or "bot" in error_msg.lower() or "cookie" in error_msg.lower():
            return fallback_api(url)
            
        return jsonify({"status": "error", "message": "حدث خطأ غير متوقع: " + error_msg}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
