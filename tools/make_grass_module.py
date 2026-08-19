#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Turn the GetLayers grass-shader source into a reusable ES module.

The GLSL is lifted verbatim from the supplied `grass-shader.html` (itself a
faithful port of the pmndrs grass-shader example) — only the surrounding
plumbing is rewritten so the field can be composed into an existing scene,
tinted from the brand palette, and scaled down for phones.
"""
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "original-shader", "grass-shader.html")
OUT = os.path.join(ROOT, "website", "assets", "js", "grass.js")

lines = open(SRC).read().split("\n")


def grab(a, b):
    """Lines a..b inclusive, with any trailing JS template backtick stripped."""
    block = lines[a - 1:b]
    if block:
        last = block[-1]
        i = last.rfind("`")
        if i != -1:
            block[-1] = last[:i]
    return "\n".join(block)


SIMPLEX_GLSL = grab(265, 287)
GRASS_VERT = grab(307, 364)   # ${SIMPLEX_GLSL} is interpolated inside it
GRASS_FRAG = grab(366, 380)
GRASS_FRAG_BODY = grab(366, 377)   # uniforms..col mixes, before gl_FragColor
SKY_FRAG = grab(197, 244) + "\n      }"
SIMPLEX_JS = grab(91, 119)      # the JS SimplexNoise class
MULBERRY = grab(124, 131)       # mulberry32

module = f'''/* ============================================================================
   Animated grass field — instanced blade shader.

   GLSL lifted verbatim from the GetLayers "grass-shader" source Marz supplied,
   which is itself a faithful port of the pmndrs grass-shader example
   (https://github.com/pmndrs/examples/tree/main/demos/grass-shader).
   Rewritten here as a composable module so the field can share a scene with
   the M&W mark, be tinted from the brand palette, and scale its blade count
   to the device.
   ========================================================================== */
import * as THREE from '../vendor/three.module.js';

/* ---------- seeded RNG + noise (unchanged) ---------- */
{MULBERRY}

{SIMPLEX_JS}

const bW = 0.032, bH = 1, joints = 5;

const SIMPLEX_GLSL = `
{SIMPLEX_GLSL}
`;

/* ---------- brand presets ------------------------------------------------ */
export const PRESETS = {{
  // Low warm sun. Dark at the zenith so headline text stays readable, warm at
  // the horizon so the amber CTA colour is motivated by the light itself.
  goldenHour: {{
    // Late light. Near-black at the zenith so headline copy reads without a
    // heavy scrim; warm only along the horizon, which is what motivates the
    // amber CTA colour.
    tipColor: '#6F8C39', bottomColor: '#111B0C',
    skyTop: '#070B08', skyHorizon: '#4E3A24',
    cloudColor: '#6B563C', cloudCover: 0.30, cloudSpeed: 0.8,
    sunElevation: 10, sunAzimuth: 148, sunColor: '#C08A4A',
    hemiSky: '#4A3E28', hemiGround: '#1A2412', hemiIntensity: 0.55,
    dirColor: '#E8C48E', dirIntensity: 1.25,
    grade: '#B99A62',
  }},
  // The original bright-daylight look, retinted slightly toward the brand moss.
  daylight: {{
    tipColor: '#7FA83C', bottomColor: '#16290F',
    skyTop: '#8FB6E8', skyHorizon: '#BBD9F2',
    cloudColor: '#FFFFFF', cloudCover: 0.5, cloudSpeed: 1.0,
    sunElevation: 34, sunAzimuth: 150, sunColor: '#FFF4D6',
    hemiSky: '#BCD4FF', hemiGround: '#33502A', hemiIntensity: 0.9,
    dirColor: '#FFF6E0', dirIntensity: 1.6,
    grade: '#E4EAD6',
  }},
  // Near-black sky, deep moss grass — closest to the original dark hero.
  dusk: {{
    // Almost mono. The darkest option — closest to the original hero.
    tipColor: '#4E6B26', bottomColor: '#080F06',
    skyTop: '#060907', skyHorizon: '#1C2619',
    cloudColor: '#28331F', cloudCover: 0.26, cloudSpeed: 0.6,
    sunElevation: 3, sunAzimuth: 152, sunColor: '#6B5A3A',
    hemiSky: '#232C1C', hemiGround: '#0C120A', hemiIntensity: 0.45,
    dirColor: '#9C8C64', dirIntensity: 0.9,
    grade: '#6E7D55',
  }},
}};

/**
 * Build the grass field, ground and sky dome into `scene`.
 * Returns handles plus an `update(elapsedSeconds)` to drive the wind.
 */
export function createGrassField(scene, opts = {{}}) {{
  const {{
    preset = 'goldenHour',
    instances = 60000,
    width = 85,
    windSpeed = 1.0,
    mouseRadius = 8.0,
    mouseStrength = 1.4,
    seed = 2241217164,
    sky: wantSky = true,
    fog = true,
  }} = opts;

  const C = {{ ...PRESETS[preset] || PRESETS.goldenHour, ...(opts.override || {{}}) }};
  const SEED = seed >>> 0;
  const simplex = new SimplexNoise(mulberry32(SEED));

  // their exact three-octave terrain
  function getYPosition(x, z) {{
    let y = 2 * simplex.noise2D(x / 50, z / 50);
    y += 4 * simplex.noise2D(x / 100, z / 100);
    y += 0.2 * simplex.noise2D(x / 10, z / 10);
    return y;
  }}

  const sun = new THREE.Vector3().setFromSphericalCoords(
    1,
    THREE.MathUtils.degToRad(90 - C.sunElevation),
    THREE.MathUtils.degToRad(C.sunAzimuth)
  );

  if (fog) scene.fog = new THREE.Fog(new THREE.Color(C.skyHorizon), 40, 190);

  /* ---------- sky dome ---------- */
  const skyUniforms = {{
    uTop: {{ value: new THREE.Color(C.skyTop).convertSRGBToLinear() }},
    uHorizon: {{ value: new THREE.Color(C.skyHorizon).convertSRGBToLinear() }},
    uSunColor: {{ value: new THREE.Color(C.sunColor).convertSRGBToLinear() }},
    uSunDir: {{ value: sun.clone() }},
    uTime: {{ value: 0 }},
    uCloudColor: {{ value: new THREE.Color(C.cloudColor).convertSRGBToLinear() }},
    uCloudCover: {{ value: C.cloudCover }},
    uCloudSpeed: {{ value: C.cloudSpeed }},
  }};
  let sky = null;
  if (wantSky) {{
    sky = new THREE.Mesh(
      new THREE.SphereGeometry(1200, 48, 32),
      new THREE.ShaderMaterial({{
        side: THREE.BackSide, depthWrite: false, fog: false, toneMapped: false,
        uniforms: skyUniforms,
        vertexShader: `varying vec3 vDir; void main(){{ vDir = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }}`,
        fragmentShader: `
{SKY_FRAG}`,
      }})
    );
    sky.frustumCulled = false;
    scene.add(sky);
  }}

  const hemi = new THREE.HemisphereLight(C.hemiSky, C.hemiGround, C.hemiIntensity);
  scene.add(hemi);
  const dirLight = new THREE.DirectionalLight(C.dirColor, C.dirIntensity);
  dirLight.position.copy(sun).multiplyScalar(50);
  scene.add(dirLight);

  /* ---------- blade textures ----------
     Resolved relative to this module when it runs as an ES module, but the
     offline single-file build inlines everything into a classic script where
     import.meta.url does not exist — so callers can pass explicit URLs (or
     data URIs) instead. */
  function texUrl(name, explicit) {{
    if (explicit) return explicit;
    try {{ return new URL('../img/' + name, import.meta.url).href; }}
    catch (e) {{ return 'assets/img/' + name; }}
  }}
  const tex = opts.textures || (typeof window !== 'undefined' && window.__MW_GRASS_TEX) || {{}};
  const loader = new THREE.TextureLoader();
  const grassTexture = loader.load(texUrl('blade_diffuse.jpg', tex.diffuse));
  grassTexture.colorSpace = THREE.SRGBColorSpace;
  const alphaMap = loader.load(texUrl('blade_alpha.jpg', tex.alpha));

  const grassUniforms = {{
    map: {{ value: grassTexture }},
    alphaMap: {{ value: alphaMap }},
    time: {{ value: 0 }},
    bladeHeight: {{ value: bH }},
    tipColor: {{ value: new THREE.Color(C.tipColor) }},
    bottomColor: {{ value: new THREE.Color(C.bottomColor) }},
    uMouse: {{ value: new THREE.Vector2(1e6, 1e6) }},
    uMouseRadius: {{ value: mouseRadius }},
    uMouseStrength: {{ value: mouseStrength }},
    uGrade: {{ value: new THREE.Color(C.grade || '#ffffff') }},
  }};

  const grassMaterial = new THREE.ShaderMaterial({{
    side: THREE.DoubleSide,
    uniforms: grassUniforms,
    vertexShader: `
{GRASS_VERT}`,
    // ADDED (not in the reference shader): the blade tips are dominated by the
    // diffuse photo texture, so tipColor alone cannot pull the field toward the
    // brand moss or match it to a darker sky. uGrade multiplies the final colour.
    fragmentShader: `
    uniform vec3 uGrade;
{GRASS_FRAG_BODY}
      gl_FragColor = vec4(col.rgb * uGrade, col.a);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }}`,
  }});

  /* ---------- instanced field ---------- */
  function generateField(count, w) {{
    const offsets = [], orientations = [], stretches = [];
    const halfRootAngleSin = [], halfRootAngleCos = [];
    const q0 = new THREE.Vector4(), q1 = new THREE.Vector4();
    const rand = mulberry32((SEED ^ 0x9e3779b9) >>> 0);

    for (let i = 0; i < count; i++) {{
      const x = rand() * w - w / 2;
      const z = rand() * w - w / 2;
      offsets.push(x, getYPosition(x, z), z);

      let angle = Math.PI - rand() * (2 * Math.PI);
      halfRootAngleSin.push(Math.sin(0.5 * angle));
      halfRootAngleCos.push(Math.cos(0.5 * angle));
      q0.set(0, Math.sin(angle / 2), 0, Math.cos(angle / 2)).normalize();

      angle = rand() * 0.5 - 0.25;
      q1.set(Math.sin(angle / 2), 0, 0, Math.cos(angle / 2)).normalize();
      mulQuat(q0, q1);

      angle = rand() * 0.5 - 0.25;
      q1.set(0, 0, Math.sin(angle / 2), Math.cos(angle / 2)).normalize();
      mulQuat(q0, q1);

      orientations.push(q0.x, q0.y, q0.z, q0.w);
      stretches.push(i < count / 3 ? rand() * 1.8 : rand());
    }}

    const base = new THREE.PlaneGeometry(bW, bH, 1, joints).translate(0, bH / 2, 0);
    const geo = new THREE.InstancedBufferGeometry();
    geo.index = base.index;
    geo.setAttribute('position', base.attributes.position);
    geo.setAttribute('uv', base.attributes.uv);
    geo.setAttribute('offset', new THREE.InstancedBufferAttribute(new Float32Array(offsets), 3));
    geo.setAttribute('orientation', new THREE.InstancedBufferAttribute(new Float32Array(orientations), 4));
    geo.setAttribute('stretch', new THREE.InstancedBufferAttribute(new Float32Array(stretches), 1));
    geo.setAttribute('halfRootAngleSin', new THREE.InstancedBufferAttribute(new Float32Array(halfRootAngleSin), 1));
    geo.setAttribute('halfRootAngleCos', new THREE.InstancedBufferAttribute(new Float32Array(halfRootAngleCos), 1));
    geo.instanceCount = count;
    base.dispose();
    return geo;
  }}

  function mulQuat(a, b) {{
    const ax = a.x, ay = a.y, az = a.z, aw = a.w;
    const bx = b.x, by = b.y, bz = b.z, bw = b.w;
    a.set(
      ax * bw + aw * bx + ay * bz - az * by,
      ay * bw + aw * by + az * bx - ax * bz,
      az * bw + aw * bz + ax * by - ay * bx,
      aw * bw - ax * bx - ay * by - az * bz
    );
  }}

  const grassMesh = new THREE.Mesh(generateField(instances, width), grassMaterial);
  grassMesh.frustumCulled = false;
  scene.add(grassMesh);

  const gGeo = new THREE.PlaneGeometry(width, width, 32, 32);
  gGeo.rotateX(-Math.PI / 2);
  const gp = gGeo.attributes.position;
  for (let i = 0; i < gp.count; i++) gp.setY(i, getYPosition(gp.getX(i), gp.getZ(i)));
  gGeo.computeVertexNormals();
  const ground = new THREE.Mesh(gGeo, new THREE.MeshStandardMaterial({{
    color: C.bottomColor, roughness: 1,
  }}));
  ground.receiveShadow = true;
  scene.add(ground);

  const mouseTarget = new THREE.Vector2(1e6, 1e6);

  function setSun(elevationDeg, azimuthDeg) {{
    sun.setFromSphericalCoords(
      1,
      THREE.MathUtils.degToRad(90 - elevationDeg),
      THREE.MathUtils.degToRad(azimuthDeg)
    );
    skyUniforms.uSunDir.value.copy(sun);
    dirLight.position.copy(sun).multiplyScalar(50);
  }}

  function applyLook(L) {{
    if (L.tipColor) grassUniforms.tipColor.value.set(L.tipColor);
    if (L.bottomColor) {{
      grassUniforms.bottomColor.value.set(L.bottomColor);
      ground.material.color.set(L.bottomColor);
    }}
    if (L.grade) grassUniforms.uGrade.value.set(L.grade);
    if (L.skyTop) skyUniforms.uTop.value.set(L.skyTop).convertSRGBToLinear();
    if (L.skyHorizon) {{
      skyUniforms.uHorizon.value.set(L.skyHorizon).convertSRGBToLinear();
      if (scene.fog) scene.fog.color.set(L.skyHorizon);
    }}
    if (L.cloudColor) skyUniforms.uCloudColor.value.set(L.cloudColor).convertSRGBToLinear();
    if (L.cloudCover !== undefined) skyUniforms.uCloudCover.value = L.cloudCover;
    if (L.cloudSpeed !== undefined) skyUniforms.uCloudSpeed.value = L.cloudSpeed;
    if (L.sunColor) skyUniforms.uSunColor.value.set(L.sunColor).convertSRGBToLinear();
    if (L.hemiSky) hemi.color.set(L.hemiSky);
    if (L.hemiGround) hemi.groundColor.set(L.hemiGround);
    if (L.hemiIntensity !== undefined) hemi.intensity = L.hemiIntensity;
    if (L.dirColor) dirLight.color.set(L.dirColor);
    if (L.dirIntensity !== undefined) dirLight.intensity = L.dirIntensity;
    if (L.sunElevation !== undefined && L.sunAzimuth !== undefined) {{
      setSun(L.sunElevation, L.sunAzimuth);
    }}
  }}

  return {{
    grassMesh, ground, sky, grassUniforms, skyUniforms, dirLight, hemi,
    sunDir: sun, getYPosition, config: C, setSun, applyLook,
    setMouseTarget(x, z) {{ mouseTarget.set(x, z); }},
    clearMouse() {{ mouseTarget.set(1e6, 1e6); }},
    update(t) {{
      grassUniforms.time.value = (t / 4) * windSpeed;
      skyUniforms.uTime.value = t;
      grassUniforms.uMouse.value.lerp(mouseTarget, 0.12);
    }},
    dispose() {{
      grassMesh.geometry.dispose(); grassMaterial.dispose();
      ground.geometry.dispose(); ground.material.dispose();
      if (sky) {{ sky.geometry.dispose(); sky.material.dispose(); }}
    }},
  }};
}}
'''

with open(OUT, "w") as f:
    f.write(module)
print(f"{os.path.getsize(OUT)/1024:.0f} KB  -> website/assets/js/grass.js")
