// ============================================================
// Unified platform compilers (frontend offline path)
// Reuses the same domain-detection + KIMIFY-layers engine that
// powers Pro Builder's auto-inference (kimifyInference.js), so the
// Generador's offline fallback applies the same prompt-engineering
// rules as the online backend path (mj81_compiler.py) instead of a
// trivial hardcoded template.
// ============================================================

import { inferFromSubject } from '@/lib/kimifyInference';

function layerStrings(subjectText, fields) {
  const kernelParts = [subjectText];
  if (fields.subjectDetails?.length) kernelParts.push(fields.subjectDetails.join(', '));
  if (fields.subjectModifiers?.length) kernelParts.push(fields.subjectModifiers.join(', '));

  const intentParts = [fields.styleIntent, fields.mood, fields.visualStyle, fields.eraPeriod].filter(Boolean);
  const mediumParts = [fields.cameraType, fields.lensType, fields.filmType, fields.renderingEngine].filter(Boolean);
  const illumParts = [fields.lightingType, fields.timeOfDay, fields.atmosphere, fields.weather].filter(Boolean);
  const formatParts = [fields.composition, fields.angle, fields.depthOfField, fields.colorGrading].filter(Boolean);

  return {
    kernel: kernelParts.filter(Boolean).join(', '),
    intent: intentParts.join(', '),
    medium: mediumParts.join(', '),
    illumination: illumParts.join(', '),
    format: formatParts.join(', '),
  };
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function compileMidjourney(layers, fields, params) {
  const content = [layers.kernel, layers.intent, layers.medium, layers.illumination, layers.format]
    .filter(Boolean)
    .join(', ');

  // Manual UI params only override the inferred domain values when the
  // user actually changed them from the platform-neutral defaults.
  const ar = params.ar && params.ar !== '1:1' ? params.ar : fields.aspectRatio;
  const stylize = params.s && params.s !== 100 ? params.s : fields.stylize;
  const chaos = params.c && params.c !== 0 ? params.c : fields.chaos;
  const weird = params.w || 0;
  const quality = params.q || 1;

  const suffix = [`--ar ${ar}`];
  if (stylize !== 100) suffix.push(`--s ${stylize}`);
  if (chaos !== 0) suffix.push(`--c ${chaos}`);
  if (weird !== 0) suffix.push(`--w ${weird}`);
  if (fields.raw) suffix.push('--raw');
  if (quality !== 1) suffix.push(`--q ${quality}`);
  suffix.push('--v 8.1');

  return `${content} ${suffix.join(' ')}`;
}

function compileDalle(layers) {
  const desc = layers.kernel;
  const article = /^[aeiou]/i.test(desc) ? 'an' : 'a';

  const sentences = [`Create an image of ${article} ${desc}.`];
  if (layers.intent) sentences.push(`${capitalize(layers.intent)}.`);
  if (layers.medium) sentences.push(`Captured with ${layers.medium}.`);
  if (layers.illumination) sentences.push(`${capitalize(layers.illumination)}.`);
  if (layers.format) sentences.push(`${capitalize(layers.format)}.`);
  sentences.push('Highly detailed, professional quality.');

  return sentences.join(' ');
}

function compileNanoBanana(layers) {
  const desc = layers.kernel;

  const parts = [`Transform into a cinematic scene: ${desc}.`];
  if (layers.intent) parts.push(`${capitalize(layers.intent)}.`);
  if (layers.medium) parts.push(`Shot using ${layers.medium}.`);
  if (layers.illumination) parts.push(`${capitalize(layers.illumination)} sets the atmosphere.`);
  if (layers.format) parts.push(`Strong ${layers.format} composition, striking environmental detail.`);

  return parts.join(' ');
}

export function compilePlatformPrompt(inputText, platform, params = {}) {
  const base = (inputText || '').trim();
  if (!base) return null;

  const { fields, meta } = inferFromSubject(base);
  const layers = layerStrings(base, fields);

  let positive;
  if (platform === 'midjourney_v8_1') {
    positive = compileMidjourney(layers, fields, params);
  } else if (platform === 'dalle_3') {
    positive = compileDalle(layers);
  } else {
    positive = compileNanoBanana(layers);
  }

  const negative =
    platform === 'midjourney_v8_1' && params.output_mode === 'prompt_plus_negative' ? fields.negative : '';

  const canvas = negative ? `POSITIVE PROMPT\n${positive}\n\nNEGATIVE PROMPT\n${negative}` : positive;

  return {
    status: 'DONE_WITH_PROMPT',
    positive_prompt: positive,
    negative_prompt: negative,
    canvas,
    file: null,
    platform,
    domain: meta,
  };
}
