/* ============================================================================
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
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

class SimplexNoise {
  constructor(r = Math.random) {
    this.perm = new Uint8Array(512); this.permMod12 = new Uint8Array(512)
    const p = new Uint8Array(256); for (let i = 0; i < 256; i++) p[i] = i
    for (let i = 255; i > 0; i--) { const n = Math.floor((i + 1) * r()); const q = p[i]; p[i] = p[n]; p[n] = q }
    for (let i = 0; i < 512; i++) { this.perm[i] = p[i & 255]; this.permMod12[i] = this.perm[i] % 12 }
    this.grad3 = new Float32Array([1,1,0,-1,1,0,1,-1,0,-1,-1,0,1,0,1,-1,0,1,1,0,-1,-1,0,-1,0,1,1,0,-1,1,0,1,-1,0,-1,-1])
  }
  noise2D(xin, yin) {
    const grad3 = this.grad3, perm = this.perm, permMod12 = this.permMod12
    const F2 = 0.5 * (Math.sqrt(3) - 1), G2 = (3 - Math.sqrt(3)) / 6
    let n0 = 0, n1 = 0, n2 = 0
    const s = (xin + yin) * F2
    const i = Math.floor(xin + s), j = Math.floor(yin + s)
    const t = (i + j) * G2
    const x0 = xin - (i - t), y0 = yin - (j - t)
    let i1, j1; if (x0 > y0) { i1 = 1; j1 = 0 } else { i1 = 0; j1 = 1 }
    const x1 = x0 - i1 + G2, y1 = y0 - j1 + G2
    const x2 = x0 - 1 + 2 * G2, y2 = y0 - 1 + 2 * G2
    const ii = i & 255, jj = j & 255
    let t0 = 0.5 - x0 * x0 - y0 * y0
    if (t0 >= 0) { const gi0 = permMod12[ii + perm[jj]] * 3; t0 *= t0; n0 = t0 * t0 * (grad3[gi0] * x0 + grad3[gi0 + 1] * y0) }
    let t1 = 0.5 - x1 * x1 - y1 * y1
    if (t1 >= 0) { const gi1 = permMod12[ii + i1 + perm[jj + j1]] * 3; t1 *= t1; n1 = t1 * t1 * (grad3[gi1] * x1 + grad3[gi1 + 1] * y1) }
    let t2 = 0.5 - x2 * x2 - y2 * y2
    if (t2 >= 0) { const gi2 = permMod12[ii + 1 + perm[jj + 1]] * 3; t2 *= t2; n2 = t2 * t2 * (grad3[gi2] * x2 + grad3[gi2 + 1] * y2) }
    return 70 * (n0 + n1 + n2)
  }
}

const bW = 0.032, bH = 1, joints = 5;

const SIMPLEX_GLSL = `
vec3 mod289(vec3 x){ return x - floor(x*(1.0/289.0))*289.0; }
vec2 mod289(vec2 x){ return x - floor(x*(1.0/289.0))*289.0; }
vec3 permute(vec3 x){ return mod289(((x*34.0)+1.0)*x); }
float snoise(vec2 v){
  const vec4 C = vec4(0.211324865405187, 0.366025403784439, -0.577350269189626, 0.024390243902439);
  vec2 i  = floor(v + dot(v, C.yy));
  vec2 x0 = v -   i + dot(i, C.xx);
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz; x12.xy -= i1;
  i = mod289(i);
  vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
  vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
  m = m*m; m = m*m;
  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
  vec3 g;
  g.x  = a0.x  * x0.x  + h.x  * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}
`;

/* ---------- brand presets ------------------------------------------------ */
export const PRESETS = {
  // The reference scene's own constants, verbatim from the grass-shader spec.
  // This is the look the field was actually designed around: saturated green
  // tips over near-black roots, under a pale blue sky, at exposure 0.58 with a
  // neutral grade. Every other preset here is a retint of it.
  reference: {
    tipColor: '#00994d', bottomColor: '#001a0d',
    skyTop: '#b3d1ff', skyHorizon: '#b3daff',
    cloudColor: '#ffffff', cloudCover: 0.5, cloudSpeed: 1.0,
    sunElevation: 34, sunAzimuth: 150, sunColor: '#fff4d6',
    hemiSky: '#bcd4ff', hemiGround: '#33502a', hemiIntensity: 0.9,
    dirColor: '#fff6e0', dirIntensity: 1.6,
    grade: '#ffffff',
    groundColor: '#3d5a2b',
    exposure: 0.58,
    fogDensity: 0.0072,
  },
  // Low warm sun. Dark at the zenith so headline text stays readable, warm at
  // the horizon so the amber CTA colour is motivated by the light itself.
  goldenHour: {
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
  },
  // The original bright-daylight look, retinted slightly toward the brand moss.
  daylight: {
    tipColor: '#7FA83C', bottomColor: '#16290F',
    skyTop: '#8FB6E8', skyHorizon: '#BBD9F2',
    cloudColor: '#FFFFFF', cloudCover: 0.5, cloudSpeed: 1.0,
    sunElevation: 34, sunAzimuth: 150, sunColor: '#FFF4D6',
    hemiSky: '#BCD4FF', hemiGround: '#33502A', hemiIntensity: 0.9,
    dirColor: '#FFF6E0', dirIntensity: 1.6,
    grade: '#E4EAD6',
  },
  // Near-black sky, deep moss grass — closest to the original dark hero.
  dusk: {
    // Almost mono. The darkest option — closest to the original hero.
    tipColor: '#4E6B26', bottomColor: '#080F06',
    skyTop: '#060907', skyHorizon: '#1C2619',
    cloudColor: '#28331F', cloudCover: 0.26, cloudSpeed: 0.6,
    sunElevation: 3, sunAzimuth: 152, sunColor: '#6B5A3A',
    hemiSky: '#232C1C', hemiGround: '#0C120A', hemiIntensity: 0.45,
    dirColor: '#9C8C64', dirIntensity: 0.9,
    grade: '#6E7D55',
  },
};

/**
 * Build the grass field, ground and sky dome into `scene`.
 * Returns handles plus an `update(elapsedSeconds)` to drive the wind.
 */
export function createGrassField(scene, opts = {}) {
  const {
    preset = 'goldenHour',
    instances = 60000,
    width = 85,
    windSpeed = 1.0,
    mouseRadius = 8.0,
    mouseStrength = 1.4,
    seed = 2241217164,
    sky: wantSky = true,
    fog = true,
  } = opts;

  const C = { ...PRESETS[preset] || PRESETS.goldenHour, ...(opts.override || {}) };
  const SEED = seed >>> 0;
  const simplex = new SimplexNoise(mulberry32(SEED));

  // their exact three-octave terrain
  function getYPosition(x, z) {
    let y = 2 * simplex.noise2D(x / 50, z / 50);
    y += 4 * simplex.noise2D(x / 100, z / 100);
    y += 0.2 * simplex.noise2D(x / 10, z / 10);
    return y;
  }

  const sun = new THREE.Vector3().setFromSphericalCoords(
    1,
    THREE.MathUtils.degToRad(90 - C.sunElevation),
    THREE.MathUtils.degToRad(C.sunAzimuth)
  );

  // The reference uses exponential haze so the far grass melts into the sky
  // with no visible field edge. Linear Fog is kept for the retint presets that
  // were tuned against it.
  if (fog) {
    scene.fog = C.fogDensity
      ? new THREE.FogExp2(new THREE.Color(C.skyHorizon), C.fogDensity)
      : new THREE.Fog(new THREE.Color(C.skyHorizon), 40, 190);
  }

  /* ---------- sky dome ---------- */
  const skyUniforms = {
    uTop: { value: new THREE.Color(C.skyTop).convertSRGBToLinear() },
    uHorizon: { value: new THREE.Color(C.skyHorizon).convertSRGBToLinear() },
    uSunColor: { value: new THREE.Color(C.sunColor).convertSRGBToLinear() },
    uSunDir: { value: sun.clone() },
    uTime: { value: 0 },
    uCloudColor: { value: new THREE.Color(C.cloudColor).convertSRGBToLinear() },
    uCloudCover: { value: C.cloudCover },
    uCloudSpeed: { value: C.cloudSpeed },
  };
  let sky = null;
  if (wantSky) {
    sky = new THREE.Mesh(
      new THREE.SphereGeometry(1200, 48, 32),
      new THREE.ShaderMaterial({
        side: THREE.BackSide, depthWrite: false, fog: false, toneMapped: false,
        uniforms: skyUniforms,
        vertexShader: `varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
        fragmentShader: `
      uniform vec3 uTop; uniform vec3 uHorizon; uniform vec3 uSunColor; uniform vec3 uSunDir;
      uniform float uTime; uniform vec3 uCloudColor; uniform float uCloudCover; uniform float uCloudSpeed;
      varying vec3 vDir;
      float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }
      float vnoise(vec2 p){
        vec2 i = floor(p), f = fract(p);
        vec2 u = f * f * (3.0 - 2.0 * f);
        float a = hash(i), b = hash(i + vec2(1.0, 0.0)), c = hash(i + vec2(0.0, 1.0)), d = hash(i + vec2(1.0, 1.0));
        return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
      }
      float fbm(vec2 p){
        float v = 0.0, a = 0.5;
        for(int i = 0; i < 5; i++){ v += a * vnoise(p); p = p * 2.02 + 7.3; a *= 0.5; }
        return v;
      }
      void main(){
        vec3 d = normalize(vDir);
        float h = clamp(d.y, 0.0, 1.0);
        vec3 col = mix(uHorizon, uTop, pow(h, 0.5));
        float sd = max(dot(d, normalize(uSunDir)), 0.0);
        col += uSunColor * pow(sd, 400.0) * 3.0;    // sun disc
        col += uSunColor * 0.20 * pow(sd, 6.0);     // soft halo

        // --- drifting FBM clouds on the dome ---
        // divide by (d.y + const), NOT max(d.y, const): the additive term keeps the
        // projection finite and smooth right down to the horizon, so there is no frozen
        // band and no vertical "drip" streaks.
        // horizonFade ramps clouds in across almost the WHOLE dome (horizon -> high sky)
        // rather than snapping them on over a narrow 0.05..0.4 band: a narrow band puts a
        // hard lower edge on the faint cloud haze that reads as a horizontal seam splitting
        // the sky. A wide, gentle ramp has no perceptible edge.
        float horizonFade = smoothstep(-0.05, 0.75, d.y);
        vec2 cp = (d.xz / (d.y + 0.35)) * 1.6;
        cp += vec2(uTime * 0.02 * uCloudSpeed, uTime * 0.006 * uCloudSpeed);
        float n = fbm(cp);
        float cover = mix(0.85, 0.20, clamp(uCloudCover, 0.0, 1.0));   // more cover -> lower threshold
        float ca = smoothstep(cover, cover + 0.28, n) * horizonFade;
        // faint sun-lit rim on the cloud tops
        vec3 cloudCol = mix(uCloudColor, uCloudColor + uSunColor * 0.4, smoothstep(0.4, 0.9, sd));
        col = mix(col, cloudCol, ca * 0.92);

        // dither: break up 8-bit banding on the smooth blue ramp so the gradient
        // reads as one continuous sky instead of splitting into flat stepped bands
        float dither = (hash(gl_FragCoord.xy) - 0.5) / 255.0;
        col += dither;

        gl_FragColor = vec4(col, 1.0);
        #include <colorspace_fragment>
      }`,
      })
    );
    sky.frustumCulled = false;
    scene.add(sky);
  }

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
  function texUrl(name, explicit) {
    if (explicit) return explicit;
    try { return new URL('../img/' + name, import.meta.url).href; }
    catch (e) { return 'assets/img/' + name; }
  }
  const tex = opts.textures || (typeof window !== 'undefined' && window.__MW_GRASS_TEX) || {};
  const loader = new THREE.TextureLoader();
  const grassTexture = loader.load(texUrl('blade_diffuse.jpg', tex.diffuse));
  grassTexture.colorSpace = THREE.SRGBColorSpace;
  const alphaMap = loader.load(texUrl('blade_alpha.jpg', tex.alpha));

  const grassUniforms = {
    map: { value: grassTexture },
    alphaMap: { value: alphaMap },
    time: { value: 0 },
    bladeHeight: { value: bH },
    tipColor: { value: new THREE.Color(C.tipColor) },
    bottomColor: { value: new THREE.Color(C.bottomColor) },
    uMouse: { value: new THREE.Vector2(1e6, 1e6) },
    uMouseRadius: { value: mouseRadius },
    uMouseStrength: { value: mouseStrength },
    uGrade: { value: new THREE.Color(C.grade || '#ffffff') },
  };

  const grassMaterial = new THREE.ShaderMaterial({
    side: THREE.DoubleSide,
    uniforms: grassUniforms,
    vertexShader: `
    attribute vec3 offset;
    attribute vec4 orientation;
    attribute float halfRootAngleSin;
    attribute float halfRootAngleCos;
    attribute float stretch;
    uniform float time;
    uniform float bladeHeight;
    uniform vec2 uMouse;
    uniform float uMouseRadius;
    uniform float uMouseStrength;
    varying vec2 vUv;
    varying float frc;
    ${SIMPLEX_GLSL}
    // rotate a vector by a quaternion
    vec3 rotateVectorByQuaternion(vec3 v, vec4 q){
      return 2.0 * cross(q.xyz, v * q.w + cross(q.xyz, v)) + v;
    }
    // spherical linear interpolation between two quaternions
    vec4 slerp(vec4 v0, vec4 v1, float t){
      normalize(v0); normalize(v1);
      float d = dot(v0, v1);
      if (d < 0.0) { v1 = -v1; d = -d; }
      const float THRESHOLD = 0.9995;
      if (d > THRESHOLD) return normalize(v0 + t * (v1 - v0));
      float theta_0 = acos(d);
      float theta = theta_0 * t;
      float sin_theta = sin(theta);
      float sin_theta_0 = sin(theta_0);
      float s0 = cos(theta) - d * sin_theta / sin_theta_0;
      float s1 = sin_theta / sin_theta_0;
      return (s0 * v0) + (s1 * v1);
    }
    void main() {
      // relative position of vertex along the blade (0 root -> 1 tip)
      frc = position.y / float(bladeHeight);
      // scrolling wind noise
      float noise = 1.0 - (snoise(vec2((time - offset.x / 50.0), (time - offset.z / 50.0))));
      // orientation slerps from the root-yaw quaternion to the blade's own
      vec4 direction = vec4(0.0, halfRootAngleSin, 0.0, halfRootAngleCos);
      direction = slerp(direction, orientation, frc);
      vec3 vPosition = vec3(position.x, position.y + position.y * stretch, position.z);
      vPosition = rotateVectorByQuaternion(vPosition, direction);
      // apply the wind bend (tips bend more)
      float halfAngle = noise * 0.15;
      vPosition = rotateVectorByQuaternion(vPosition,
        normalize(vec4(sin(halfAngle), 0.0, -sin(halfAngle), cos(halfAngle))));
      // --- added: cursor breeze — blades near the mouse bow away from it (tips most) ---
      vec2 toBlade = offset.xz - uMouse;
      float dist = length(toBlade);
      float infl = smoothstep(uMouseRadius, 0.0, dist) * uMouseStrength;
      vec2 pushDir = dist > 0.0001 ? toBlade / dist : vec2(1.0, 0.0);
      float bend = infl * frc;
      vPosition.x += pushDir.x * bend;
      vPosition.z += pushDir.y * bend;
      vPosition.y -= bend * bend * 0.35;
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(offset + vPosition, 1.0);
    }`,
    // ADDED (not in the reference shader): the blade tips are dominated by the
    // diffuse photo texture, so tipColor alone cannot pull the field toward the
    // brand moss or match it to a darker sky. uGrade multiplies the final colour.
    fragmentShader: `
    uniform vec3 uGrade;
    uniform sampler2D map;
    uniform sampler2D alphaMap;
    uniform vec3 tipColor;
    uniform vec3 bottomColor;
    varying vec2 vUv;
    varying float frc;
    void main() {
      float alpha = texture2D(alphaMap, vUv).r;
      if (alpha < 0.15) discard;
      vec4 col = vec4(texture2D(map, vUv));
      col = mix(vec4(tipColor, 1.0), col, frc);
      col = mix(vec4(bottomColor, 1.0), col, frc);
      gl_FragColor = vec4(col.rgb * uGrade, col.a);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }`,
  });

  /* ---------- instanced field ---------- */
  function generateField(count, w) {
    const offsets = [], orientations = [], stretches = [];
    const halfRootAngleSin = [], halfRootAngleCos = [];
    const q0 = new THREE.Vector4(), q1 = new THREE.Vector4();
    const rand = mulberry32((SEED ^ 0x9e3779b9) >>> 0);

    for (let i = 0; i < count; i++) {
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
    }

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
  }

  function mulQuat(a, b) {
    const ax = a.x, ay = a.y, az = a.z, aw = a.w;
    const bx = b.x, by = b.y, bz = b.z, bw = b.w;
    a.set(
      ax * bw + aw * bx + ay * bz - az * by,
      ay * bw + aw * by + az * bx - ax * bz,
      az * bw + aw * bz + ax * by - ay * bx,
      aw * bw - ax * bx - ay * by - az * bz
    );
  }

  const grassMesh = new THREE.Mesh(generateField(instances, width), grassMaterial);
  grassMesh.frustumCulled = false;
  scene.add(grassMesh);

  const gGeo = new THREE.PlaneGeometry(width, width, 32, 32);
  gGeo.rotateX(-Math.PI / 2);
  const gp = gGeo.attributes.position;
  for (let i = 0; i < gp.count; i++) gp.setY(i, getYPosition(gp.getX(i), gp.getZ(i)));
  gGeo.computeVertexNormals();
  const ground = new THREE.Mesh(gGeo, new THREE.MeshStandardMaterial({
    color: C.groundColor || C.bottomColor, roughness: 1,
  }));
  ground.receiveShadow = true;
  scene.add(ground);

  const mouseTarget = new THREE.Vector2(1e6, 1e6);

  function setSun(elevationDeg, azimuthDeg) {
    sun.setFromSphericalCoords(
      1,
      THREE.MathUtils.degToRad(90 - elevationDeg),
      THREE.MathUtils.degToRad(azimuthDeg)
    );
    skyUniforms.uSunDir.value.copy(sun);
    dirLight.position.copy(sun).multiplyScalar(50);
  }

  function applyLook(L) {
    if (L.tipColor) grassUniforms.tipColor.value.set(L.tipColor);
    if (L.bottomColor) {
      grassUniforms.bottomColor.value.set(L.bottomColor);
      ground.material.color.set(L.bottomColor);
    }
    if (L.grade) grassUniforms.uGrade.value.set(L.grade);
    if (L.skyTop) skyUniforms.uTop.value.set(L.skyTop).convertSRGBToLinear();
    if (L.skyHorizon) {
      skyUniforms.uHorizon.value.set(L.skyHorizon).convertSRGBToLinear();
      if (scene.fog) scene.fog.color.set(L.skyHorizon);
    }
    if (L.cloudColor) skyUniforms.uCloudColor.value.set(L.cloudColor).convertSRGBToLinear();
    if (L.cloudCover !== undefined) skyUniforms.uCloudCover.value = L.cloudCover;
    if (L.cloudSpeed !== undefined) skyUniforms.uCloudSpeed.value = L.cloudSpeed;
    if (L.sunColor) skyUniforms.uSunColor.value.set(L.sunColor).convertSRGBToLinear();
    if (L.hemiSky) hemi.color.set(L.hemiSky);
    if (L.hemiGround) hemi.groundColor.set(L.hemiGround);
    if (L.hemiIntensity !== undefined) hemi.intensity = L.hemiIntensity;
    if (L.dirColor) dirLight.color.set(L.dirColor);
    if (L.dirIntensity !== undefined) dirLight.intensity = L.dirIntensity;
    if (L.sunElevation !== undefined && L.sunAzimuth !== undefined) {
      setSun(L.sunElevation, L.sunAzimuth);
    }
  }

  return {
    grassMesh, ground, sky, grassUniforms, skyUniforms, dirLight, hemi,
    sunDir: sun, getYPosition, config: C, setSun, applyLook,
    setMouseTarget(x, z) { mouseTarget.set(x, z); },
    clearMouse() { mouseTarget.set(1e6, 1e6); },
    update(t) {
      grassUniforms.time.value = (t / 4) * windSpeed;
      skyUniforms.uTime.value = t;
      grassUniforms.uMouse.value.lerp(mouseTarget, 0.12);
    },
    dispose() {
      grassMesh.geometry.dispose(); grassMaterial.dispose();
      ground.geometry.dispose(); ground.material.dispose();
      if (sky) { sky.geometry.dispose(); sky.material.dispose(); }
    },
  };
}
