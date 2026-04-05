def get_weather(city: str):
    return {
        "city": city,
        "forecast": [
            {"day": "Day 1", "temp": "20°C", "advice": "Light jacket"},
            {"day": "Day 2", "temp": "22°C", "advice": "Comfortable"},
            {"day": "Day 3", "temp": "18°C", "advice": "Bring umbrella"},
        ]
    }