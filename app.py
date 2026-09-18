import random
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pocket Option Siqnal Paneli</title>
    <style>
        body { background-color: #121212; color: #fff; font-family: Arial, sans-serif; text-align: center; padding: 20px; }
        .card { background: #1e1e1e; padding: 20px; border-radius: 10px; max-width: 400px; margin: auto; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        select, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 5px; border: none; font-size: 16px; }
        select { background: #333; color: #fff; }
        button { background: #0088cc; color: #fff; font-weight: bold; cursor: pointer; }
        button:hover { background: #006699; }
        .result { margin-top: 20px; padding: 15px; background: #262626; border-radius: 5px; text-align: left; display: none; }
        .up { color: #2ecc71; font-weight: bold; }
        .down { color: #e74c3c; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Pocket Option Siqnal</h2>
        <select id="asset">
            <option value="EUR/USD">EUR/USD (OTC)</option>
            <option value="GBP/USD">GBP/USD (OTC)</option>
            <option value="AUD/CAD">AUD/CAD (OTC)</option>
            <option value="USD/JPY">USD/JPY (OTC)</option>
        </select>
        <select id="duration">
            <option value="15s">15 Saniyə</option>
            <option value="1m">1 Dəqiqə</option>
        </select>
        <button onclick="getSignal()">Siqnal Al</button>
        
        <div id="resBox" class="result">
            <p><b>Aktiv:</b> <span id="resAsset"></span></p>
            <p><b>İstiqamət:</b> <span id="resAction"></span></p>
            <p><b>Müddət:</b> <span id="resDuration"></span></p>
            <p><b>Etibarlılıq:</b> %<span id="resConf"></span></p>
        </div>
    </div>

    <script>
        function getSignal() {
            const asset = document.getElementById('asset').value;
            const duration = document.getElementById('duration').value;
            const actions = ['YUXARI (UP)', 'AŞAĞI (DOWN)'];
            const randomAction = actions[Math.floor(Math.random() * actions.length)];
            const conf = Math.floor(Math.random() * (98 - 85 + 1)) + 85;

            document.getElementById('resAsset').innerText = asset + " (OTC)";
            const actionEl = document.getElementById('resAction');
            actionEl.innerText = randomAction;
            actionEl.className = randomAction.includes('UP') ? 'up' : 'down';
            
            document.getElementById('resDuration').innerText = duration;
            document.getElementById('resConf').innerText = conf;
            document.getElementById('resBox').style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
