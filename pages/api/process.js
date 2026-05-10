# pages/api/process.py
import os
import tempfile
import sys
sys.path.append(os.getcwd())
from engine_3d import Engine3D
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
engine = Engine3D(max_height=0.28, max_faces=4000)

@app.route('/', methods=['POST'])
def process():
    if 'file' not in request.files:
        return {'error': 'No file'}, 400
    file = request.files['file']
    if file.filename == '':
        return {'error': 'Empty filename'}, 400

    fd, temp_input = tempfile.mkstemp(suffix='.jpg')
    os.close(fd)
    file.save(temp_input)

    fd_out, temp_output = tempfile.mkstemp(suffix='.obj')
    os.close(fd_out)

    try:
        success, _ = engine.process(temp_input, temp_output)
        if not success:
            return {'error': 'Processing failed'}, 500
        return send_file(temp_output, as_attachment=True, download_name='model.obj')
    except Exception as e:
        return {'error': str(e)}, 500
    finally:
        for f in [temp_input, temp_output]:
            if os.path.exists(f):
                os.unlink(f)

handler = app
