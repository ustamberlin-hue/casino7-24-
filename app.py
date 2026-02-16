from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <body style="background:#1a1a1a; color:gold; text-align:center; font-family:sans-serif; padding-top:100px;">
        <h1 style="font-size:3em;">🏢 GOKAYBETT HOLDİNG</h1>
        <div style="border:2px solid gold; display:inline-block; padding:30px; border-radius:20px; background:#222;">
            <h2 style="color:white;">YÖNETİM PANELİ</h2>
            <hr style="border-color:gold;">
            <p style="font-size:1.5em; color:#00ff00;">DURUM: SİSTEM AKTİF</p>
            <p style="color:white;">Holding merkezi internet üzerinden yayına alınmıştır.</p>
        </div>
    </body>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
