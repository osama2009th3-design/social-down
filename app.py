import os
from flask import Flask, render_template_string, request, jsonify, Response
import yt_dlp
import requests

app = Flask(__name__)

# نستخدم نفس الـ UI_TEMPLATE الخاص بك دون تغيير
UI_TEMPLATE = """ ... (ضع كود الـ HTML الخاص بك هنا) ... """

@app.route("/")
def index():
    return render_template_string(UI_TEMPLATE)

@app.route("/api/preview", methods=["POST"])
def get_preview():
    url = request.json.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # جلب رابط الفيديو المباشر من المنصة
            stream_url = info.get('url') or (info['formats'][0]['url'] if info.get('formats') else None)
            
            return jsonify({
                "title": info.get('title', 'Untitled Video'),
                "stream_url": stream_url,
                "original_url": url
            })
    except Exception as e:
        return jsonify({"error": "Platform not supported or private video."}), 500

@app.route("/api/download")
def download_video():
    url = request.args.get("url")
    if not url:
        return "Missing URL", 400

    try:
        ydl_opts = {'format': 'best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info['url']
            title = info.get('title', 'video')

            # جلب الفيديو كـ Stream
            req = requests.get(video_url, stream=True)
            
            # إرسال الفيديو كاستجابة بث (Stream Response) للمتصفح
            def generate():
                for chunk in req.iter_content(chunk_size=8192):
                    yield chunk

            return Response(
                generate(),
                headers={
                    "Content-Disposition": f"attachment; filename=hixu_{title[:20]}.mp4",
                    "Content-Type": "video/mp4"
                }
            )
    except Exception as e:
        return f"Download Failed: {str(e)}", 500
