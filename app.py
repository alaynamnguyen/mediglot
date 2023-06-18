import os
from translate import Translator
import openai
from flask import Flask, redirect, render_template, request, url_for
from gtts import gTTS

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():
    print("INDEX", request.form)
    print()
    if request.method == "POST":
        if "simplify" in request.form:
            medical_text = request.form["medical_text"]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": generate_prompt(medical_text)}]
            )

            result2 = response['choices'][0].message.content.lstrip('\n')
            translated_result = translate_and_join(result2, translate_en_to_es)
        
            # Generate speech using gTTS
            tts = gTTS(translated_result, lang='es')
            tts.save('static/output.mp3')
            next_url = "/more.html"

            return redirect(url_for("more", result=translated_result, next=next_url))
        elif "restart" in request.form:
            response = ""
            next_url = "/"
            return redirect(url_for("index", result=response, next=next_url))
    
    result = request.args.get("result")
    # translated_result = translate_en_to_es(result)
    return render_template("index.html", result=result)

@app.route("/more", methods=("GET", "POST"))
def more():
    print("MORE", request.form)
    print()
    # if request.method == "POST":
    if "morelaymans" in request.form:
        medical_text = request.form["medical_text"]
        simplified_text = generate_simplified_text(medical_text)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": simplified_text}]
        )

        result2 = response['choices'][0].message.content.lstrip('\n')
        translated_result = translate_and_join(result2, translate_en_to_es)
    
        # Generate speech using gTTS
        tts = gTTS(translated_result, lang='es')
        tts.save('static/output.mp3')
        next_url = "/more.html"

        return redirect(url_for("more", result=translated_result, next=next_url))
    elif "restart" in request.form:
        response = ""
        next_url = "/"
        return redirect(url_for("index", result=response, next=next_url))

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
    return """Rephrase this text: "{}" to be way more simpler and keep it to 10 sentences.
    """.format(
        medical_text.capitalize()
    )

def translate_en_to_es(text):
    translator = Translator(from_lang='en', to_lang='es')
    translation = translator.translate(text)
    return translation

def translate_and_join(text, translate):
    # Split text by periods
    split_text = text.split('. ')
    
    # Loop through each element and apply 'translate' function
    translated_text = [translate(sentence)[:-1] for sentence in split_text]
    
    # Join the translated text together
    joined_text = '. '.join(translated_text).strip()
    
    return joined_text