import formidable from "formidable";
import fs from "fs";
import path from "path";
import { execFile } from "child_process";

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).end("Method Not Allowed");

  const form = new formidable.IncomingForm();

  form.parse(req, async (err, fields, files) => {
    if (err) return res.status(400).json({ success: false, error: err.message });

    if (!files.imageFile) return res.status(400).json({ success: false, error: "No image uploaded" });

    const image = files.imageFile;
    const uploadDir = path.join(process.cwd(), "uploads");
    if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);

    const imagePath = path.join(uploadDir, image.originalFilename);

    await fs.promises.rename(image.filepath, imagePath);

    // اجرای پردازش مدل پایتون (مثلا engine_3d.py) برای تبدیل تصویر به مدل obj
    // فرض بر این است که فایل engine_3d.py قابلیت دریافت ورودی و خروجی را دارد
    
    const outputDir = path.join(process.cwd(), "public/models");
    if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);

    const outputModelPath = path.join(outputDir, "3d_object.obj");

    // اجرای پایتون به شکل sync/async
    execFile("python3", ["engine_3d.py", imagePath, outputModelPath], (error, stdout, stderr) => {
      if (error) {
        console.error(stderr);
        return res.status(500).json({ success: false, error: "Error processing model" });
      }
      return res.status(200).json({
        success: true,
        modelUrl: "/models/3d_object.obj",
      });
    });
  });
}
