import os
from flask import Flask, render_template_string

app = Flask(__name__)
app.secret_key = "goruntulu_sohbet_2026_pro"

# ---------------- GÖRSEL VE BAĞLANTI KODU (HTML/JS) ----------------
# Bu kod PeerJS kütüphanesini kullanarak karmaşık sunucu işlemlerini otomatiğe bağlar.
SOHBET_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Canlı Görüntülü Sohbet Odası</title>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <style>
        body { background: #0f0f0f; color: white; font-family: 'Segoe UI', sans-serif; text-align: center; margin: 0; padding: 20px; }
        .main-container { max-width: 900px; margin: auto; }
        .video-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        video { width: 100%; background: #222; border-radius: 15px; border: 2px solid #3498db; transform: scaleX(-1); }
        .info-box { background: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-bottom: 4px solid #27ae60; }
        input { padding: 10px; border-radius: 5px; border: none; width: 200px; }
        button { padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer; font-weight: bold; }
        .btn-call { background: #e74c3c; color: white; }
        .btn-start { background: #27ae60; color: white; }
    </style>
</head>
<body>
    <div class="main-container">
        <h1>🎥 PRO Görüntülü Sohbet</h1>
        
        <div class="info-box">
            <p>Senin Numaran (ID): <strong id="my-id" style="color: #f1c40f;">Yükleniyor...</strong></p>
            <p style="font-size: 12px; color: #888;">Bu numarayı arkadaşına gönder, seni arasın!</p>
        </div>

        <div class="controls">
            <input type="text" id="peer-id" placeholder="Arkadaşının ID'sini yaz...">
            <button class="btn-call" onclick="makeCall()">ARA</button>
        </div>

        <div class="video-grid">
            <div>
                <p>Kendi Kameran</p>
                <video id="localVideo" autoplay playsinline muted></video>
            </div>
            <div>
                <p>Arkadaşının Görüntüsü</p>
                <video id="remoteVideo" autoplay playsinline></video>
            </div>
        </div>
    </div>

    <script>
        const localVideo = document.getElementById('localVideo');
        const remoteVideo = document.getElementById('remoteVideo');
        let myStream;
        let peer;

        // 1. Kamerayı ve Mikrofonu Başlat
        navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
            myStream = stream;
            localVideo.srcObject = stream;
            
            // 2. Peer Bağlantısını Kur (Kamera açılmadan ID alma)
            peer = new Peer(); 

            peer.on('open', (id) => {
                document.getElementById('my-id').innerText = id;
            });

            // 3. Gelen Aramayı Cevapla
            peer.on('call', (call) => {
                call.answer(myStream);
                call.on('stream', (userRemoteStream) => {
                    remoteVideo.srcObject = userRemoteStream;
                });
            });
        });

        // 4. Arkadaşını Ara
        function makeCall() {
            const remoteId = document.getElementById('peer-id').value;
            if(!remoteId) return alert("Lütfen bir ID girin!");
            
            const call = peer.call(remoteId, myStream);
            call.on('stream', (userRemoteStream) => {
                remoteVideo.srcObject = userRemoteStream;
            });
        }
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
