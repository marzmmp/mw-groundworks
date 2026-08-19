/* ============================================================================
   The extruded M&W mark — shared by the hero scene and the video sting.
   Built from the same letterform outlines as the flat SVG logos.
   ========================================================================== */
import * as THREE from '../vendor/three.module.js';
import { SVGLoader } from '../vendor/SVGLoader.js';
import { MW_PATH } from './mw-path.js';

export const PAL = {
  ink: 0x070a08,
  bone: 0xf2ede1,
  moss: 0x7a9a3e,
  mossDark: 0x33461b,
  amber: 0xe8a33d,
};

export function pathToShapes(d) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg"><path d="${d}"/></svg>`;
  const data = new SVGLoader().parse(svg);
  const shapes = [];
  data.paths.forEach((p) => {
    SVGLoader.createShapes(p).forEach((s) => shapes.push(s));
  });
  return shapes;
}

/**
 * Returns { group, mark, bar, blade, box } with the mark centred on the origin.
 * `box` is the local bounding box so callers can sit it on a surface.
 */
export function buildMark(opts = {}) {
  const {
    depth = 26,
    faceColor = PAL.bone,
    sideColor = PAL.moss,
    barColor = PAL.moss,
    bladeColor = PAL.amber,
    castShadow = true,
    withBar = true,
    withBlade = true,
  } = opts;

  const group = new THREE.Group();

  const geo = new THREE.ExtrudeGeometry(pathToShapes(MW_PATH), {
    depth, bevelEnabled: true, bevelThickness: 2.2,
    bevelSize: 1.7, bevelSegments: 3, curveSegments: 8,
  });
  geo.computeBoundingBox();
  const bb = geo.boundingBox;
  geo.translate(-(bb.max.x + bb.min.x) / 2, -(bb.max.y + bb.min.y) / 2, -depth / 2);

  const mark = new THREE.Mesh(geo, [
    new THREE.MeshStandardMaterial({ color: faceColor, roughness: 0.46, metalness: 0.04 }),
    new THREE.MeshStandardMaterial({ color: sideColor, roughness: 0.42, metalness: 0.34 }),
  ]);
  mark.castShadow = castShadow;
  group.add(mark);

  const blade = new THREE.Mesh(
    new THREE.BoxGeometry(3.0, 148, 3.0),
    new THREE.MeshStandardMaterial({
      color: bladeColor, emissive: bladeColor, emissiveIntensity: 0.7,
      roughness: 0.3, metalness: 0.5,
    })
  );
  blade.position.set(26, 6, -30);
  blade.rotation.z = 0.24;
  blade.castShadow = castShadow;
  if (withBlade) group.add(blade);

  const bar = new THREE.Group();
  const barMat = new THREE.MeshStandardMaterial({
    color: barColor, roughness: 0.45, metalness: 0.3,
  });
  const plate = new THREE.Mesh(new THREE.BoxGeometry(196, 11, 20), barMat);
  plate.castShadow = castShadow;
  bar.add(plate);
  for (let i = 0; i < 7; i++) {
    const t = new THREE.Mesh(new THREE.CylinderGeometry(0, 11, 17, 4), barMat);
    t.position.set(-81 + i * 27, -13, 0);
    t.rotation.y = Math.PI / 4;
    t.castShadow = castShadow;
    bar.add(t);
  }
  bar.position.y = -54;
  if (withBar) group.add(bar);

  // local extents: mark cap ±~35, tooth tips down to ~-75
  const box = new THREE.Box3(
    new THREE.Vector3(-100, -76, -34),
    new THREE.Vector3(100, 38, 18)
  );

  return { group, mark, bar, blade, box };
}
