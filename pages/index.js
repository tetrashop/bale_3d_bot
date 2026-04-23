import { useState } from "react";
import WireframePreview from "../components/WireframePreview";

export default function Home() {
  const [modelUrl, setModelUrl] = useState(null);
  const [isPaid, setIsPaid] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setError(null);
    setLoading(true);
    setIsPaid(false);
    setModelUrl(null);

    const formData = new FormData();
    formData.append("modelFile", file);

    try {
      const res = await fetch("/api/uploadModel", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();

      if (data.success) setModelUrl(data.modelUrl);
      else setError("خطا در آپلود مدل");
    } catch {
      setError("خطا در اتصال به سرور");
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = () => {
    // شبیه‌سازی پرداخت موفق
    alert("پرداخت با موفقیت انجام شد");
    setIsPaid(true);
  };

  return (
    <div style={{ textAlign: "center", padding: 20 }}>
      <h1>آپلود و پیش‌نمایش مدل سه‌بعدی</h1>
      <input type="file" accept=".obj,.glb" onChange={handleUpload} disabled={loading} />

      {loading && <p>در حال آپلود...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {modelUrl && !isPaid && (
        <>
          <h3>پیش‌نمایش مدل (سیمی):</h3>
          <WireframePreview modelUrl={modelUrl} />
          <button style={{ marginTop: 10 }} onClick={handlePayment}>
            پرداخت و دریافت مدل نهایی
          </button>
        </>
      )}

      {isPaid && modelUrl && (
        <div style={{ marginTop: 20 }}>
          <h3>پرداخت انجام شد. می‌توانید فایل مدل را دانلود کنید:</h3>
          <a href={modelUrl} download style={{ fontSize: 18, color: "blue" }}>
            دانلود مدل سه‌بعدی
          </a>
        </div>
      )}
    </div>
  );
}
