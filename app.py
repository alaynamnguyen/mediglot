import os
from translate import Translator
import openai
from flask import Flask, redirect, render_template, request, url_for
from gtts import gTTS
from tempfile import NamedTemporaryFile
import requests

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        if "simplify" in request.form:
            # Check if the request contains an audio file
            if "audio" not in request.files:
                return "No audio file provided", 400
            
            # Convert speech to text
            audio_file= open("Delaware St 2.mp3", "rb")
            medical_text = openai.Audio.transcribe("whisper-1", audio_file)
            medical_text = medical_text['text'].lstrip('\n')
            print(medical_text)

            # Simplify english transcript
            simplified_text = generate_prompt(medical_text)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": simplified_text}]
            )
            translated = response['choices'][0].message.content.lstrip('\n')

            # Translate simplified english
            translated_result = translate_and_join2(translated, translate_en_to_es)
        
            # Generate speech using gTTS
            tts = gTTS(translated_result, lang='es')
            tts.save('static/output.mp3')
            next_url = "/more.html"

            return redirect(url_for("more", result=translated_result, next=next_url, loading=True))
        elif "restart" in request.form:
            response = ""
            next_url = "/"
            return redirect(url_for("index", result=response, next=next_url, loading=False))
        elif "translate" in request.form:
            # Check if the request contains an audio file
            if "audio" not in request.files:
                return "No audio file provided", 400
            
            # Convert speech to text
            audio_file= open("Delaware St 2.mp3", "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            medical_text = transcript['text'].lstrip('\n')

            # Translate simplified english
            translated_result = translate_and_join2(medical_text, translate_en_to_es)
        
            # Generate speech using gTTS
            tts = gTTS(translated_result, lang='es')
            tts.save('static/output.mp3')
            next_url = "/more.html"

            return redirect(url_for("more", result=translated_result, next=next_url, loading=True))
    
    result = request.args.get("result")
    # translated_result = translate_en_to_es(result)
    return render_template("index.html", result=result, loading=False)

@app.route("/more", methods=("GET", "POST"))
def more():
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

        return redirect(url_for("more", result=translated_result, next=next_url, loading=True))
    elif "restart" in request.form:
        response = ""
        next_url = "/"
        return redirect(url_for("index", result=response, next=next_url, loading=False))

    result = request.args.get("result")
    return render_template("more.html", result=result, loading=False)

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

def translate_and_join2(transcript, translate):
    # Split text by periods
    split_text = transcript.split('. ')

    # Loop through each element and apply 'translate' function
    translated_text = [translate(sentence)[:-1] for sentence in split_text]

    # Join the translated text together
    joined_text = '. '.join(translated_text).strip()

    return joined_text
