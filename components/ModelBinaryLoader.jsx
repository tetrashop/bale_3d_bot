import { useEffect, useState, useRef } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

export default function ModelBinaryLoader({ apiUrl }) {
  const containerRef = useRef();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [modelUrl, setModelUrl] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch(apiUrl)
      .then(res => {
        if (!res.ok) throw new Error("خطا در بارگذاری مدل");
        return res.blob();
      })
      .then(blob => {
        const url = URL.createObjectURL(blob);
        setModelUrl(url);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [apiUrl]);

  useEffect(() => {
    if (!modelUrl) return;

    const width = 400;
    const height = 300;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 3;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);

    containerRef.current.appendChild(renderer.domElement);

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 1, 1).normalize();
    scene.add(light);

    const loader = new GLTFLoader();
    let model;

    loader.load(
      modelUrl,
      (gltf) => {
        model = gltf.scene;
        model.traverse((child) => {
          if (child.isMesh) {
            child.material.wireframe = true;
          }
        });
        scene.add(model);
        animate();
      },
      undefined,
      (error) => {
        setError("خطا در بارگذاری مدل");
        console.error("Loader error:", error);
      }
    );

    function animate() {
      requestAnimationFrame(animate);
      if (model) model.rotation.y += 0.01;
      renderer.render(scene, camera);
    }

    return () => {
      renderer.dispose();
      while (containerRef.current.firstChild) {
        containerRef.current.removeChild(containerRef.current.firstChild);
      }
      if(modelUrl) URL.revokeObjectURL(modelUrl);
    };
  }, [modelUrl]);

  if (loading) return <div>در حال بارگذاری مدل...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;

  return <div ref={containerRef} style={{ width: 400, height: 300, border: "1px solid #ccc", marginTop: 10 }} />;
}
