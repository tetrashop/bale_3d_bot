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
  const [zScale, setZScale] = useState(0.5);
  const [token, setToken] = useState(null);
  const [paymentPending, setPaymentPending] = useState(false);
  const [objContent, setObjContent] = useState(null);
  const [filename, setFilename] = useState('');
  const mountRef = useRef(null);

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
      setFilename('');
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
    setToken(null);
    setDownloadUrl(null);
    setObjContent(null);

    const reader = new FileReader();
    reader.onload = async (ev) => {
      try {
        const res = await fetch('/api/upload', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: ev.target.result, filename: originalName, zScale }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'خطا در تبدیل');
        setToken(data.token);
        setObjContent(data.objContent);
        setFilename(data.filename || `${originalName}.obj`);
        alert('مدل ساخته شد. اکنون می‌توانید پرداخت کنید.');
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
    setPaymentPending(true);
    try {
      const res = await fetch('/api/create-payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      // شبیه‌سازی پرداخت: بلافاصله فایل را دانلود کن (بدون درخواست اضافه)
      setDownloadUrl(URL.createObjectURL(new Blob([objContent], { type: 'text/plain' })));
      setPaymentPending(false);
    } catch (err) {
      setError(err.message);
      setPaymentPending(false);
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>📷 تبدیل تصویر به نقش برجسته (پرداختی)</h1>
      <form onSubmit={(e) => e.preventDefault()}>
        <div style={{ marginBottom: '1rem' }}>
          <input type="file" accept="image/*" onChange={handleFileChange} />
        </div>
        {previewImg && (
          <div style={{ marginBottom: '1rem' }}>
            <img src={previewImg} alt="Preview" style={{ maxWidth: '100%', maxHeight: '200px' }} />
          </div>
        )}
        {objContent && (
          <div ref={mountRef} style={{ marginBottom: '1rem', width: '400px', height: '400px', backgroundColor: '#111' }}></div>
        )}
        <div style={{ marginBottom: '1rem' }}>
          <label>ضریب ارتفاع: </label>
          <input type="range" min="0.1" max="1.5" step="0.01" value={zScale} onChange={(e) => setZScale(e.target.value)} />
          <span>{zScale}</span>
        </div>
        <button type="button" onClick={handleConvertAndPreview} disabled={!file || loading} style={{ marginRight: '10px' }}>
          {loading ? 'در حال ساخت مدل...' : '🔄 تبدیل و پیش‌نمایش'}
        </button>
        <button type="button" onClick={handlePayment} disabled={!token || paymentPending}>
          {paymentPending ? 'منتظر تأیید پرداخت...' : '💳 پرداخت و دانلود'}
        </button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {downloadUrl && (
        <p>✅ <a href={downloadUrl} download={filename || `${originalName}.obj`}>دانلود فایل {filename || originalName}.obj</a></p>
      )}
    </div>
  );
}
