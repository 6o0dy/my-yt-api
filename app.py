from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.request
import json
import re

app = Flask(__name__)
# السماح لبلوجر بالاتصال
CORS(app)

# دالة استخراج الـ ID الخاصة بك
def get_video_id(url):
    pattern = r'(?:v=|\/|be\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route('/', methods=['GET'])
def home():
    return "سيرفر Invidious السري يعمل بنجاح!"

@app.route('/api/download', methods=['GET'])
def get_download_link():
    url = request.args.get('url')
    if not url:
        return jsonify({"status": "error", "message": "لم يتم إرسال رابط"}), 400

    video_id = get_video_id(url)
    if not video_id:
        return jsonify({"status": "error", "message": "رابط يوتيوب غير صحيح"}), 400

    # قائمتك العبقرية بعد التحديث بأقوى سيرفرات Invidious تعمل الآن
    instances = [
        "https://inv.tux.pizza",
        "https://invidious.perennialte.ch",
        "https://invidious.lunar.icu",
        "https://yt.artemislena.eu",
        "https://invidious.flokinet.to"
    ]

    for instance in instances:
        api_url = f"{instance}/api/v1/videos/{video_id}"
        try:
            # استخدام urllib لتجنب مشاكل المكتبات الخارجية في Vercel
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    # استخراج العنوان
                    title = data.get('title', 'فيديو يوتيوب')
                    
                    # استخراج أفضل صورة مصغرة
                    thumb = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                    video_thumbnails = data.get('videoThumbnails', [])
                    if video_thumbnails:
                        thumb = video_thumbnails[-1].get('url')

                    # استخراج رابط التحميل المباشر (صوت وصورة mp4)
                    streams = data.get('formatStreams', [])
                    if streams:
                        # جلب الرابط الأول من القائمة (غالباً 720p وهو الأكثر استقراراً)
                        direct_url = streams[0].get('url')
                        
                        return jsonify({
                            "status": "success",
                            "title": title,
                            "thumbnail": thumb,
                            "direct_url": direct_url
                        })
        except Exception as e:
            # إذا تعطل هذا السيرفر، انتقل للذي يليه بصمت
            print(f"Failed on {instance}: {e}")
            continue 

    # إذا تعطلت كل السيرفرات
    return jsonify({
        "status": "error", 
        "message": "جميع سيرفرات فك التشفير مشغولة حالياً، يرجى المحاولة بعد قليل."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
