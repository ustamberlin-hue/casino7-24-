import os
from flask import Flask, render_template_string

app = Flask(__name__)
app.secret_key = "sohbet_odasi_2026"

# ---------------- GÖRSEL TASARIM VE GÖRÜNTÜ KODU ----------------
# Bu HTML, tarayıcının kamerasını açar ve diğer kişiye bağlanmayı sağlar.
SOHBET_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Canlı Görüntülü Sohbet</title>
    <style>
        body { background: #121212; color: white; font-family: sans-serif; text-align: center; }
        .video-container { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-top: 20px; }
        video { background: #333; width: 45%; max-width: 400px; border-radius: 15px; border: 3px solid #3498db; }
        .controls { margin-top: 20px; }
        button { padding: 10px 20px; font-size: 16px; cursor: pointer; border-radius: 5px; border: none; background: #27ae60; color: white; }
    </style>
</head>
<body>
    <h1>🎥 Görüntülü Sohbet Odası</h1>
    <p>Oda ID: <strong>Genel Oda</strong></p>
    
    <div class="video-container">
        <div>
            <p>Senin Görüntün</p>
            <video id="localVideo" autoplay playsinline muted></video>
        </div>
        <div>
            <p>Karşıdaki Kişi</p>
            <video id="remoteVideo" autoplay playsinline></video>
        </div>
    </div>

    <div class="controls">
        <button onclick="startVideo()">Kamerayı Aç</button>
    </div>

    <script>
        let localStream;
        const localVideo = document.getElementById('localVideo');

        async function startVideo() {
            try {
                localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                localVideo.srcObject = localStream;
            } catch (error) {
                alert("Kameraya ulaşılamadı! Lütfen izin verin.");
            }
        }
        // Not: Gerçek bir bağlantı için (WebRTC Signaling) ek bir sunucu servisi gerekir. 
        // Bu temel kod şu an kameranı açmanı ve görüntünü görmeni sağlar.
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(SOHBET_HTML)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
