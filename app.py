import os
from translate import Translator
import openai
from flask import Flask, redirect, render_template, request, url_for
from gtts import gTTS

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        if "simplify" in request.form:
            medical_text = request.form["medical_text"]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": generate_prompt(medical_text)}]
            )

            result2 = response.choices[0].message.content
        
            # Generate speech using gTTS
            tts = gTTS(result2, lang='en')
            tts.save('static/output.mp3')

            return redirect(url_for("more", result=response['choices'][0].message.content.lstrip('\n')))
        elif "restart" in request.form:
            response = ""
            return redirect(url_for("index", result=response))
    
    result = request.args.get("result")
    # translated_result = translate_en_to_es(result)
    return render_template("index.html", result=result)

@app.route("/more", methods=("GET", "POST"))
def more():
    if request.method == "POST":
        if "morelaymans" in request.form:
            medical_text = request.form["medical_text"]
            simplified_text = generate_simplified_text(medical_text)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": simplified_text}]
            )

            result2 = response.choices[0].message.content
        
            # Generate speech using gTTS
            tts = gTTS(result2, lang='en')
            tts.save('static/output.mp3')

            return redirect(url_for("more", result=response['choices'][0].message.content.lstrip('\n')))
        elif "restart" in request.form:
            response = ""
            return redirect(url_for("index", result=response))

    result = request.args.get("result")
    return render_template("more.html", result=result)

def generate_prompt(medical_text):
    return """Rephrase this text: "{}" into layman's terms 
    so that a patient who is old and has very limited medical 
    terminology knowledge will understand and keep it to 10 sentences.
    Also include any potential risks mentioned to the patient.""".format(
        medical_text.capitalize()
    )

def generate_simplified_text(medical_text):
    return """Rephrase this text: "{}" to be a little bit simpler and keep it to 10 sentences.
    """.format(
        medical_text.capitalize()
    )

def translate_en_to_es(text):
    translator = Translator(from_lang='en', to_lang='es')
    translation = translator.translate(text)
    return translation