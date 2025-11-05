import os
from flask import Flask, request, jsonify, render_template
import PyPDF2
from summarizer import get_summary, get_keywords

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Create folder if it doesn't exist

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize_text():
    """API endpoint for summarizing raw text."""
    try:
        data = request.json
        if 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        summary = get_summary(text)
        keywords = get_keywords(text)
        
        return jsonify({
            'summary': summary,
            'keywords': keywords
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """API endpoint for summarizing an uploaded file."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        text = ""
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the file based on its type
        if filename.endswith('.pdf'):
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        
        elif filename.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        
        else:
            os.remove(filepath) # Clean up
            return jsonify({'error': 'Unsupported file type. Please upload .txt or .pdf'}), 400

        os.remove(filepath) # Clean up the uploaded file

        if not text.strip():
             return jsonify({'error': 'Could not extract text from the file.'}), 400

        summary = get_summary(text)
        keywords = get_keywords(text)
        
        return jsonify({
            'summary': summary,
            'keywords': keywords
        })

    except Exception as e:
        # Clean up in case of error
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)