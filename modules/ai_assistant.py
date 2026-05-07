from google import genai

API_KEY = "AIzaSyC28dwbpY-JFYy1iHrkwT-GBoW-MFjxvWg"

client = genai.Client(api_key=API_KEY)


def ask_ai(message):

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=message
        )

        return response.text

    except Exception as e:
        return f"AI Error: {str(e)}"