import os
import subprocess
import time
import signal
from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
# أسرار الموقع - يفضل تغييرها عند الرفع الفعلي
app.config['SECRET_KEY'] = 'HixuCloud-Secure-99'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hixu_hosting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# إعداد المسارات - سيتم التعرف عليها تلقائياً
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)

# --- قاعدة بيانات المستخدمين ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    active_pid = db.Column(db.Integer) # لتتبع العملية المشغلة فعلياً
    start_time = db.Column(db.Float)   # وقت البدء لحساب التايمر

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- واجهة المستخدم (تنسيق احترافي للشركات) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hixu Hosting | Dashboard</title>
    <style>
        :root { --primary: #3b82f6; --bg: #0f172a; --card: #1e293b; --accent: #10b981; --danger: #ef4444; }
        body { background: var(--bg); color: #f8fafc; font-family: 'Inter', sans-serif; margin: 0; display: flex; flex-direction: column; min-height: 100vh; }
        .navbar { background: var(--card); padding: 1rem 5%; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; }
        .container { width: 100%; max-width: 480px; margin: auto; padding: 20px; box-sizing: border-box; }
        .card { background: var(--card); border-radius: 1rem; padding: 2rem; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); border: 1px solid #334155; }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 0.5rem; border: 1px solid #334155; background: #0f172a; color: white; box-sizing: border-box; }
        .btn { width: 100%; padding: 12px; border: none; border-radius: 0.5rem; font-weight: 700; cursor: pointer; transition: 0.2s; background: var(--primary); color: white; margin-top: 1rem; }
        .btn:hover { opacity: 0.9; transform: translateY(-1px); }
        .btn-stop { background: var(--danger); }
        .timer { font-size: 2.5rem; color: var(--accent); font-family: monospace; margin: 1.5rem 0; text-shadow: 0 0 15px rgba(16, 185, 129, 0.3); }
        .alert { color: #f87171; font-size: 0.85rem; margin-bottom: 1rem; }
        a { color: var(--primary); text-decoration: none; font-size: 0.85rem; }
    </style>
</head>
<body>
    <div class="navbar">
        <b style="font-size: 1.5rem;">HIXU <span style="color:var(--primary)">CLOUD</span></b>
        {% if current_user.is_authenticated %}<a href="/logout" style="color:#94a3b8;">تسجيل خروج</a>{% endif %}
    </div>
    <div class="container">
        {% with messages = get_flashed_messages() %}{% for m in messages %}<div class="alert">{{m}}</div>{% endfor %}{% endwith %}
        
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

# --- الروابط (Logic) ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if User.query.filter((User.email == request.form['email']) | (User.username == request.form['username'])).first():
            flash('البيانات مسجلة مسبقاً!')
            return redirect(url_for('signup'))
        new_user = User(username=request.form['username'], email=request.form['email'], password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE + """
    {% block content %}
    <div class="card">
        <h2>إنشاء حساب استضافة</h2>
        <form method="post">
            <input name="username" placeholder="اسم المستخدم" required>
            <input name="email" type="email" placeholder="البريد الإلكتروني" required>
            <input name="password" type="password" placeholder="كلمة المرور" required>
            <button class="btn">ابدأ الآن مجاناً</button>
        </form>
        <p style="text-align:center;">لديك حساب؟ <a href="/login">دخول</a></p>
    </div>
    {% endblock %}
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email'], password=request.form['password']).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        flash('خطأ في الإيميل أو كلمة المرور!')
    return render_template_string(HTML_TEMPLATE + """
    {% block content %}
    <div class="card">
        <h2>تسجيل الدخول</h2>
        <form method="post">
            <input name="email" type="email" placeholder="البريد الإلكتروني" required>
            <input name="password" type="password" placeholder="كلمة المرور" required>
            <button class="btn">دخول للمنصة</button>
        </form>
        <p style="text-align:center;">جديد هنا؟ <a href="/signup">سجل حسابك</a></p>
    </div>
    {% endblock %}
    """)

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user_file = f"bot_run_{current_user.id}.py"
    file_path = os.path.join(UPLOAD_FOLDER, user_file)

    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.py'):
            # قتل أي عملية قديمة للمستخدم قبل البدء بالجديدة
            if current_user.active_pid:
                try: os.kill(current_user.active_pid, signal.SIGTERM)
                except: pass
            
            file.save(file_path)
            # تشغيل حقيقي (مو شكل) وحفظ الـ PID
            proc = subprocess.Popen(['python3', file_path])
            current_user.active_pid = proc.pid
            current_user.start_time = time.time()
            db.session.commit()
            flash('🚀 استضافتك الآن تعمل بنجاح!')
            return redirect(url_for('index'))

    # حساب وقت التايمر (24 ساعة)
    time_left = 0
    if current_user.start_time:
        passed = time.time() - current_user.start_time
        time_left = max(0, int(86400 - passed))

    return render_template_string(HTML_TEMPLATE + """
    {% block content %}
    <div class="card" style="text-align:center;">
        <h3>مرحباً بك، {{ current_user.username }}</h3>
        {% if current_user.active_pid %}
            <div class="timer" id="timer">00:00:00</div>
            <p style="color:#94a3b8;">الاستضافة نشطة 🟢</p>
            <form action="/stop" method="post"><button class="btn btn-stop">إيقاف الاستضافة نهائياً</button></form>
        {% else %}
            <form method="post" enctype="multipart/form-data">
                <label style="font-size:0.8rem; color:#94a3b8;">ارفع السكربت الرئيسي (.py)</label>
                <input type="file" name="file" accept=".py" required>
                <button class="btn">🚀 تشغيل السيرفر</button>
            </form>
        {% endif %}
    </div>
    <script>
        let s = {{ time_left }};
        if(s > 0){
            setInterval(() => {
                if(s <= 0) { location.reload(); return; }
                s--;
                let h=Math.floor(s/3600), m=Math.floor((s%3600)/60), sc=s%60;
                document.getElementById('timer').innerText = 
                    `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${sc.toString().padStart(2,'0')}`;
            }, 1000);
        }
    </script>
    {% endblock %}
    """, time_left=time_left)

@app.route('/stop', methods=['POST'])
@login_required
def stop():
    # إيقاف العملية فعلياً من السيرفر
    if current_user.active_pid:
        try: os.kill(current_user.active_pid, signal.SIGTERM)
        except: pass
    
    # حذف الملف لتنظيف المساحة
    user_file = f"bot_run_{current_user.id}.py"
    path = os.path.join(UPLOAD_FOLDER, user_file)
    if os.path.exists(path): os.remove(path)
    
    current_user.active_pid = None
    current_user.start_time = None
    db.session.commit()
    flash('تم إيقاف وحذف الاستضافة.')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
