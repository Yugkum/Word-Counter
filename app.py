from flask import Flask, request, jsonify, render_template
import PyPDF2
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def count_words_in_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        words = text.split()
        return len(words)

def count_words_in_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8', errors='ignore') as file:
        text = file.read()
        words = text.split()
        return len(words)

def count_words_in_docx(docx_path):
    try:
        import docx
    except ImportError:
        raise ImportError('python-docx is required for DOCX support. Install with: pip install python-docx')
    doc = docx.Document(docx_path)
    text = '\n'.join([para.text for para in doc.paragraphs])
    words = text.split()
    return len(words)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files and 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files.get('pdf') or request.files.get('file')
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    ext = os.path.splitext(filename)[1].lower()
    try:
        if ext == '.pdf':
            word_count = count_words_in_pdf(filepath)
        elif ext == '.txt':
            word_count = count_words_in_txt(filepath)
        elif ext == '.docx':
            word_count = count_words_in_docx(filepath)
        else:
            os.remove(filepath)
            return jsonify({'error': 'Unsupported file type. Please upload PDF, TXT, or DOCX.'}), 400
    except Exception as e:
        os.remove(filepath)
        return jsonify({'error': str(e)}), 500
    os.remove(filepath)
    return jsonify({'word_count': word_count})

if __name__ == '__main__':
    app.run(debug=True)
