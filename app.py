import os
import requests
from flask import Flask, request, render_template
from dotenv import load_dotenv
import re
import json

# Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

app = Flask(__name__)

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
HEADERS = {
    "Content-Type": "application/json",
    "X-goog-api-key": api_key
}

def generate_excuses(situation, num_excuses):
    prompt = (
        f"I need {num_excuses} distinct and realistic excuses for being {situation}. "
        "Each excuse must be:\n"
        "- A concise sentence or two (maximum 30 words).\n"
        "- Directly relevant to the situation.\n"
        "- Believable in a professional or academic context.\n"
        "- Unique from the other excuses provided.\n"
        "AVOID:\n"
        "- Vague or generic responses (e.g., 'Something came up').\n"
        "- Unrealistic or humorous excuses (e.g., 'My cat did it').\n"
        "- Excuses that imply irresponsibility or lack of planning.\n"
        f"EXAMPLES for being {situation.upper()}:\n"
        "1. I encountered an unexpected delay on my commute due to a traffic incident.\n"
        "2. I had a prior commitment that ran slightly over schedule.\n"
        "3. I needed to address a pressing family matter this morning.\n"
        f"NOW GENERATE {num_excuses} DISTINCT EXCUSES FOR {situation.upper()}:\n"
    )

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_ENDPOINT, headers=HEADERS, data=json.dumps(data))
        response.raise_for_status()
        gemini_output = response.json()

        # Extract the generated text
        text = gemini_output["candidates"][0]["content"]["parts"][0]["text"]
        lines = re.findall(r'(?:^\d+\.|^-)\s*(.+)', text, re.MULTILINE)
        if not lines:
            # fallback: split by newline
            lines = [line.strip() for line in text.split('\n') if line.strip()]

        excuses = []
        for line in lines:
            if len(excuses) >= num_excuses:
                break
            line = line.strip().rstrip('.')
            if line:
                line = f"{line[0].upper()}{line[1:]}"
                excuses.append(f"{line}.")

        while len(excuses) < num_excuses:
            excuses.append("I was caught up with an urgent and unavoidable situation.")

        return excuses[:num_excuses]

    except Exception as e:
        print(f"Gemini API error: {e}")
        return [f"I encountered an urgent situation this morning." for _ in range(num_excuses)]

# Route: Welcome Page
@app.route("/")
def welcome():
    return render_template("welcome.html")

# Route: Excuse Generator Main Page
@app.route("/generate", methods=["GET", "POST"])
def generate():
    result = None
    situation = ""
    num_excuses = 1

    if request.method == "POST":
        situation = request.form["situation"].strip()
        num_excuses = min(max(int(request.form.get("num_excuses", 1)), 1), 50)

        if api_key and situation:
            result = generate_excuses(situation, num_excuses)
        elif not situation:
            result = ["Please describe your situation"]
        else:
            result = ["System error: API key not set"]

    return render_template("index.html", result=result, situation=situation, num_excuses=num_excuses)

if __name__ == "__main__":
    app.run(debug=True)
