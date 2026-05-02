import os
import uuid
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from engine_3d import Engine3D

app = Flask(__name__)
engine = Engine3D(max_height=0.28, max_faces=12000)

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/process', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400
    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    # ذخیره موقت
    filename = secure_filename(file.filename)
    temp_input = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
    file.save(temp_input)

    output_filename = f"{uuid.uuid4()}.obj"
    temp_output = os.path.join(UPLOAD_FOLDER, output_filename)

    try:
        success, result = engine.process(temp_input, temp_output)
        if not success:
            return jsonify({'error': 'Processing failed'}), 500
        return send_file(temp_output, as_attachment=True, download_name='model.obj')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # پاکسازی فایل‌های موقت
        if os.path.exists(temp_input):
            os.remove(temp_input)
        if os.path.exists(temp_output):
            os.remove(temp_output)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
