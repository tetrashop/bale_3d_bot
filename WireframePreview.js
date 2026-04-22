import { useEffect, useRef } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

export default function WireframePreview({ modelPath }) {
  const mountRef = useRef();

  useEffect(() => {
    if (!modelPath) return;

    const width = 400;
    const height = 300;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(70, width / height, 0.1, 1000);
    camera.position.z = 3;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    mountRef.current.appendChild(renderer.domElement);

    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 1, 1).normalize();
    scene.add(light);

    const loader = new GLTFLoader();
    let modelScene;

    loader.load(
      modelPath,
      (gltf) => {
        modelScene = gltf.scene;
        modelScene.traverse((child) => {
          if (child.isMesh) {
            child.material = new THREE.MeshBasicMaterial({
              color: 0x00ff00,
              wireframe: true,
            });
          }
        });
        scene.add(modelScene);
        animate();
      },
      undefined,
      (error) => {
        console.error("Error loading wireframe model:", error);
      }
    );

    const animate = () => {
      requestAnimationFrame(animate);
      if (modelScene) modelScene.rotation.y += 0.01;
      renderer.render(scene, camera);
    };

    return () => {
      renderer.dispose();
      while (mountRef.current.firstChild) mountRef.current.removeChild(mountRef.current.firstChild);
    };
  }, [modelPath]);

  return <div ref={mountRef} style={{ border: "1px solid #ccc", marginTop: 10 }} />;
}
