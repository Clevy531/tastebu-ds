import { useState, useMemo } from 'react';
import { MenuItem, DietaryPreferences } from '../types';
import { mockMenuItems } from '../data/mockMenuData';
import { MealCard } from './MealCard';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Settings, Calendar } from 'lucide-react';
import { Card } from './ui/card';
import logo from 'figma:asset/70f214ea2ac6aa9aecf1b8959b9d70d7a7be81d9.png';

interface MealPlannerProps {
  preferences: DietaryPreferences;
  onEditPreferences: () => void;
}

export function MealPlanner({ preferences, onEditPreferences }: MealPlannerProps) {
  const [selectedDiningHall, setSelectedDiningHall] = useState<string>('all');
  const [selectedDate] = useState(new Date());

  const diningHalls = useMemo(() => {
    const halls = new Set(mockMenuItems.map((item) => item.diningHall));
    return Array.from(halls);
  }, []);

  const filteredItems = useMemo(() => {
    return mockMenuItems.filter((item) => {
      // Filter by dining hall
      if (selectedDiningHall !== 'all' && item.diningHall !== selectedDiningHall) {
        return false;
      }

      // Filter out items with allergens
      if (preferences.allergens.some((allergen) => item.allergens.includes(allergen))) {
        return false;
      }

      // Filter by dietary restrictions (item must have all selected tags)
      if (preferences.dietaryRestrictions.length > 0) {
        return preferences.dietaryRestrictions.every((restriction) =>
          item.dietaryTags.includes(restriction)
        );
      }

      return true;
    });
  }, [selectedDiningHall, preferences]);

  const getMealsByType = (mealType: 'breakfast' | 'lunch' | 'dinner') => {
    return filteredItems.filter((item) => item.mealType === mealType);
  };

  const breakfastItems = getMealsByType('breakfast');
  const lunchItems = getMealsByType('lunch');
  const dinnerItems = getMealsByType('dinner');

  const calculateTotalNutrition = (items: MenuItem[]) => {
    return items.reduce(
      (acc, item) => ({
        calories: acc.calories + item.nutrition.calories,
        protein: acc.protein + item.nutrition.protein,
        carbs: acc.carbs + item.nutrition.carbs,
        fat: acc.fat + item.nutrition.fat,
      }),
      { calories: 0, protein: 0, carbs: 0, fat: 0 }
    );
  };

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <div className="bg-zinc-900 border-b border-zinc-800 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-6">
              <img 
                src={logo} 
                alt="Taste BU-DS" 
                className="h-12 w-auto cursor-pointer"
                onClick={onEditPreferences}
              />
              <div>
                <h1 className="text-white">BU Dining Meal Planner</h1>
                <div className="flex items-center gap-2 text-sm text-gray-300 mt-1">
                  <Calendar className="h-4 w-4" />
                  <span>{selectedDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</span>
                </div>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-3">
              <Select value={selectedDiningHall} onValueChange={setSelectedDiningHall}>
                <SelectTrigger className="w-full sm:w-[200px]">
                  <SelectValue placeholder="Select dining hall" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Dining Halls</SelectItem>
                  {diningHalls.map((hall) => (
                    <SelectItem key={hall} value={hall}>
                      {hall}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                onClick={onEditPreferences}
                className="gap-2"
              >
                <Settings className="h-4 w-4" />
                Dietary Preferences
              </Button>
            </div>
          </div>

          {/* Active Preferences Summary */}
          {(preferences.allergens.length > 0 || preferences.dietaryRestrictions.length > 0) && (
            <div className="mt-4 p-3 bg-zinc-800 rounded-lg border border-zinc-700">
              <p className="text-sm text-gray-300">
                <span>Filtering for: </span>
                {preferences.allergens.length > 0 && (
                  <span>
                    <span className="text-red-500">Avoiding {preferences.allergens.join(', ')}</span>
                    {preferences.dietaryRestrictions.length > 0 && ' • '}
                  </span>
                )}
                {preferences.dietaryRestrictions.length > 0 && (
                  <span className="text-white">{preferences.dietaryRestrictions.join(', ')}</span>
                )}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Tabs defaultValue="all" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 max-w-2xl mx-auto">
            <TabsTrigger value="all">All Meals</TabsTrigger>
            <TabsTrigger value="breakfast">
              Breakfast
              <span className="ml-1.5 text-xs bg-gray-200 px-1.5 py-0.5 rounded">
                {breakfastItems.length}
              </span>
            </TabsTrigger>
            <TabsTrigger value="lunch">
              Lunch
              <span className="ml-1.5 text-xs bg-gray-200 px-1.5 py-0.5 rounded">
                {lunchItems.length}
              </span>
            </TabsTrigger>
            <TabsTrigger value="dinner">
              Dinner
              <span className="ml-1.5 text-xs bg-gray-200 px-1.5 py-0.5 rounded">
                {dinnerItems.length}
              </span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="space-y-8">
            {breakfastItems.length > 0 && (
              <div>
                <h2 className="text-white mb-4">Breakfast</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {breakfastItems.map((item) => (
                    <MealCard key={item.id} item={item} />
                  ))}
                </div>
              </div>
            )}

            {lunchItems.length > 0 && (
              <div>
                <h2 className="text-white mb-4">Lunch</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {lunchItems.map((item) => (
                    <MealCard key={item.id} item={item} />
                  ))}
                </div>
              </div>
            )}

            {dinnerItems.length > 0 && (
              <div>
                <h2 className="text-white mb-4">Dinner</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {dinnerItems.map((item) => (
                    <MealCard key={item.id} item={item} />
                  ))}
                </div>
              </div>
            )}

            {filteredItems.length === 0 && (
              <Card className="p-12 text-center bg-zinc-900 border-zinc-800">
                <p className="text-gray-300 mb-4">
                  No items match your dietary preferences for this dining hall.
                </p>
                <Button onClick={onEditPreferences} variant="outline" className="border-zinc-700 text-white hover:bg-zinc-800">
                  Adjust Preferences
                </Button>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="breakfast">
            {breakfastItems.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {breakfastItems.map((item) => (
                  <MealCard key={item.id} item={item} />
                ))}
              </div>
            ) : (
              <Card className="p-12 text-center bg-zinc-900 border-zinc-800">
                <p className="text-gray-300">No breakfast items match your preferences.</p>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="lunch">
            {lunchItems.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {lunchItems.map((item) => (
                  <MealCard key={item.id} item={item} />
                ))}
              </div>
            ) : (
              <Card className="p-12 text-center bg-zinc-900 border-zinc-800">
                <p className="text-gray-300">No lunch items match your preferences.</p>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="dinner">
            {dinnerItems.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dinnerItems.map((item) => (
                  <MealCard key={item.id} item={item} />
                ))}
              </div>
            ) : (
              <Card className="p-12 text-center bg-zinc-900 border-zinc-800">
                <p className="text-gray-300">No dinner items match your preferences.</p>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
