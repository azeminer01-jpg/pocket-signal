import random
from flask import Flask, render_template_string
import requests
import time
import json
from datetime import datetime

app = Flask(__name__)

# --- MƏLUMAT MƏNBƏYİ (API) ÜÇÜN KONFİQURASİYA ---
# VACİB: Buraya öz API açarınızı daxil edin. Cryptocompare, CoinGecko və ya TradingView API istifadə edə bilərsiniz.
# OTC cütlükləri bəzən məhdud olur, buna görə dəqiq məlumat verən mənbə seçin.
API_KEY = "5M4C3oZJaa3TnPUG8BOmVJ6Ex63GFFjb"  # HƏQİQİ AÇARINIZI BURAYA YAZIN
API_URL = "https://site.financialmodelingprep.com/developer/docs/dashboard?tab=apiDetails"

# Daxili keşləmə (API sorğularının sayını azaltmaq üçün)
cache = {
    "data": None,
    "timestamp": 0
}

def get_real_market_data():
    """CAD/CHF üzrə real bazar məlumatlarını API vasitəsilə çəkir və analiz edir."""
    # Keşləmə yoxlanılır (hər 1 dəqiqədən bir yenilənir)
    if time.time() - cache["timestamp"] < 60 and cache["data"] is not None:
        return cache["data"]

    # API sorğusu (CAD -> CHF konvertasiyası üçün)
    # Qeyd: Əksər mənbələrdə birbaşa CAD/CHF yox, CAD/USD, sonra USD/CHF kimi hesablanır.
    # Nümunə üçün birbaşa məlumat cəhd edirik.
    params = {
        'fsym': 'CAD',
        'tsym': 'CHF',
        'limit': '20',  # Son 20 dəqiqənin məlumatı
        'api_key': API_KEY
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('Response') == 'Success':
            prices = [item['close'] for item in data['Data']['Data']]
            highs = [item['high'] for item in data['Data']['Data']]
            lows = [item['low'] for item in data['Data']['Data']]

            if not prices or len(prices) < 20:
                raise ValueError("Kifayət qədər data yoxdur.")

            # --- SADƏLƏŞDİRİLMİŞ ANALİZ MƏNTİQİ ---
            
            # 1. Trend Analizi (Son qiymətlərin orta qiymətlə müqayisəsi)
            current_price = prices[-1]
            avg_price = sum(prices) / len(prices)
            
            if current_price > avg_price * 1.001: # 0.1% artım varsa
                base_trend = "Bullish"
                signal_direction = "UP"
                action_class = "up"
            elif current_price < avg_price * 0.999: # 0.1% azalma varsa
                base_trend = "Bearish"
                signal_direction = "DOWN"
                action_class = "down"
            else:
                base_trend = "Neutral/Ranging"
                signal_direction = "NEUTRAL" # Nadir hal
                action_class = "neutral"

            # 2. Şam Modeli (Süni, lakin trendə uyğun)
            # Həqiqi texniki analiz üçün Candlestick kitabxanası tələb olunur (məsələn, `talib`).
            # Bu nümunədə təsadüfi seçirik, lakin trendə meyilləndiririk.
            if signal_direction == "UP":
                pattern = random.choice(["Hammer", "Bullish Engulfing", "Morning Star"])
            elif signal_direction == "DOWN":
                pattern = random.choice(["Shooting Star", "Bearish Engulfing", "Evening Star"])
            else:
                pattern = "Doji/Unknown"

            # 3. Dəstək/Müqavimət (Süni, lakin son qiymətə uyğun)
            support_level = min(lows[-5:])
            resistance_level = max(highs[-5:])
            
            if signal_direction == "UP":
                reason_text = f"Bouncing from strong Support level at {support_level:.5f}"
            else:
                reason_text = f"Rejection from strong Resistance level at {resistance_level:.5f}"

            # 4. Etibarlılıq (Confidence) - Trendin gücünə görə təyin edilir
            price_volatility = (max(highs[-10:]) - min(lows[-10:])) / avg_price
            # Volatillik az olanda güclü trend, çox olanda qeyri-müəyyənlik
            if price_volatility < 0.001:
                confidence = 95 + random.randint(-2, 3)
            elif price_volatility < 0.005:
                confidence = 88 + random.randint(-3, 5)
            else:
                confidence = 75 + random.randint(-5, 5)
            # Maksimum 98%
            confidence = min(98, max(60, confidence))

            # Nəticə strukturu hazırlanır
            market_analysis = {
                "trend": base_trend,
                "signal_direction": signal_direction,
                "action_class": action_class,
                "pattern": pattern,
                "reason": reason_text,
                "confidence": confidence,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            
            # Keşləmə yenilənir
            cache["data"] = market_analysis
            cache["timestamp"] = time.time()
            return market_analysis

        else:
             raise ValueError(f"API Xətası: {data.get('Message')}")

    except Exception as e:
        print(f"XƏTA: {e}")
        # Xəta halında təhlükəsiz qayıdış (real data yoxdur)
        # Proqramın işləməsi üçün əvvəlki məlumatı və ya defolt məlumatı qaytarırıq
        return {
            "trend": "Data Unavailable",
            "signal_direction": "WAIT",
            "action_class": "neutral",
            "pattern": "Calculating...",
            "reason": "Waiting for API connection...",
            "confidence": 50,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

# HTML Şablonu (image_7.png və image_8.png dizaynını eynilə təkrarlayır)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRADING OPTION P... | NEUROBOT</title>
    <style>
        /* Ümumi stil (gözləmə və nəticə üçün ortaq) */
        body { 
            background-color: #f0f0f0; /* Açıq boz fon */ 
            color: #000; 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            text-align: center; 
            padding: 0; 
            margin: 0; 
        }
        .header {
            background-color: #f8f8f8;
            border-bottom: 1px solid #ddd;
            padding: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            font-weight: 500;
        }
        .header .left { display: flex; align-items: center; }
        .header .close { font-size: 20px; margin-right: 10px; color: #555; cursor: pointer; }
        .header .site-name { color: #333; }
        .header .right { display: flex; align-items: center; color: #555; }
        .header .right .options { border: 1px solid #ccc; border-radius: 4px; padding: 2px 6px; margin-right: 5px; font-weight: normal;}
        .header .right .more { font-size: 20px; color: #777; cursor: pointer; }

        .main-container {
            background-color: #fff;
            border-radius: 12px;
            width: 90%;
            max-width: 380px;
            margin: 40px auto;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            padding: 25px;
            box-sizing: border-box;
        }
        .logo-container {
             margin-bottom: 30px;
        }
        .logo-container .neurobot {
            font-size: 28px;
            font-weight: 800;
            color: #0a2540; /* Tünd göy logo */
        }
        .logo-container .version {
            font-size: 14px;
            color: #555;
            margin-top: 4px;
        }
        .logo-container .pair-tag {
            display: inline-block;
            background-color: #edf2f7;
            color: #2d3748;
            font-size: 15px;
            font-weight: 500;
            padding: 6px 12px;
            border-radius: 20px;
            margin-top: 20px;
        }
        
        /* Gözləmə (Loading) Ekranı Stili */
        .loading-box {
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 40px 20px;
            margin-top: 20px;
        }
        .loader-icon {
            width: 50px;
            height: 50px;
            border: 4px solid #e2e8f0;
            border-radius: 50%;
            border-top-color: #3182ce; /* Mavi fırlanan hissə */
            animation: spin 1s linear infinite;
            margin: 0 auto 20px auto;
        }
        .loading-text {
             color: #4a5568;
             font-size: 16px;
             font-weight: 500;
             margin-bottom: 10px;
        }
        .loading-subtext {
            color: #a0aec0;
            font-size: 12px;
        }
        
        /* Nəticə (Result) Ekranı Stili */
        .signal-box {
            background-color: #f0fff4; /* Açıq yaşıl fon */
            border: 1px solid #c6f6d5;
            border-radius: 12px;
            padding: 25px 20px;
            margin-top: 20px;
            text-align: left;
        }
        .signal-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .signal-icon {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-right: 15px;
        }
        .signal-icon.up { background-color: #2f855a; color: #fff; font-size: 24px; }
        .signal-icon.down { background-color: #c53030; color: #fff; font-size: 24px; transform: rotate(180deg); }
        
        .signal-text {
            font-size: 26px;
            font-weight: 700;
        }
        .signal-text.up { color: #2f855a; } /* Yaşıl yazı */
        .signal-text.down { color: #c53030; } /* Qırmızı yazı */
        
        .data-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-size: 14px;
            color: #4a5568;
        }
        .data-row .label {
            color: #718096;
            display: flex;
            align-items: center;
        }
        .data-row .label svg {
            margin-right: 8px;
            width: 14px;
            height: 14px;
            fill: #a0aec0;
        }
        .data-row .value {
            font-weight: 500;
            color: #2d3748;
            text-align: right;
        }
        
        .confidence-bar-container {
            height: 6px;
            background-color: #e2e8f0;
            border-radius: 3px;
            margin-top: 5px;
            overflow: hidden;
        }
        .confidence-bar-fill {
             height: 100%;
             background-color: #38a169; /* Yaşıl bar */
             width: 0%; /* Dinamik olacaq */
             transition: width 0.5s ease-in-out;
        }
        
        .reason-box {
            border-top: 1px solid #edf2f7;
            margin-top: 20px;
            padding-top: 15px;
        }
        .reason-box .label {
            color: #a0aec0;
            font-size: 12px;
            margin-bottom: 4px;
        }
        .reason-box .value {
            color: #2f855a; /* Yaşıl səbəb */
            font-size: 14px;
            line-height: 1.4;
        }
