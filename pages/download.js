import { useState, useEffect } from 'react';

export default function DownloadPage() {
  const [token, setToken] = useState(null);
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setToken(params.get('token'));
  }, []);

  const handleDownload = async () => {
    if (!token) return;
    window.location.href = `/api/download?token=${token}`;
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>پرداخت موفق</h2>
      <p>مدل سه‌بعدی شما آماده است.</p>
      <button onClick={handleDownload}>دانلود فایل OBJ</button>
    </div>
  );
}
