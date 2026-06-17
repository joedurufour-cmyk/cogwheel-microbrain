// ============================================================
// Fixed output-style presets
// JS mirror of the backend's style_presets.STYLE_PRESETS. Unlike
// kimifyInference.js's DOMAINS (which infer *scene* fields from the
// free text), these presets describe a fixed *rendering medium/look*
// applied on top of the inferred domain, independent of the scene.
// Used to compile the same Kernel into all 6 styles at once.
// ============================================================

export const STYLE_PRESETS = [
  {
    id: 'cinema',
    label: 'Cine / Cinematográfico',
    visualStyle: 'cinematic, movie still, anamorphic lens flare, film grain',
    styleIntent: 'cinematic movie still, blockbuster film photography',
    cameraType: 'shot on ARRI Alexa 65',
    lensType: 'anamorphic 40mm lens, subtle lens flare',
    filmType: 'Kodak Vision3 500T film stock',
    renderingEngine: '',
    colorGrading: 'teal and orange cinematic LUT, color graded',
    lightingType: 'motivated practical lighting, volumetric haze',
    aspectRatio: '21:9', stylize: 350, chaos: 20, raw: false,
  },
  {
    id: 'vintage_photo',
    label: 'Foto vintage',
    visualStyle: 'vintage analog photography, retro film aesthetic, nostalgic',
    styleIntent: 'vintage film photography, 1970s analog look',
    cameraType: 'shot on Leica M6 rangefinder',
    lensType: '50mm f/1.4 vintage lens, soft vignette',
    filmType: 'Kodak Portra 400 film, grain texture, light leaks',
    renderingEngine: '',
    colorGrading: 'faded warm tones, sepia undertone, desaturated highlights',
    lightingType: 'soft natural window light, warm afternoon glow',
    aspectRatio: '4:5', stylize: 150, chaos: 10, raw: true,
  },
  {
    id: 'anime_dark_pro',
    label: 'Anime Dark Pro',
    visualStyle: 'dark fantasy anime, Anime Dark Pro style, high-contrast cel shading',
    styleIntent: 'professional anime illustration, dark fantasy manga aesthetic',
    cameraType: '', lensType: '', filmType: '',
    renderingEngine: 'anime production cel-shading pipeline, digital ink and paint',
    colorGrading: 'deep shadows, saturated neon accents, high contrast palette',
    lightingType: 'dramatic rim lighting, dark moody atmosphere',
    aspectRatio: '2:3', stylize: 600, chaos: 30, raw: false,
  },
  {
    id: 'ghibli',
    label: 'Studio Ghibli',
    visualStyle: 'Studio Ghibli style, hand-painted anime, whimsical watercolor backgrounds',
    styleIntent: 'Hayao Miyazaki inspired animation still, soft painterly illustration',
    cameraType: '', lensType: '', filmType: '',
    renderingEngine: 'traditional 2D cel animation, watercolor background art',
    colorGrading: 'soft pastel palette, warm natural tones',
    lightingType: 'soft diffused daylight, gentle volumetric light through leaves',
    aspectRatio: '16:9', stylize: 250, chaos: 15, raw: false,
  },
  {
    id: 'pvc_resin_3d',
    label: 'PVC Resina 3D Realista',
    visualStyle: 'PVC resin figure, collectible action figure render, realistic toy photography',
    styleIntent: 'commercial product photography of a 1/7 scale PVC resin figure',
    cameraType: '', lensType: '', filmType: '',
    renderingEngine: 'ZBrush sculpt, Substance Painter PBR textures, Octane Render',
    colorGrading: 'studio-accurate color calibration, glossy resin highlights',
    lightingType: 'softbox studio lighting, three-point setup, subtle specular highlights',
    depthOfField: 'shallow depth of field, product on display base, blurred shelf background',
    aspectRatio: '1:1', stylize: 100, chaos: 0, raw: true,
  },
  {
    id: 'cgi_3d_realistic',
    label: 'CGI 3D Realista',
    visualStyle: 'full CGI render, photorealistic 3D, hyperrealistic digital rendering',
    styleIntent: 'high-end CGI rendering, AAA game cinematic quality',
    cameraType: '', lensType: '', filmType: '',
    renderingEngine: 'Unreal Engine 5, Lumen global illumination, Nanite geometry',
    colorGrading: 'physically accurate PBR materials, realistic color grading',
    lightingType: 'ray-traced global illumination, HDRI environment lighting',
    depthOfField: 'cinematic depth of field, ray-traced reflections',
    aspectRatio: '16:9', stylize: 400, chaos: 15, raw: false,
  },
];

const OVERRIDABLE_KEYS = [
  'visualStyle', 'styleIntent', 'cameraType', 'lensType', 'filmType',
  'renderingEngine', 'colorGrading', 'lightingType', 'depthOfField',
  'aspectRatio', 'stylize', 'chaos', 'raw',
];

// Overlay a style preset's medium/look fields onto inferred domain fields.
// Scene-level fields (mood, atmosphere, composition, angle, etc.) are left
// untouched since they describe what's happening, not how it's rendered.
export function applyStylePreset(fields, preset) {
  const overlaid = { ...fields };
  for (const key of OVERRIDABLE_KEYS) {
    if (key in preset) overlaid[key] = preset[key];
  }
  return overlaid;
}
