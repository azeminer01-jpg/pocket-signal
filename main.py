import os, base64, json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse
from openai import OpenAI

app = FastAPI(title="Chart Signal Analyzer")
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

ALLOWED_ASSETS = {
    "GBP/USD OTC", "EUR/USD OTC", "USD/JPY OTC",
    "AUD/USD OTC", "USD/CAD OTC", "GBP/JPY OTC",
    "EUR/USD", "GBP/USD", "USD/JPY", "XAU/USD"
}
ALLOWED_DURATIONS = {"30 seconds", "1 minute"}

SYSTEM_PROMPT = """You are a cautious technical-analysis assistant.
Analyze ONLY the chart image supplied by the user. Do not invent candles, prices,
indicators, news, or market data that are not visible. The requested duration is
very short (30 seconds or 1 minute), so explicitly account for uncertainty.

Return JSON with:
signal: one of CALL, PUT, WAIT
duration: requested duration
asset: requested asset
confidence: integer 0-100, representing analytical confidence, NOT probability of profit
trend: short text
support: short text
resistance: short text
patterns: array of observed patterns
indicators: array of observations; if an indicator is not visible, say unavailable
reasoning: concise explanation
risk_flags: array
data_quality: HIGH, MEDIUM, or LOW

Rules:
- Never claim certainty or guaranteed profit.
- Never fabricate exact prices or indicator values.
- If the screenshot is unclear, choose WAIT and data_quality LOW.
- For OTC, state that screenshot-based analysis cannot independently verify the
  platform's OTC price feed.
- CALL/PUT are analytical directions only, not guaranteed outcomes.
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(open("index.html", encoding="utf-8").read())

@app.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    asset: str = Form(...),
    duration: str = Form(...)
):
    if asset not in ALLOWED_ASSETS:
        raise HTTPException(400, "Unsupported asset")
    if duration not in ALLOWED_DURATIONS:
        raise HTTPException(400, "Unsupported duration")
    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(500, "OPENAI_API_KEY is not configured")

    data = await image.read()
    if len(data) > 12 * 1024 * 1024:
        raise HTTPException(400, "Image is too large")

    mime = image.content_type or "image/png"
    if mime not in {"image/png", "image/jpeg", "image/webp"}:
        raise HTTPException(400, "Use PNG, JPG or WEBP")

    b64 = base64.b64encode(data).decode()
    prompt = f"""Asset: {asset}
Requested operation duration: {duration}

Analyze the supplied screenshot. Focus on the most recent visible candles and
the timeframe shown on the chart. Combine price structure, trend, support/resistance,
and any visible indicators. Do not assume a timeframe that is not visible.
Because this is a very short-duration request, prefer WAIT when the evidence is mixed."""

    try:
        response = client.responses.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-5.6-luna"),
            input=[{
                "role": "system",
                "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]
            }, {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image",
                     "image_url": f"data:{mime};base64,{b64}",
                     "detail": "high"}
                ]
            }],
            text={"format": {"type": "json_object"}}
        )
        result = json.loads(response.output_text)
        return result
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")
