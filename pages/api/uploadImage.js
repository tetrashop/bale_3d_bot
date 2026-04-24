import formidable from "formidable";
import fs from "fs";
import path from "path";
import { execFile } from "child_process";

export const config = {
  api: { bodyParser: false },
};

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method Not Allowed" });

  const form = formidable();

  form.parse(req, (err, fields, files) => {
    if (err) return res.status(400).json({ error: err.message });
    if (!files.imageFile) return res.status(400).json({ error: "No file uploaded" });

    const uploadDir = path.join(process.cwd(), "uploads");
    if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);

    const file = Array.isArray(files.imageFile) ? files.imageFile[0] : files.imageFile;
    const tempPath = file.filepath || file.path;  // بسته به نسخه formidable

    const imagePath = path.join(uploadDir, file.originalFilename);

    fs.rename(tempPath, imagePath, (err) => {
      if (err) return res.status(500).json({ error: err.message });

      const outputPath = path.join(process.cwd(), "public/models/3d_object.obj");

      execFile("python3", ["engine_3d.py", imagePath, outputPath], (error, stdout, stderr) => {
        if (error) {
          console.error(stderr);
          return res.status(500).json({ error: "Failed to generate 3D model" });
        }
        res.status(200).json({ success: true, modelUrl: "/models/3d_object.obj" });
      });
    });
  });
}
