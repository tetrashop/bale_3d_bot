import fs from "fs";
import path from "path";
import formidable from "formidable";

export const config = { api: { bodyParser: false } };

export default function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end("Method Not Allowed");

  const form = new formidable.IncomingForm();

  form.parse(req, (err, fields, files) => {
    if (err) return res.status(400).json({ success: false, error: err.message });

    const modelFile = files.modelFile;
    if (!modelFile) return res.status(400).json({ success: false, error: "فایل مدل ارسال نشده" });

    const newPath = path.join(process.cwd(), "/public/models/", modelFile.originalFilename);

    fs.rename(modelFile.filepath, newPath, (err) => {
      if (err) return res.status(500).json({ success: false, error: err.message });

      // ساخت فایل فلگ آماده بودن مدل
      const readyFlag = path.join(process.cwd(), "/public/models/", ".ready");
      fs.writeFileSync(readyFlag, "ready");

      res.status(200).json({
        success: true,
        modelUrl: `/models/${modelFile.originalFilename}`,
        ready: true,
      });
    });
  });
}
