from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# دالة الجلب باستخدام API خارجي (أضمن وأسرع للمنصات المجانية)
def get_download_url(video_url):
    # نستخدم بروتوكول جلب مفتوح يدعم أغلب المنصات
    api_url = f"https://api.vkrdown.com/api/index.php?url={video_url}"
    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        # محاولة استخراج أفضل رابط تحميل مباشر
        if data.get('success'):
            # يبحث في قائمة التحميلات عن أفضل جودة
            downloads = data.get('download', [])
            if downloads:
                return downloads[0].get('url')
        return None
    except:
        return None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SocialJet V2 | المحمل السريع</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body { background: #0f172a; color: white; font-family: 'Cairo', sans-serif; padding-top: 50px; }
        .main-card { background: #1e293b; border-radius: 25px; padding: 40px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); border: 1px solid #38bdf822; }
        .btn-go { background: linear-gradient(135deg, #38bdf8, #818cf8); border: none; color: white; padding: 12px; border-radius: 12px; font-weight: bold; width: 100%; }
        .btn-download { background: #10b981; border: none; color: white; padding: 15px; border-radius: 12px; font-weight: bold; display: block; text-align: center; text-decoration: none; margin-top: 20px; }
        .preview-img { width: 100%; border-radius: 15px; margin-top: 20px; border: 2px solid #38bdf8; }
        input { background: #0f172a !important; color: white !important; border: 1px solid #334155 !important; padding: 15px !important; border-radius: 12px !important; }
    </style>
</head>
<body>
    <div class="container"><div class="row justify-content-center"><div class="col-md-7 text-center">
        <h1 class="fw-bold mb-4" style="color: #38bdf8;">SocialJet <span class="text-white">V2</span></h1>
        <div class="main-card">
            <p class="mb-4 text-secondary">الصق رابط (تيك توك، فيسبوك، انستغرام) وسنقوم بالباقي</p>
            <form action="/analyze" method="post">
                <input type="text" name="url" class="form-control mb-3" placeholder="https://www.tiktok.com/..." required>
                <button type="submit" class="btn-go">ابدأ التحليل الآن 🚀</button>
            </form>

            {% if video_url %}
            <div class="mt-4">
                <p class="text-success fw-bold">✅ تم العثور على الفيديو!</p>
                <a href="{{ video_url }}" target="_blank" class="btn-download">اضغط هنا لتحميل/فتح الفيديو 📥</a>
                <small class="text-secondary d-block mt-2">إذا فتح الفيديو في صفحة جديدة، اضغط مطولاً واختر "حفظ الفيديو"</small>
            </div>
            {% endif %}

            {% if error %}<div class="alert alert-danger mt-4 bg-danger bg-opacity-10">{{ error }}</div>{% endif %}
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
    direct_link = get_download_url(url)
    
    if direct_link:
        return render_template_string(HTML_TEMPLATE, video_url=direct_link)
    else:
        return render_template_string(HTML_TEMPLATE, error="عذراً، هذا الرابط محمي أو غير مدعوم حالياً.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
