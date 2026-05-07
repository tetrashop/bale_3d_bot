import { useState, useRef, useEffect } from 'react';
import * as THREE from 'three';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js';

export default function Home() {
  const [file, setFile] = useState(null);
  const [previewImg, setPreviewImg] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [error, setError] = useState('');
  const [originalName, setOriginalName] = useState('');
  const [quality, setQuality] = useState('normal');
  const [token, setToken] = useState(null);
  const [objContent, setObjContent] = useState(null);
  const [filename, setFilename] = useState('');
  const [chatId, setChatId] = useState('');
  const mountRef = useRef(null);

  const qualitySettings = {
    normal: { maxRes: 300, zScale: 0.5, price: 50000, label: 'معمولی', priceLabel: '۵۰,۰۰۰ ریال' },
    high: { maxRes: 600, zScale: 1.0, price: 150000, label: 'بالا', priceLabel: '۱۵۰,۰۰۰ ریال' },
    pro: { maxRes: 1200, zScale: 1.5, price: 300000, label: 'حرفه‌ای', priceLabel: '۳۰۰,۰۰۰ ریال' }
  };

  useEffect(() => {
    if (objContent && mountRef.current) {
      while (mountRef.current.firstChild) mountRef.current.removeChild(mountRef.current.firstChild);
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x111111);
      const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
      camera.position.set(2, 2, 2);
      camera.lookAt(0, 0, 0);
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(400, 400);
      mountRef.current.appendChild(renderer.domElement);
      const loader = new OBJLoader();
      const blob = new Blob([objContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      loader.load(url, (group) => {
        group.scale.set(0.5, 0.5, 0.5);
        scene.add(group);
        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(1, 2, 1);
        scene.add(light);
        scene.add(new THREE.AmbientLight(0x404040));
        const animate = () => {
          requestAnimationFrame(animate);
          group.rotation.y += 0.01;
          renderer.render(scene, camera);
        };
        animate();
      }, undefined, (err) => console.error(err));
      return () => {
        URL.revokeObjectURL(url);
        renderer.dispose();
      };
    }
  }, [objContent]);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.type.startsWith('image/')) {
      setFile(selected);
      setOriginalName(selected.name.replace(/\.[^/.]+$/, ''));
      const reader = new FileReader();
      reader.onload = (ev) => setPreviewImg(ev.target.result);
      reader.readAsDataURL(selected);
      setError('');
      setToken(null);
      setDownloadUrl(null);
      setObjContent(null);
    } else {
      setFile(null);
      setPreviewImg(null);
      setError('لطفاً یک فایل تصویری انتخاب کنید');
    }
  };

  const handleConvertAndPreview = async () => {
    if (!file) return;
    setLoading(true);
    setError('');

    const reader = new FileReader();
    reader.onload = async (ev) => {
      try {
        const res = await fetch('/api/upload', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            image: ev.target.result,
            filename: originalName,
            maxRes: qualitySettings[quality].maxRes,
            zScale: qualitySettings[quality].zScale
          }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error);
        setToken(data.token);
        setObjContent(data.objContent);
        setFilename(data.filename);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    reader.readAsDataURL(file);
  };

  const handlePayment = async () => {
    if (!token) {
      setError('لطفاً ابتدا تصویر را تبدیل کنید');
      return;
    }
    if (!chatId) {
      setError('شناسه چت بله (Chat ID) را وارد کنید. از ربات @userinfo_idbot در بله دریافت کنید.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/create-payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, quality, chatId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      alert('فاکتور در ربات بله برای شما ارسال شد. پس از پرداخت، صفحه به‌طور خودکار دانلود می‌کند.');
      const interval = setInterval(async () => {
        const checkRes = await fetch(`/api/download?token=${token}`, { method: 'HEAD' });
        if (checkRes.status === 200) {
          clearInterval(interval);
          const blobRes = await fetch(`/api/download?token=${token}`);
          const blob = await blobRes.blob();
          setDownloadUrl(URL.createObjectURL(blob));
          setLoading(false);
        }
      }, 3000);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>📷 تبدیل تصویر به نقش برجسته (پرداختی)</h1>
      <form onSubmit={(e) => e.preventDefault()}>
        <div style={{ marginBottom: '1rem' }}>
          <input type="file" accept="image/*" onChange={handleFileChange} />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <input 
            type="text" 
            placeholder="شناسه چت بله (Chat ID)" 
            value={chatId} 
            onChange={(e) => setChatId(e.target.value)} 
            style={{ width: '260px', padding: '8px', direction: 'ltr' }}
          />
          <small style={{ display: 'block', color: '#666' }}>
            🔑 راهنما: ربات <strong>@userinfo_idbot</strong> را در بله باز کنید. با Start عددی مثل <code>123456789</code> دریافت کنید. همان را اینجا وارد کنید.
          </small>
        </div>
        {previewImg && (
          <div style={{ marginBottom: '1rem' }}>
            <img src={previewImg} alt="Preview" style={{ maxWidth: '100%', maxHeight: '200px' }} />
          </div>
        )}
        <div style={{ marginBottom: '1rem' }}>
          <strong>کیفیت خروجی:</strong>
          <div>
            {Object.keys(qualitySettings).map(key => (
              <label key={key} style={{ marginRight: '1rem' }}>
                <input type="radio" name="quality" value={key} checked={quality === key} onChange={() => setQuality(key)} />
                {qualitySettings[key].label} ({qualitySettings[key].priceLabel})
              </label>
            ))}
          </div>
        </div>
        <button type="button" onClick={handleConvertAndPreview} disabled={!file || loading} style={{ marginRight: '10px' }}>
          {loading ? 'در حال ساخت مدل...' : '🔄 تبدیل و پیش‌نمایش'}
        </button>
        <button type="button" onClick={handlePayment} disabled={!token || loading}>
          {loading ? 'منتظر پرداخت...' : '💳 پرداخت واقعی و دانلود'}
        </button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {downloadUrl && (
        <p>✅ <a href={downloadUrl} download={filename || `${originalName}.obj`}>دانلود فایل {filename || originalName}.obj</a></p>
      )}
      {objContent && !downloadUrl && (
        <div ref={mountRef} style={{ marginTop: '1rem', width: '400px', height: '400px', backgroundColor: '#111' }}></div>
      )}
    </div>
  );
}
