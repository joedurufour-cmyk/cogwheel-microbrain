// ============================================================
// KIMIFY Inference Engine
// Heuristic rules that read the free-text K (Kernel) subject and
// auto-populate I / M / I2 / F / Y using the curated token library,
// so the methodology's "golden rules" are actually applied instead
// of leaving every other layer empty.
// ============================================================

import { tokenLibrary } from '@/data/kimifyData';

function tokenValue(categoryId, tokenId) {
  const category = tokenLibrary.find((c) => c.id === categoryId);
  const token = category?.tokens.find((t) => t.id === tokenId);
  return token ? token.value : '';
}

function tokenValues(categoryId, tokenIds) {
  return tokenIds.map((id) => tokenValue(categoryId, id)).filter(Boolean);
}

const DOMAINS = [
  {
    id: 'superhero_action',
    label: 'Acción heroica / superhéroe',
    keywords: ['supergirl', 'superman', 'superhero', 'super hero', 'heroina', 'heroína', 'heroe', 'héroe',
      'batman', 'wonder woman', 'muscular', 'warrior', 'guerrera', 'guerrero', 'tactical', 'cape', 'capa',
      'powerful', 'poderosa', 'action pose'],
    tokens: { mood: 'mood_epic', visual_style: 'style_cinematic', camera: 'cam_dslr', lens: 'lens_35mm',
      lighting: 'light_rim', composition: 'comp_leading', angle: 'angle_low', dof: 'dof_moderate', color: 'color_warm' },
    styleIntent: 'cinematic superhero photography, movie poster style',
    aspectRatio: '2:3', stylize: 350, chaos: 20, raw: false,
    subjectDetailsIds: ['posture_dynamic', 'texture_detailed'],
    subjectModifiers: ['hyper-detailed', 'photorealistic', 'masterpiece'],
  },
  {
    id: 'fashion_editorial',
    label: 'Moda / editorial',
    keywords: ['fashion', 'moda', 'editorial', 'model', 'modelo', 'vogue', 'runway', 'pasarela', 'outfit',
      'vestimenta', 'street style'],
    tokens: { mood: 'mood_dramatic', visual_style: 'style_editorial', camera: 'cam_dslr', lens: 'lens_85mm',
      lighting: 'light_studio', composition: 'comp_rule3rds', angle: 'angle_threeq', dof: 'dof_shallow2', color: 'color_warm' },
    styleIntent: 'editorial fashion photography',
    aspectRatio: '3:4', stylize: 300, chaos: 30, raw: false,
    subjectModifiers: ['photorealistic', 'professional'],
  },
  {
    id: 'portrait',
    label: 'Retrato',
    keywords: ['retrato', 'portrait', 'headshot', 'rostro', 'face close', 'close-up face', 'close up portrait'],
    tokens: { mood: 'mood_serene', visual_style: 'style_photoreal', camera: 'cam_dslr', lens: 'lens_85mm',
      lighting: 'light_rembrandt', composition: 'comp_rule3rds', angle: 'angle_eye', dof: 'dof_shallow', color: 'color_warm' },
    styleIntent: 'editorial portrait photography',
    aspectRatio: '4:5', stylize: 150, chaos: 5, raw: true,
  },
  {
    id: 'cyberpunk',
    label: 'Cyberpunk / sci-fi urbano',
    keywords: ['cyberpunk', 'neon', 'futuristic', 'futurista', 'dystopia', 'distopia', 'blade runner', 'cyber'],
    tokens: { mood: 'mood_mysterious', visual_style: 'style_cyberpunk', lighting: 'light_neon', atmosphere: 'atm_smoke',
      composition: 'comp_leading', angle: 'angle_low', dof: 'dof_moderate', color: 'color_cyber' },
    styleIntent: 'cyberpunk concept photography',
    aspectRatio: '16:9', stylize: 500, chaos: 40, raw: false,
  },
  {
    id: 'product_commercial',
    label: 'Producto comercial',
    keywords: ['producto', 'product', 'ecommerce', 'watch', 'reloj', 'bottle', 'botella', 'perfume', 'packshot'],
    tokens: { visual_style: 'style_photoreal', lighting: 'light_studio', composition: 'comp_center',
      angle: 'angle_eye', dof: 'dof_deep', color: 'color_highsat' },
    styleIntent: 'commercial product photography',
    aspectRatio: '1:1', stylize: 50, chaos: 0, raw: true,
  },
  {
    id: 'landscape_nature',
    label: 'Paisaje / naturaleza',
    keywords: ['paisaje', 'landscape', 'mountain', 'montaña', 'forest', 'bosque', 'ocean', 'océano', 'valley',
      'valle', 'nature', 'naturaleza', 'vista'],
    tokens: { mood: 'mood_epic', visual_style: 'style_fineart', lighting: 'light_golden', atmosphere: 'atm_sunset',
      composition: 'comp_wide', angle: 'angle_high', dof: 'dof_deep', color: 'color_earthy' },
    styleIntent: 'epic landscape photography',
    aspectRatio: '16:9', stylize: 350, chaos: 15, raw: false,
  },
  {
    id: 'wildlife_macro',
    label: 'Vida salvaje / macro',
    keywords: ['macro', 'insect', 'insecto', 'wildlife', 'vida salvaje', 'butterfly', 'mariposa', 'animal close'],
    tokens: { visual_style: 'style_photoreal', lighting: 'light_midday', composition: 'comp_macro',
      angle: 'angle_eye', dof: 'dof_shallow', color: 'color_highsat' },
    styleIntent: 'macro wildlife photography',
    aspectRatio: '3:2', stylize: 80, chaos: 10, raw: true,
  },
  {
    id: 'horror_gothic',
    label: 'Horror / gótico',
    keywords: ['horror', 'terror', 'gothic', 'gótico', 'mansion', 'haunted', 'embrujada', 'siniestro', 'sombrio', 'sombrío'],
    tokens: { mood: 'mood_somber', visual_style: 'style_baroque', lighting: 'light_rim', atmosphere: 'atm_foggy',
      composition: 'comp_framing', angle: 'angle_low', dof: 'dof_moderate', color: 'color_desat' },
    styleIntent: 'gothic horror cinematic photography',
    aspectRatio: '21:9', stylize: 380, chaos: 30, raw: false,
  },
  {
    id: 'cinematic_film',
    label: 'Cinematográfico',
    keywords: ['cinematic', 'cinematográfico', 'película', 'movie still', 'film noir', 'western', 'standoff'],
    tokens: { mood: 'mood_tense', visual_style: 'style_cinematic', lighting: 'light_rim', composition: 'comp_leading',
      angle: 'angle_low', dof: 'dof_moderate', color: 'color_warm' },
    styleIntent: 'cinematic movie still',
    aspectRatio: '21:9', stylize: 350, chaos: 25, raw: false,
  },
  {
    id: 'fine_art_bw',
    label: 'Bellas artes / blanco y negro',
    keywords: ['black and white', 'blanco y negro', 'b&w', 'monochrome', 'fine art'],
    tokens: { mood: 'mood_melancholic', visual_style: 'style_fineart', lighting: 'light_split',
      composition: 'comp_negative', angle: 'angle_eye', dof: 'dof_shallow2', color: 'color_bw' },
    styleIntent: 'fine art black and white photography',
    aspectRatio: '3:2', stylize: 400, chaos: 20, raw: false,
  },
  {
    id: 'architecture_interior',
    label: 'Arquitectura / interiorismo',
    keywords: ['arquitectura', 'architecture', 'interior', 'interiorismo', 'building', 'edificio', 'habitación', 'habitacion'],
    tokens: { visual_style: 'style_minimalist', lighting: 'light_overcast', composition: 'comp_leading',
      angle: 'angle_eye', dof: 'dof_deep', color: 'color_cool' },
    styleIntent: 'architectural interior photography',
    aspectRatio: '16:9', stylize: 150, chaos: 5, raw: true,
  },
  {
    id: 'fantasy_concept_art',
    label: 'Fantasía / concept art',
    keywords: ['fantasy', 'fantasía', 'concept art', 'dragon', 'dragón', 'magic', 'mágico', 'spaceship', 'nave espacial'],
    tokens: { mood: 'mood_epic', visual_style: 'style_surreal', lighting: 'light_volumetric',
      composition: 'comp_layers', angle: 'angle_low', dof: 'dof_moderate', color: 'color_cool' },
    styleIntent: 'fantasy concept art',
    aspectRatio: '16:9', stylize: 500, chaos: 30, raw: false,
  },
];

const DEFAULT_DOMAIN = {
  id: 'general_photoreal',
  label: 'General fotorrealista (sin dominio detectado)',
  tokens: { mood: 'mood_serene', visual_style: 'style_photoreal', lighting: 'light_golden',
    composition: 'comp_rule3rds', angle: 'angle_eye', dof: 'dof_shallow2', color: 'color_warm' },
  styleIntent: 'professional photography',
  aspectRatio: '1:1', stylize: 100, chaos: 0, raw: false,
};

const TIME_OF_DAY_RULES = [
  { test: /\bnight\b|\bnoche\b|nighttime/, value: 'night, after dark' },
  { test: /\bdawn\b|\bamanecer\b|sunrise/, value: 'dawn, early morning light' },
  { test: /\bdusk\b|\batardecer\b|twilight/, value: 'dusk, twilight' },
  { test: /\bnoon\b|\bmediod[ií]a\b/, value: 'midday' },
];

const WEATHER_RULES = [
  { test: /\brain\b|\blluvia\b/, value: 'light rain, wet surfaces' },
  { test: /\bsnow\b|\bnieve\b/, value: 'snowfall' },
  { test: /\bstorm\b|\btormenta\b/, value: 'stormy weather' },
];

const ERA_RULES = [
  { test: /\b(19|20)\d0s\b/, value: null }, // handled below to keep matched text
  { test: /medieval/, value: 'medieval period' },
  { test: /futuristic|futurista/, value: 'far future' },
];

const RENDER_ENGINE_RULES = [
  { test: /\b3d\b|render|cgi/, value: 'Octane Render' },
  { test: /unreal/, value: 'Unreal Engine 5' },
];

const DEFAULT_NEGATIVE = 'text, watermark, blurry, deformed, extra limbs, low quality';

export function inferFromSubject(subjectText, _state = {}) {
  const text = (subjectText || '').toLowerCase();

  let domain = DEFAULT_DOMAIN;
  let matchedKeywords = [];
  let bestScore = 0;
  for (const candidate of DOMAINS) {
    const matched = candidate.keywords.filter((k) => text.includes(k));
    if (matched.length > bestScore) {
      bestScore = matched.length;
      domain = candidate;
      matchedKeywords = matched;
    }
  }

  const fields = {};

  if (domain.tokens.mood) fields.mood = tokenValue('mood', domain.tokens.mood);
  if (domain.tokens.visual_style) fields.visualStyle = tokenValue('visual_style', domain.tokens.visual_style);
  if (domain.tokens.camera) fields.cameraType = tokenValue('camera', domain.tokens.camera);
  if (domain.tokens.lens) fields.lensType = tokenValue('lens', domain.tokens.lens);
  if (domain.tokens.film) fields.filmType = tokenValue('film', domain.tokens.film);
  if (domain.tokens.lighting) fields.lightingType = tokenValue('lighting', domain.tokens.lighting);
  if (domain.tokens.atmosphere) fields.atmosphere = tokenValue('atmosphere', domain.tokens.atmosphere);
  if (domain.tokens.composition) fields.composition = tokenValue('composition', domain.tokens.composition);
  if (domain.tokens.angle) fields.angle = tokenValue('angle', domain.tokens.angle);
  if (domain.tokens.dof) fields.depthOfField = tokenValue('dof', domain.tokens.dof);
  if (domain.tokens.color) fields.colorGrading = tokenValue('color', domain.tokens.color);

  if (domain.styleIntent) fields.styleIntent = domain.styleIntent;
  if (domain.aspectRatio) fields.aspectRatio = domain.aspectRatio;
  if (typeof domain.stylize === 'number') fields.stylize = domain.stylize;
  if (typeof domain.chaos === 'number') fields.chaos = domain.chaos;
  if (typeof domain.raw === 'boolean') fields.raw = domain.raw;

  if (domain.subjectDetailsIds?.length) {
    fields.subjectDetails = tokenValues('subject_details', domain.subjectDetailsIds);
  }
  if (domain.subjectModifiers?.length) {
    fields.subjectModifiers = [...domain.subjectModifiers];
  }

  for (const rule of TIME_OF_DAY_RULES) {
    if (rule.test.test(text)) {
      fields.timeOfDay = rule.value;
      break;
    }
  }
  for (const rule of WEATHER_RULES) {
    if (rule.test.test(text)) {
      fields.weather = rule.value;
      break;
    }
  }
  for (const rule of ERA_RULES) {
    const match = text.match(rule.test);
    if (match) {
      fields.eraPeriod = rule.value || match[0];
      break;
    }
  }
  for (const rule of RENDER_ENGINE_RULES) {
    if (rule.test.test(text)) {
      fields.renderingEngine = rule.value;
      break;
    }
  }

  fields.negative = DEFAULT_NEGATIVE;

  return {
    fields,
    meta: {
      domainId: domain.id,
      label: domain.label,
      matchedKeywords,
    },
  };
}
