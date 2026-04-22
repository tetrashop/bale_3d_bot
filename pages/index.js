import { useState } from "react";
import ModelPreview from "../components/ModelPreview";

export default function Home() {
  const [image, setImage] = useState(null);
  const [modelUrl, setModelUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setError(null);
    setLoading(true);
    setModelUrl(null);
    setImage(URL.createObjectURL(file));

    const formData = new FormData();
    formData.append("modelFile", file);

    try {
      const res = await fetch("/api/checkReady", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("خطا در آپلود مدل");

      const data = await res.json();
      if (data.success) {
        setModelUrl(data.modelUrl);
      } else {
        setError("آپلود موفق نبود");
      }
    } catch {
      setError("خطا در اتصال به سرور");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: 20 }}>
      <h1>تبدیل دو بعدی به سه بعدی</h1>
      <p>لطفاً تصویری برای تبدیل انتخاب کنید:</p>

      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={loading}
      />

      {loading && <p>در حال پردازش تصویر و ساخت مدل...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {image && (
        <div style={{ marginTop: 20 }}>
          <h3>تصویر اصلی:</h3>
          <img
            src={image}
            alt="Original"
            style={{ maxWidth: "80vw", maxHeight: 300 }}
          />
        </div>
      )}

      {modelUrl && (
        <div style={{ marginTop: 20 }}>
          <h3>پیش‌نمایش مدل سه‌بعدی:</h3>
          <ModelPreview modelUrl={modelUrl} />
          <button
            style={{ marginTop: 20 }}
            onClick={() => alert("اینجا پرداخت را مدیریت کن")}
          >
            پرداخت و دریافت مدل نهایی
          </button>
        </div>
      )}
    </div>
  );
}
