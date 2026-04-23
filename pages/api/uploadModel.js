import { IncomingForm } from "formidable";
import fs from "fs";
import path from "path";

export const config = {
  api: { bodyParser: false },
};

export default function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method Not Allowed" });

  const form = new IncomingForm();
  form.parse(req, (err, fields, files) => {
    if (err) return res.status(400).json({ error: err.message });

    const keys = Object.keys(files);
    if (keys.length === 0) return res.status(400).json({ error: "No file uploaded" });

    const modelFile = files[keys[0]];
    const fileData = Array.isArray(modelFile) ? modelFile[0] : modelFile;

    if (!fileData.originalFilename || !fileData.filepath)
      return res.status(400).json({ error: "Missing file name or path" });

    const modelsDir = path.join(process.cwd(), "public/models");
    if (!fs.existsSync(modelsDir)) fs.mkdirSync(modelsDir);

    const newPath = path.join(modelsDir, fileData.originalFilename);

    fs.rename(fileData.filepath, newPath, (err) => {
      if (err) return res.status(500).json({ error: err.message });

      // Create .ready flag file
      const readyFlag = path.join(modelsDir, ".ready");
      fs.writeFileSync(readyFlag, "ready");

      res.status(200).json({
        success: true,
        modelUrl: `/models/${fileData.originalFilename}`,
      });
    });
  });
}
