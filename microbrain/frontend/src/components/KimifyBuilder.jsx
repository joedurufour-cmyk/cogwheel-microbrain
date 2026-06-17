import { useMemo } from 'react';
import { tokenLibrary, mjParameters, aspectRatioGuide, stylizeGuide, chaosGuide } from '@/data/kimifyData';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { Info, Check, Wand2 } from 'lucide-react';

export function KimifyBuilder({ state, activeLayer, updateField, toggleDetail, autoInfer, lastInference }) {
  const layerColor = useMemo(() => {
    const colors = {
      K: '#FF3B5C', I: '#FF9F1C', M: '#2EC4B6', I2: '#3A86FF', F: '#8338EC', Y: '#06D6A0',
    };
    return colors[activeLayer] || '#zinc-400';
  }, [activeLayer]);

  const renderKernel = () => (
    <div className="space-y-6">
      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-2 block">
          Sujeto Principal <span className="text-rose-500">*</span>
        </Label>
        <Textarea
          placeholder="Describe el sujeto principal: persona, objeto, escena, personaje..."
          value={state.subject}
          onChange={(e) => updateField('subject', e.target.value)}
          className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 min-h-[80px] resize-none focus:border-rose-500 focus:ring-rose-500/20"
        />
        <p className="text-[10px] text-zinc-500 mt-1">Ej: "a confident young woman, warrior princess"</p>
        <Button
          variant="outline"
          size="sm"
          disabled={!state.subject}
          onClick={autoInfer}
          className="mt-3 h-8 text-[11px] border-rose-500/40 text-rose-300 hover:bg-rose-500/10 hover:text-rose-200"
        >
          <Wand2 className="w-3.5 h-3.5 mr-1.5" />
          Auto-inferir capas I · M · I2 · F · Y
        </Button>
        {lastInference && (
          <p className="text-[10px] text-zinc-500 mt-1.5">
            Dominio detectado: <span className="text-rose-400">{lastInference.label}</span>
            {lastInference.matchedKeywords.length > 0 && (
              <> — palabras clave: {lastInference.matchedKeywords.join(', ')}</>
            )}
          </p>
        )}
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Detalles del Sujeto</Label>
        <div className="flex flex-wrap gap-2">
          {tokenLibrary.find(t => t.id === 'subject_details')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => toggleDetail('subjectDetails', token.value)}
              className={`px-3 py-1.5 rounded-full text-[11px] font-medium transition-all border ${
                state.subjectDetails.includes(token.value)
                  ? 'bg-rose-500/20 border-rose-500/50 text-rose-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-300'
              }`}
            >
              {state.subjectDetails.includes(token.value) && <Check className="w-3 h-3 inline mr-1" />}
              {token.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Modificadores</Label>
        <div className="flex flex-wrap gap-2">
          {['hyper-detailed', '8k resolution', 'photorealistic', 'studio quality', 'award-winning',
            'breathtaking', 'masterpiece', 'ultra-sharp', 'intricate details', 'professional'].map(mod => (
            <button
              key={mod}
              onClick={() => toggleDetail('subjectModifiers', mod)}
              className={`px-3 py-1.5 rounded-full text-[11px] font-medium transition-all border ${
                state.subjectModifiers.includes(mod)
                  ? 'bg-rose-500/20 border-rose-500/50 text-rose-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-300'
              }`}
            >
              {state.subjectModifiers.includes(mod) && <Check className="w-3 h-3 inline mr-1" />}
              {mod}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderIntent = () => (
    <div className="space-y-6">
      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-2 block">Intención de Estilo</Label>
        <Input
          placeholder="ej: editorial fashion, cinematic movie still, fine art..."
          value={state.styleIntent}
          onChange={(e) => updateField('styleIntent', e.target.value)}
          className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-orange-500 focus:ring-orange-500/20"
        />
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Mood / Estado de Ánimo</Label>
        <div className="grid grid-cols-2 gap-2">
          {tokenLibrary.find(t => t.id === 'mood')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => updateField('mood', state.mood === token.value ? '' : token.value)}
              className={`px-3 py-2 rounded-lg text-[11px] font-medium transition-all border text-left ${
                state.mood === token.value
                  ? 'bg-orange-500/20 border-orange-500/50 text-orange-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {token.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Estilo Visual</Label>
        <div className="grid grid-cols-2 gap-2">
          {tokenLibrary.find(t => t.id === 'visual_style')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => updateField('visualStyle', state.visualStyle === token.value ? '' : token.value)}
              className={`px-3 py-2 rounded-lg text-[11px] font-medium transition-all border text-left ${
                state.visualStyle === token.value
                  ? 'bg-orange-500/20 border-orange-500/50 text-orange-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {token.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-2 block">Época / Periodo</Label>
        <Input
          placeholder="ej: 1920s Art Deco, 1980s retro, medieval..."
          value={state.eraPeriod}
          onChange={(e) => updateField('eraPeriod', e.target.value)}
          className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-orange-500 focus:ring-orange-500/20"
        />
      </div>
    </div>
  );

  const renderMedium = () => (
    <div className="space-y-6">
      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Cámara</Label>
        <div className="grid grid-cols-1 gap-2">
          {tokenLibrary.find(t => t.id === 'camera')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => updateField('cameraType', state.cameraType === token.value ? '' : token.value)}
              className={`px-3 py-2 rounded-lg text-[11px] font-medium transition-all border text-left ${
                state.cameraType === token.value
                  ? 'bg-teal-500/20 border-teal-500/50 text-teal-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {token.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Lente</Label>
        <div className="grid grid-cols-2 gap-2">
          {tokenLibrary.find(t => t.id === 'lens')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => updateField('lensType', state.lensType === token.value ? '' : token.value)}
              className={`px-3 py-2 rounded-lg text-[11px] font-medium transition-all border text-left ${
                state.lensType === token.value
                  ? 'bg-teal-500/20 border-teal-500/50 text-teal-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {token.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Película / Emulsión</Label>
        <div className="grid grid-cols-2 gap-2">
          {tokenLibrary.find(t => t.id === 'film')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => updateField('filmType', state.filmType === token.value ? '' : token.value)}
              className={`px-3 py-2 rounded-lg text-[11px] font-medium transition-all border text-left ${
                state.filmType === token.value
                  ? 'bg-teal-500/20 border-teal-500/50 text-teal-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {token.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-2 block">Motor de Render (opcional)</Label>
        <Input
          placeholder="ej: Octane Render, Unreal Engine 5, V-Ray..."
          value={state.renderingEngine}
          onChange={(e) => updateField('renderingEngine', e.target.value)}
          className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-teal-500 focus:ring-teal-500/20"
        />
      </div>
    </div>
  );

  const renderIllumination = () => (
    <div className="space-y-6">
      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Iluminación</Label>
        <div className="grid grid-cols-2 gap-2">
          {tokenLibrary.find(t => t.id === 'lighting')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => updateField('lightingType', state.lightingType === token.value ? '' : token.value)}
              className={`px-3 py-2 rounded-lg text-[11px] font-medium transition-all border text-left ${
                state.lightingType === token.value
                  ? 'bg-blue-500/20 border-blue-500/50 text-blue-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {token.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Atmósfera / Clima</Label>
        <div className="grid grid-cols-2 gap-2">
          {tokenLibrary.find(t => t.id === 'atmosphere')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => {
                const current = state.atmosphere;
                updateField('atmosphere', current === token.value ? '' : token.value);
              }}
              className={`px-3 py-2 rounded-lg text-[11px] font-medium transition-all border text-left ${
                state.atmosphere === token.value
                  ? 'bg-blue-500/20 border-blue-500/50 text-blue-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {token.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-2 block">Hora del Día</Label>
        <Input
          placeholder="ej: golden hour, blue hour, midnight..."
          value={state.timeOfDay}
          onChange={(e) => updateField('timeOfDay', e.target.value)}
          className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-blue-500 focus:ring-blue-500/20"
        />
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-2 block">Clima Adicional</Label>
        <Input
          placeholder="ej: light drizzle, heavy snow, clear sky..."
          value={state.weather}
          onChange={(e) => updateField('weather', e.target.value)}
          className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 focus:border-blue-500 focus:ring-blue-500/20"
        />
      </div>
    </div>
  );

  const renderFormat = () => (
    <div className="space-y-6">
      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Composición</Label>
        <div className="grid grid-cols-2 gap-2">
          {tokenLibrary.find(t => t.id === 'composition')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => updateField('composition', state.composition === token.value ? '' : token.value)}
              className={`px-3 py-2 rounded-lg text-[11px] font-medium transition-all border text-left ${
                state.composition === token.value
                  ? 'bg-violet-500/20 border-violet-500/50 text-violet-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {token.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Ángulo de Cámara</Label>
        <div className="grid grid-cols-2 gap-2">
          {tokenLibrary.find(t => t.id === 'angle')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => updateField('angle', state.angle === token.value ? '' : token.value)}
              className={`px-3 py-2 rounded-lg text-[11px] font-medium transition-all border text-left ${
                state.angle === token.value
                  ? 'bg-violet-500/20 border-violet-500/50 text-violet-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {token.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Profundidad de Campo</Label>
        <div className="grid grid-cols-1 gap-2">
          {tokenLibrary.find(t => t.id === 'dof')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => updateField('depthOfField', state.depthOfField === token.value ? '' : token.value)}
              className={`px-3 py-2 rounded-lg text-[11px] font-medium transition-all border text-left ${
                state.depthOfField === token.value
                  ? 'bg-violet-500/20 border-violet-500/50 text-violet-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {token.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Gradación de Color</Label>
        <div className="grid grid-cols-2 gap-2">
          {tokenLibrary.find(t => t.id === 'color')?.tokens.map(token => (
            <button
              key={token.id}
              onClick={() => updateField('colorGrading', state.colorGrading === token.value ? '' : token.value)}
              className={`px-3 py-2 rounded-lg text-[11px] font-medium transition-all border text-left ${
                state.colorGrading === token.value
                  ? 'bg-violet-500/20 border-violet-500/50 text-violet-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {token.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderYield = () => (
    <div className="space-y-6">
      {/* Aspect Ratio */}
      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-3 block">Aspect Ratio</Label>
        <div className="grid grid-cols-4 gap-2">
          {mjParameters.find(p => p.flag === '--ar')?.options?.map(ar => (
            <button
              key={ar}
              onClick={() => updateField('aspectRatio', ar)}
              className={`px-2 py-2 rounded-lg text-[10px] font-mono font-medium transition-all border text-center ${
                state.aspectRatio === ar
                  ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                  : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
              }`}
            >
              {ar}
            </button>
          ))}
        </div>
        {aspectRatioGuide[state.aspectRatio] && (
          <p className="text-[10px] text-zinc-500 mt-1.5">
            {aspectRatioGuide[state.aspectRatio].use}
          </p>
        )}
      </div>

      <Separator className="bg-zinc-800" />

      {/* Stylize */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <Label className="text-xs uppercase tracking-wider text-zinc-400">--stylize</Label>
          <span className="text-xs font-mono text-emerald-400">{state.stylize}</span>
        </div>
        <Slider
          value={[state.stylize]}
          onValueChange={([v]) => updateField('stylize', v)}
          min={0}
          max={1000}
          step={10}
          className="py-2"
        />
        <div className="mt-1">
          {stylizeGuide.map(g => {
            const [min, max] = g.range.split('-').map(Number);
            if (state.stylize >= min && state.stylize <= max) {
              return (
                <div key={g.range} className="flex items-start gap-2 text-[10px]">
                  <Info className="w-3 h-3 text-emerald-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="text-emerald-400 font-medium">{g.label}</span>
                    <span className="text-zinc-500"> — {g.description}</span>
                  </div>
                </div>
              );
            }
            return null;
          })}
        </div>
      </div>

      {/* Chaos */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <Label className="text-xs uppercase tracking-wider text-zinc-400">--chaos</Label>
          <span className="text-xs font-mono text-emerald-400">{state.chaos}</span>
        </div>
        <Slider
          value={[state.chaos]}
          onValueChange={([v]) => updateField('chaos', v)}
          min={0}
          max={100}
          step={1}
          className="py-2"
        />
        <div className="mt-1">
          {chaosGuide.map(g => {
            const [min, max] = g.range.split('-').map(Number);
            if (state.chaos >= min && state.chaos <= max) {
              return (
                <div key={g.range} className="flex items-start gap-2 text-[10px]">
                  <Info className="w-3 h-3 text-emerald-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="text-emerald-400 font-medium">{g.label}</span>
                    <span className="text-zinc-500"> — {g.description}</span>
                  </div>
                </div>
              );
            }
            return null;
          })}
        </div>
      </div>

      {/* Weird */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <Label className="text-xs uppercase tracking-wider text-zinc-400">--weird</Label>
          <span className="text-xs font-mono text-emerald-400">{state.weird}</span>
        </div>
        <Slider
          value={[state.weird]}
          onValueChange={([v]) => updateField('weird', v)}
          min={0}
          max={3000}
          step={10}
          className="py-2"
        />
        <p className="text-[10px] text-zinc-500 mt-1">0 = normal | 500-1000 = surrealista | 2000+ = experimental</p>
      </div>

      {/* Experimental */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <Label className="text-xs uppercase tracking-wider text-zinc-400">--exp (Experimental Detail)</Label>
          <span className="text-xs font-mono text-emerald-400">{state.exp}</span>
        </div>
        <Slider
          value={[state.exp]}
          onValueChange={([v]) => updateField('exp', v)}
          min={0}
          max={100}
          step={1}
          className="py-2"
        />
        <p className="text-[10px] text-zinc-500 mt-1">Sweet spot: 10-25 para mayor detalle sin distorsión</p>
      </div>

      <Separator className="bg-zinc-800" />

      {/* Toggles */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <Label className="text-xs text-zinc-300">--raw</Label>
            <p className="text-[10px] text-zinc-500">Control literal, menos interpretación artística</p>
          </div>
          <Switch checked={state.raw} onCheckedChange={(v) => updateField('raw', v)} />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <Label className="text-xs text-zinc-300">--hd</Label>
            <p className="text-[10px] text-zinc-500">HD nativo 2048px (1.33 GPU min)</p>
          </div>
          <Switch checked={state.hd} onCheckedChange={(v) => updateField('hd', v)} />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <Label className="text-xs text-zinc-300">--tile</Label>
            <p className="text-[10px] text-zinc-500">Textura seamless repetible</p>
          </div>
          <Switch checked={state.tile} onCheckedChange={(v) => updateField('tile', v)} />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <Label className="text-xs text-zinc-300">--personalization (-p)</Label>
            <p className="text-[10px] text-zinc-500">Aplica tu perfil de personalización</p>
          </div>
          <Switch checked={state.personalization} onCheckedChange={(v) => updateField('personalization', v)} />
        </div>
      </div>

      <Separator className="bg-zinc-800" />

      {/* Text inputs */}
      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-2 block">--seed</Label>
        <Input
          placeholder="Número de semilla para reproducibilidad"
          value={state.seed}
          onChange={(e) => updateField('seed', e.target.value)}
          className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 text-xs focus:border-emerald-500"
        />
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-2 block">--no (Prompt Negativo)</Label>
        <Input
          placeholder="text, watermark, blurry, deformed..."
          value={state.negative}
          onChange={(e) => updateField('negative', e.target.value)}
          className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 text-xs focus:border-emerald-500"
        />
      </div>

      <div>
        <Label className="text-xs uppercase tracking-wider text-zinc-400 mb-2 block">--sref (Style Reference URL)</Label>
        <Input
          placeholder="https://..."
          value={state.sref}
          onChange={(e) => updateField('sref', e.target.value)}
          className="bg-zinc-900 border-zinc-700 text-zinc-100 placeholder:text-zinc-600 text-xs focus:border-emerald-500"
        />
        {state.sref && (
          <div className="mt-2">
            <div className="flex justify-between items-center mb-1">
              <Label className="text-[10px] text-zinc-400">--sw (Style Weight)</Label>
              <span className="text-[10px] font-mono text-emerald-400">{state.sw}</span>
            </div>
            <Slider
              value={[state.sw]}
              onValueChange={([v]) => updateField('sw', v)}
              min={0}
              max={1000}
              step={10}
              className="py-1"
            />
          </div>
        )}
      </div>

      <div>
        <div className="flex justify-between items-center mb-2">
          <Label className="text-xs uppercase tracking-wider text-zinc-400">--iw (Image Weight)</Label>
          <span className="text-xs font-mono text-emerald-400">{state.iw.toFixed(2)}</span>
        </div>
        <Slider
          value={[state.iw]}
          onValueChange={([v]) => updateField('iw', v)}
          min={0}
          max={2}
          step={0.05}
          className="py-2"
        />
      </div>
    </div>
  );

  const layerContent = {
    K: renderKernel(),
    I: renderIntent(),
    M: renderMedium(),
    I2: renderIllumination(),
    F: renderFormat(),
    Y: renderYield(),
  };

  return (
    <div className="flex-1 overflow-auto">
      <div className="max-w-2xl mx-auto p-6">
        {/* Layer Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: layerColor }}
            />
            <h2 className="text-lg font-bold text-white">
              {activeLayer === 'I2' ? 'ILLUMINATION' :
               activeLayer === 'Y' ? 'YIELD / OUTPUT' :
               ['K','I','M','F'].includes(activeLayer)
                 ? {K:'KERNEL', I:'INTENT', M:'MEDIUM', F:'FORMAT'}[activeLayer]
                 : activeLayer}
            </h2>
          </div>
          <p className="text-xs text-zinc-500">
            {activeLayer === 'K' && 'Define QUÉ se renderiza — el núcleo del sujeto'}
            {activeLayer === 'I' && 'Define CÓMO se quiere que se vea — estilo y mood'}
            {activeLayer === 'M' && 'Define CON QUÉ se captura — cámara, lente, película'}
            {activeLayer === 'I2' && 'Define la LUZ y el AMBIENTE — iluminación y atmósfera'}
            {activeLayer === 'F' && 'Define el ENCUADRE — composición y formato'}
            {activeLayer === 'Y' && 'Define los PARÁMETROS técnicos de Midjourney v8.1'}
          </p>
        </div>

        {/* Content */}
        <div className="bg-zinc-900/50 rounded-xl border border-zinc-800 p-5">
          {layerContent[activeLayer] || null}
        </div>
      </div>
    </div>
  );
}
