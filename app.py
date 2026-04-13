from flask import Flask, render_template_string, request, Response
import yt_dlp
import requests
import urllib.parse

app = Flask(__name__)

# المحرك البرمجي للجلب
def get_video_info(url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# نظام التحميل القسري (إجبار المتصفح على التحميل)
@app.route('/force_download')
def force_download():
    video_url = request.args.get('url')
    r = requests.get(video_url, stream=True)
    return Response(
        r.iter_content(chunk_size=1024*1024),
        headers={
            "Content-Disposition": "attachment; filename=MediaPro_Video.mp4",
            "Content-Type": "video/mp4"
        }
    )

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SocialJet | المنصة الاحترافية لتحميل الوسائط</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --primary-dark: #0f172a;
            --accent-blue: #38bdf8;
            --premium-purple: #818cf8;
            --glass-bg: rgba(255, 255, 255, 0.03);
        }

        body { 
            background-color: #0b0f19; 
            color: #f8fafc; 
            font-family: 'Cairo', sans-serif;
            min-height: 100vh;
        }

        /* الهيدر الاحترافي */
        .navbar {
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        .hero-section {
            padding: 80px 0 40px;
            background: radial-gradient(circle at top right, rgba(56, 189, 248, 0.1), transparent);
        }

        /* الأقسام التفاعلية */
        .platform-nav {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 40px;
        }

        .platform-item {
            background: var(--glass-bg);
            border: 1px solid rgba(255,255,255,0.1);
            padding: 12px 25px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: #94a3b8;
        }

        .platform-item:hover, .platform-item.active {
            background: rgba(56, 189, 248, 0.1);
            border-color: var(--accent-blue);
            color: var(--accent-blue);
            transform: translateY(-3px);
        }

        /* صندوق الإدخال */
        .download-card {
            background: #1e293b;
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.05);
        }

        .input-wrapper {
            background: #0f172a;
            padding: 8px;
            border-radius: 16px;
            display: flex;
            border: 2px solid transparent;
            transition: 0.3s;
        }

        .input-wrapper:focus-within {
            border-color: var(--premium-purple);
        }

        .input-wrapper input {
            background: transparent;
            border: none;
            color: white;
            padding-left: 15px;
            outline: none;
            width: 100%;
        }

        .btn-analyze {
            background: linear-gradient(135deg, var(--accent-blue), var(--premium-purple));
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 12px;
            font-weight: bold;
            transition: 0.3s;
        }

        /* قسم النتيجة والمعاينة */
        .preview-container {
            margin-top: 30px;
            background: #0f172a;
            border-radius: 20px;
            padding: 20px;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }

        .video-frame {
            border-radius: 12px;
            overflow: hidden;
            background: black;
            margin-bottom: 20px;
        }

        .btn-download-final {
            background: #10b981;
            color: white;
            width: 100%;
            padding: 15px;
            border-radius: 12px;
            font-weight: bold;
            text-decoration: none;
            display: inline-block;
            transition: 0.3s;
            text-align: center;
        }

        .btn-download-final:hover {
            background: #059669;
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
            color: white;
        }

        .footer-text {
            color: #64748b;
            font-size: 0.9rem;
            margin-top: 50px;
        }
    </style>
</head>
<body>

<nav class="navbar navbar-dark fixed-top">
    <div class="container">
        <a class="navbar-brand fw-bold" href="#">
            <i class="fas fa-rocket text-info me-2"></i> SocialJet <span class="badge bg-primary fs-6">Pro</span>
        </a>
    </div>
</nav>

<div class="hero-section text-center">
    <div class="container">
        <h1 class="display-5 fw-bold mb-3">تحميل الوسائط بلا قيود</h1>
        <p class="text-secondary lead">منصة موثوقة للشركات وصناع المحتوى لتحميل الفيديوهات بجودة 4K</p>
    </div>
</div>

<div class="container mb-5">
    <div class="row justify-content-center">
        <div class="col-lg-7">
            
            <div class="platform-nav">
                <div class="platform-item active"><i class="fab fa-instagram me-1"></i> Instagram</div>
                <div class="platform-item"><i class="fab fa-tiktok me-1"></i> TikTok</div>
                <div class="platform-item"><i class="fab fa-facebook me-1"></i> Facebook</div>
            </div>

            <div class="download-card">
                <form action="/analyze" method="post">
                    <div class="input-wrapper">
                        <input type="text" name="url" placeholder="أدخل رابط الفيديو هنا (Reels, TikTok, Video)..." required>
                        <button type="submit" class="btn-analyze">تحليل</button>
                    </div>
                </form>

                {% if video_url %}
                <div class="preview-container">
                    <div class="text-center mb-3">
                        <span class="text-info small"><i class="fas fa-check-circle"></i> تم التحقق من الرابط بنجاح</span>
                    </div>
                    <div class="video-frame shadow">
                        <video width="100%" controls>
                            <source src="{{ video_url }}" type="video/mp4">
                        </video>
                    </div>
                    <a href="/force_download?url={{ video_url | urlencode }}" class="btn btn-download-final">
                        <i class="fas fa-download me-2"></i> تحميل الفيديو مباشرة لجهازك
                    </a>
                </div>
                {% endif %}

                {% if error %}
                <div class="alert alert-danger bg-danger bg-opacity-10 border-danger text-danger mt-4 rounded-3 text-center">
                    <i class="fas fa-exclamation-triangle me-2"></i> {{ error }}
                </div>
                {% endif %}
            </div>

            <div class="footer-text text-center">
                <p>© 2026 SocialJet Enterprise Solution. جميع الحقوق محفوظة.</p>
                <div class="d-flex justify-content-center gap-3">
                    <small>الشروط</small> • <small>الخصوصية</small> • <small>اتصل بنا</small>
                </div>
            </div>
        </div>
    </div>
</div>

</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form.get('url')
    try:
        data = get_video_info(url)
        return render_template_string(HTML_TEMPLATE, video_url=data.get('url'))
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, error="عذراً، هذا الرابط غير مدعوم أو الحساب خاص.")

if __name__ == '__main__':
    app.run(debug=True)
