from flask import Flask, request, render_template, redirect, url_for
import PyPDF2
import requests
import google.generativeai as genai

app = Flask(__name__)

# Hugging Face API key and URL (Free API)
HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HUGGING_FACE_API_KEY = "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"

headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}

# Google Gemini API Key
GENAI_API_KEY = "AIzaSyCUCfvQG4rO_XigA0gqMvU_DauvtAw4DO0"

# Helper function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

# Helper function to summarize text using Hugging Face API
def summarize_text(text):
    payload = {"inputs": text}
    response = requests.post(HUGGING_FACE_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()[0]["summary_text"]
    else:
        return "Error: Unable to summarize."

# Route for the homepage with two buttons
@app.route('/')
def index():
    return render_template('index.html')

# Route for PDF summarization feature
@app.route('/summarize', methods=['GET', 'POST'])
def summarize_pdf():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('index'))
        
        file = request.files['file']
        
        if file.filename == '':
            return redirect(url_for('index'))
        
        if file and file.filename.endswith('.pdf'):
            extracted_text = extract_text_from_pdf(file)
            
            if extracted_text:
                summary = summarize_text(extracted_text)
                return render_template('summarize.html', summary=summary)
            else:
                return "Error: Could not extract text from PDF."
        
        return "Error: Invalid file type. Only PDFs are allowed."
    
    return render_template('summarize.html')

# Route for Google Gemini chatbot
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        genai.configure(api_key=GENAI_API_KEY)

        generation_config = {
            "temperature": 0.5,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
        )

        chat_session = model.start_chat(
            history=[
                {"role": "user", "parts": ["act as a personal assistant\n"]},
                {"role": "model", "parts": ["Okay, I'm ready to assist you!  Tell me, what can I do for you today? 😊\n"]},
                {"role": "user", "parts": ["I own a semiconductor company. You are my assistant John Bihari."]},
                {"role": "model", "parts": ["Understood, Mr. Iyer. I'm John Bihari, your personal assistant. My priority is to streamline your day.\n"]},
            ]
        )

        prompt = request.form.get("message")
        response = chat_session.send_message(prompt)

        return render_template("personal.html", response=response.text)

    return render_template("personal.html", response=None)

if __name__ == "__main__":
    app.run(port=80, host="0.0.0.0")
    