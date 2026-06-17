// ============================================================
// KIMIFY - YAML Export Engine
// Exports prompt state to structured YAML
// ============================================================

import { buildPrompt, buildParameterString } from './promptBuilder';

export function exportToYAML(state) {
  const exportData = {
    methodology: 'KIMIFY',
    version: '1.0.0-mj81',
    generatedAt: new Date().toISOString(),
    kimify: {
      kernel: {
        subject: state.subject,
        details: state.subjectDetails,
        modifiers: state.subjectModifiers,
      },
      intent: {
        style: state.styleIntent,
        mood: state.mood,
        visualStyle: state.visualStyle,
        era: state.eraPeriod,
      },
      medium: {
        camera: state.cameraType,
        lens: state.lensType,
        film: state.filmType,
        rendering: state.renderingEngine,
      },
      illumination: {
        lighting: state.lightingType,
        timeOfDay: state.timeOfDay,
        atmosphere: state.atmosphere,
        weather: state.weather,
      },
      format: {
        composition: state.composition,
        angle: state.angle,
        depthOfField: state.depthOfField,
        colorGrading: state.colorGrading,
      },
      yield: {
        aspectRatio: state.aspectRatio,
        stylize: state.stylize,
        chaos: state.chaos,
        weird: state.weird,
        raw: state.raw,
        hd: state.hd,
        seed: state.seed || null,
        negative: state.negative || null,
        sref: state.sref || null,
        sw: state.sref ? state.sw : null,
        iw: state.iw !== 1 ? state.iw : null,
        exp: state.exp > 0 ? state.exp : null,
        tile: state.tile,
        personalization: state.personalization,
        version: '8.1',
      },
    },
    finalPrompt: buildPrompt(state),
    parameterString: buildParameterString(state),
  };

  // Manual YAML serialization for clean output
  const lines = [];
  lines.push(`# KIMIFY Prompt Export for Midjourney v8.1`);
  lines.push(`# Generated: ${exportData.generatedAt}`);
  lines.push(`# Methodology: ${exportData.methodology} v${exportData.version}`);
  lines.push('');
  lines.push(`methodology: "${exportData.methodology}"`);
  lines.push(`version: "${exportData.version}"`);
  lines.push(`generatedAt: "${exportData.generatedAt}"`);
  lines.push('');
  lines.push('kimify:');

  // KERNEL
  lines.push('  kernel:');
  lines.push(`    subject: "${escapeYaml(state.subject)}"`);
  lines.push(`    details: [${state.subjectDetails.map(d => `"${escapeYaml(d)}"`).join(', ')}]`);
  lines.push(`    modifiers: [${state.subjectModifiers.map(m => `"${escapeYaml(m)}"`).join(', ')}]`);

  // INTENT
  lines.push('  intent:');
  lines.push(`    style: "${escapeYaml(state.styleIntent)}"`);
  lines.push(`    mood: "${escapeYaml(state.mood)}"`);
  lines.push(`    visualStyle: "${escapeYaml(state.visualStyle)}"`);
  lines.push(`    era: "${escapeYaml(state.eraPeriod)}"`);

  // MEDIUM
  lines.push('  medium:');
  lines.push(`    camera: "${escapeYaml(state.cameraType)}"`);
  lines.push(`    lens: "${escapeYaml(state.lensType)}"`);
  lines.push(`    film: "${escapeYaml(state.filmType)}"`);
  lines.push(`    rendering: "${escapeYaml(state.renderingEngine)}"`);

  // ILLUMINATION
  lines.push('  illumination:');
  lines.push(`    lighting: "${escapeYaml(state.lightingType)}"`);
  lines.push(`    timeOfDay: "${escapeYaml(state.timeOfDay)}"`);
  lines.push(`    atmosphere: "${escapeYaml(state.atmosphere)}"`);
  lines.push(`    weather: "${escapeYaml(state.weather)}"`);

  // FORMAT
  lines.push('  format:');
  lines.push(`    composition: "${escapeYaml(state.composition)}"`);
  lines.push(`    angle: "${escapeYaml(state.angle)}"`);
  lines.push(`    depthOfField: "${escapeYaml(state.depthOfField)}"`);
  lines.push(`    colorGrading: "${escapeYaml(state.colorGrading)}"`);

  // YIELD
  lines.push('  yield:');
  const yieldEntries = Object.entries(exportData.kimify.yield).filter(([_, v]) => v !== null);
  for (const [key, value] of yieldEntries) {
    if (typeof value === 'boolean') {
      lines.push(`    ${key}: ${value}`);
    } else if (typeof value === 'number') {
      lines.push(`    ${key}: ${value}`);
    } else {
      lines.push(`    ${key}: "${escapeYaml(String(value))}"`);
    }
  }

  lines.push('');
  lines.push(`finalPrompt: "${escapeYaml(buildPrompt(state))}"`);
  lines.push(`parameterString: "${escapeYaml(buildParameterString(state))}"`);

  return lines.join('\n');
}

function escapeYaml(str) {
  return str.replace(/"/g, '\\"').replace(/\n/g, ' ');
}

export function downloadYAML(content, filename = 'kimify-prompt.yml') {
  const blob = new Blob([content], { type: 'text/yaml' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
