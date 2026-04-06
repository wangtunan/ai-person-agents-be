import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv();

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

def translate_agent_stream(text: str):
    system_prompt = f"You ara a good translator, use Teacher Style to teach the student."
    user_prompt = f"""
        Detect  the language and translate:
        - If input is Chinese -> translate to English
        - If input is English -> translate to Chinese

        Only Return result with Simple usage Example, No other text.

        Example:
        Input: 天才
        Output： 
          翻译结果：Genius
          例句: Einstein was a genius in physics

        Original Text: {text}

        Always Response in Markdown format.
    """

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
    )

    for chunk in response:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta.content:
            yield f"data: {json.dumps({'type': 'delta', 'text': delta.content}, ensure_ascii=False)}\n\n"
    
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


if __name__ == "__main__":
    text = input("Enter text to translate: ")
    for chunk in translate_agent_stream(text):
        if not chunk.startswith("data:"):
            continue
        payload = json.loads(chunk.removeprefix("data:").strip())
        if payload.get("type") == "delta":
            print(payload.get("text", ""), end="", flush=True)
        elif payload.get("type") == "done":
            print()
    