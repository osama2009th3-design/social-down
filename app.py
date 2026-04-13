from flask import Flask, render_template_string, request, Response
import yt_dlp
import requests
import os

app = Flask(__name__)

# دالة الجلب الاحترافية - تم تحديثها لتخطي حماية المنصات
def get_video_info(url):
    ydl_opts = {
        # محاولة جلب أفضل جودة فيديو MP4 مباشرة
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        # انتحال شخصية متصفح حديث جداً (ضروري لفيسبوك وتيك توك)
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_color': True,
        'geo_bypass': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return None
            
            # البحث عن الرابط المباشر في النتائج
            video_url = info.get('url')
            if not video_url and 'entries' in info:
                video_url = info['entries'][0].get('url')
            
            return video_url
        except Exception as e:
            print(f"YDL Error: {e}")
            return None

@app.route('/force_download')
def force_download():
    video_url = request.args.get('url')
    if not video_url:
        return "الرابط مفقود", 400
    
    # تمرير الفيديو عبر السيرفر لإجبار التحميل وتخطى الحظر
    r = requests.get(video_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
    return Response(
        r.iter_content(chunk_size=1024*1024),
        headers={
            "Content-Disposition": "attachment; filename=SocialJet_Video.mp4",
            "Content-Type": "video/mp4"
        }
    )

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SocialJet | المحمل الذكي</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: white; font-family: 'Cairo', sans-serif; text-align: center; padding-top: 50px; }
        .card { background: #1e293b; border-radius: 20px; padding: 30px; border: none; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .btn-primary { background: #38bdf8; border: none; font-weight: bold; }
        .btn-success { background: #10b981; border: none; font-weight: bold; padding: 15px; width: 100%; margin-top: 20px; }
        input { background: #0f172a !important; color: white !important; border: 1px solid #334155 !important; border-radius: 10px !important; }
        video { border-radius: 15px; margin-top: 20px; background: #000; }
    </style>
</head>
<body>
    <div class="container"><div class="row justify-content-center"><div class="col-md-8">
        <h2 class="mb-4">🚀 SocialJet PRO</h2>
        <div class="card">
            <form action="/analyze" method="post">
                <input type="text" name="url" class="form-control mb-3" placeholder="ضع رابط فيسبوك، تيك توك، أو انستا هنا..." required>
                <button type="submit" class="btn btn-primary w-100">تحليل الرابط</button>
            </form>

            {% if video_url %}
            <video width="100%" controls><source src="{{ video_url }}" type="video/mp4"></video>
            <a href="/force_download?url={{ video_url | urlencode }}" class="btn btn-success">تحميل الفيديو الآن</a>
            {% endif %}

            {% if error %}<div class="alert alert-danger mt-3">{{ error }}</div>{% endif %}
        </div>
    </div></div></div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form.get('url')
    video_url = get_video_info(url)
    if video_url:
        return render_template_string(HTML_TEMPLATE, video_url=video_url)
    else:
        return render_template_string(HTML_TEMPLATE, error="فشل جلب الفيديو. تأكد أن الرابط عام وليس خاص.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
