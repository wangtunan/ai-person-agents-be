import json
import os
import requests

from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv();

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

def get_weather(city: str):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": os.getenv("OPEN_WEATHER_API_KEY"),
        "units": "metric",
        "lang": "zh_cn"
    }
    print("city", city)

    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()

    # 取未来三天
    forecast = []
    used_dates = set()

    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        date_str = dt.strftime("%Y-%m-%d")

        if date_str not in used_dates:
            used_dates.add(date_str)

            forecast.append({
                "date": date_str,
                "temp": item["main"]["temp"],
                "weather": item["weather"][0]["description"],
            })
        
        if len(forecast) >= 3:
            break
    
    return forecast


def generate_advice(city: str, forecast: list):
    system_prompt = "You are a helpful weather assistant."
    user_prompt = f"""You are a weather assistant.
        City: {city}
        Forecast:
        {forecast}

        Please generate:
        1. A short summary
        2. Practical advice (clothing, travel, etc.)

        Only Plain Text, No Markdown.
    """

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[
            { "role": "system", "content": system_prompt },
            { "role": "user", "content": user_prompt }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


def generate_advice_stream(city: str, forecast: list):
    system_prompt = (
        "You are a helpful weather assistant. "
        "Respond in Markdown: use ## for sections, bullet lists, and **bold** for emphasis."
        "Respond In Chinese."
    )
    user_prompt = f"""City: {city}
        Forecast:
        {forecast}

        Please provide:
        ## Summary
        - Date, Temperature, Weather
        ## Practical advice
        - Clothing, travel, etc.

        
    """

    stream = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content


def get_weather_agent_stream(city: str):
    """SSE: first event carries forecast JSON, then delta events (Markdown text), then done."""
    forecast = get_weather(city)
    for piece in generate_advice_stream(city, forecast):
        yield f"data: {json.dumps({'type': 'delta', 'text': piece}, ensure_ascii=False)}\n\n"
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


def get_weather_agent(city: str):
    forecast = get_weather(city)
    advice = generate_advice(city,forecast)
    
    return {
        "city": city,
        "forecast": forecast,
        "advice": advice
    }


if __name__ == "__main__":
    city = "Shanghai"
    for raw in get_weather_agent_stream(city):
        line = raw.strip()
        if not line.startswith("data:"):
            continue
        payload = json.loads(line.removeprefix("data:").strip())
        if payload.get("type") == "forecast":
            print("Forecast:", payload.get("forecast"))
            print("--- advice (markdown stream) ---")
        elif payload.get("type") == "delta":
            print(payload.get("text", ""), end="", flush=True)
        elif payload.get("type") == "done":
            print()