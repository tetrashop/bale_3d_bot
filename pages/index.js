'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Home() {
  const router = useRouter();
  const [modelUrl, setModelUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [paid, setPaid] = useState(false);
  const [chatId, setChatId] = useState('');

  useEffect(() => {
    // دریافت chatId از پارامتر URL
    const { chatId } = router.query;
    if (chatId) {
      setChatId(chatId);
      localStorage.setItem('bale_chat_id', chatId);
    } else {
      const stored = localStorage.getItem('bale_chat_id');
      if (stored) setChatId(stored);
    }
  }, [router.query]);

  const uploadImage = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    setError(null);
    setModelUrl(null);
    setPaid(false);

    const formData = new FormData();
    formData.append('imageFile', file);

    try {
      const res = await fetch('/api/uploadImage', { method: 'POST', body: formData });
      if (!res.ok) throw new Error('Upload failed');
      const data = await res.json();
      if (data.success) setModelUrl(data.modelUrl);
      else setError('Conversion failed');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    if (!chatId) {
      alert('شناسه کاربر یافت نشد. لطفاً از طریق ربات بله اقدام کنید.');
      return;
    }
    const amount = 5000; // تومان

    try {
      const res = await fetch('/api/payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chatId, amount })
      });
      const data = await res.json();
      if (data.ok) {
        setPaid(true);
        alert('فاکتور پرداخت در ربات بله ارسال شد. لطفاً آن را نهایی کنید.');
      } else {
        alert('خطا: ' + (data.error || 'مشخص نیست'));
      }
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
      {modelUrl && !paid && (
        <div style={{ marginTop: '1rem' }}>
          <iframe
            src="/preview.html"
            style={{ width: '100%', maxWidth: '600px', height: '400px', border: 'none', borderRadius: '8px' }}
            title="پیش‌نمایش سه‌بعدی"
          />
          <button
            onClick={handlePayment}
            style={{ marginTop: 20, padding: '12px 24px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: 4, cursor: 'pointer' }}
          >
            💳 پرداخت و دریافت مدل نهایی
          </button>
        </div>
      )}
      {paid && modelUrl && (
        <div style={{ marginTop: '1rem' }}>
          <a
            href={modelUrl}
            download
            style={{ padding: '12px 24px', backgroundColor: '#2196F3', color: 'white', textDecoration: 'none', borderRadius: 4 }}
          >
            📥 دانلود مدل سه‌بعدی (OBJ)
          </a>
        </div>
      )}
    </div>
  );
}
