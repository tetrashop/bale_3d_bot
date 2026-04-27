// pages/index.js
'use client';
import { useState } from 'react';

export default function Home() {
  const [modelUrl, setModelUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const uploadImage = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);
    setModelUrl(null);

    const formData = new FormData();
    formData.append('imageFile', file);

    try {
      const res = await fetch('/api/uploadImage', { method: 'POST', body: formData });
      if (!res.ok) throw new Error('Upload failed');
      const data = await res.json();
      if (data.success) setModelUrl(data.modelUrl);
      else setError('Conversion failed');
    } catch (err) {
      setError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    try {
      const walletId = 'WALLET-as6NfAMYM6r5ZKUv';
      const message = 'پرداخت مدل سه‌بعدی شما تایید شد.';
      const res = await fetch('/api/payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ walletId, message }),
      });
      const data = await res.json();
      if (data.ok) alert('پرداخت موفقیت‌آمیز بود');
      else alert('خطا در پرداخت');
    } catch (err) {
      alert('خطا در اتصال به سرور');
    }
  };

  return (
    <div style={{ textAlign: 'center', padding: '2rem' }}>
      <h1>🦟 تبدیل تصویر به مدل سه‌بعدی</h1>
      <input type="file" accept="image/*" onChange={uploadImage} disabled={loading} />
      {loading && <p>در حال پردازش مدل...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {modelUrl && (
        <>
          <iframe src={modelUrl.replace('.obj', '.html') || '/preview.html'} style={{ width: '100%', height: '400px', border: 'none' }} />
          <button style={{ marginTop: 20, padding: '10px 20px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: 4 }} onClick={handlePayment}>
            💳 پرداخت و دریافت مدل نهایی
          </button>
        </>
      )}
    </div>
  );
}
