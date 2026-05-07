import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import { writeFile, unlink, mkdir, readFile } from 'fs/promises';
import crypto from 'crypto';
import { pendingModels } from '../../lib/state';

const execAsync = promisify(exec);
export const config = { api: { bodyParser: { sizeLimit: '20mb' } } };

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });
  try {
    const { image, filename, maxRes, zScale } = req.body;
    if (!image) return res.status(400).json({ error: 'No image' });
    let baseName = (filename || 'model').replace(/[^a-z0-9\-_]/gi, '_').substring(0, 50);
    if (!baseName) baseName = 'model';
    const buffer = Buffer.from(image.split(',')[1] || image, 'base64');
    const tempDir = path.join(process.cwd(), 'tmp');
    await mkdir(tempDir, { recursive: true });
    const tempImagePath = path.join(tempDir, `input_${Date.now()}.jpg`);
    const outputObjPath = path.join(tempDir, `${baseName}_${Date.now()}.obj`);
    await writeFile(tempImagePath, buffer);
    const command = `python engine_3d.py "${tempImagePath}" "${outputObjPath}" ${maxRes || 300} ${zScale || 0.5}`;
    await execAsync(command);
    const objContent = await readFile(outputObjPath, 'utf-8');
    await unlink(tempImagePath).catch(() => {});
    await unlink(outputObjPath).catch(() => {});
    const token = crypto.randomBytes(16).toString('hex');
    pendingModels.set(token, { objContent, filename: `${baseName}.obj`, createdAt: Date.now() });
    res.status(200).json({ success: true, token, objContent, filename: `${baseName}.obj` });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: error.message });
  }
}
