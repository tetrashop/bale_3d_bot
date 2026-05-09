import os
import uuid
import tempfile
from flask import Flask, request, jsonify, send_file
from engine_3d import Engine3D

app = Flask(__name__)
engine = Engine3D(max_height=0.28, max_faces=2000)  # همان تنظیمات پایدار

@app.route('/process', methods=['POST'])
def process():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # ذخیره موقت تصویر دریافتی
    fd, temp_path = tempfile.mkstemp(suffix='.jpg')
    os.close(fd)
    file.save(temp_path)

    # خروجی موقت OBJ
    out_fd, out_path = tempfile.mkstemp(suffix='.obj')
    os.close(out_fd)

    try:
        success, result = engine.process(temp_path, out_path)
        if not success:
            return jsonify({'error': 'Processing failed'}), 500
        return send_file(out_path, as_attachment=True, download_name='model.obj')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # پاکسازی فایل‌های موقت
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if os.path.exists(out_path):
            os.unlink(out_path)

if __name__ == '__main__':
    # اجرا روی پورت ۵۰۰۰ در تمام شبکه (برای دسترسی از Next.js)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
