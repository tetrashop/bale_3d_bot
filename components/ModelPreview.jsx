import { useEffect, useRef } from "react";
import * as THREE from "three";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader";

const ModelPreview = ({ modelUrl }) => {
  const containerRef = useRef();

  useEffect(() => {
    if (!modelUrl) return;

    const width = 400, height = 300;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 3;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
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
      (err) => console.error(err)
    );

    function animate() {
      requestAnimationFrame(animate);
      if (object) object.rotation.y += 0.01;
      renderer.render(scene, camera);
    }

    return () => {
      renderer.dispose();
      while (containerRef.current.firstChild) {
        containerRef.current.removeChild(containerRef.current.firstChild);
      }
    };
  }, [modelUrl]);

  return <div ref={containerRef} />;
};

export default ModelPreview;
