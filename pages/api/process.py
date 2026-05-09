import os
import tempfile
from engine_3d import Engine3D
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename

# Vercel ماژول‌های Flask را خودکار می‌شناسد، ما فقط یک تابع handler می‌سازیم
app = Flask(__name__)

@app.route('/', methods=['POST'])
def process():
    if 'file' not in request.files:
        return {'error': 'No file'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'error': 'Empty filename'}, 400

    fd, temp_path = tempfile.mkstemp(suffix='.jpg')
    os.close(fd)
    file.save(temp_path)

    fd_out, out_path = tempfile.mkstemp(suffix='.obj')
    os.close(fd_out)

    engine = Engine3D(max_height=0.28, max_faces=4000)
    success, result = engine.process(temp_path, out_path)

    os.unlink(temp_path)
    if not success:
        os.unlink(out_path)
        return {'error': result}, 500

    return send_file(out_path, as_attachment=True, download_name='model.obj')

# Vercel به جای app.run، تابع handler را صدا می‌زند
handler = app
