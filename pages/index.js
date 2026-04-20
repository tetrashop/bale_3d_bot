// pages/index.js
import { useState } from "react";

export default function Home() {
  const sendMessage = async () => {}; // تابع خالی موقت

  const [image, setImage] = useState(null);
  const [converted, setConverted] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setError(null);
    setLoading(true);
    const reader = new FileReader();

    reader.onload = async (event) => {
      setImage(event.target.result);

      try {
        const res = await fetch("/api/convert", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ imageBase64: event.target.result }),
        });
        if (!res.ok) throw new Error("خطا در تبدیل تصویر");

        const data = await res.json();
        setConverted(data.convertedImage);

        await sendMessage({ type: "text", text: "تصویر تبدیل شد." });
      } catch (err) {
        setError(err.message || "خطایی رخ داد");
      } finally {
        setLoading(false);
      }
    };
    reader.readAsDataURL(file);
  };

  return (
    <div style={{ textAlign: "center", padding: 20 }}>
      <h1>تبدیل دو بعدی به سه بعدی</h1>
      <p>لطفا تصویری را آپلود کنید تا تبدیل شود.</p>

      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={loading}
      />

      {loading && <p>در حال پردازش تصویر...</p>}
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

      {converted && (
        <div style={{ marginTop: 20 }}>
          <h3>تصویر سه بعدی تبدیل شده:</h3>
          <img
            src={converted}
            alt="3D Converted"
            style={{ maxWidth: "80vw", maxHeight: 300 }}
          />
        </div>
      )}
    </div>
  );
}
