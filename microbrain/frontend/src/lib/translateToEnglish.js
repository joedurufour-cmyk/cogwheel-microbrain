// ============================================================
// KIMIFY - Spanish->English Kernel Translator
// JS mirror of the backend's visual_blueprint.translate_full_text,
// so Pro Builder's Kernel text is compiled to English (like the
// Generador's backend path) instead of being passed through verbatim
// and mixed with the English layer values from kimifyInference.js.
// ============================================================

const RESEMBLANCE_PATTERNS = [
  [/con\s+(?:la\s+)?cara\s+de\s+([^,.]+)/gi, 'resembling $1'],
  [/con\s+(?:el\s+)?rostro\s+de\s+([^,.]+)/gi, 'resembling $1'],
  [/parecida?\s+a\s+([^,.]+)/gi, 'resembling $1'],
  [/que\s+se\s+parece\s+a\s+([^,.]+)/gi, 'resembling $1'],
  [/al\s+estilo\s+de\s+([^,.]+)/gi, 'in the style of $1'],
];

// Posture participle + preposition phrases, collapsed so the preposition
// doesn't get translated again right after (e.g. "apoyada en X" -> "leaning
// against X", not "leaning against in X").
const POSTURE_PATTERNS = [
  [/apoyad[ao]\s+(?:en|contra)\s+/gi, 'leaning against '],
  [/recostad[ao]\s+(?:en|sobre)\s+/gi, 'reclining on '],
  [/sentad[ao]\s+(?:en|sobre)\s+/gi, 'seated on '],
  [/parad[ao]\s+(?:en|sobre)\s+/gi, 'standing on '],
  [/acostad[ao]\s+(?:en|sobre)\s+/gi, 'lying on '],
  [/arrodillad[ao]\s+(?:en|sobre)\s+/gi, 'kneeling on '],
];

const ES_GERUNDS = {
  levitando: 'levitating', volando: 'flying', corriendo: 'running',
  luchando: 'fighting', cayendo: 'falling', saltando: 'jumping',
  mirando: 'looking', sosteniendo: 'holding', caminando: 'walking',
  flotando: 'floating', destruyendo: 'destroying', atacando: 'attacking',
  defendiendo: 'defending', huyendo: 'fleeing', escalando: 'climbing',
  nadando: 'swimming', bailando: 'dancing', meditando: 'meditating',
  observando: 'observing', disparando: 'shooting',
};

const ES_NOUNS = {
  ciudad: 'city', bosque: 'forest', desierto: 'desert',
  montaña: 'mountain', océano: 'ocean', mar: 'sea', cielo: 'sky',
  noche: 'night', amanecer: 'dawn', atardecer: 'sunset',
  fuego: 'fire', agua: 'water', hielo: 'ice', nieve: 'snow',
  lluvia: 'rain', tormenta: 'storm', nebulosa: 'nebula',
  espacio: 'space', galaxia: 'galaxy', universo: 'universe',
  puente: 'bridge', rascacielo: 'skyscraper', templo: 'temple',
  castillo: 'castle', ruinas: 'ruins', selva: 'jungle',
  cueva: 'cave', aldea: 'village', metrópoli: 'metropolis',
  laboratorio: 'laboratory', nave: 'spaceship', planeta: 'planet',
  arena: 'sand', playa: 'beach', isla: 'island', volcán: 'volcano',
  techo: 'rooftop', calle: 'street', edificio: 'building',
  pared: 'wall', muro: 'wall', capa: 'cape', torre: 'tower',
  roca: 'rock', puerta: 'door', ventana: 'window', columna: 'column',
  estilo: 'style',
};

const ES_ADJECTIVES = {
  destruida: 'destroyed', destruido: 'destroyed',
  abandonada: 'abandoned', abandonado: 'abandoned',
  oscuro: 'dark', oscura: 'dark',
  luminoso: 'radiant', luminosa: 'radiant',
  apocalíptico: 'apocalyptic', épico: 'epic',
  mágico: 'magical', mágica: 'magical',
  antiguo: 'ancient', antigua: 'ancient',
  futurista: 'futuristic', helado: 'frozen', helada: 'frozen',
  ardiente: 'burning', sumergido: 'submerged', sumergida: 'submerged',
  nevado: 'snowy', nevada: 'snowy', lluvioso: 'rainy', lluviosa: 'rainy',
  // Descriptor adjectives (critical for preserving user input)
  sexy: 'sexy', sensual: 'sensual',
  muscular: 'muscular', musculosa: 'muscular', musculoso: 'muscular',
  definida: 'defined', definido: 'defined',
  alta: 'tall', alto: 'tall',
  baja: 'short', bajo: 'short',
  delgada: 'slender', delgado: 'slender',
  fuerte: 'strong',
  poderosa: 'powerful', poderoso: 'powerful',
  hermosa: 'beautiful', hermoso: 'beautiful',
  elegante: 'elegant',
  feroz: 'fierce',
  majestuosa: 'majestic', majestuoso: 'majestic',
  enorme: 'enormous',
  pequeña: 'small', pequeño: 'small',
  joven: 'young',
  anciana: 'elderly', anciano: 'elderly',
  veloce: 'swift', veloz: 'swift',
  brillante: 'brilliant',
  dorada: 'golden', dorado: 'golden',
  plateada: 'silver', plateado: 'silver',
  // Past-participle posture descriptors
  apoyada: 'leaning against', apoyado: 'leaning against',
  recostada: 'reclining', recostado: 'reclining',
  sentada: 'seated', sentado: 'seated',
  parada: 'standing', parado: 'standing',
  acostada: 'lying down', acostado: 'lying down',
  arrodillada: 'kneeling', arrodillado: 'kneeling',
  hiper: 'hyper',
};

const ES_PREPOSITIONS = {
  sobre: 'above', encima: 'above',
  bajo: 'below', debajo: 'below',
  dentro: 'inside',
  fuera: 'outside',
  en: 'in',
  entre: 'between',
  detrás: 'behind',
  junto: 'beside',
  con: 'with',
  de: 'of',
  frente: 'in front of',
};

const ARTICLES = new Set(['un', 'una', 'el', 'la', 'los', 'las', 'unos', 'unas', 'al', 'del']);

const CHARACTER_MAP = {
  supergirl: 'superheroine', superman: 'superhero',
  batman: 'dark knight', batgirl: 'dark heroine',
  'wonder woman': 'warrior goddess', 'iron man': 'armored hero',
  'spider-man': 'web-slinging hero', spiderman: 'web-slinging hero',
  thor: 'norse god warrior', hulk: 'hulking green warrior',
  'captain america': 'super soldier', 'black widow': 'elite spy',
  aquaman: 'underwater king', flash: 'speedster hero',
  'green lantern': 'cosmic guardian', catwoman: 'feline thief',
  guerrero: 'warrior', guerrera: 'female warrior',
  mago: 'sorcerer', maga: 'sorceress',
  bruja: 'witch', brujo: 'warlock',
  dragón: 'dragon', dragon: 'dragon',
  robot: 'robot', androide: 'android', cyborg: 'cyborg',
  astronauta: 'astronaut', vikingo: 'viking warrior',
  samurai: 'samurai', ninja: 'ninja',
  caballero: 'knight', princesa: 'princess',
  reina: 'queen', rey: 'king',
  soldado: 'soldier', detective: 'detective',
  héroe: 'hero', heroína: 'heroine',
  villano: 'villain', villana: 'villainess',
  científico: 'scientist', explorador: 'explorer',
};

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export function translateToEnglish(text) {
  let result = (text || '').trim().replace(/,+$/, '');

  // Step 1: Resemblance phrases (before any other substitution)
  for (const [pattern, repl] of RESEMBLANCE_PATTERNS) {
    result = result.replace(pattern, repl);
  }

  // Step 1b: Posture participle + preposition phrases
  for (const [pattern, repl] of POSTURE_PATTERNS) {
    result = result.replace(pattern, repl);
  }

  // Step 2: Normalize known character names (longest match first)
  for (const name of Object.keys(CHARACTER_MAP).sort((a, b) => b.length - a.length)) {
    result = result.replace(new RegExp(`\\b${escapeRegExp(name)}\\b`, 'gi'), CHARACTER_MAP[name]);
  }

  // Step 3: Handle Spanish noun+adj -> English adj+noun word order
  for (const [esNoun, enNoun] of Object.entries(ES_NOUNS)) {
    for (const [esAdj, enAdj] of Object.entries(ES_ADJECTIVES)) {
      result = result.replace(
        new RegExp(`\\b${escapeRegExp(esNoun)}\\s+${escapeRegExp(esAdj)}\\b`, 'gi'),
        `${enAdj} ${enNoun}`
      );
    }
  }

  // Step 4: Token-by-token translation of remaining Spanish words
  const tokens = result.split(/\s+/).filter(Boolean);
  const translated = [];
  for (const token of tokens) {
    const match = token.match(/^([.,;]*)(.*?)([.,;]*)$/);
    const [, prefixPunct, clean, suffixPunct] = match;
    const t = clean.toLowerCase();

    if (ARTICLES.has(t)) continue; // Drop Spanish articles

    const en =
      ES_GERUNDS[t] || ES_PREPOSITIONS[t] || ES_NOUNS[t] || ES_ADJECTIVES[t] || clean;
    translated.push(prefixPunct + en + suffixPunct);
  }

  return translated.join(' ');
}
