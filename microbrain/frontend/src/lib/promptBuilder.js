// ============================================================
// KIMIFY - Prompt Builder Engine
// Assembles the final Midjourney prompt from state
// ============================================================

export function buildPrompt(state) {
  const parts = [];

  // ─── K: KERNEL ───
  if (state.subject) {
    let subjectPart = state.subject;
    if (state.subjectDetails.length > 0) {
      subjectPart += ', ' + state.subjectDetails.join(', ');
    }
    if (state.subjectModifiers.length > 0) {
      subjectPart += ', ' + state.subjectModifiers.join(', ');
    }
    parts.push(subjectPart);
  }

  // ─── I: INTENT ───
  const intentParts = [];
  if (state.styleIntent) intentParts.push(state.styleIntent);
  if (state.mood) intentParts.push(state.mood);
  if (state.visualStyle) intentParts.push(state.visualStyle);
  if (state.eraPeriod) intentParts.push(state.eraPeriod);
  if (intentParts.length > 0) {
    parts.push(intentParts.join(', '));
  }

  // ─── M: MEDIUM ───
  const mediumParts = [];
  if (state.cameraType) mediumParts.push(state.cameraType);
  if (state.lensType) mediumParts.push(state.lensType);
  if (state.filmType) mediumParts.push(state.filmType);
  if (state.renderingEngine) mediumParts.push(state.renderingEngine);
  if (mediumParts.length > 0) {
    parts.push(mediumParts.join(', '));
  }

  // ─── I2: ILLUMINATION ───
  const illumParts = [];
  if (state.lightingType) illumParts.push(state.lightingType);
  if (state.timeOfDay) illumParts.push(state.timeOfDay);
  if (state.atmosphere) illumParts.push(state.atmosphere);
  if (state.weather) illumParts.push(state.weather);
  if (illumParts.length > 0) {
    parts.push(illumParts.join(', '));
  }

  // ─── F: FORMAT ───
  const formatParts = [];
  if (state.composition) formatParts.push(state.composition);
  if (state.angle) formatParts.push(state.angle);
  if (state.depthOfField) formatParts.push(state.depthOfField);
  if (state.colorGrading) formatParts.push(state.colorGrading);
  if (formatParts.length > 0) {
    parts.push(formatParts.join(', '));
  }

  return parts.join(', ');
}

export function buildParameterString(state) {
  const params = [];

  // Aspect Ratio
  params.push(`--ar ${state.aspectRatio}`);

  // Stylize
  if (state.stylize !== 100) {
    params.push(`--s ${state.stylize}`);
  }

  // Chaos
  if (state.chaos > 0) {
    params.push(`--c ${state.chaos}`);
  }

  // Weird
  if (state.weird > 0) {
    params.push(`--w ${state.weird}`);
  }

  // Raw
  if (state.raw) {
    params.push('--raw');
  }

  // HD / SD
  if (state.hd) {
    params.push('--hd');
  }

  // Seed
  if (state.seed) {
    params.push(`--seed ${state.seed}`);
  }

  // Negative
  if (state.negative) {
    params.push(`--no ${state.negative}`);
  }

  // Style Reference
  if (state.sref) {
    params.push(`--sref ${state.sref}`);
    if (state.sw !== 100) {
      params.push(`--sw ${state.sw}`);
    }
  }

  // Image Weight
  if (state.iw !== 1) {
    params.push(`--iw ${state.iw}`);
  }

  // Experimental
  if (state.exp > 0) {
    params.push(`--exp ${state.exp}`);
  }

  // Tile
  if (state.tile) {
    params.push('--tile');
  }

  // Personalization
  if (state.personalization) {
    params.push('--p');
  }

  // Version (always v8.1)
  params.push('--v 8.1');

  return params.join(' ');
}

export function buildFullCommand(state) {
  const prompt = buildPrompt(state);
  const params = buildParameterString(state);

  if (!prompt) return `/imagine ${params}`;
  return `/imagine ${prompt} ${params}`;
}

export function estimateTokenCount(state) {
  const prompt = buildPrompt(state);
  // Rough estimate: ~0.75 tokens per word for GPT-style tokenization
  const words = prompt.split(/\s+/).filter(w => w.length > 0).length;
  return Math.ceil(words * 0.75) + 10; // +10 for parameters
}

// Quality score based on prompt completeness
export function calculateQualityScore(state) {
  let score = 0;
  const maxScore = 100;

  // K: Subject (20 pts)
  if (state.subject) score += 10;
  if (state.subjectDetails.length > 0) score += 5;
  if (state.subjectModifiers.length > 0) score += 5;

  // I: Intent (15 pts)
  if (state.styleIntent) score += 5;
  if (state.mood) score += 5;
  if (state.visualStyle) score += 5;

  // M: Medium (15 pts)
  if (state.cameraType) score += 5;
  if (state.lensType) score += 5;
  if (state.filmType) score += 5;

  // I2: Illumination (15 pts)
  if (state.lightingType) score += 5;
  if (state.timeOfDay) score += 5;
  if (state.atmosphere || state.weather) score += 5;

  // F: Format (15 pts)
  if (state.composition) score += 5;
  if (state.angle) score += 5;
  if (state.depthOfField || state.colorGrading) score += 5;

  // Y: Parameters (20 pts)
  if (state.aspectRatio !== '1:1') score += 3;
  if (state.stylize !== 100) score += 3;
  if (state.raw || state.hd) score += 4;
  if (state.negative) score += 5;
  if (state.sref) score += 5;

  return Math.min(score, maxScore);
}
