import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("openai_key")

def rewrite_text(text: str, tone: str = "confident") -> str:
    prompt = (
        f"You are a communication coach. Rewrite the following message to sound more {tone}, "
        f"while keeping the original meaning and keeping it short and natural:\n\n{text}"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Sorry, something went wrong with rewriting."
