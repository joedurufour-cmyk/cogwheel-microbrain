import { useState } from 'react';
import { recipes, recipeCategories } from '@/data/recipes';
import { stylePresets } from '@/data/kimifyData';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BookOpen, Zap, Copy, Check, ChevronRight, Sparkles, Star } from 'lucide-react';

export function KimifyRecipes({ loadPreset, onClose }) {
  const [activeTab, setActiveTab] = useState('recipes');
  const [selectedCategory, setSelectedCategory] = useState('Todos');
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  const filteredRecipes = selectedCategory === 'Todos'
    ? recipes
    : recipes.filter(r => r.category === selectedCategory);

  const selectedRecipeData = recipes.find(r => r.id === selectedRecipe);

  const loadRecipeAsPreset = (recipeId) => {
    const recipe = recipes.find(r => r.id === recipeId);
    if (!recipe) return;

    const preset = {
      subject: recipe.prompt.split(',')[0],
      styleIntent: recipe.category,
      ...recipe.parameters,
    };

    loadPreset(preset);
    onClose();
  };

  const copyPrompt = async (recipeId, prompt) => {
    await navigator.clipboard.writeText(prompt);
    setCopiedId(recipeId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-5 border-b border-zinc-800">
        <div className="flex items-center gap-2 mb-1">
          <BookOpen className="w-4 h-4 text-zinc-400" />
          <h2 className="text-lg font-bold text-white">Recetas KIMIFY</h2>
        </div>
        <p className="text-xs text-zinc-500">Prompts ejecutables con explicación para Midjourney v8.1</p>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
        <div className="px-5 pt-4">
          <TabsList className="bg-zinc-900 border border-zinc-800">
            <TabsTrigger value="recipes" className="text-xs data-[state=active]:bg-zinc-800">
              <Zap className="w-3 h-3 mr-1" /> Recetas
            </TabsTrigger>
            <TabsTrigger value="presets" className="text-xs data-[state=active]:bg-zinc-800">
              <Sparkles className="w-3 h-3 mr-1" /> Style Presets
            </TabsTrigger>
          </TabsList>
        </div>

        {/* Recipes Tab */}
        <div className={`flex-1 overflow-auto px-5 py-4 ${activeTab !== 'recipes' ? 'hidden' : ''}`}>
          {/* Category Filter */}
          <div className="flex flex-wrap gap-1.5 mb-4">
            {recipeCategories.map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-2.5 py-1 rounded-full text-[10px] font-medium transition-all border ${
                  selectedCategory === cat
                    ? 'bg-zinc-100 text-zinc-900 border-zinc-100'
                    : 'bg-zinc-900 border-zinc-700 text-zinc-400 hover:border-zinc-500'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Recipe Cards */}
          <div className="space-y-3">
            {filteredRecipes.map(recipe => (
              <div
                key={recipe.id}
                className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 hover:border-zinc-700 transition-all cursor-pointer group"
                onClick={() => setSelectedRecipe(recipe.id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-sm font-semibold text-white group-hover:text-zinc-200">{recipe.name}</h4>
                      <Badge variant="outline" className="text-[9px] border-zinc-700 text-zinc-500">
                        {recipe.category}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-zinc-500 mt-0.5">{recipe.description}</p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 flex-shrink-0 mt-0.5" />
                </div>

                {/* Preview */}
                <p className="text-[10px] text-zinc-600 italic line-clamp-2 mb-2">{recipe.preview}</p>

                {/* Tags & Params */}
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-1">
                    {recipe.tags.slice(0, 3).map(tag => (
                      <span key={tag} className="text-[9px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-500">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="flex gap-1">
                    {Object.entries(recipe.parameters).slice(0, 3).map(([key, val]) => (
                      <span key={key} className="text-[9px] font-mono text-zinc-500">
                        {key.replace('--', '')} {String(val).slice(0, 8)}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Presets Tab */}
        <div className={`flex-1 overflow-auto px-5 py-4 ${activeTab !== 'presets' ? 'hidden' : ''}`}>
          <div className="space-y-3">
            {stylePresets.map(preset => (
              <div
                key={preset.id}
                className="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 hover:border-zinc-700 transition-all cursor-pointer group"
                onClick={() => {
                  loadPreset({
                    stylize: preset.recommendedS,
                    chaos: preset.recommendedC,
                    aspectRatio: preset.recommendedAR,
                    styleIntent: preset.name,
                    ...preset.parameters,
                  });
                  onClose();
                }}
              >
                <div className="flex items-start justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <Star className="w-3.5 h-3.5 text-zinc-500" />
                    <h4 className="text-sm font-semibold text-white">{preset.name}</h4>
                  </div>
                  <Badge variant="outline" className="text-[9px] border-zinc-700 text-zinc-500 capitalize">
                    {preset.category}
                  </Badge>
                </div>
                <p className="text-[11px] text-zinc-500 mb-2">{preset.description}</p>
                <div className="flex gap-2">
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">S:{preset.recommendedS}</span>
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">C:{preset.recommendedC}</span>
                  <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400">AR:{preset.recommendedAR}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Tabs>

      {/* Recipe Detail Dialog */}
      <Dialog open={!!selectedRecipe} onOpenChange={() => setSelectedRecipe(null)}>
        <DialogContent className="max-w-2xl bg-zinc-950 border-zinc-800 text-zinc-100 max-h-[85vh] overflow-auto">
          {selectedRecipeData && (
            <>
              <DialogHeader>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-[10px] border-zinc-700 text-zinc-400">
                    {selectedRecipeData.category}
                  </Badge>
                </div>
                <DialogTitle className="text-xl text-white mt-2">{selectedRecipeData.name}</DialogTitle>
                <DialogDescription className="text-zinc-400">
                  {selectedRecipeData.description}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4 mt-2">
                {/* Preview */}
                <div className="rounded-lg bg-zinc-900 border border-zinc-800 p-3">
                  <p className="text-[11px] text-zinc-500 uppercase tracking-wider mb-1">Preview Visual</p>
                  <p className="text-sm text-zinc-300 italic">{selectedRecipeData.preview}</p>
                </div>

                {/* Full Prompt */}
                <div className="rounded-lg bg-zinc-900 border border-zinc-800 overflow-hidden">
                  <div className="flex items-center justify-between px-3 py-2 border-b border-zinc-800">
                    <span className="text-[10px] uppercase tracking-wider text-zinc-500">Prompt Completo</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 px-2 text-[10px]"
                      onClick={() => copyPrompt(selectedRecipeData.id, selectedRecipeData.prompt)}
                    >
                      {copiedId === selectedRecipeData.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    </Button>
                  </div>
                  <div className="p-3">
                    <code className="text-[11px] font-mono text-zinc-300 whitespace-pre-wrap break-all leading-relaxed">
                      {selectedRecipeData.prompt}
                    </code>
                  </div>
                </div>

                {/* Parameters */}
                <div>
                  <p className="text-[11px] text-zinc-500 uppercase tracking-wider mb-2">Parámetros</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(selectedRecipeData.parameters).map(([key, val]) => (
                      <Badge key={key} variant="outline" className="text-[10px] font-mono border-zinc-700 text-emerald-400">
                        {key} {String(val)}
                      </Badge>
                    ))}
                    <Badge variant="outline" className="text-[10px] font-mono border-zinc-700 text-blue-400">
                      --v 8.1
                    </Badge>
                  </div>
                </div>

                {/* Explanation */}
                <div className="rounded-lg bg-zinc-900/50 border border-zinc-800 p-3">
                  <p className="text-[11px] text-zinc-500 uppercase tracking-wider mb-1">Explicación KIMIFY</p>
                  <p className="text-xs text-zinc-300 leading-relaxed">{selectedRecipeData.explanation}</p>
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1">
                  {selectedRecipeData.tags.map(tag => (
                    <span key={tag} className="text-[9px] px-2 py-1 rounded-full bg-zinc-800 text-zinc-500">
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Action */}
                <Button
                  className="w-full bg-gradient-to-r from-rose-600 to-orange-600 hover:from-rose-500 hover:to-orange-500 text-white"
                  onClick={() => loadRecipeAsPreset(selectedRecipeData.id)}
                >
                  <Zap className="w-4 h-4 mr-2" />
                  Cargar en Builder
                </Button>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
