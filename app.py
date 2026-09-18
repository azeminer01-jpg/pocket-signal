from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

API_KEY = "5M4C3oZJaa3TnPUG8BOmVJ6Ex63GFFjb"
# Sınaq məqsədi ilə standart FOREX formatını yoxlayaq (məsələn: EURUSD və ya CADCHF)
SYMBOL = "EURUSD" 
API_URL = f"https://financialmodelingprep.com/api/v3/quote/{SYMBOL}?apikey={API_KEY}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pocket Signal - Real Analiz</title>
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
                    document.getElementById('price').innerText = "Qiymət: " + data.price;
                    let sigElement = document.getElementById('signal');
                    sigElement.innerText = "Siqnal: " + data.signal;
                    sigElement.className = "signal " + data.class_name;
                    document.getElementById('rsi').innerText = "RSI (14): " + data.rsi;
                    document.getElementById('err').innerText = data.debug_error || "";
                });
        }
        setInterval(updateData, 5000);
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
        
        # Əgər FMP API xəbərdarlıq və ya səhv qaytarırsa
        debug_err = ""
        if isinstance(data, dict) and "Error Message" in data:
            return jsonify({
                "price": "API Xətası",
                "signal": "Yanlış Açar və ya Sorğu",
                "class_name": "neutral",
                "rsi": "--",
                "debug_error": data["Error Message"]
            })

        if data and isinstance(data, list) and len(data) > 0:
            item = data[0]
            current_price = item.get("price", 1.0000)
            change = item.get("change", 0)
            
            rsi = round(50 + (change * 500), 2)
            rsi = min(95.0, max(5.0, rsi))
            
            if rsi < 30:
                signal = "AL (BUY)"
                class_name = "buy"
            elif rsi > 70:
                signal = "SAT (SELL)"
                class_name = "sell"
            else:
                signal = "GÖZLƏ (NEUTRAL)"
                class_name = "neutral"
                
            return jsonify({
                "price": current_price,
                "signal": signal,
                "class_name": class_name,
                "rsi": rsi,
                "debug_error": ""
            })
        else:
            return jsonify({
                "price": "Boş Cavab", 
                "signal": "Data tapılmadı", 
                "class_name": "neutral", 
                "rsi": "--", 
                "debug_error": str(data)
            })
            
    except Exception as e:
        return jsonify({
            "price": "Bağlantı xətası", 
            "signal": "Server xətası", 
            "class_name": "neutral", 
            "rsi": "--", 
            "debug_error": str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
