/* ============================================================================
   M&W GroundWorks — 3D animated logo
   Extrudes the real M&W letterform geometry (exported from the same font
   outlines used in the SVG identity) and stages it over a low-poly terrain
   that grades itself flat — the "clear" half of the tagline, in motion.
   ========================================================================== */
import * as THREE from '../vendor/three.module.js';
import { SVGLoader } from '../vendor/SVGLoader.js';
import { MW_PATH } from './mw-path.js';

const PAL = {
  ink: 0x070a08,
  bone: 0xf2ede1,
  moss: 0x7a9a3e,
  mossDark: 0x33461b,
  amber: 0xe8a33d,
};

export function mountLogo3D(canvas, opts = {}) {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const {
    spin = true,
    autoResize = true,
    dpr = Math.min(window.devicePixelRatio || 1, 2),
    terrain = true,
    centred = false,
  } = opts;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      canvas, antialias: true, alpha: true, powerPreference: 'high-performance',
    });
  } catch (e) {
    canvas.classList.add('no-webgl');
    return null;
  }
  renderer.setPixelRatio(dpr);
  renderer.setSize(canvas.clientWidth || 800, canvas.clientHeight || 600, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.3;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(PAL.ink, 620, 1500);

  const camera = new THREE.PerspectiveCamera(38, 1, 1, 2000);
  camera.position.set(0, 40, 395);
  camera.lookAt(0, 6, 0);

  // ---- lighting: cool key from upper-left, warm amber rim from the right ----
  scene.add(new THREE.AmbientLight(0xd6d8cf, 0.55));
  const key = new THREE.DirectionalLight(0xfff6e6, 3.6);
  key.position.set(-150, 210, 190);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  key.shadow.camera.near = 10; key.shadow.camera.far = 700;
  key.shadow.camera.left = -240; key.shadow.camera.right = 240;
  key.shadow.camera.top = 240; key.shadow.camera.bottom = -240;
  key.shadow.bias = -0.0016;
  scene.add(key);
  const rim = new THREE.DirectionalLight(PAL.amber, 1.55);
  rim.position.set(230, 70, -140);
  scene.add(rim);
  const fill = new THREE.DirectionalLight(PAL.moss, 0.30);
  fill.position.set(60, -90, 120);
  scene.add(fill);
  // camera-aligned front light so the bone faces read as bone, not grey
  const front = new THREE.DirectionalLight(0xfffaf0, 1.45);
  front.position.set(30, 70, 420);
  scene.add(front);
  const back = new THREE.DirectionalLight(0xe8f0dc, 0.85);
  back.position.set(-40, 120, -220);
  scene.add(back);

  // ---- the mark ------------------------------------------------------------
  const group = new THREE.Group();
  scene.add(group);

  const shapes = pathToShapes(MW_PATH);

  const DEPTH = 26;
  const geo = new THREE.ExtrudeGeometry(shapes, {
    depth: DEPTH, bevelEnabled: true, bevelThickness: 2.2,
    bevelSize: 1.7, bevelSegments: 3, curveSegments: 8,
  });
  geo.computeBoundingBox();
  const bb = geo.boundingBox;
  const cx = (bb.max.x + bb.min.x) / 2;
  const cy = (bb.max.y + bb.min.y) / 2;
  geo.translate(-cx, -cy, -DEPTH / 2);

  const faceMat = new THREE.MeshStandardMaterial({
    color: PAL.bone, roughness: 0.46, metalness: 0.04,
  });
  const sideMat = new THREE.MeshStandardMaterial({
    color: PAL.moss, roughness: 0.42, metalness: 0.34,
  });
  const mark = new THREE.Mesh(geo, [faceMat, sideMat]);
  mark.castShadow = true;
  mark.receiveShadow = false;
  mark.scale.setScalar(1.0);
  group.add(mark);

  // amber blade line — the "cut", slicing behind the mark
  const blade = new THREE.Mesh(
    new THREE.BoxGeometry(3.0, 148, 3.0),
    new THREE.MeshStandardMaterial({
      color: PAL.amber, emissive: PAL.amber, emissiveIntensity: 0.75,
      roughness: 0.3, metalness: 0.5,
    })
  );
  blade.position.set(26, 6, -30);
  blade.rotation.z = 0.24;
  group.add(blade);

  // bucket-tooth bar under the mark
  const bar = new THREE.Group();
  const barMat = new THREE.MeshStandardMaterial({
    color: PAL.moss, roughness: 0.45, metalness: 0.3,
  });
  const plate = new THREE.Mesh(new THREE.BoxGeometry(196, 11, 20), barMat);
  plate.castShadow = true;
  bar.add(plate);
  for (let i = 0; i < 7; i++) {
    const t = new THREE.Mesh(new THREE.CylinderGeometry(0, 11, 17, 4), barMat);
    t.position.set(-81 + i * 27, -13, 0);
    t.rotation.y = Math.PI / 4;
    t.castShadow = true;
    bar.add(t);
  }
  bar.position.y = -54;
  group.add(bar);

  // ---- terrain: jagged on the left, graded flat on the right ---------------
  let ground = null, groundGeo = null, baseZ = null;
  if (terrain) {
    const SEG = 56;
    groundGeo = new THREE.PlaneGeometry(1500, 900, SEG, Math.round(SEG * 0.6));
    const pos = groundGeo.attributes.position;
    baseZ = new Float32Array(pos.count);
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i), y = pos.getY(i);
      // rough on the left, progressively graded toward the right
      const wild = Math.max(0, Math.min(1, (120 - x) / 520));
      const n = Math.sin(x * 0.021) * Math.cos(y * 0.026) * 22
              + Math.sin(x * 0.058 + y * 0.031) * 11
              + Math.cos(x * 0.11) * 5;
      baseZ[i] = n * wild;
      pos.setZ(i, baseZ[i]);
    }
    groundGeo.computeVertexNormals();
    ground = new THREE.Mesh(groundGeo, new THREE.MeshStandardMaterial({
      color: 0x2b3a18, roughness: 1.0, metalness: 0.0,
      flatShading: true,
    }));
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -128;
    ground.receiveShadow = true;
    scene.add(ground);

    const grid = new THREE.GridHelper(1500, 46, PAL.moss, PAL.moss);
    grid.material.transparent = true;
    grid.material.opacity = 0.16;
    grid.position.y = -127;
    scene.add(grid);
  }

  // ---- animation -----------------------------------------------------------
  let baseY = 0;
  let t0 = performance.now();
  let raf = 0, visible = true, pointer = { x: 0, y: 0 };

  if (reduce) {
    group.rotation.set(0, -0.14, 0);
    mark.position.y = 0;
    group.position.y = baseY;
  } else {
    mark.position.y = 200;
    bar.scale.x = 0.001;
    blade.scale.y = 0.001;
  }

  function easeOutExpo(x) { return x === 1 ? 1 : 1 - Math.pow(2, -9 * x); }
  function easeOutBack(x) { const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); }

  function update(t) {

    if (!reduce) {
      // entrance: the mark drops in, the bar snaps open, the blade cuts down
      const dp = Math.min(1, t / 1.15);
      mark.position.y = 200 * (1 - easeOutExpo(dp));
      const bp = Math.max(0, Math.min(1, (t - 0.5) / 0.75));
      bar.scale.x = Math.max(0.001, easeOutBack(bp));
      const sp = Math.max(0, Math.min(1, (t - 0.85) / 0.7));
      blade.scale.y = Math.max(0.001, easeOutExpo(sp));

      // terrain grades itself flat over the first few seconds, then breathes
      if (ground && baseZ) {
        const gp = Math.max(0, Math.min(1, (t - 1.1) / 2.6));
        const flat = 1 - easeOutExpo(gp) * 0.72;
        const pos = groundGeo.attributes.position;
        for (let i = 0; i < pos.count; i++) {
          pos.setZ(i, baseZ[i] * flat + Math.sin(t * 0.5 + i * 0.09) * 0.5 * flat);
        }
        pos.needsUpdate = true;
        if (gp < 1) groundGeo.computeVertexNormals();
      }

      if (spin) {
        const idle = Math.max(0, t - 1.3);
        group.rotation.y = -0.16 + Math.sin(idle * 0.34) * 0.30 + pointer.x * 0.22;
        group.rotation.x = Math.sin(idle * 0.26) * 0.075 + pointer.y * 0.11;
        group.position.y = baseY + Math.sin(idle * 0.55) * 4.5;
      }
      blade.material.emissiveIntensity = 0.6 + Math.sin(t * 2.1) * 0.22;
    }

  }

  function frame(now) {
    raf = requestAnimationFrame(frame);
    if (!visible) return;
    update((now - t0) / 1000);
    renderer.render(scene, camera);
  }

  function resize() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    // pull the camera back and lift the framing on narrow screens
    // Frame from the actual geometry so the mark never crops, at any ratio.
    const narrow = w < 900;
    camera.fov = narrow ? 44 : 38;
    camera.position.set(0, narrow ? 26 : 40, narrow ? 470 : 395);
    camera.lookAt(0, centred ? 0 : (narrow ? 128 : 4), 0);
    const visH = 2 * camera.position.z * Math.tan((camera.fov / 2) * Math.PI / 180);
    const visW = visH * (w / h);
    const markW = 190, markH = 190;               // mark + tooth bar, world units
    const fitW = (visW * (centred ? 0.62 : narrow ? 0.78 : 0.46)) / markW;
    const fitH = (visH * (centred ? 0.60 : narrow ? 0.30 : 0.62)) / markH;
    const k = Math.min(fitW, fitH, 1.25);
    group.scale.setScalar(k);
    group.position.x = centred ? 0 : (narrow ? 0 : visW * 0.22);
    baseY = centred ? visH * 0.255 : 0;
    camera.updateProjectionMatrix();
  }

  resize();
  if (autoResize) {
    const ro = new ResizeObserver(resize);
    ro.observe(canvas);
  }

  if (!reduce) {
    window.addEventListener('pointermove', (e) => {
      pointer.x = (e.clientX / window.innerWidth - 0.5) * 2;
      pointer.y = (e.clientY / window.innerHeight - 0.5) * 2;
    }, { passive: true });
  }

  // pause when scrolled out of view — no wasted GPU
  const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; }, { threshold: 0.01 });
  io.observe(canvas);
  document.addEventListener('visibilitychange', () => {
    visible = !document.hidden;
  });

  raf = requestAnimationFrame(frame);

  return {
    scene, camera, renderer, group, mark,
    // deterministic seek + render, used by the offline video renderer
    renderAt(sec) { update(sec); renderer.render(scene, camera); },
    setTime(sec) { t0 = performance.now() - sec * 1000; },
    renderNow() { renderer.render(scene, camera); },
    stop() { cancelAnimationFrame(raf); io.disconnect(); },
  };
}

/* Turn a raw SVG path 'd' string into THREE.Shape objects.
   The path is exported y-up from the font outlines, so no axis flip is needed. */
function pathToShapes(d) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg"><path d="${d}"/></svg>`;
  const data = new SVGLoader().parse(svg);
  const shapes = [];
  data.paths.forEach((p) => {
    SVGLoader.createShapes(p).forEach((s) => shapes.push(s));
  });
  return shapes;
}
