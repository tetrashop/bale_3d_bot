import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader";

export default function WireframePreview() {
  const containerRef = useRef();
  const modelUrl = "/models/3d_model.obj";

  const width = 400;
  const height = 300;

  useEffect(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 3;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    containerRef.current.appendChild(renderer.domElement);

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 1, 1).normalize();
    scene.add(light);

    const loader = new OBJLoader();
    let object;

    loader.load(
      modelUrl,
      (obj) => {
        obj.traverse((child) => {
          if (child.isMesh) child.material.wireframe = true;
        });
        object = obj;
        scene.add(object);
        animate();
      },
      undefined,
      (error) => console.error("Error loading model:", error)
    );

    function animate() {
      requestAnimationFrame(animate);
      if (object) object.rotation.y += 0.01;
      renderer.render(scene, camera);
    }

    return () => {
      renderer.dispose();
      if (containerRef.current) {
        while (containerRef.current.firstChild) {
          containerRef.current.removeChild(containerRef.current.firstChild);
        }
      }
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{ width: width, height: height, border: "1px solid #ccc", marginTop: 10 }}
    />
  );
}
