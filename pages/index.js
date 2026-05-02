import { useState, useRef, useEffect } from 'react';
import Head from 'next/head';
import Script from 'next/script';

export default function Home() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [modelUrl, setModelUrl] = useState(null);
  const [error, setError] = useState('');
  const [showPayment, setShowPayment] = useState(false);
  const viewerRef = useRef(null);
  const [threeReady, setThreeReady] = useState(false);

  useEffect(() => {
    if (modelUrl && threeReady && viewerRef.current) {
      initThree(modelUrl);
    }
  }, [modelUrl, threeReady]);

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
    formData.append('image', file);

    try {
      const res = await fetch('/api/process', { method: 'POST', body: formData });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'خطا در پردازش');
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setModelUrl(url);
      setShowPayment(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    try {
      const res = await fetch('/api/payment', { method: 'POST' });
      const data = await res.json();
      if (data.paymentUrl) {
        window.location.href = data.paymentUrl;
      } else {
        setError('خطا در ایجاد درگاه پرداخت');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const initThree = (url) => {
    const container = viewerRef.current;
    if (!container) return;
    while (container.firstChild) container.removeChild(container.firstChild);

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x111122);
    const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(2, 1.5, 2);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    const loader = new THREE.OBJLoader();
    loader.load(url, (obj) => {
      scene.add(obj);
    }, undefined, (err) => console.error(err));

    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
      camera.aspect = container.clientWidth / container.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(container.clientWidth, container.clientHeight);
    });
  };

  return (
    <>
      <Head>
        <title>تبدیل تصویر به مدل سه‌بعدی</title>
      </Head>
      <Script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js" strategy="beforeInteractive" onLoad={() => setThreeReady(true)} />
      <Script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/OBJLoader.js" strategy="beforeInteractive" />
      <Script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js" strategy="beforeInteractive" />
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
            <h3>پیش‌نمایش مدل:</h3>
            <div ref={viewerRef} style={{ width: '100%', height: '400px', border: '1px solid #ccc' }}></div>
            {showPayment && (
              <button onClick={handlePayment}>پرداخت و دانلود مدل نهایی</button>
            )}
          </div>
        )}
      </main>
    </>
  );
}
