import { useState } from "react";
import ModelPreview from "../components/ModelPreview";

export default function Home() {
  const [modelUrl, setModelUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    const data = new FormData();
    data.append("modelFile", file);

    try {
      const res = await fetch("/api/uploadModel", {
        method: "POST",
        body: data,
      });
      const result = await res.json();
      if (result.success) setModelUrl(result.modelUrl);
      else setError("آپلود ناموفق");
    } catch {
      setError("خطا در اتصال");
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = () => {
    alert("پرداخت اینجا انجام شود");
  };

  return (
    <div style={{ textAlign: "center", padding: 20 }}>
      <h1>آپلود مدل سه‌بعدی و پیش‌نمایش</h1>
      <input type="file" onChange={handleUpload} />

      {loading && <p>در حال آپلود...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {modelUrl && (
        <>
          <h3>پیش‌نمایش مدل:</h3>
          <ModelPreview modelUrl={modelUrl} />
          <button onClick={handlePayment} style={{ marginTop: 20 }}>
            پرداخت و دریافت مدل نهایی
          </button>
        </>
      )}
    </div>
  );
}
