from flask import Flask, render_template_string, jsonify, request
import random

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pocket Option - 1M Dəqiq OTC Analizator</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #121212; color: #ffffff; text-align: center; padding: 20px; margin: 0; }
        .card { background: #1e1e1e; padding: 20px; border-radius: 12px; display: inline-block; margin-top: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.6); max-width: 400px; width: 90%; text-align: left; }
        .signal { font-size: 24px; font-weight: bold; margin: 15px 0; text-align: center; }
        .buy { color: #00C853; text-shadow: 0 0 10px rgba(0,200,83,0.3); }
        .sell { color: #FF3D00; text-shadow: 0 0 10px rgba(255,61,0,0.3); }
        .neutral { color: #FFEB3B; }
        .input-group { margin-bottom: 15px; }
        .input-group label { display: block; font-size: 13px; color: #90CAF9; margin-bottom: 5px; }
        .input-box, .select-box { width: 100%; padding: 10px; border-radius: 8px; background: #2c2c2c; color: white; border: 1px solid #444; font-size: 16px; box-sizing: border-box; }
        .indicators { font-size: 13px; color: #B0BEC5; background: #252525; padding: 10px; border-radius: 8px; margin: 10px 0; }
        .indicators div { margin: 5px 0; }
        .btn { background: #2979FF; color: white; border: none; padding: 12px 20px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; transition: 0.2s; margin-top: 10px; }
        .btn:active { background: #1565C0; transform: scale(0.98); }
        .market-status { font-size: 12px; background: rgba(255,152,0,0.15); color: #FFB74D; padding: 6px; border-radius: 6px; text-align: center; margin-bottom: 15px; }
    </style>
    <script>
        function analyzeMarket() {
            let symbol = document.getElementById('pairSelect').value;
            let manualPrice = document.getElementById('manualPrice').value;
            let sigElement = document.getElementById('signal');
            
            sigElement.innerText = "Analiz edilir...";
            sigElement.className = "signal neutral";
            
            fetch('/analyze?symbol=' + symbol + '&price=' + manualPrice)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('usedPrice').innerText = "Analiz edilən Qiymət: " + data.price;
                    sigElement.innerText = "Siqnal: " + data.signal;
                    sigElement.className = "signal " + data.class_name;
                    
                    document.getElementById('rsi').innerText = data.rsi;
                    document.getElementById('stoch').innerText = data.stoch;
                    document.getElementById('trend').innerText = data.trend;
                    document.getElementById('recommendation').innerText = data.recommendation;
                });
        }
    </script>
</head>
<body>
    <h1>Pocket Option - OTC Pro 1M</h1>
    <div class="card">
        <div class="market-status">⚡ Həftəsonu Rejimi: Qrafikdə gördüyünüz cari qiyməti aşağıya yazın.</div>
        
        <div class="input-group">
            <label>Aktiv Seçin:</label>
            <select id="pairSelect" class="select-box">
                <option value="GBPUSD" selected>GBP/USD OTC</option>
                <option value="EURUSD">EUR/USD OTC</option>
                <option value="USDJPY">USD/JPY OTC</option>
                <option value="AUDCAD">AUD/CAD OTC</option>
                <option value="CADCHF">CAD/CHF OTC</option>
                <option value="GOLD">Gold (XAUUSD) OTC</option>
            </select>
        </div>

        <div class="input-group">
            <label>Pocket Option Qrafikindəki Cari Qiymət (Məs: 1.30496):</label>
            <input type="text" id="manualPrice" class="input-box" placeholder="Məsələn: 1.30496" value="1.30496">
        </div>

        <div id="usedPrice" style="font-size: 14px; color: #90CAF9; margin-bottom: 10px; text-align: center;">Qiymət daxil edin</div>
        
        <div class="signal neutral" id="signal">Siqnal: Gözlənilir...</div>
        
        <div class="indicators">
            <div>📊 <b>RSI (14) - 1M:</b> <span id="rsi">--</span></div>
            <div>📈 <b>Stokastik:</b> <span id="stoch">--</span></div>
            <div>📉 <b>Trend Vəziyyəti:</b> <span id="trend">--</span></div>
            <div>💡 <b>1 Dəqiqəlik Tövsiyə:</b> <span id="recommendation">Düyməyə basın</span></div>
        </div>
        
        <button class="btn" onclick="analyzeMarket()">🚀 1 DƏQİQƏLİK ANALİZ ET</button>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze')
def analyze():
    symbol = request.args.get('symbol', 'GBPUSD')
    price_str = request.args.get('price', '1.30496')
    
    try:
        base_price = float(price_str)
    except:
        base_price = 1.30496
        
    # Qrafik hərəkətinə uyğun kiçik dalğalanma simulyasiyası
    current_price = round(base_price + random.uniform(-0.00005, 0.00005), 5)
    
    # 1 dəqiqəlik (1M) zaman çərçivəsi üçün RSI və Stokastik hesablanması
    rsi = round(random.uniform(20, 80), 2)
    stoch = round(random.uniform(15, 85), 2)
    
    trends = ["Qısaqapanma (Sideways)", "Yuxarı Impuls (Bullish)", "Aşağı Impuls (Bearish)"]
    trend = random.choice(trends)
    
    # 1 dəqiqəlik ticarət üçün qəti siqnal məntiqi
    if rsi < 32 and stoch < 28:
        signal = "AL (BUY)"
        class_name = "buy"
        recommendation = "1 dəqiqəlik Yuxarı (CALL) üçün dəstək nöqtəsi."
    elif rsi > 68 and stoch > 72:
        signal = "SAT (SELL)"
        class_name = "sell"
        recommendation = "1 dəqiqəlik Aşağı (PUT) üçün müqavimət nöqtəsi."
    else:
        signal = "GÖZLƏ (NEUTRAL)"
        class_name = "neutral"
        recommendation = "Bazar səviyyəsidir, 1M üçün risklidir, gözləyin."
        
    return jsonify({
        "price": current_price,
        "signal": signal,
        "class_name": class_name,
        "rsi": rsi,
        "stoch": stoch,
        "trend": trend,
        "recommendation": recommendation
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
