import os
# from translate import Translator
import openai
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        english = request.form["english"]
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=generate_prompt(english),
            temperature=0.6,
        )
        return redirect(url_for("index", result=response.choices[0].text))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def generate_prompt(english):
    return """Give me a 20 sentence summary of the declaration of independence.""".format(
        english.capitalize()
    )

def translate_en_to_es(text):
    translator = Translator(from_lang='en', to_lang='es')
    translation = translator.translate(text)
    return translation

"""
 Example usage 
english_text = "Hello, how are you?"
translated_text = translate_text(english_text)
print(translated_text)

"""""""""