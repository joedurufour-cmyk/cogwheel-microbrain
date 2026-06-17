// ============================================================
// KIMIFY - Central State Hook
// Manages the entire prompt building state
// ============================================================

import { useState, useCallback, useMemo } from 'react';

const defaultState = {
  // K - KERNEL
  subject: '',
  subjectDetails: [],
  subjectModifiers: [],

  // I - INTENT
  styleIntent: '',
  mood: '',
  visualStyle: '',
  eraPeriod: '',

  // M - MEDIUM
  cameraType: '',
  lensType: '',
  filmType: '',
  renderingEngine: '',

  // I2 - ILLUMINATION
  lightingType: '',
  timeOfDay: '',
  atmosphere: '',
  weather: '',

  // F - FORMAT
  composition: '',
  angle: '',
  depthOfField: '',
  colorGrading: '',

  // Y - YIELD
  aspectRatio: '1:1',
  stylize: 100,
  chaos: 0,
  weird: 0,
  raw: false,
  hd: false,
  seed: '',
  negative: '',
  sref: '',
  sw: 100,
  iw: 1,
  exp: 0,
  tile: false,
  personalization: false,
};

export function useKimify() {
  const [state, setState] = useState({ ...defaultState });
  const [activeLayer, setActiveLayer] = useState('K');

  const updateField = useCallback((field, value) => {
    setState(prev => ({ ...prev, [field]: value }));
  }, []);

  const toggleDetail = useCallback((field, value) => {
    setState(prev => {
      const current = prev[field];
      const updated = current.includes(value)
        ? current.filter(v => v !== value)
        : [...current, value];
      return { ...prev, [field]: updated };
    });
  }, []);

  const resetState = useCallback(() => {
    setState({ ...defaultState });
  }, []);

  const loadPreset = useCallback((preset) => {
    setState(prev => ({ ...prev, ...preset }));
  }, []);

  const isLayerComplete = useCallback((layer) => {
    switch (layer) {
      case 'K': return state.subject.length > 0;
      case 'I': return state.styleIntent.length > 0 || state.mood.length > 0;
      case 'M': return state.cameraType.length > 0 || state.lensType.length > 0;
      case 'I2': return state.lightingType.length > 0;
      case 'F': return state.composition.length > 0 || state.angle.length > 0;
      case 'Y': return true;
      default: return false;
    }
  }, [state]);

  const completionPercentage = useMemo(() => {
    const layers = ['K', 'I', 'M', 'I2', 'F', 'Y'];
    const completed = layers.filter(l => isLayerComplete(l)).length;
    return Math.round((completed / layers.length) * 100);
  }, [isLayerComplete]);

  return {
    state,
    activeLayer,
    setActiveLayer,
    updateField,
    toggleDetail,
    resetState,
    loadPreset,
    isLayerComplete,
    completionPercentage,
  };
}
