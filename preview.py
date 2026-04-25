<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>پیش‌نمایش مدل سه‌بعدی</title>
    <style>
        body { margin: 0; overflow: hidden; font-family: Tahoma; background-color: #111122; }
        #info {
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 8px 15px;
            border-radius: 8px;
            z-index: 10;
            pointer-events: none;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div id="info">
        🧵 مدل سیمی (wireframe) – پس از پرداخت، فایل OBJ قابل دانلود است
    </div>
    <script type="importmap">
        {
            "imports": {
                "three": "https://unpkg.com/three@0.128.0/build/three.module.js",
                "three/addons/": "https://unpkg.com/three@0.128.0/examples/jsm/"
            }
        }
    </script>
    <script type="module">
        import * as THREE from 'three';
        import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x111122);
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(2, 2, 3);
        camera.lookAt(0, 0, 0);
        
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // نورپردازی
        const ambientLight = new THREE.AmbientLight(0x404060);
        scene.add(ambientLight);
        const dirLight = new THREE.DirectionalLight(0xffffff, 1);
        dirLight.position.set(1, 2, 1);
        scene.add(dirLight);
        const backLight = new THREE.DirectionalLight(0x88aaff, 0.5);
        backLight.position.set(-1, 1, -1);
        scene.add(backLight);

        // بارگذاری مدل OBJ از مسیر سرور (public/models/3d_object.obj)
        const objUrl = '/models/3d_object.obj';
        const loader = new OBJLoader();
        let model;
        loader.load(objUrl, (obj) => {
            model = obj;
            obj.traverse(child => {
                if (child.isMesh) {
                    child.material.wireframe = true;      // حالت سیمی
                    child.material.color.setHex(0x88aaff);
                    child.material.emissive = 0x224466;
                }
            });
            scene.add(obj);
        }, undefined, (error) => console.error('خطا در بارگذاری مدل:', error));

        // کنترل چرخش با ماوس
        let mouseX = 0, mouseY = 0;
        document.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX / window.innerWidth) * 2 - 1;
            mouseY = (e.clientY / window.innerHeight) * 2 - 1;
        });

        function animate() {
            requestAnimationFrame(animate);
            // چرخش ملایم دوربین بر اساس حرکت ماوس
            camera.position.x += (mouseX * 0.5 - camera.position.x) * 0.05;
            camera.position.y += (-mouseY * 0.5 - camera.position.y) * 0.05;
            camera.lookAt(0, 0, 0);
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
