import os
from fastapi import FastAPI, Request
import google.generativeai as genai

app = FastAPI()

# Configure AI Studio via Environment Variable (Security)
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/")
def home():
    return {"status": "Webhook is Online"}

@app.post("/webhook")
async def tradingview_webhook(request: Request):
    data = await request.json()
    
    # Process with Gemini
    prompt = f"Trading Signal: {data}. Give a short risk rating 1-10."
    response = model.generate_content(prompt)
    
    print(f"AI Result: {response.text}")
    return {"status": "received", "ai_analysis": response.text}
