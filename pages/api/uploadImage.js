import multer from 'multer';
import { spawn } from 'child_process';
import { unlink } from 'fs/promises';
import path from 'path';
import os from 'os';

// تنظیمات multer برای ذخیره فایل در مسیر موقت
const upload = multer({ dest: os.tmpdir(), limits: { fileSize: 10 * 1024 * 1024 } });
export const config = { api: { bodyParser: false } };

function runMiddleware(req, res, fn) {
  return new Promise((resolve, reject) => {
    fn(req, res, (result) => {
      if (result instanceof Error) return reject(result);
      return resolve(result);
    });
  });
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  try {
    await runMiddleware(req, res, upload.any());
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    const file = req.files[0];
    const tempPath = file.path;
    const outputPath = path.join(process.cwd(), 'public/models/3d_object.obj');
    const pythonScript = path.join(process.cwd(), 'engine_3d.py');

    // استفاده از spawn برای اجرای پایدارتر فرآیند
    const pythonProcess = spawn('python3', [pythonScript, tempPath, outputPath], {
      timeout: 0,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    let stderr = '';
    pythonProcess.stderr.on('data', (data) => { stderr += data.toString(); });

    const exitCode = await new Promise((resolve) => {
      pythonProcess.on('close', resolve);
      setTimeout(() => pythonProcess.kill('SIGKILL'), 180000);
    });

    await unlink(tempPath).catch(() => {});

    if (exitCode !== 0) {
      console.error('Python error:', stderr);
      return res.status(500).json({ error: 'پردازش تصویر با خطا مواجه شد', details: stderr });
    }

    res.status(200).json({ success: true, modelUrl: '/models/3d_object.obj' });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: error.message });
  }
}
