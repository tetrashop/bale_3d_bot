import multer from 'multer';
import { unlink } from 'fs/promises';
import path from 'path';
import os from 'os';
import { createReadStream } from 'fs';
import FormData from 'form-data';
import fetch from 'node-fetch';

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

    const form = new FormData();
    form.append('file', createReadStream(tempPath), 'image.jpg');

    // آدرس Flask API - از IP شبکه استفاده شده تا مرورگر گوشی هم بتواند وصل شود
    const response = await fetch('http://192.168.1.101:5000/process', {
      method: 'POST',
      body: form,
      headers: form.getHeaders()
    });

    await unlink(tempPath).catch(() => {});

    if (!response.ok) {
      const errorText = await response.text();
      return res.status(response.status).json({ error: errorText });
    }

    const blob = await response.buffer();
    res.setHeader('Content-Type', 'application/octet-stream');
    res.setHeader('Content-Disposition', 'attachment; filename=model.obj');
    res.send(blob);
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: error.message });
  }
}
