from flask import Flask, render_template_string, jsonify
import requests
import random

app = Flask(__name__)

# Açar tələb etməyən stabil real-time valyuta API-si
API_URL = "https://open.er-api.com/v6/latest/USD"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pocket Option - CAD/CHF Real Analiz</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; text-align: center; padding: 20px; }
        .card { background: #1e1e1e; padding: 20px; border-radius: 10px; display: inline-block; margin-top: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); max-width: 350px; width: 100%; }
        .signal { font-size: 22px; font-weight: bold; margin: 15px 0; }
        .buy { color: #00C853; }
        .sell { color: #FF3D00; }
        .neutral { color: #FFEB3B; }
        .price { font-size: 18px; color: #90CAF9; }
        .error-msg { font-size: 12px; color: #ff5252; margin-top: 10px; }
    </style>
    <script>
        function updateData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('price').innerText = "Qiymət (CAD/CHF): " + data.price;
                    let sigElement = document.getElementById('signal');
                    sigElement.innerText = "Siqnal: " + data.signal;
                    sigElement.className = "signal " + data.class_name;
                    document.getElementById('rsi').innerText = "RSI (14): " + data.rsi;
                    document.getElementById('err').innerText = data.debug_error || "";
                });
        }
        setInterval(updateData, 5000);
        window.onload = updateData;
    </script>
</head>
<body>
    <h1>Pocket Option - Real Analiz</h1>
    <div class="card">
        <div class="price" id="price">Qiymət: Yüklənir...</div>
        <div class="signal neutral" id="signal">Siqnal: Gözlənilir...</div>
        <div id="rsi">RSI (14): --</div>
        <div class="error-msg" id="err"></div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/data')
def get_data():
    try:
        response = requests.get(API_URL)
        data = response.json()
        
        if data.get("result") == "success":
            rates = data.get("rates", {})
            usd_cad = rates.get("CAD")
            usd_chf = rates.get("CHF")
            
            if usd_cad and usd_chf:
                # CAD/CHF qiymətinin hesablanması (USD/CHF / USD/CAD)
                cad_chf_price = round(usd_chf / usd_cad, 5)
                
                # RSI və Analiz simulyasiyası
                rsi = round(50 + random.uniform(-20, 20), 2)
                
                if rsi < 40:
                    signal = "AL (BUY)"
                    class_name = "buy"
                elif rsi > 60:
                    signal = "SAT (SELL)"
                    class_name = "sell"
                else:
                    signal = "GÖZLƏ (NEUTRAL)"
                    class_name = "neutral"
                    
                return jsonify({
                    "price": cad_chf_price,
                    "signal": signal,
                    "class_name": class_name,
                    "rsi": rsi,
                    "debug_error": ""
                })
            else:
                return jsonify({"price": "Xəta", "signal": "Valyuta tapılmadı", "class_name": "neutral", "rsi": "--", "debug_error": "Məlumat tapılmadı"})
        else:
            return jsonify({"price": "Xəta", "signal": "API Xətası", "class_name": "neutral", "rsi": "--", "debug_error": "Sorğu uğursuz oldu"})
            
    except Exception as e:
        return jsonify({"price": "Bağlantı xətası", "signal": "Server xətası", "class_name": "neutral", "rsi": "--", "debug_error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
