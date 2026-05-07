// pages/api/process.js
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';
import { writeFile, unlink, mkdir } from 'fs/promises';

const execAsync = promisify(exec);
export const config = { api: { bodyParser: { sizeLimit: '20mb' } } };

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Only POST' });

  const { image, filename, zScale = 0.5, transactionId } = req.body;

  // 1. اعتبارسنجی پرداخت
  if (!transactionId) {
    return res.status(400).json({ error: 'Transaction ID required' });
  }

  // بررسی وضعیت پرداخت با استفاده از API داخلی
  const verifyRes = await fetch(`${process.env.NEXTAUTH_URL}/api/verify-payment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transactionId }),
  });
  const verifyData = await verifyRes.json();
  if (!verifyRes.ok || !verifyData.success) {
    return res.status(402).json({ error: 'Payment required or invalid' });
  }

  // 2. پرداخت تأیید شد -> تولید OBJ
  try {
    let baseName = (filename || 'model').replace(/[^a-z0-9\-_]/gi, '_').substring(0, 50);
    if (!baseName) baseName = 'model';

    const buffer = Buffer.from(image.split(',')[1] || image, 'base64');
    const tempDir = path.join(process.cwd(), 'tmp');
    const modelsDir = path.join(process.cwd(), 'public', 'models');
    await mkdir(tempDir, { recursive: true });
    await mkdir(modelsDir, { recursive: true });

    const tempImagePath = path.join(tempDir, `input_${Date.now()}.jpg`);
    const outputObjPath = path.join(modelsDir, `${baseName}.obj`);

    await writeFile(tempImagePath, buffer);
    const command = `python engine_3d.py "${tempImagePath}" "${outputObjPath}" 500 ${zScale}`;
    await execAsync(command);
    const objContent = await fs.promises.readFile(outputObjPath, 'utf-8');

    await unlink(tempImagePath).catch(() => {});

    res.setHeader('Content-Type', 'application/octet-stream');
    res.setHeader('Content-Disposition', `attachment; filename="${baseName}.obj"`);
    res.status(200).send(objContent);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'OBJ generation failed' });
  }
}
