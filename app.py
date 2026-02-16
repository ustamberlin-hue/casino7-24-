from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <body style="background:#0a0a0a; color:gold; text-align:center; font-family:sans-serif; margin:0; padding:20px;">
        <header style="border-bottom:2px solid gold; padding:20px;">
            <h1 style="font-size:3em; margin:0;">🏢 GOKAYBETT HOLDİNG</h1>
            <p style="color:#00ff00; font-weight:bold;">● SİSTEM CANLI VE AKTİF</p>
        </header>

        <main style="max-width:800px; margin:20px auto;">
            <section style="background:#222; padding:15px; border-radius:15px; margin-bottom:20px; border:1px solid #444;">
                <h2 style="color:white; text-align:left;">📡 CANLI SKORLAR (ANLIK)</h2>
                <div style="display:flex; justify-content:space-between; background:#333; padding:10px; border-radius:8px; margin-bottom:5px;">
                    <span>Galatasaray - Beşiktaş</span>
                    <span style="color:#00ff00; font-weight:bold;">2 - 1</span>
                    <span style="color:gray;">Dk 82'</span>
                </div>
                <div style="display:flex; justify-content:space-between; background:#333; padding:10px; border-radius:8px;">
                    <span>Real Madrid - Barcelona</span>
                    <span style="color:#00ff00; font-weight:bold;">0 - 0</span>
                    <span style="color:gray;">Dk 15'</span>
                </div>
            </section>

            <section style="background:#1a1a1a; padding:15px; border-radius:15px; border:1px solid gold;">
                <h2 style="color:gold;">💰 GÜNÜN BANKO KUPONU</h2>
                <table style="width:100%; color:white; border-collapse:collapse;">
                    <tr style="border-bottom:1px solid #444;">
                        <th style="padding:10px; text-align:left;">Maç</th>
                        <th>Tahmin</th>
                        <th>Oran</th>
                    </tr>
                    <tr>
                        <td style="padding:10px; text-align:left;">Fenerbahçe - Kasımpaşa</td>
                        <td>MS 1</td>
                        <td>1.45</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; text-align:left;">Liverpool - Chelsea</td>
                        <td>KG VAR</td>
                        <td>1.60</td>
                    </tr>
                </table>
                <div style="margin-top:15px; font-size:1.2em; font-weight:bold;">TOPLAM ORAN: <span style="color:#00ff00;">2.32</span></div>
            </section>
        </main>

        <footer style="margin-top:40px; color:gray; font-size:0.8em;">
            GokayBett Holding © 2024 - Tüm Hakları Saklıdır.
        </footer>
    </body>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
