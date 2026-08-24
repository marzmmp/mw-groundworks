/* ============================================================================
   Live day cycle for the hero.

   The look isn't picked from a clock — it's driven by where the sun actually
   is over Jefferson County right now. Sun elevation is computed from the
   visitor's local date/time with a standard solar-position algorithm, so the
   scene shifts with the seasons on its own: golden hour lands near 4:45pm in
   December and near 8:15pm in June, without anything being hard-coded.

   Elevation also drives how dark the copy scrim needs to be, which is the
   detail that keeps the headline readable at noon as well as at midnight.
   ========================================================================== */

const RAD = Math.PI / 180;

/**
 * Solar elevation + azimuth for a date at a lat/lon.
 * Simplified NOAA solar position — accurate to a fraction of a degree, which
 * is far more than a sky gradient needs.
 * @returns {{elevation:number, azimuth:number}} degrees; azimuth from true north
 */
export function sunPosition(date, latDeg, lonDeg) {
  const start = Date.UTC(date.getUTCFullYear(), 0, 0);
  const dayMs = 86400000;
  const doy = Math.floor((Date.UTC(
    date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()) - start) / dayMs);

  const utcHours = date.getUTCHours()
    + date.getUTCMinutes() / 60
    + date.getUTCSeconds() / 3600;

  // fractional year (radians)
  const g = (2 * Math.PI / 365) * (doy - 1 + (utcHours - 12) / 24);

  // equation of time (minutes)
  const eqTime = 229.18 * (0.000075
    + 0.001868 * Math.cos(g) - 0.032077 * Math.sin(g)
    - 0.014615 * Math.cos(2 * g) - 0.040849 * Math.sin(2 * g));

  // solar declination (radians)
  const decl = 0.006918
    - 0.399912 * Math.cos(g) + 0.070257 * Math.sin(g)
    - 0.006758 * Math.cos(2 * g) + 0.000907 * Math.sin(2 * g)
    - 0.002697 * Math.cos(3 * g) + 0.00148 * Math.sin(3 * g);

  const trueSolarMin = utcHours * 60 + eqTime + 4 * lonDeg;
  let hourAngle = trueSolarMin / 4 - 180;                 // degrees
  while (hourAngle < -180) hourAngle += 360;
  while (hourAngle > 180) hourAngle -= 360;

  const lat = latDeg * RAD;
  const ha = hourAngle * RAD;
  const cosZen = Math.sin(lat) * Math.sin(decl)
    + Math.cos(lat) * Math.cos(decl) * Math.cos(ha);
  const zenith = Math.acos(Math.max(-1, Math.min(1, cosZen)));
  const elevation = 90 - zenith / RAD;

  let az = Math.acos(Math.max(-1, Math.min(1,
    (Math.sin(lat) * Math.cos(zenith) - Math.sin(decl))
    / (Math.cos(lat) * Math.sin(zenith)))) ) / RAD;
  az = hourAngle > 0 ? (360 - az) % 360 : az;             // afternoon → west

  return { elevation, azimuth: az };
}

/* ---------- looks, keyed by sun elevation (degrees) --------------------- */
// Each stop is a full grass/sky look. Everything between two stops is
// interpolated, so the transition is continuous rather than three snapping
// states. `scrim` is how hard the hero overlay has to work to keep the
// headline legible against that sky.
const STOPS = [
  // tipColor and bottomColor are the reference grass and never change. Time of
  // day is carried by `grade` (a final multiplier on the blade colour), the sky,
  // the clouds and the three lights -- which is how real light works, and which
  // keeps the field the same field from midnight to noon. The midday stop is
  // exactly the `reference` preset, so at noon the cycle resolves to the spec.
  // Exposures are the reference 0.58 at midday, lifted toward night in the same
  // proportion the originals used.

  { el: -18, name: 'night', scrim: 0.36,
    tipColor: '#00994d', bottomColor: '#001a0d', grade: '#2F3D57',
    skyTop: '#03060A', skyHorizon: '#0A1119',
    cloudColor: '#141C24', cloudCover: 0.2, cloudSpeed: 0.5,
    sunColor: '#2A3550', hemiSky: '#131C28', hemiGround: '#070C06',
    hemiIntensity: 0.32, dirColor: '#5A6D8C', dirIntensity: 0.45,
    keyColor: 0xaebbd6, keyIntensity: 0.55, fillIntensity: 0.55, exposure: 0.71 },

  { el: -6, name: 'twilight', scrim: 0.4,
    tipColor: '#00994d', bottomColor: '#001a0d', grade: '#47536F',
    skyTop: '#050A0C', skyHorizon: '#1E2233',
    cloudColor: '#22283A', cloudCover: 0.24, cloudSpeed: 0.55,
    sunColor: '#6B5F6E', hemiSky: '#1E2432', hemiGround: '#0A1008',
    hemiIntensity: 0.4, dirColor: '#8A87A0', dirIntensity: 0.7,
    keyColor: 0xc2c0d4, keyIntensity: 0.8, fillIntensity: 0.9, exposure: 0.675 },

  { el: 0, name: 'dusk', scrim: 0.44,
    tipColor: '#00994d', bottomColor: '#001a0d', grade: '#8A6E52',
    skyTop: '#060907', skyHorizon: '#3A2A1C',
    cloudColor: '#3A2E20', cloudCover: 0.26, cloudSpeed: 0.6,
    sunColor: '#8A6238', hemiSky: '#2A2A1C', hemiGround: '#0C120A',
    hemiIntensity: 0.45, dirColor: '#B08C5E', dirIntensity: 0.9,
    keyColor: 0xffe0b4, keyIntensity: 1.1, fillIntensity: 1.5, exposure: 0.639 },

  { el: 8, name: 'goldenHour', scrim: 0.44,
    tipColor: '#00994d', bottomColor: '#001a0d', grade: '#D6A76B',
    skyTop: '#070B08', skyHorizon: '#4E3A24',
    cloudColor: '#6B563C', cloudCover: 0.3, cloudSpeed: 0.8,
    sunColor: '#C08A4A', hemiSky: '#4A3E28', hemiGround: '#1A2412',
    hemiIntensity: 0.55, dirColor: '#E8C48E', dirIntensity: 1.25,
    keyColor: 0xfff1d4, keyIntensity: 1.35, fillIntensity: 1.75, exposure: 0.621 },

  { el: 22, name: 'morning', scrim: 0.46,
    tipColor: '#00994d', bottomColor: '#001a0d', grade: '#F0EEE0',
    skyTop: '#4E7CB8', skyHorizon: '#9FC2E0',
    cloudColor: '#F2F0E8', cloudCover: 0.42, cloudSpeed: 0.9,
    sunColor: '#FFEBC8', hemiSky: '#9CBAE4', hemiGround: '#2E4A26',
    hemiIntensity: 0.8, dirColor: '#FFF2DE', dirIntensity: 1.45,
    keyColor: 0xfff6e6, keyIntensity: 1.2, fillIntensity: 1.5, exposure: 0.592 },

  { el: 55, name: 'daylight', scrim: 0.52,
    tipColor: '#00994d', bottomColor: '#001a0d', grade: '#FFFFFF',
    skyTop: '#b3d1ff', skyHorizon: '#b3daff',
    cloudColor: '#FFFFFF', cloudCover: 0.5, cloudSpeed: 1.0,
    sunColor: '#fff4d6', hemiSky: '#bcd4ff', hemiGround: '#33502a',
    hemiIntensity: 0.9, dirColor: '#fff6e0', dirIntensity: 1.6,
    keyColor: 0xfffaf0, keyIntensity: 1.15, fillIntensity: 1.4, exposure: 0.58 },

];

const NUMERIC = ['scrim', 'cloudCover', 'cloudSpeed', 'hemiIntensity',
  'dirIntensity', 'keyIntensity', 'fillIntensity', 'exposure'];
const COLOURS = ['tipColor', 'bottomColor', 'grade', 'skyTop', 'skyHorizon',
  'cloudColor', 'sunColor', 'hemiSky', 'hemiGround', 'dirColor'];

function hexToRgb(h) {
  const n = parseInt(h.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map((v) =>
    Math.round(Math.max(0, Math.min(255, v))).toString(16).padStart(2, '0')).join('');
}
function mixHex(a, b, t) {
  const A = hexToRgb(a), B = hexToRgb(b);
  // mix in linear-ish space so dark→bright ramps don't go muddy in the middle
  return rgbToHex(
    Math.sqrt(A[0] ** 2 * (1 - t) + B[0] ** 2 * t),
    Math.sqrt(A[1] ** 2 * (1 - t) + B[1] ** 2 * t),
    Math.sqrt(A[2] ** 2 * (1 - t) + B[2] ** 2 * t)
  );
}
const smooth = (t) => t * t * (3 - 2 * t);

/** Interpolated look for a given sun elevation. */
export function lookForElevation(elevation) {
  if (elevation <= STOPS[0].el) return { ...STOPS[0] };
  if (elevation >= STOPS[STOPS.length - 1].el) return { ...STOPS[STOPS.length - 1] };

  let i = 0;
  while (i < STOPS.length - 2 && elevation > STOPS[i + 1].el) i++;
  const a = STOPS[i], b = STOPS[i + 1];
  const t = smooth((elevation - a.el) / (b.el - a.el));

  const out = { name: t < 0.5 ? a.name : b.name, blend: t, from: a.name, to: b.name };
  NUMERIC.forEach((k) => { out[k] = a[k] + (b[k] - a[k]) * t; });
  COLOURS.forEach((k) => { out[k] = mixHex(a[k], b[k], t); });
  return out;
}

/**
 * The look for a moment in time at a place. Defaults to Jefferson County, MO
 * so the seasons behave correctly for the business's own latitude.
 */
export function lookForTime(date = new Date(), lat = 38.2306, lon = -90.5626) {
  const sun = sunPosition(date, lat, lon);
  const look = lookForElevation(sun.elevation);
  look.sunElevation = sun.elevation;
  look.sunAzimuth = sun.azimuth;
  return look;
}

export const SITE_TZ = 'America/Chicago';

/** Minutes that `tz` is ahead of UTC at this instant (handles DST). */
export function tzOffsetMinutes(date = new Date(), tz = SITE_TZ) {
  try {
    const parts = Object.fromEntries(
      new Intl.DateTimeFormat('en-US', {
        timeZone: tz, hour12: false, year: 'numeric', month: '2-digit',
        day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit',
      }).formatToParts(date).map((p) => [p.type, p.value]));
    const asUTC = Date.UTC(+parts.year, +parts.month - 1, +parts.day,
      +parts.hour % 24, +parts.minute, +parts.second);
    return Math.round((asUTC - date.getTime()) / 60000);
  } catch (e) {
    return -date.getTimezoneOffset();     // fall back to the device
  }
}

/** Wall-clock hour (decimal) in Jefferson County right now. */
export function siteHour(date = new Date(), tz = SITE_TZ) {
  const off = tzOffsetMinutes(date, tz);
  const local = new Date(date.getTime() + off * 60000);
  return local.getUTCHours() + local.getUTCMinutes() / 60;
}

/**
 * The UTC instant corresponding to today at `hour` **in Jefferson County**.
 * The scrubber means "what does the field look like at 7pm in Missouri",
 * not "7pm wherever the visitor happens to be sitting".
 */
export function dateAtHour(hour, base = new Date(), tz = SITE_TZ) {
  const off = tzOffsetMinutes(base, tz);
  const local = new Date(base.getTime() + off * 60000);
  const wanted = Date.UTC(
    local.getUTCFullYear(), local.getUTCMonth(), local.getUTCDate(),
    Math.floor(hour), Math.round((hour % 1) * 60), 0);
  return new Date(wanted - off * 60000);
}

/** Plain-language label, for the preview scrubber and a11y announcements. */
export function describe(look) {
  const el = look.sunElevation;
  if (el === undefined) return look.name;
  if (el < -12) return 'Night';
  if (el < -3) return 'Twilight';
  if (el < 3) return 'Sunrise / sunset';
  if (el < 12) return 'Golden hour';
  if (el < 30) return 'Morning / late afternoon';
  return 'Midday';
}
