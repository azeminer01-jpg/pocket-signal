import base64
import json
import os
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

app = FastAPI(title="Pocket Option Live Chart Scanner")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

SYSTEM_PROMPT = """
You are a chart-reading assistant for Pocket Option screenshots.
This is ANALYSIS ONLY. Never claim certainty, guaranteed profit, or 100% accuracy.
The screenshot is the only market data source. Do not invent prices, candles, indicators,
support/resistance, or timeframes that are not visible.

Return ONLY valid JSON with exactly these keys:
signal, confidence, trend, timeframe_visible, support, resistance,
patterns, indicators, reasoning, risk_flags, data_quality

Rules:
- signal must be exactly CALL, PUT, or WAIT.
- confidence is 0-100 analytical confidence, NOT probability of profit.
- For 30s/1m decisions, be conservative. If the chart is unclear, timeframe is not visible,
  candles are too small, or evidence conflicts, use WAIT.
- Prefer WAIT over a weak signal.
- Examine recent candle direction, candle bodies/wicks, momentum, visible support/resistance,
  EMA/RSI/MACD or other indicators only if actually visible.
- Do not invent an indicator value.
- If an indicator is not visible, say "not visible".
- Explain the main evidence briefly.
"""

def make_prompt(asset: str, duration: str) -> str:
    return f"""
Asset selected by the user: {asset}
Requested trade duration: {duration}

Analyze the latest visible chart. Focus on the most recent candles and the immediate
context. If the selected asset/timeframe cannot be verified from the screenshot, lower
data_quality and use WAIT.

Important: this is not a guarantee of what the next candle will do. Return JSON only.
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return Path("index.html").read_text(encoding="utf-8")

@app.get("/health")
def health():
    return {"ok": True, "model": MODEL}

@app.post("/analyze-frame")
async def analyze_frame(
    image: UploadFile = File(...),
    asset: str = Form("GBP/USD OTC"),
    duration: str = Form("30 seconds"),
):
    if not os.getenv("OPENAI_API_KEY"):
        return JSONResponse({"error": "OPENAI_API_KEY Render Environment Variable yoxdur."}, status_code=500)

    data = await image.read()
    if not data:
        return JSONResponse({"error": "Boş görüntü göndərildi."}, status_code=400)

    if len(data) > 5_000_000:
        return JSONResponse({"error": "Şəkil çox böyükdür. Brauzer sıxışdırması işləməyib."}, status_code=413)

    mime = image.content_type or "image/jpeg"
    if mime not in {"image/jpeg", "image/png", "image/webp"}:
        mime = "image/jpeg"

    b64 = base64.b64encode(data).decode("ascii")

    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": make_prompt(asset, duration)},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{b64}",
                                "detail": "high",
                            },
                        },
                    ],
                },
            ],
        )
        raw = response.choices[0].message.content
        result = json.loads(raw)

        allowed = {"CALL", "PUT", "WAIT"}
        if result.get("signal") not in allowed:
            result["signal"] = "WAIT"

        try:
            result["confidence"] = max(0, min(100, int(result.get("confidence", 0))))
        except Exception:
            result["confidence"] = 0

        result["asset"] = asset
        result["duration"] = duration
        return result

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
