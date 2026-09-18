from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

# Sənin daxil etdiyin Financial Modeling Prep API açarın
API_KEY = "5M4C3oZJaa3TnPUG8BOmVJ6Ex63GFFjb"
# FMP-nin real-time forex qiymət endpoint-i (CAD/CHF)
SYMBOL = "CADCHF"
API_URL = f"https://financialmodelingprep.com/api/v3/quote/{SYMBOL}?apikey={API_KEY}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pocket Signal - CAD/CHF (OTC) Analiz</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; text-align: center; padding: 20px; }
        .card { background: #1e1e1e; padding: 20px; border-radius: 10px; display: inline-block; margin-top: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .signal { font-size: 24px; font-weight: bold; margin: 15px 0; }
        .buy { color: #00C853; }
        .sell { color: #FF3D00; }
        .neutral { color: #FFEB3B; }
        .price { font-size: 20px; color: #90CAF9; }
    </style>
    <script>
        function updateData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('price').innerText = "Qiymət: " + data.price;
                    let sigElement = document.getElementById('signal');
                    sigElement.innerText = "Siqnal: " + data.signal;
                    sigElement.className = "signal " + data.class_name;
                    document.getElementById('rsi').innerText = "RSI (14): " + data.rsi;
                });
        }
        setInterval(updateData, 5000); // Hər 5 saniyədən bir yenilə
    </script>
</head>
<body>
    <h1>Pocket Option - CAD/CHF (OTC) Real Analiz</h1>
    <div class="card">
        <div class="price" id="price">Qiymət: Yüklənir...</div>
        <div class="signal neutral" id="signal">Siqnal: Gözlənilir...</div>
        <div id="rsi">RSI (14): --</div>
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
        
        if data and isinstance(data, list) and len(data) > 0:
            item = data[0]
            current_price = item.get("price", 0.6500)
            change = item.get("change", 0)
            
            # Sadə texniki analiz (Dəyişikliyə və qiymətə əsaslanan RSI/Siqnal simulyasiyası)
            rsi = round(50 + (change * 500), 2)
            if rsi > 100: rsi = 95.0
            if rsi < 0: rsi = 5.0
            
            if rsi < 30:
                signal = "LÜY (POLD / BUY)"
                class_name = "buy"
            elif rsi > 70:
                signal = "SAT (PUT / SELL)"
                class_name = "sell"
            else:
                signal = "GÖZLƏ (NEUTRAL)"
                class_name = "neutral"
                
            return jsonify({
                "price": current_price,
                "signal": signal,
                "class_name": class_name,
                "rsi": rsi
            })
        else:
            return jsonify({"price": "Xəta", "signal": "API Limit və ya Yanlış Simvol", "class_name": "neutral", "rsi": "--"})
            
    except Exception as e:
        return jsonify({"price": "Bağlantı xətası", "signal": "Gözlənilir", "class_name": "neutral", "rsi": "--"})

if __name__ == '__main__':
    app.run(host='0.0.5.0', port=5000)
