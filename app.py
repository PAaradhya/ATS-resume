from flask import Flask, render_template, request, jsonify
import os
import pdf2image
import pytesseract
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

//
#base_dir = os.path.dirname(__file__)

# Construct the relative path to the Tesseract executable
#tesseract_path = os.path.join(base_dir, 'Tesseract1-OCR', 'tesseract.exe')
//
#Set up pytesseract path if necessary
tesseract_path = os.getenv('TESSERACT_CMD_PATH', r'Tesseract1-OCR\tesseract.exe')

pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Initialize Flask app
app = Flask(__name__)

# Function to extract text from PDF using OCR
def extract_text_from_pdf(file):
    images = pdf2image.convert_from_bytes(file.read())
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text.strip()

# Function to preprocess text by removing special characters and converting to lowercase
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-z\s]', '', text)  # Remove special characters, numbers, and punctuations
    return text

# Function to analyze resume against job description
def analyze_resume_locally(job_description, resume_text):
    job_description = preprocess_text(job_description)
    resume_text = preprocess_text(resume_text)

    job_keywords = set(job_description.split())
    resume_keywords = set(resume_text.split())

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
