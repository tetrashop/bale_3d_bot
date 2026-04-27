import { useState } from "react";
import WireframePreview from "../components/WireframePreview";

export default function Home() {
  const [modelUrl, setModelUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paid, setPaid] = useState(false);

  const uploadImage = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setPaid(false);
    setModelUrl(null);

    const formData = new FormData();
    formData.append("imageFile", file);

    try {
      const res = await fetch("/api/uploadImage", { method: "POST", body: formData });
      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();
      if (data.success) setModelUrl(data.modelUrl);
      else setError("Conversion failed");
    } catch (err) {
      setError(err.message || "Network error");
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    try {
      const walletId = "WALLET-as6NfAMYM6r5ZKUv"; // شناسه ولت تست
      const message = "پرداخت مدل سه‌بعدی شما تایید شد.";
      const res = await fetch("/api/payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ walletId, message }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Payment error");
      }
      alert("پرداخت موفقیت‌آمیز بود.");
      setPaid(true);
    } catch (err) {
      alert("خطا در پرداخت: " + err.message);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: 20 }}>
      <h1>تبدیل تصویر به مدل سه‌بعدی</h1>
      <input type="file" accept="image/*" onChange={uploadImage} disabled={loading} />

      {loading && <p>در حال پردازش مدل...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {modelUrl && !paid && (
        <>
          <WireframePreview modelUrl={modelUrl} />
          <button style={{ marginTop: 20 }} onClick={handlePayment}>
            پرداخت و دریافت مدل نهایی
          </button>
        </>
      )}

      {paid && modelUrl && (
        <div style={{ marginTop: 20 }}>
          <a href={modelUrl} download>
            دانلود مدل سه‌بعدی
          </a>
        </div>
      )}
    </div>
  );
}
