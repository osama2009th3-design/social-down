from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# دالة الجلب العالمية - تستخدم محرك سريع ومجاني
def fetch_video(video_url):
    # هذا API خارجي قوي جداً لتخطي حماية المنصات
    api_url = f"https://api.vkrdown.com/api/index.php?url={video_url}"
    try:
        response = requests.get(api_url, timeout=15)
        data = response.json()
        if data.get('success'):
            # استخراج رابط الفيديو المباشر
            return data['download'][0]['url']
        return None
    except:
        return None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>محمل الريلز الاحترافي</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: #0f172a; color: white; font-family: sans-serif; padding-top: 30px; }
        .nav-pills .nav-link { color: white; border: 1px solid #38bdf8; margin: 5px; }
        .nav-pills .nav-link.active { background: #38bdf8; }
        .card { background: #1e293b; border: none; border-radius: 20px; padding: 30px; margin-top: 20px; }
        .btn-download { background: #10b981; color: white; font-weight: bold; width: 100%; padding: 15px; border-radius: 10px; text-decoration: none; display: block; margin-top: 20px; }
        .input-group input { background: #0f172a; color: white; border: 1px solid #334155; }
    </style>
</head>
<body>
    <div class="container text-center">
        <h2 class="mb-4 text-info"><i class="fas fa-cloud-download-alt"></i> محمل الريلز الشامل</h2>
        
        <ul class="nav nav-pills justify-content-center mb-4" id="pills-tab" role="tablist">
            <li class="nav-item"><button class="nav-link active" data-bs-toggle="pill" data-bs-target="#tiktok"><i class="fab fa-tiktok"></i> TikTok</button></li>
            <li class="nav-item"><button class="nav-link" data-bs-toggle="pill" data-bs-target="#insta"><i class="fab fa-instagram"></i> Instagram</button></li>
            <li class="nav-item"><button class="nav-link" data-bs-toggle="pill" data-bs-target="#fb"><i class="fab fa-facebook"></i> Facebook</button></li>
        </ul>

        <div class="tab-content">
            <div class="tab-pane fade show active" id="tiktok">
                <div class="card">
                    <h4>تحميل من تيك توك</h4>
                    <form action="/download" method="post">
                        <input type="hidden" name="platform" value="TikTok">
                        <input type="text" name="url" class="form-control mb-3" placeholder="ضع رابط تيك توك هنا..." required>
                        <button type="submit" class="btn btn-info w-100 text-white">استخراج الفيديو</button>
                    </form>
                </div>
            </div>
            
            <div class="tab-pane fade" id="insta">
                <div class="card">
                    <h4>تحميل من انستغرام</h4>
                    <form action="/download" method="post">
                        <input type="hidden" name="platform" value="Instagram">
                        <input type="text" name="url" class="form-control mb-3" placeholder="ضع رابط ريلز انستا هنا..." required>
                        <button type="submit" class="btn btn-info w-100 text-white">استخراج الفيديو</button>
                    </form>
                </div>
            </div>

            <div class="tab-pane fade" id="fb">
                <div class="card">
                    <h4>تحميل من فيسبوك</h4>
                    <form action="/download" method="post">
                        <input type="hidden" name="platform" value="Facebook">
                        <input type="text" name="url" class="form-control mb-3" placeholder="ضع رابط فيديو فيسبوك هنا..." required>
                        <button type="submit" class="btn btn-info w-100 text-white">استخراج الفيديو</button>
                    </form>
                </div>
            </div>
        </div>

        {% if download_link %}
        <div class="mt-4 p-4 border border-success rounded">
            <p class="text-success fw-bold">جاري التحضير من منصة {{ platform }}...</p>
            <a href="{{ download_link }}" target="_blank" class="btn-download">اضغط هنا للتحميل المباشر</a>
        </div>
        {% endif %}

        {% if error %}<div class="alert alert-danger mt-4">{{ error }}</div>{% endif %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    platform = request.form.get('platform')
    link = fetch_video(url)
    if link:
        return render_template_string(HTML_TEMPLATE, download_link=link, platform=platform)
    return render_template_string(HTML_TEMPLATE, error="فشل جلب الفيديو، تأكد أن الرابط صحيح وعام.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
