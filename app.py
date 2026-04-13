import os
import uuid
import time
import threading
from flask import Flask, render_template_string, request, jsonify, send_file, after_this_request
import yt_dlp

app = Flask(__name__)

# Configuration
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# --- THE SAAS EXPERIENCE (HTML/CSS/JS) ---
UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>hixu Downloadr | Premium Video Extraction</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;800&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
    <style>
        :root {
            --primary: #6366f1;
            --secondary: #a855f7;
            --bg: #030712;
            --glass: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text: #f8fafc;
            --text-dim: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            overflow-x: hidden;
            min-height: 100vh;
        }

        /* Animated Mesh Gradient Background */
        .bg-gradient {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1;
            background: radial-gradient(circle at 0% 0%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 100% 100%, rgba(168, 85, 247, 0.15) 0%, transparent 50%);
            animation: pulse 10s ease-in-out infinite alternate;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            100% { transform: scale(1.1); }
        }

        /* Layout Structure */
        header {
            padding: 2rem;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -1px;
            background: linear-gradient(to right, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero {
            max-width: 900px;
            margin: 4rem auto;
            padding: 0 1.5rem;
            text-align: center;
        }

        h1 {
            font-size: clamp(2.5rem, 8vw, 4.5rem);
            font-weight: 800;
            line-height: 1.1;
            letter-spacing: -0.05em;
            margin-bottom: 1.5rem;
            animation: fadeInUp 0.8s ease;
        }

        .tagline {
            color: var(--text-dim);
            font-size: 1.25rem;
            margin-bottom: 3rem;
            animation: fadeInUp 1s ease;
        }

        /* The Main Glass Card */
        .glass-card {
            background: var(--glass);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 32px;
            padding: 3rem;
            max-width: 650px;
            margin: 0 auto;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            transition: transform 0.3s ease;
        }

        .input-group {
            display: flex;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 8px;
            gap: 10px;
            transition: all 0.3s ease;
        }

        .input-group:focus-within {
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
        }

        input {
            flex: 1;
            background: transparent;
            border: none;
            color: white;
            padding: 15px 20px;
            font-size: 1rem;
            outline: none;
        }

        /* Premium Button Style */
        .btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            position: relative;
            overflow: hidden;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px -5px rgba(99, 102, 241, 0.5);
            background: #4f46e5;
        }

        .btn:active { transform: scale(0.96); }

        /* Preview Section */
        #previewArea {
            margin-top: 3rem;
            display: none;
            animation: scaleIn 0.5s cubic-bezier(0.23, 1, 0.32, 1);
        }

        .video-container {
            width: 100%;
            border-radius: 24px;
            overflow: hidden;
            background: #000;
            aspect-ratio: 16 / 9;
            margin: 2rem 0;
            border: 1px solid var(--glass-border);
        }

        video { width: 100%; height: 100%; }

        #videoTitle {
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--text-dim);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        /* Interactive Elements */
        .loader {
            display: none;
            width: 40px;
            height: 40px;
            border: 3px solid rgba(255,255,255,0.1);
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 2rem auto;
        }

        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes scaleIn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }

        footer {
            margin-top: auto;
            padding: 4rem 2rem;
            text-align: center;
            color: var(--text-dim);
            font-size: 0.9rem;
            opacity: 0.6;
        }

        /* Responsive */
        @media (max-width: 600px) {
            h1 { font-size: 2.8rem; }
            .glass-card { padding: 1.5rem; border-radius: 24px; }
            .input-group { flex-direction: column; background: transparent; border: none; padding: 0; }
            input { background: rgba(0,0,0,0.3); border-radius: 16px; border: 1px solid var(--glass-border); margin-bottom: 10px; }
            .btn { width: 100%; }
        }
    </style>
</head>
<body>
    <div class="bg-gradient"></div>

    <header>
        <div class="logo">hixu.</div>
    </header>

    <main class="hero">
        <h1>Download moments, <br><span style="color: var(--primary)">seamlessly.</span></h1>
        <p class="tagline">The high-performance video toolkit for the modern web.</p>

        <div class="glass-card">
            <div class="input-group">
                <input type="text" id="urlInput" placeholder="Paste link (TikTok, Instagram, Facebook)..." autocomplete="off">
                <button id="fetchBtn" class="btn">
                    <span>Preview</span> <i class="fas fa-arrow-right"></i>
                </button>
            </div>

            <div id="loader" class="loader"></div>
            <div id="error" style="color: #f87171; margin-top: 1.5rem; display: none; font-size: 0.9rem;"></div>

            <div id="previewArea">
                <p id="videoTitle"></p>
                <div class="video-container">
                    <video id="player" controls playsinline></video>
                </div>
                <button id="downloadBtn" class="btn" style="width: 100%; padding: 20px; background: white; color: black;">
                    <i class="fas fa-download"></i> <span>Download Now</span>
                </button>
            </div>
        </div>
    </main>

    <footer>
        <p>&copy; 2026 hixu Downloadr • Built with Gemini 3 Flash</p>
    </footer>

    <script>
        const fetchBtn = document.getElementById('fetchBtn');
        const urlInput = document.getElementById('urlInput');
        const loader = document.getElementById('loader');
        const error = document.getElementById('error');
        const previewArea = document.getElementById('previewArea');
        const player = document.getElementById('player');
        const videoTitle = document.getElementById('videoTitle');
        const downloadBtn = document.getElementById('downloadBtn');

        let currentData = null;

        fetchBtn.addEventListener('click', async () => {
            const url = urlInput.value.trim();
            if (!url) return;

            // Reset UI
            error.style.display = 'none';
            previewArea.style.display = 'none';
            loader.style.display = 'block';
            fetchBtn.disabled = true;

            try {
                const res = await fetch('/api/preview', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ url })
                });
                
                const data = await res.json();
                if (!res.ok) throw new Error(data.error);

                currentData = data;
                videoTitle.innerText = data.title;
                player.src = data.stream_url;
                
                loader.style.display = 'none';
                previewArea.style.display = 'block';
            } catch (err) {
                error.innerText = err.message;
                error.style.display = 'block';
                loader.style.display = 'none';
            } finally {
                fetchBtn.disabled = false;
            }
        });

        downloadBtn.addEventListener('click', () => {
            if (!currentData) return;
            downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Downloading...';
            window.location.href = `/api/download?url=${encodeURIComponent(currentData.original_url)}`;
            
            setTimeout(() => {
                downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Now';
            }, 5000);
        });
    </script>
</body>
</html>
"""

# --- BACKEND ARCHITECTURE ---

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
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            # Find a streamable URL for the preview player
            stream_url = info.get('url') or (info.get('formats')[0].get('url') if info.get('formats') else None)
            
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

    job_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_FOLDER, f"{job_id}.%(ext)s")

    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Clean up logic
            @after_this_request
            def cleanup(response):
                def delete_file():
                    time.sleep(20) # Wait for download to start
                    try:
                        if os.path.exists(filename): os.remove(filename)
                    except: pass
                threading.Thread(target=delete_file).start()
                return response

            return send_file(
                filename, 
                as_attachment=True, 
                download_name=f"hixu_{info.get('title', 'video')[:30]}.mp4"
            )
    except Exception as e:
        return f"Download Failed: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
