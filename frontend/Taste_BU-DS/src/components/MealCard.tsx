import { MenuItem } from '../types';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Info } from 'lucide-react';

interface MealCardProps {
  item: MenuItem;
}

export function MealCard({ item }: MealCardProps) {
  return (
    <Card className="p-4 hover:shadow-md transition-shadow bg-zinc-900 border-zinc-800">
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <h3 className="text-white mb-1">{item.name}</h3>
          <p className="text-sm text-gray-300 mb-2">{item.description}</p>
          <p className="text-xs text-gray-400">{item.diningHall}</p>
        </div>
        <Dialog>
          <DialogTrigger asChild>
            <button className="ml-2 p-1.5 rounded-full hover:bg-zinc-800 transition-colors">
              <Info className="h-4 w-4 text-gray-400" />
            </button>
          </DialogTrigger>
          <DialogContent className="max-w-md bg-zinc-900 border-zinc-800 text-white">
            <DialogHeader>
              <DialogTitle className="text-white">{item.name}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-300 mb-2">{item.description}</p>
                <p className="text-sm text-gray-400">
                  {item.diningHall} • {item.category}
                </p>
              </div>

              <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-4">
                <h4 className="text-sm mb-3 text-white">Nutrition Facts</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between border-b border-zinc-700 pb-2">
                    <span className="text-white">Calories</span>
                    <span className="text-white">{item.nutrition.calories}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Protein</span>
                    <span className="text-white">{item.nutrition.protein}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Carbohydrates</span>
                    <span className="text-white">{item.nutrition.carbs}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-300">Fat</span>
                    <span className="text-white">{item.nutrition.fat}g</span>
                  </div>
                  {item.nutrition.fiber !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-gray-300">Fiber</span>
                      <span className="text-white">{item.nutrition.fiber}g</span>
                    </div>
                  )}
                  {item.nutrition.sodium !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-gray-300">Sodium</span>
                      <span className="text-white">{item.nutrition.sodium}mg</span>
                    </div>
                  )}
                  {item.nutrition.sugar !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-gray-300">Sugar</span>
                      <span className="text-white">{item.nutrition.sugar}g</span>
                    </div>
                  )}
                </div>
              </div>

              {item.allergens.length > 0 && (
                <div>
                  <h4 className="text-sm mb-2 text-red-500">Contains Allergens:</h4>
                  <div className="flex flex-wrap gap-2">
                    {item.allergens.map((allergen) => (
                      <Badge key={allergen} variant="destructive" className="text-xs">
                        {allergen}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {item.dietaryTags.length > 0 && (
                <div>
                  <h4 className="text-sm mb-2 text-white">Dietary Tags:</h4>
                  <div className="flex flex-wrap gap-2">
                    {item.dietaryTags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-xs bg-zinc-700 text-white">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex gap-4 text-sm">
          <span className="text-white">
            <span className="text-gray-400">Cal:</span> {item.nutrition.calories}
          </span>
          <span className="text-white">
            <span className="text-gray-400">P:</span> {item.nutrition.protein}g
          </span>
          <span className="text-white">
            <span className="text-gray-400">C:</span> {item.nutrition.carbs}g
          </span>
          <span className="text-white">
            <span className="text-gray-400">F:</span> {item.nutrition.fat}g
          </span>
        </div>
      </div>

      <div className="flex flex-wrap gap-1 mt-3">
        {item.dietaryTags.slice(0, 3).map((tag) => (
          <Badge key={tag} variant="secondary" className="text-xs bg-zinc-800 text-gray-300 border-zinc-700">
            {tag}
          </Badge>
        ))}
      </div>
    </Card>
  );
}
