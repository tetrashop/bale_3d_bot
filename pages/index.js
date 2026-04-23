import { useState } from "react";
import ModelPreview from "../components/ModelPreview";

export default function Home() {
  const [image, setImage] = useState(null);
  const [modelUrl, setModelUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // تابع فشرده‌سازی تصویر قبل از آپلود
  function compressImage(file, maxWidth = 800, maxHeight = 800, quality = 0.7) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.src = URL.createObjectURL(file);

      image.onload = () => {
        let width = image.width;
        let height = image.height;

        if (width > maxWidth) {
          height = Math.round((height * maxWidth) / width);
          width = maxWidth;
        }
        if (height > maxHeight) {
          width = Math.round((width * maxHeight) / height);
          height = maxHeight;
        }

        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext("2d");
        ctx.drawImage(image, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            if (blob) resolve(blob);
            else reject(new Error("فشرده‌سازی ناموفق بود"));
          },
          "image/jpeg",
          quality
        );
      };

      image.onerror = (err) => reject(err);
    });
  }

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setError(null);
    setLoading(true);
    setModelUrl(null);
    setImage(null);

    try {
      const compressedBlob = await compressImage(file);
      setImage(URL.createObjectURL(compressedBlob));

      const formData = new FormData();
      formData.append("modelFile", compressedBlob, file.name);

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
    } catch (err) {
      setError(err.message || "خطا در پردازش فایل");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ textAlign: "center", padding: 20 }}>
      <h1>تبدیل دو بعدی به سه بعدی</h1>
      <p>لطفا تصویری را انتخاب کنید:</p>

      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={loading}
      />

      {loading && <p>در حال آپلود و پردازش مدل...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {image && (
        <div style={{ marginTop: 20 }}>
          <h3>تصویر اصلی:</h3>
          <img
            src={image}
            alt="تصویر اصلی"
            style={{ maxWidth: "80vw", maxHeight: 300 }}
          />
        </div>
      )}

      {modelUrl && (
        <>
          <h3 style={{ marginTop: 20 }}>پیش‌نمایش مدل سه‌بعدی (سیمی):</h3>
          <ModelPreview modelUrl={modelUrl} />
          <button
            style={{ marginTop: 20 }}
            onClick={() => alert("اینجا روند پرداخت را اضافه کنید")}
          >
            پرداخت و دریافت مدل نهایی
          </button>
        </>
      )}
    </div>
  );
}
