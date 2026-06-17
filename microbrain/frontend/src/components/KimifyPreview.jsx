import { useMemo, useState } from 'react';
import { buildPrompt, buildParameterString, buildFullCommand, calculateQualityScore, estimateTokenCount } from '@/lib/promptBuilder';
import { exportToYAML, downloadYAML } from '@/lib/yamlExport';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

import { Copy, Download, Terminal, Sparkles, Zap, AlertCircle, Check } from 'lucide-react';

export function KimifyPreview({ state }) {
  const [copied, setCopied] = useState(false);
  const [yamlCopied, setYamlCopied] = useState(false);

  const prompt = useMemo(() => buildPrompt(state), [state]);
  const params = useMemo(() => buildParameterString(state), [state]);
  const fullCommand = useMemo(() => buildFullCommand(state), [state]);
  const qualityScore = useMemo(() => calculateQualityScore(state), [state]);
  const tokenEstimate = useMemo(() => estimateTokenCount(state), [state]);

  const qualityLabel = useMemo(() => {
    if (qualityScore >= 90) return { label: 'EXCELENTE', color: 'text-emerald-400', bg: 'bg-emerald-500/10' };
    if (qualityScore >= 70) return { label: 'BUENO', color: 'text-blue-400', bg: 'bg-blue-500/10' };
    if (qualityScore >= 50) return { label: 'REGULAR', color: 'text-yellow-400', bg: 'bg-yellow-500/10' };
    return { label: 'BÁSICO', color: 'text-zinc-400', bg: 'bg-zinc-500/10' };
  }, [qualityScore]);

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(fullCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const copyYAML = async () => {
    const yaml = exportToYAML(state);
    await navigator.clipboard.writeText(yaml);
    setYamlCopied(true);
    setTimeout(() => setYamlCopied(false), 2000);
  };

  const handleDownloadYAML = () => {
    const yaml = exportToYAML(state);
    downloadYAML(yaml, `kimify-${Date.now()}.yml`);
  };

  const hasContent = prompt.length > 0;

  return (
    <div className="w-full lg:w-96 bg-zinc-950 border-l border-zinc-800 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-zinc-800">
        <div className="flex items-center gap-2 mb-3">
          <Terminal className="w-4 h-4 text-zinc-400" />
          <h3 className="text-sm font-semibold text-white">Output Preview</h3>
        </div>

        {/* Quality Score */}
        <div className={`rounded-lg p-3 ${qualityLabel.bg} border border-zinc-800`}>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-zinc-400" />
              <span className="text-[10px] uppercase tracking-wider text-zinc-400">Calidad del Prompt</span>
            </div>
            <Badge variant="outline" className={`text-[10px] ${qualityLabel.color} border-zinc-700`}>
              {qualityLabel.label}
            </Badge>
          </div>
          <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${qualityScore}%`,
                backgroundColor: qualityScore >= 90 ? '#10B981' : qualityScore >= 70 ? '#3B82F6' : qualityScore >= 50 ? '#F59E0B' : '#6B7280',
              }}
            />
          </div>
          <div className="flex justify-between mt-1">
            <span className="text-[10px] text-zinc-500">Score: {qualityScore}/100</span>
            <span className="text-[10px] text-zinc-500">~{tokenEstimate} tokens</span>
          </div>
        </div>
      </div>

      {/* Prompt Preview */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {!hasContent ? (
          <div className="flex flex-col items-center justify-center py-12 text-zinc-600">
            <AlertCircle className="w-8 h-8 mb-3" />
            <p className="text-xs">Empieza construyendo tu prompt</p>
            <p className="text-[10px] mt-1">Ve a KERNEL y define el sujeto</p>
          </div>
        ) : (
          <>
            {/* Final Command */}
            <div className="bg-zinc-900 rounded-lg border border-zinc-800 overflow-hidden">
              <div className="flex items-center justify-between px-3 py-2 bg-zinc-900 border-b border-zinc-800">
                <span className="text-[10px] uppercase tracking-wider text-zinc-500">Comando Midjourney</span>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 px-2 text-[10px] text-zinc-400 hover:text-white"
                    onClick={copyToClipboard}
                  >
                    {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    {copied ? ' Copiado' : ' Copiar'}
                  </Button>
                </div>
              </div>
              <div className="p-3">
                <code className="text-[11px] font-mono text-zinc-300 whitespace-pre-wrap break-all leading-relaxed">
                  <span className="text-emerald-500">/imagine</span>{' '}
                  <span className="text-zinc-100">{prompt}</span>{' '}
                  <span className="text-blue-400">{params}</span>
                </code>
              </div>
            </div>

            {/* Decomposed View */}
            <div className="space-y-3">
              <h4 className="text-[10px] uppercase tracking-wider text-zinc-500 font-medium">Descomposición KIMIFY</h4>

              {state.subject && (
                <div className="rounded-lg border border-zinc-800/50 bg-zinc-900/30 p-3">
                  <div className="flex items-center gap-1.5 mb-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-rose-500" />
                    <span className="text-[10px] font-bold text-rose-400 uppercase">K — Kernel</span>
                  </div>
                  <p className="text-[11px] text-zinc-300 font-mono">{state.subject}</p>
                  {state.subjectDetails.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {state.subjectDetails.map((d, i) => (
                        <span key={i} className="text-[9px] px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-300">{d}</span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {(state.styleIntent || state.mood || state.visualStyle) && (
                <div className="rounded-lg border border-zinc-800/50 bg-zinc-900/30 p-3">
                  <div className="flex items-center gap-1.5 mb-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-orange-500" />
                    <span className="text-[10px] font-bold text-orange-400 uppercase">I — Intent</span>
                  </div>
                  <div className="space-y-0.5">
                    {state.styleIntent && <p className="text-[11px] text-zinc-300 font-mono">{state.styleIntent}</p>}
                    {state.mood && <p className="text-[11px] text-zinc-300 font-mono">{state.mood}</p>}
                    {state.visualStyle && <p className="text-[11px] text-zinc-300 font-mono">{state.visualStyle}</p>}
                    {state.eraPeriod && <p className="text-[11px] text-zinc-300 font-mono">{state.eraPeriod}</p>}
                  </div>
                </div>
              )}

              {(state.cameraType || state.lensType || state.filmType) && (
                <div className="rounded-lg border border-zinc-800/50 bg-zinc-900/30 p-3">
                  <div className="flex items-center gap-1.5 mb-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-teal-500" />
                    <span className="text-[10px] font-bold text-teal-400 uppercase">M — Medium</span>
                  </div>
                  <div className="space-y-0.5">
                    {state.cameraType && <p className="text-[11px] text-zinc-300 font-mono">{state.cameraType}</p>}
                    {state.lensType && <p className="text-[11px] text-zinc-300 font-mono">{state.lensType}</p>}
                    {state.filmType && <p className="text-[11px] text-zinc-300 font-mono">{state.filmType}</p>}
                  </div>
                </div>
              )}

              {(state.lightingType || state.atmosphere) && (
                <div className="rounded-lg border border-zinc-800/50 bg-zinc-900/30 p-3">
                  <div className="flex items-center gap-1.5 mb-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                    <span className="text-[10px] font-bold text-blue-400 uppercase">I — Illumination</span>
                  </div>
                  <div className="space-y-0.5">
                    {state.lightingType && <p className="text-[11px] text-zinc-300 font-mono">{state.lightingType}</p>}
                    {state.timeOfDay && <p className="text-[11px] text-zinc-300 font-mono">{state.timeOfDay}</p>}
                    {state.atmosphere && <p className="text-[11px] text-zinc-300 font-mono">{state.atmosphere}</p>}
                  </div>
                </div>
              )}

              {(state.composition || state.angle || state.depthOfField || state.colorGrading) && (
                <div className="rounded-lg border border-zinc-800/50 bg-zinc-900/30 p-3">
                  <div className="flex items-center gap-1.5 mb-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-violet-500" />
                    <span className="text-[10px] font-bold text-violet-400 uppercase">F — Format</span>
                  </div>
                  <div className="space-y-0.5">
                    {state.composition && <p className="text-[11px] text-zinc-300 font-mono">{state.composition}</p>}
                    {state.angle && <p className="text-[11px] text-zinc-300 font-mono">{state.angle}</p>}
                    {state.depthOfField && <p className="text-[11px] text-zinc-300 font-mono">{state.depthOfField}</p>}
                    {state.colorGrading && <p className="text-[11px] text-zinc-300 font-mono">{state.colorGrading}</p>}
                  </div>
                </div>
              )}

              {/* Parameters */}
              <div className="rounded-lg border border-zinc-800/50 bg-zinc-900/30 p-3">
                <div className="flex items-center gap-1.5 mb-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  <span className="text-[10px] font-bold text-emerald-400 uppercase">Y — Yield / Parámetros</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  <Badge variant="outline" className="text-[9px] font-mono border-zinc-700 text-zinc-400">
                    --ar {state.aspectRatio}
                  </Badge>
                  {state.stylize !== 100 && (
                    <Badge variant="outline" className="text-[9px] font-mono border-zinc-700 text-zinc-400">
                      --s {state.stylize}
                    </Badge>
                  )}
                  {state.chaos > 0 && (
                    <Badge variant="outline" className="text-[9px] font-mono border-zinc-700 text-zinc-400">
                      --c {state.chaos}
                    </Badge>
                  )}
                  {state.weird > 0 && (
                    <Badge variant="outline" className="text-[9px] font-mono border-zinc-700 text-zinc-400">
                      --w {state.weird}
                    </Badge>
                  )}
                  {state.raw && (
                    <Badge variant="outline" className="text-[9px] font-mono border-zinc-700 text-zinc-400">
                      --raw
                    </Badge>
                  )}
                  {state.hd && (
                    <Badge variant="outline" className="text-[9px] font-mono border-zinc-700 text-zinc-400">
                      --hd
                    </Badge>
                  )}
                  {state.exp > 0 && (
                    <Badge variant="outline" className="text-[9px] font-mono border-zinc-700 text-zinc-400">
                      --exp {state.exp}
                    </Badge>
                  )}
                  {state.negative && (
                    <Badge variant="outline" className="text-[9px] font-mono border-zinc-700 text-zinc-400">
                      --no {state.negative}
                    </Badge>
                  )}
                  {state.tile && (
                    <Badge variant="outline" className="text-[9px] font-mono border-zinc-700 text-zinc-400">
                      --tile
                    </Badge>
                  )}
                  {state.personalization && (
                    <Badge variant="outline" className="text-[9px] font-mono border-zinc-700 text-zinc-400">
                      --p
                    </Badge>
                  )}
                  <Badge variant="outline" className="text-[9px] font-mono border-emerald-800 text-emerald-400">
                    --v 8.1
                  </Badge>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-zinc-800 space-y-2">
        <Button
          className="w-full h-9 bg-gradient-to-r from-rose-600 to-orange-600 hover:from-rose-500 hover:to-orange-500 text-white text-xs font-medium"
          onClick={copyToClipboard}
          disabled={!hasContent}
        >
          <Zap className="w-3.5 h-3.5 mr-1.5" />
          Copiar Comando
        </Button>
        <div className="flex gap-2">
          <Button
            variant="outline"
            className="flex-1 h-8 text-[10px] border-zinc-700 text-zinc-400 hover:text-white hover:bg-zinc-800"
            onClick={copyYAML}
          >
            {yamlCopied ? <Check className="w-3 h-3 mr-1 text-emerald-400" /> : <Copy className="w-3 h-3 mr-1" />}
            YAML
          </Button>
          <Button
            variant="outline"
            className="flex-1 h-8 text-[10px] border-zinc-700 text-zinc-400 hover:text-white hover:bg-zinc-800"
            onClick={handleDownloadYAML}
            disabled={!hasContent}
          >
            <Download className="w-3 h-3 mr-1" />
            Exportar .yml
          </Button>
        </div>
      </div>
    </div>
  );
}
