import { IncomingForm } from "formidable";
import fs from "fs";
import path from "path";

export const config = { api: { bodyParser: false } };

export default function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end("Method Not Allowed");

  const form = new IncomingForm();

  form.parse(req, (err, fields, files) => {
    if (err) return res.status(400).json({ success: false, error: err.message });

    const modelFile = files.modelFile || files.file;
    if (!modelFile) return res.status(400).json({ success: false, error: "فایل مدل ارسال نشده" });

    const modelsDir = path.join(process.cwd(), "public/models");
    if (!fs.existsSync(modelsDir)) fs.mkdirSync(modelsDir, { recursive: true });

    const newPath = path.join(modelsDir, modelFile.originalFilename);
    const tempPath = Array.isArray(modelFile) ? modelFile[0].filepath : modelFile.filepath;

    fs.rename(tempPath, newPath, (err) => {
      if (err) return res.status(500).json({ success: false, error: err.message });

      const readyFlag = path.join(modelsDir, ".ready");
      fs.writeFileSync(readyFlag, "ready");

      res.status(200).json({
        success: true,
        modelUrl: `/models/${modelFile.originalFilename}`,
        ready: true,
        downloadUrl: `/models/${modelFile.originalFilename}`
      });
    });
  });
}
