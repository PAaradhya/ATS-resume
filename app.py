from flask import Flask, render_template, request, jsonify
import os
import pdf2image
import spacy
import pytesseract
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Set up pytesseract path if necessary
# Set up pytesseract path if necessary
tesseract_path = os.getenv('TESSERACT_CMD_PATH', r'C:\Program Files\Tesseract-OCR\tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = tesseract_path
# Initialize Flask app
app = Flask(__name__)

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF using OCR
def extract_text_from_pdf(file):
    images = pdf2image.convert_from_bytes(file.read())
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text.strip()

# Function to analyze resume against job description
def analyze_resume_locally(job_description, resume_text):
    job_doc = nlp(job_description)
    resume_doc = nlp(resume_text)
    job_keywords = set([token.lemma_ for token in job_doc if not token.is_stop and not token.is_punct])
    resume_keywords = set([token.lemma_ for token in resume_doc if not token.is_stop and not token.is_punct])
    matched_keywords = job_keywords.intersection(resume_keywords)
    missing_keywords = job_keywords.difference(resume_keywords)
    match_percentage = len(matched_keywords) / len(job_keywords) * 100 if len(job_keywords) > 0 else 0
    return {
        "matched_keywords": list(matched_keywords),
        "missing_keywords": list(missing_keywords),
        "match_percentage": match_percentage
    }

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload and analysis
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    job_description = request.form.get('job_description', '')
    resume_text = extract_text_from_pdf(file)
    if not resume_text:
        return jsonify({'error': 'Failed to extract text from PDF'}), 500
    result = analyze_resume_locally(job_description, resume_text)
    return jsonify(result)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
