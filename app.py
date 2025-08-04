import os
from flask import Flask, request, render_template
from transformers import pipeline, set_seed

# Set random seed for consistency
set_seed(42)

app = Flask(__name__)

# Load the text generation pipeline outside the function for efficiency
try:
    pipe = pipeline("text-generation", model="distilgpt2")
except Exception as e:
    print(f"Error loading model: {e}")
    pipe = None  # Set pipe to None if loading fails

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        situation = request.form["situation"]
        prompt = f"I need a believable excuse for: {situation}.  The excuse should be short, polite, and realistic."

        if pipe:  # Check if the pipeline is loaded successfully
            try:
                outputs = pipe(prompt, max_length=75, do_sample=True, temperature=0.7, top_p=0.9, num_return_sequences=1)
                result = outputs[0]["generated_text"]

                # Clean up the generated text (remove the prompt from the output)
                result = result.replace(prompt, "").strip()

            except Exception as e:
                result = f"An error occurred during excuse generation: {str(e)}"
        else:
            result = "Model loading failed. Please check the console for errors."

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)