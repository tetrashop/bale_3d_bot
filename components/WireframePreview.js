import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader";

export default function WireframePreview({ modelUrl }) {
  const mountRef = useRef();

  useEffect(() => {
    if (!modelUrl) return;

    const width = 400, height = 300;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 3;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    mountRef.current.appendChild(renderer.domElement);

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 1, 1).normalize();
    scene.add(light);

    const loader = new OBJLoader();
    let object;

    loader.load(
      modelUrl,
      (obj) => {
        obj.traverse((child) => {
          if (child.isMesh) {
            child.material = new THREE.MeshBasicMaterial({ color: 0x00ff00, wireframe: true });
          }
        });
        object = obj;
        scene.add(object);
        animate();
      },
      undefined,
      (err) => console.error("Error loading OBJ:", err)
    );

    function animate() {
      requestAnimationFrame(animate);
      if (object) object.rotation.y += 0.01;
      renderer.render(scene, camera);
    }

    return () => {
      if (renderer) {
        renderer.dispose();
        while (mountRef.current.firstChild) {
          mountRef.current.removeChild(mountRef.current.firstChild);
        }
      }
    };
  }, [modelUrl]);

  return <div ref={mountRef} style={{ border: "1px solid #ccc", marginTop: 10 }} />;
}
