import fs from "fs";
import path from "path";

export default function handler(req, res) {
  const outputDir = path.join(process.cwd(), "outputs");
  const readyFlag = path.join(outputDir, ".ready");

  if (!fs.existsSync(readyFlag)) {
    return res.status(404).json({ success: false, error: "مدل آماده نیست" });
  }

  // لیست فایل‌های glb در خروجی
  const files = fs.readdirSync(outputDir).filter(f => f.toLowerCase().endsWith(".glb"));
  if (files.length === 0) {
    return res.status(404).json({ success: false, error: "هیچ مدل glb موجود نیست" });
  }

  // مرتب‌سازی بر اساس زمان تغییر فایل (جدیدترین اول)
  files.sort((a, b) => {
    const aTime = fs.statSync(path.join(outputDir, a)).mtimeMs;
    const bTime = fs.statSync(path.join(outputDir, b)).mtimeMs;
    return bTime - aTime;
  });

  const latestModel = files[0];
  const modelUrl = `/outputs/${latestModel}`;

  res.status(200).json({ success: true, modelUrl });
}
