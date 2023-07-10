# Mediglot.ai

MediGlot.ai leverages GPT-3.5 to simplify and translate doctor instructions for patients whose first language may not be English to better understand and make informed decisions about their health.

## How we built it
Our project is built with the following languages: Python, Flask, HTML, CSS, and Javascript. We also made use of partner resources including Pinecone, Featureform, and OpenAI (Whisper, GPT-3.5). Lastly, we used Google text-to-speech software.

## Setup

1. If you don’t have Python installed, [install it from here](https://www.python.org/downloads/).

2. Clone this repository.

3. Navigate into the project directory:

   ```bash
   $ cd mediglot
   ```

4. Create a new virtual environment:

   ```bash
   $ python -m venv venv
   $ . venv/bin/activate
   ```

5. Install the requirements:

   ```bash
   $ pip install -r requirements.txt
   ```

6. Make a copy of the example environment variables file:

   ```bash
   $ cp .env.example .env
   ```

7. Add your [API key](https://beta.openai.com/account/api-keys) to the newly created `.env` file.

8. Run the app:

   ```bash
   $ flask run
   ```

You should now be able to access the app at [http://localhost:5000](http://localhost:5000)!
