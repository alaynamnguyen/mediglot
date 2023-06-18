import os
from translate import Translator
import openai
from flask import Flask, redirect, render_template, request, url_for, request
from gtts import gTTS
from translatepy import Translator
from translatepy.exceptions import TranslatepyException, UnknownLanguage
from werkzeug.utils import secure_filename
from pydub import AudioSegment
translator = Translator()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'recording'
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        if "simplify" in request.form:
            # Check if the request contains an audio file
            if "audio" not in request.files:
                return "No audio file provided", 400
            
            # recording = "Delaware St 2.mp3"
            # audio_file = open(recording, "rb")
            text_file = request.form['medical_text']

            medical_text = text_file

            # if audio_file:
            #     transcript = openai.Audio.transcribe("whisper-1", audio_file)
            #     medical_text = transcript['text'].lstrip('\n')
            # else:
            #     medical_text = text_file

            # Simplify english transcript
            simplified_text = generate_prompt(medical_text)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": simplified_text}]
            )
            result = response['choices'][0].message.content.lstrip('\n')

            # Translate simplified english
            translated_result = translate_and_join(result)
        
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
            # audio_file= open("Delaware St 2.mp3", "rb")
            # transcript = openai.Audio.transcribe("whisper-1", audio_file)
            # medical_text = transcript['text'].lstrip('\n')

            # Translate simplified english
            translated_result = translate_and_join(medical_text)
        
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

        result = response['choices'][0].message.content.lstrip('\n')
        translated_result = translate_and_join(result)
    
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

def translate(text):
    try:
        result = translator.translate(text, destination_language = 'es', source_language = 'auto')
        return result
    except UnknownLanguage as err:
        print('Couldn\'t recognize the language. The language found is: ', err.guessed_language)
        print('Please try recording again or try typing in text.')
        return
    except TranslatepyException:
        print('An error occured while translating. Please try again.')
        return
    except Exception:
        print('An unknown error occured')
        return    

def translate_and_join(text):
    # Split text by periods
    split_text = text.split('. ')
    
    # Loop through each element and apply 'translate' function
    translated_text = [translate(sentence).result[:-1] for sentence in split_text]
    
    # Join the translated text together
    joined_text = '. '.join(translated_text).strip()
    
    return joined_text

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return 'No file part', 400
    file = request.files['audio']
    if file.filename == '':
        return 'No selected file', 400
    if file:
        filename = secure_filename(file.filename)
        webm_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(webm_path)
        
        # convert webm file to mp3
        audio = AudioSegment.from_file(webm_path, format="webm")
        mp3_path = os.path.splitext(webm_path)[0] + '.mp3'
        audio.export(mp3_path, format="mp3")

        return 'File uploaded and converted to MP3 successfully', 200
