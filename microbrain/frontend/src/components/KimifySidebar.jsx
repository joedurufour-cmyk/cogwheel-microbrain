import { kimifySteps } from '@/data/kimifyData';
import { Check, Box, Flame, Camera, Sun, Frame, Terminal } from 'lucide-react';

const iconMap = {
  Box: <Box className="w-4 h-4" />,
  Flame: <Flame className="w-4 h-4" />,
  Camera: <Camera className="w-4 h-4" />,
  Sun: <Sun className="w-4 h-4" />,
  Frame: <Frame className="w-4 h-4" />,
  Terminal: <Terminal className="w-4 h-4" />,
};

export function KimifySidebar({ activeLayer, onSelectLayer, isLayerComplete, completionPercentage }) {
  return (
    <div className="w-full lg:w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col">
      {/* Header */}
      <div className="p-5 border-b border-zinc-800">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-rose-500 to-orange-500 flex items-center justify-center">
            <span className="text-white font-bold text-sm">K</span>
          </div>
          <h1 className="text-lg font-bold text-white tracking-tight">KIMIFY</h1>
        </div>
        <p className="text-[10px] text-zinc-500 uppercase tracking-widest">Midjourney v8.1</p>
      </div>

      {/* Progress */}
      <div className="px-5 py-3 border-b border-zinc-800">
        <div className="flex justify-between items-center mb-1.5">
          <span className="text-[10px] text-zinc-400 uppercase tracking-wider">Progreso</span>
          <span className="text-[10px] font-mono text-zinc-300">{completionPercentage}%</span>
        </div>
        <div className="w-full h-1 bg-zinc-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-rose-500 via-orange-500 to-emerald-500 transition-all duration-500"
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="flex-1 overflow-auto py-2">
        {kimifySteps.map((step, index) => {
          const isActive = activeLayer === step.id;
          const isComplete = isLayerComplete(step.id);
          const stepNum = index + 1;

          return (
            <button
              key={step.id}
              onClick={() => onSelectLayer(step.id)}
              className={`w-full text-left px-4 py-3 flex items-center gap-3 transition-all duration-200 group relative ${
                isActive
                  ? 'bg-zinc-900'
                  : 'hover:bg-zinc-900/50'
              }`}
            >
              {/* Active indicator */}
              {isActive && (
                <div className="absolute left-0 top-0 bottom-0 w-[2px]"
                  style={{ backgroundColor: step.color }}
                />
              )}

              {/* Step number / check */}
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0 transition-all ${
                  isComplete
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : isActive
                    ? 'text-white'
                    : 'bg-zinc-800 text-zinc-500'
                }`}
                style={isActive && !isComplete ? { backgroundColor: `${step.color}20`, color: step.color } : {}}
              >
                {isComplete ? <Check className="w-3 h-3" /> : stepNum}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <span
                    className={`text-xs font-semibold uppercase tracking-wider ${
                      isActive ? 'text-white' : 'text-zinc-400 group-hover:text-zinc-300'
                    }`}
                  >
                    {step.name}
                  </span>
                </div>
                <p className={`text-[10px] truncate ${isActive ? 'text-zinc-400' : 'text-zinc-600'}`}>
                  {step.subtitle}
                </p>
              </div>

              {/* Icon */}
              <div className={`flex-shrink-0 ${isActive ? 'text-zinc-400' : 'text-zinc-700'}`}>
                {iconMap[step.icon]}
              </div>
            </button>
          );
        })}
      </div>

      {/* Footer info */}
      <div className="p-4 border-t border-zinc-800 text-[10px] text-zinc-600">
        <p>KIMIFY v1.0</p>
        <p>Midjourney v8.1 compatible</p>
      </div>
    </div>
  );
}
