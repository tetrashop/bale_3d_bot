import { useState } from "react";
import WireframePreview from "../components/WireframePreview";

export default function Home() {
  const [modelUrl, setModelUrl] = useState("/models/3d_model.obj"); // پیش‌فرض مسیر مدل
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // آپلود فایل مدل سه‌بعدی (OBJ)
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setError(null);
    setLoading(true);
    setModelUrl(null);

    const formData = new FormData();
    formData.append("modelFile", file);

    try {
      const res = await fetch("/api/uploadModel", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("خطا در آپلود مدل");

      const data = await res.json();
      if (data.success) {
        setModelUrl(data.modelUrl);
      } else {
        setError("آپلود مدل ناموفق بود");
      }
    } catch (err) {
      setError(err.message || "خطا در اتصال به سرور");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: 20 }}>
      <h1>آپلود و پیش‌نمایش مدل سه‌بعدی</h1>

      <input type="file" accept=".obj" onChange={handleFileChange} disabled={loading} />

      {loading && <p>در حال آپلود مدل...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {modelUrl && <WireframePreview modelUrl={modelUrl} />}
    </div>
  );
}
