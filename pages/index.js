import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [modelUrl, setModelUrl] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('لطفاً یک تصویر انتخاب کنید');
      return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch('/api/process', { method: 'POST', body: formData });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'خطا در پردازش');
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setModelUrl(url);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>تبدیل تصویر به مدل سه‌بعدی</h1>
      <div>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={loading}>
          {loading ? 'در حال پردازش...' : 'تبدیل به سه‌بعدی'}
        </button>
      </div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {modelUrl && !loading && (
        <div>
          <p>✅ مدل ساخته شد. <a href={modelUrl} download="model.obj">دانلود فایل OBJ</a></p>
        </div>
      )}
    </main>
  );
}
