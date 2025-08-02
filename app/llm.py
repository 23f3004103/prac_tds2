import requests
import re
from .config import OPENROUTER_API_KEY

def extract_code(response_text: str) -> str:
    import re
    # Match code inside `````` or ``````
    match = re.search(r"``````", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # fallback: remove any leading/trailing backticks lines
    lines = response_text.strip().splitlines()
    lines = [line for line in lines if not line.strip().startswith("```")]
    return "\n".join(lines).strip()


async def ask_llm(prompt: str, 
                #   model="openai/gpt-3.5-turbo", 
                #   model="openai/gpt-4o-mini", 
                  model="deepseek/deepseek-r1-0528:free", 
                #   model="google/gemini-2.0-flash-exp:free", 
                  temperature=0.2):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload, headers=headers, timeout=60
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise Exception(f"LLM request error: {e}")
    try:
        return extract_code(data['choices'][0]['message']['content'])
    except (KeyError, IndexError):
        raise Exception("Unexpected format from LLM response.")

async def debug_llm(prompt: str, 
                    model="google/gemini-2.0-flash-exp:free",
                    temperature=0.2):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload, headers=headers, timeout=60
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise Exception(f"LLM request error: {e}")
    return data

