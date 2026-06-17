import { useState } from 'react';
import { useKimify } from '@/hooks/useKimify';
import { KimifySidebar } from '@/components/KimifySidebar';
import { KimifyBuilder } from '@/components/KimifyBuilder';
import { KimifyPreview } from '@/components/KimifyPreview';
import { KimifyRecipes } from '@/components/KimifyRecipes';
import { Button } from '@/components/ui/button';
import { BookOpen, RotateCcw, Menu, X } from 'lucide-react';

export function KimifyApp() {
  const {
    state,
    activeLayer,
    setActiveLayer,
    updateField,
    toggleDetail,
    resetState,
    loadPreset,
    isLayerComplete,
    completionPercentage,
    autoInfer,
    lastInference,
  } = useKimify();

  const [showRecipes, setShowRecipes] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="kimify-pro h-full w-full bg-zinc-950 text-zinc-100 flex flex-col lg:flex-row overflow-hidden">
      {/* Mobile Header */}
      <div className="lg:hidden flex items-center justify-between px-4 py-3 border-b border-zinc-800 bg-zinc-950">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-rose-500 to-orange-500 flex items-center justify-center">
            <span className="text-white font-bold text-xs">K</span>
          </div>
          <h1 className="text-sm font-bold text-white">KIMIFY</h1>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 text-zinc-400"
            onClick={() => setShowRecipes(!showRecipes)}
          >
            <BookOpen className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 w-8 p-0 text-zinc-400"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </Button>
        </div>
      </div>

      {/* Mobile Layer Selector */}
      {mobileMenuOpen && (
        <div className="lg:hidden absolute top-14 left-0 right-0 z-50 bg-zinc-950 border-b border-zinc-800 max-h-64 overflow-auto">
          <KimifySidebar
            activeLayer={activeLayer}
            onSelectLayer={(layer) => {
              setActiveLayer(layer);
              setMobileMenuOpen(false);
            }}
            isLayerComplete={isLayerComplete}
            completionPercentage={completionPercentage}
          />
        </div>
      )}

      {/* Desktop Sidebar */}
      <div className="hidden lg:block">
        <KimifySidebar
          activeLayer={activeLayer}
          onSelectLayer={setActiveLayer}
          isLayerComplete={isLayerComplete}
          completionPercentage={completionPercentage}
        />
      </div>

      {/* Main Builder Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <div className="hidden lg:flex items-center justify-between px-6 py-3 border-b border-zinc-800 bg-zinc-950">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-medium text-zinc-300">
              Prompt Builder
            </h2>
            <span className="text-[10px] text-zinc-600">|</span>
            <span className="text-[10px] text-zinc-500">
              {activeLayer === 'K' && 'Define el sujeto'}
              {activeLayer === 'I' && 'Establece la intención'}
              {activeLayer === 'M' && 'Selecciona el medio'}
              {activeLayer === 'I2' && 'Configura la iluminación'}
              {activeLayer === 'F' && 'Ajusta el formato'}
              {activeLayer === 'Y' && 'Parametriza el output'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              className="h-8 text-[11px] text-zinc-400 hover:text-white hover:bg-zinc-800"
              onClick={() => setShowRecipes(!showRecipes)}
            >
              <BookOpen className="w-3.5 h-3.5 mr-1.5" />
              {showRecipes ? 'Cerrar Recetas' : 'Recetas'}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-8 text-[11px] text-zinc-400 hover:text-white hover:bg-zinc-800"
              onClick={resetState}
            >
              <RotateCcw className="w-3.5 h-3.5 mr-1.5" />
              Reset
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {showRecipes ? (
            <KimifyRecipes
              loadPreset={(preset) => {
                loadPreset(preset);
                setShowRecipes(false);
              }}
              onClose={() => setShowRecipes(false)}
            />
          ) : (
            <KimifyBuilder
              state={state}
              activeLayer={activeLayer}
              updateField={updateField}
              toggleDetail={toggleDetail}
              autoInfer={autoInfer}
              lastInference={lastInference}
            />
          )}
        </div>
      </div>

      {/* Preview Panel */}
      <div className="hidden lg:block">
        <KimifyPreview state={state} />
      </div>

      {/* Mobile Preview Toggle */}
      <div className="lg:hidden border-t border-zinc-800 bg-zinc-950">
        <KimifyPreview state={state} />
      </div>
    </div>
  );
}
