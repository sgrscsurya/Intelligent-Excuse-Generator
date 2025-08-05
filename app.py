import os
from flask import Flask, request, render_template
from transformers import pipeline, set_seed

app = Flask(__name__)

# Improved model loading with better parameters
try:
    pipe = pipeline(
        "text-generation",
        model="distilgpt2",
        device=-1,
        framework="pt"
    )
except Exception as e:
    print(f"Error loading model: {e}")
    pipe = None

def generate_excuses(situation, num_excuses):
    # Ultra-specific prompt engineering
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
    
    try:
        outputs = pipe(
            prompt,
            max_new_tokens=num_excuses*60,  # Dynamic token allocation
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.95,
            num_return_sequences=1,
            repetition_penalty=1.4,
            pad_token_id=50256,
            eos_token_id=198,  # New line token
            return_full_text=False
        )
        
        # Process the output
        generated_text = outputs[0]["generated_text"].strip()
        excuses = []
        
        # Split and clean each excuse
        for i, line in enumerate(generated_text.split('\n')[:num_excuses]):
            excuse = line.strip()
            if excuse and not any(bad in excuse.lower() for bad in ["sorry", "error", "can't"]):
                # Remove any numbering if present
                if excuse.split('.')[0].isdigit():
                    excuse = '.'.join(excuse.split('.')[1:]).strip()
                excuses.append(f"{excuse[0].upper()}{excuse[1:]}" if excuse else "")
        
        # Fallback generation if we didn't get enough
        while len(excuses) < num_excuses:
            excuses.append(f"My transportation had unexpected issues this morning.")
        
        return excuses[:num_excuses]
    
    except Exception as e:
        print(f"Generation error: {str(e)}")
        # Return generic but believable excuses
        return [f"There was an unexpected delay this morning." for _ in range(num_excuses)]

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    situation = ""
    num_excuses = 1
    
    if request.method == "POST":
        situation = request.form["situation"].strip()
        num_excuses = min(max(int(request.form.get("num_excuses", 1)), 1), 50)  # Ensure between 1-50
        
        if pipe and situation:
            result = generate_excuses(situation, num_excuses)
        elif not situation:
            result = ["Please describe your situation"]
        else:
            result = ["System error: Model not loaded"]

    return render_template("index.html", result=result, situation=situation, num_excuses=num_excuses)

if __name__ == "__main__":
    app.run(debug=True)