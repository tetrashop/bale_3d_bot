import formidable from 'formidable';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // ایجاد پوشه موقت درون پروژه (Termux به آن دسترسی دارد)
  const tmpDir = path.join(process.cwd(), 'tmp_uploads');
  if (!fs.existsSync(tmpDir)) {
    fs.mkdirSync(tmpDir, { recursive: true });
  }

  const form = formidable({
    multiples: false,
    uploadDir: tmpDir,
    keepExtensions: true,
    maxFileSize: 10 * 1024 * 1024, // 10MB
  });

  try {
    const [fields, files] = await form.parse(req);
    const imageFile = files.imageFile?.[0] || files.file?.[0];
    if (!imageFile) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const tempPath = imageFile.filepath;
    const outputModelPath = path.join(process.cwd(), 'public/models/3d_object.obj');
    const modelDir = path.dirname(outputModelPath);
    if (!fs.existsSync(modelDir)) fs.mkdirSync(modelDir, { recursive: true });

    const pythonScript = path.join(process.cwd(), 'engine_3d.py');
    const command = `python3 "${pythonScript}" "${tempPath}" "${outputModelPath}"`;
    
    const { stdout, stderr } = await execPromise(command, { timeout: 60000 });
    if (stderr) console.error('Python stderr:', stderr);
    console.log('Python stdout:', stdout);
    
    if (fs.existsSync(outputModelPath) && fs.statSync(outputModelPath).size > 0) {
      // حذف فایل موقت
      fs.unlinkSync(tempPath);
      return res.status(200).json({ success: true, modelUrl: '/models/3d_object.obj' });
    } else {
      throw new Error('مدل ساخته نشد');
    }
  } catch (error) {
    console.error('Error in uploadImage:', error);
    return res.status(500).json({ error: error.message || 'Internal server error' });
  }
}
