/* ============================================================================
   Hero scene — the M&W mark standing in a live, wind-blown grass field.

   Composes the GetLayers grass shader (see grass.js) with the extruded mark
   (mark3d.js). Blade count scales to the device, the loop pauses when the
   canvas is off screen or the tab is hidden, and reduced-motion renders a
   single still frame.
   ========================================================================== */
import * as THREE from '../vendor/three.module.js';
import { createGrassField, PRESETS } from './grass.js';
import { lookForTime, dateAtHour, describe, siteHour } from './daycycle.js';
import { buildMark } from './mark3d.js';
import BLADE_TEX from './blade-tex.js';

export function mountHeroGrass(canvas, opts = {}) {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const {
    preset = 'auto',
    // Explicitly opt the live day cycle in or out. Left undefined it falls
    // back to the old behaviour of only running for preset 'auto'.
    dayCycle = undefined,
    quality = 'auto',
    markScale = 0.070,
    centred = false,
    // Inlined data URIs. Referencing the JPEGs by path meant the build's
    // WebP-only image step stripped them and every blade got discarded.
    textures = BLADE_TEX,
  } = opts;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      canvas, antialias: true, alpha: false, powerPreference: 'high-performance',
    });
  } catch (e) {
    canvas.classList.add('no-webgl');
    return null;
  }

  const w0 = canvas.clientWidth || 1280;
  const h0 = canvas.clientHeight || 720;
  const coarse = window.matchMedia('(pointer: coarse)').matches;
  const small = w0 < 900;

  // Blade count is the single biggest cost. The reference scene uses 190k;
  // a marketing hero does not need that, and phones certainly do not.
  let instances = 190000;
  if (quality === 'high') instances = 190000;
  else if (quality === 'low') instances = 12000;
  else if (small || coarse) instances = 24000;
  const baseDpr = Math.min(window.devicePixelRatio || 1, small ? 1.6 : 2);

  renderer.setPixelRatio(baseDpr);
  renderer.setSize(w0, h0, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, w0 / h0, 0.1, 2000);

  // The day cycle drives the scene whenever dayCycle is on. This used to be
  // `preset === 'auto'` only, which meant a named preset silently disabled the
  // clock: startClock() bailed, and even pressing Live painted one frame and
  // then froze. Passing an explicit dayCycle keeps a named preset as the BASE
  // look while still letting the clock light it.
  const live = dayCycle === undefined ? preset === 'auto' : !!dayCycle;
  let look = live ? lookForTime() : null;

  const field = createGrassField(scene, {
    // The requested preset is the BASE look the cycle paints on top of.
    // Hardcoding 'dusk' here threw away the reference preset's FogExp2 density
    // and ground colour the moment the cycle was live.
    preset: preset === 'auto' ? 'reference' : preset,
    instances,
    width: 85,
    windSpeed: 1.0,
    mouseRadius: 8.0,
    mouseStrength: 1.4,
    textures,
  });

  if (look) field.applyLook(look);

  // The reference scene is graded at 0.58; the old hardcoded 1.05 blew the

  // sky out along the horizon band the hero framing shows.

  if (field.config.exposure !== undefined) {

    renderer.toneMappingExposure = field.config.exposure;

  }

  /* ---------- the mark, standing in the field ---------- */
  // In the field the grass supplies all the context, so the tooth bar and
  // blade come off — a clean extruded monolith standing in the lawn.
  const { group, mark, bar, blade } = buildMark({
    sideColor: 0x4c6626,
    castShadow: false,
    withBar: false,
    withBlade: false,
  });
  group.scale.setScalar(markScale);
  // the mark's local baseline is at -35; drop just its foot into the blades
  let restY = 0, seatX = 0, seatZ = 0;
  function seat(x, z) {
    seatX = x; seatZ = z;
    restY = field.getYPosition(x, z) + 35 * markScale + 0.62;
    return restY;
  }
  seat(0, 0);
  group.position.set(0, restY, 0);
  group.rotation.y = -0.13;
  scene.add(group);

  // a warm key from the sun side so the bone faces catch the light
  const keyLight = new THREE.DirectionalLight(0xfff1d4, 1.35);
  keyLight.position.copy(field.sunDir).multiplyScalar(60);
  scene.add(keyLight);
  const frontFill = new THREE.DirectionalLight(0xfff8ec, 1.75);
  frontFill.position.set(6, 16, 40);
  scene.add(frontFill);
  const markAmbient = new THREE.AmbientLight(0xe6e2d2, 0.5);
  scene.add(markAmbient);

  /* ---------- day cycle ---------------------------------------------------
     The scene follows the sun's real position over Jefferson County, so it
     drifts through night → dawn → midday → golden hour → dusk on its own,
     and the timing moves with the seasons rather than being pinned to fixed
     clock hours. The scrim strength rides along, because a headline that is
     legible against a midnight sky is not legible against a noon one.      */
  const hero = canvas.closest('.hero') || canvas.parentElement;
  function paint(L) {
    look = L;
    field.applyLook(L);
    if (L.keyColor !== undefined) keyLight.color.setHex(L.keyColor);
    if (L.keyIntensity !== undefined) keyLight.intensity = L.keyIntensity;
    if (L.fillIntensity !== undefined) frontFill.intensity = L.fillIntensity;
    if (L.exposure !== undefined) renderer.toneMappingExposure = L.exposure;
    if (hero && L.scrim !== undefined) {
      // base gradient alphas are tuned for the dusk look (scrim 0.22)
      hero.style.setProperty('--scrim-k',
        String(Math.max(1.0, Math.min(1.8, L.scrim / 0.30))));
    }
  }
  if (look) paint(look);

  let clockTimer = 0;
  function startClock() {
    if (!live || clockTimer) return;
    // one minute is plenty — the sun moves ~0.25° in that time
    clockTimer = setInterval(() => paint(lookForTime()), 60000);
  }
  function stopClock() { clearInterval(clockTimer); clockTimer = 0; }
  if (live) startClock();

  /* ---------- cursor breeze ---------- */
  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2();
  if (!reduce && !coarse) {
    canvas.addEventListener('pointermove', (e) => {
      const r = canvas.getBoundingClientRect();
      ndc.x = ((e.clientX - r.left) / r.width) * 2 - 1;
      ndc.y = -((e.clientY - r.top) / r.height) * 2 + 1;
      raycaster.setFromCamera(ndc, camera);
      const hit = raycaster.intersectObject(field.ground);
      if (hit.length) field.setMouseTarget(hit[0].point.x, hit[0].point.z);
    }, { passive: true });
    canvas.addEventListener('pointerleave', () => field.clearMouse(), { passive: true });
  }

  /* ---------- animation ---------- */
  const clock = new THREE.Clock();
  let raf = 0, visible = true;

  if (reduce) {
    mark.position.y = 0;
  } else {
    mark.position.y = 260;
    bar.scale.x = 0.001;
    blade.scale.y = 0.001;
  }

  const easeOutExpo = (x) => (x === 1 ? 1 : 1 - Math.pow(2, -9 * x));
  const easeOutBack = (x) => { const c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2; };

  function update(t) {
    field.update(t);
    if (reduce) return;
    const dp = Math.min(1, t / 1.2);
    mark.position.y = 260 * (1 - easeOutExpo(dp));
    const bp = Math.max(0, Math.min(1, (t - 0.55) / 0.75));
    bar.scale.x = Math.max(0.001, easeOutBack(bp));
    const sp = Math.max(0, Math.min(1, (t - 0.9) / 0.7));
    blade.scale.y = Math.max(0.001, easeOutExpo(sp));
    const idle = Math.max(0, t - 1.4);
    group.rotation.y = -0.13 + Math.sin(idle * 0.22) * 0.055;
    group.position.y = restY + Math.sin(idle * 0.5) * 0.05;
    blade.material.emissiveIntensity = 0.55 + Math.sin(t * 2.1) * 0.2;
  }

  /* ---------- adaptive quality -------------------------------------------
     This scene is fill-bound: hundreds of thousands of alpha-tested blade
     fragments. A modern GPU eats it, an old phone or a software rasteriser
     does not — so rather than guess the device from its user agent, measure
     the actual frame time and step down until it is comfortable.
     Pixel ratio comes off first (biggest win per unit of visual loss), then
     blade density, which is free to change: InstancedBufferGeometry lets us
     lower `instanceCount` and the field simply thins out uniformly, because
     the blades were generated in random order.                             */
  const LADDER = [
    { dpr: 1.00, blades: 1.00 },
    { dpr: 0.80, blades: 1.00 },
    { dpr: 0.70, blades: 0.62 },
    { dpr: 0.60, blades: 0.35 },
    { dpr: 0.50, blades: 0.18 },
  ];
  let tier = 0, samples = [], lastT = 0, settled = false;

  function applyTier() {
    const s = LADDER[tier];
    renderer.setPixelRatio(Math.max(0.5, baseDpr * s.dpr));
    renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
    field.grassMesh.geometry.instanceCount = Math.max(1200, Math.round(instances * s.blades));
  }

  function sampleFrame(now) {
    if (settled) return;
    if (lastT) {
      const dt = now - lastT;
      // A catastrophically slow first frame means a very weak device (or a
      // software rasteriser). Don't creep down one rung at a time at 1fps —
      // drop straight to the floor, then let it climb back if it was a blip.
      if (dt > 150 && tier < LADDER.length - 1) {
        tier = LADDER.length - 1; applyTier(); samples = []; lastT = now; return;
      }
      samples.push(dt);
      if (samples.length >= 8) {
        samples.sort((a, b) => a - b);
        const median = samples[samples.length >> 1];
        samples = [];
        if (median > 26 && tier < LADDER.length - 1) { tier++; applyTier(); }
        else if (median < 11 && tier > 0) { tier--; applyTier(); }
        else settled = true;
      }
    }
    lastT = now;
  }

  function frame(now) {
    raf = requestAnimationFrame(frame);
    if (!visible) { lastT = 0; return; }
    sampleFrame(now);
    update(clock.getElapsedTime());
    renderer.render(scene, camera);
  }

  /* Measure the mark's real projected size and solve for the scale that fits
     it inside a fraction of the canvas. Deriving this from the actual
     projection rather than from assumed world-unit constants means it stays
     correct no matter where the mark sits relative to the focal plane —
     perspective was quietly making it far larger than a units-based estimate
     predicted. Two passes are enough to converge. */
  const _corner = new THREE.Vector3();
  function projectedSize() {
    const bb = mark.geometry.boundingBox;
    const restore = mark.position.y;
    mark.position.y = 0;                       // ignore the entrance animation
    group.updateMatrixWorld(true);
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const x of [bb.min.x, bb.max.x]) {
      for (const y of [bb.min.y, bb.max.y]) {
        for (const z of [bb.min.z, bb.max.z]) {
          _corner.set(x, y, z);
          mark.localToWorld(_corner);
          _corner.project(camera);
          if (_corner.x < minX) minX = _corner.x;
          if (_corner.x > maxX) maxX = _corner.x;
          if (_corner.y < minY) minY = _corner.y;
          if (_corner.y > maxY) maxY = _corner.y;
        }
      }
    }
    mark.position.y = restore;
    // NDC spans -1..1, so half of the delta is the fraction of the viewport
    return { w: (maxX - minX) / 2, h: (maxY - minY) / 2 };
  }

  function fitMark(maxW, maxH) {
    for (let pass = 0; pass < 2; pass++) {
      const s = projectedSize();
      if (!(s.w > 0) || !(s.h > 0)) return;
      const factor = Math.min(maxW / s.w, maxH / s.h);
      const next = Math.max(0.008, Math.min(0.35, group.scale.x * factor));
      group.scale.setScalar(next);
      group.updateMatrixWorld(true);
    }
  }

  function resize() {
    const w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return;
    renderer.setPixelRatio(Math.max(0.5, baseDpr * LADDER[tier].dpr));
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    const narrow = w < 900;
    let fit;
    if (centred) {
      camera.fov = 42;
      camera.position.set(0, 5.4, 24);
      camera.lookAt(0, 3.6, -4);
      group.position.set(0, seat(0, 0), 0);
      fit = [0.60, 0.52];
    } else if (narrow) {
      // Phone: the copy column is tall (headline + tagline + sub + two CTAs),
      // so the mark has to sit clearly below all of it rather than behind it.
      camera.fov = 52;
      camera.position.set(0, 4.4, 29);
      camera.lookAt(0, 9.4, -4);
      group.position.set(0, seat(0, -1.0), -1.0);
      fit = [0.82, 0.17];
    } else {
      // desktop: mark right of centre, headline owns the dark left third
      camera.fov = 40;
      camera.position.set(0, 5.6, 25);
      camera.lookAt(-2.6, 3.4, -4);
      group.position.set(4.6, seat(4.6, 0), 0);
      fit = [0.46, 0.46];
    }
    camera.updateProjectionMatrix();
    fitMark(fit[0], fit[1]);
    // Re-seat at the fitted scale. Seating depends on the current scale, so
    // doing it before the fit leaves the mark floating on wide screens and
    // sunk into the field on narrow ones.
    group.position.y = seat(seatX, seatZ);
    group.updateMatrixWorld(true);
  }

  resize();
  new ResizeObserver(resize).observe(canvas);

  const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; }, { threshold: 0.01 });
  io.observe(canvas);
  document.addEventListener('visibilitychange', () => {
    visible = !document.hidden;
    // A backgrounded tab throttles timers hard, so someone returning after
    // hours would be looking at a stale sky. Repaint on the way back in.
    if (visible && clockTimer) paint(lookForTime());
  });

  if (reduce) {
    update(6.0);
    renderer.render(scene, camera);
  } else {
    raf = requestAnimationFrame(frame);
  }

  return {
    scene, camera, renderer, field, group, mark, instances,
    get qualityTier() { return tier; },
    get liveBlades() { return field.grassMesh.geometry.instanceCount; },
    renderAt(sec) { update(sec); renderer.render(scene, camera); },
    setGrade(hex) { field.grassUniforms.uGrade.value.set(hex); },
    get look() { return look; },
    get isLive() { return live && !!clockTimer; },
    describeLook() { return look ? describe(look) : ''; },
    /** Current wall-clock hour in Jefferson County. */
    siteHour() { return siteHour(); },
    /** Freeze the scene at a given hour of today — preview scrubber only. */
    previewHour(hour) {
      stopClock();
      paint(lookForTime(dateAtHour(hour)));
      return look;
    },
    /** Hand control back to the real clock. */
    goLive() { paint(lookForTime()); startClock(); },
    setPreset(name) {
      const C = PRESETS[name];
      if (!C) return;
      field.grassUniforms.tipColor.value.set(C.tipColor);
      field.grassUniforms.bottomColor.value.set(C.bottomColor);
      field.skyUniforms.uTop.value.set(C.skyTop).convertSRGBToLinear();
      field.skyUniforms.uHorizon.value.set(C.skyHorizon).convertSRGBToLinear();
      field.skyUniforms.uCloudColor.value.set(C.cloudColor).convertSRGBToLinear();
      field.skyUniforms.uCloudCover.value = C.cloudCover;
      field.ground.material.color.set(C.bottomColor);
      if (C.grade) field.grassUniforms.uGrade.value.set(C.grade);
      if (scene.fog) scene.fog.color.set(C.skyHorizon);
    },
    stop() { cancelAnimationFrame(raf); io.disconnect(); stopClock(); field.dispose(); },
  };
}
