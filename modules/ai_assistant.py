from groq import Groq

client = Groq(
    api_key="YOUR_GROQ_API_KEY"
)


def ask_ai(message):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful AI Driver Assistant for a "
                        "Commercial Driver Management System. "
                        "Give short, useful, safety-focused answers."
                    )
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.7,
            max_tokens=150
        )

        return completion.choices[0].message.content

    except Exception:
        return "AI service temporarily unavailable."