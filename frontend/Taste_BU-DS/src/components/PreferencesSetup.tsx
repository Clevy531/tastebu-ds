import { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { DietaryPreferences } from '../types';
import { ArrowRight, Search, X } from 'lucide-react';
import logo from 'figma:asset/70f214ea2ac6aa9aecf1b8959b9d70d7a7be81d9.png';

interface PreferencesSetupProps {
  onComplete: (preferences: DietaryPreferences) => void;
  initialPreferences?: DietaryPreferences;
}

const COMMON_ALLERGENS = [
  'Milk',
  'Eggs',
  'Fish',
  'Shellfish',
  'Tree Nuts',
  'Peanuts',
  'Wheat',
  'Gluten',
  'Soy',
  'Sesame',
];

const DIETARY_RESTRICTIONS = [
  'Vegan',
  'Vegetarian',
  'Gluten-Free',
  'Dairy-Free',
  'Nut-Free',
  'Halal',
  'Kosher',
  'Low-Carb',
];

export function PreferencesSetup({ onComplete, initialPreferences }: PreferencesSetupProps) {
  const [allergens, setAllergens] = useState<string[]>(initialPreferences?.allergens || []);
  const [dietaryRestrictions, setDietaryRestrictions] = useState<string[]>(
    initialPreferences?.dietaryRestrictions || []
  );
  const [allergenSearch, setAllergenSearch] = useState('');
  const [dietarySearch, setDietarySearch] = useState('');
  const [showAllergenSuggestions, setShowAllergenSuggestions] = useState(false);
  const [showDietarySuggestions, setShowDietarySuggestions] = useState(false);

  const allergenInputRef = useRef<HTMLInputElement>(null);
  const dietaryInputRef = useRef<HTMLInputElement>(null);

  const addAllergen = (allergen: string) => {
    if (!allergens.includes(allergen)) {
      setAllergens((prev) => [...prev, allergen]);
    }
    setAllergenSearch('');
    setShowAllergenSuggestions(false);
  };

  const removeAllergen = (allergen: string) => {
    setAllergens((prev) => prev.filter((a) => a !== allergen));
  };

  const addDietaryRestriction = (restriction: string) => {
    if (!dietaryRestrictions.includes(restriction)) {
      setDietaryRestrictions((prev) => [...prev, restriction]);
    }
    setDietarySearch('');
    setShowDietarySuggestions(false);
  };

  const removeDietaryRestriction = (restriction: string) => {
    setDietaryRestrictions((prev) => prev.filter((r) => r !== restriction));
  };

  const handleSubmit = () => {
    onComplete({ allergens, dietaryRestrictions });
  };

  const filteredAllergens = COMMON_ALLERGENS.filter(
    (allergen) =>
      allergen.toLowerCase().includes(allergenSearch.toLowerCase()) &&
      !allergens.includes(allergen)
  );

  const filteredDietaryRestrictions = DIETARY_RESTRICTIONS.filter(
    (restriction) =>
      restriction.toLowerCase().includes(dietarySearch.toLowerCase()) &&
      !dietaryRestrictions.includes(restriction)
  );

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (allergenInputRef.current && !allergenInputRef.current.contains(event.target as Node)) {
        setShowAllergenSuggestions(false);
      }
      if (dietaryInputRef.current && !dietaryInputRef.current.contains(event.target as Node)) {
        setShowDietarySuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="min-h-screen bg-black py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Logo */}
        <div className="mb-8">
          <img 
            src={logo} 
            alt="Taste BU-DS" 
            className="h-16 w-auto cursor-pointer"
          />
        </div>

        <div className="text-center mb-8">
          <h1 className="text-white mb-2">BU Dining Meal Planner</h1>
          <p className="text-xl text-gray-300">
            Set your dietary preferences to see personalized meal options
          </p>
        </div>

        <div className="space-y-6">
          {/* Allergens Section */}
          <Card className="p-6 bg-zinc-900 border-zinc-800">
            <h2 className="text-white mb-4">Allergens to Avoid</h2>
            <p className="text-gray-300 mb-4">
              Search and select any allergens you need to avoid. We'll filter out menu items containing these ingredients.
            </p>
            <div className="relative" ref={allergenInputRef}>
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 z-10" />
              <Input
                type="text"
                placeholder="Search allergens..."
                value={allergenSearch}
                onChange={(e) => {
                  setAllergenSearch(e.target.value);
                  setShowAllergenSuggestions(true);
                }}
                onFocus={() => setShowAllergenSuggestions(true)}
                className="pl-10 bg-zinc-800 border-zinc-700 text-white placeholder:text-gray-500"
              />
              {showAllergenSuggestions && allergenSearch && filteredAllergens.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-zinc-800 border border-zinc-700 rounded-md shadow-lg max-h-48 overflow-y-auto z-20">
                  {filteredAllergens.map((allergen) => (
                    <button
                      key={allergen}
                      onClick={() => addAllergen(allergen)}
                      className="w-full text-left px-4 py-2 hover:bg-zinc-700 text-sm text-white"
                    >
                      {allergen}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {allergens.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-4">
                {allergens.map((allergen) => (
                  <Badge
                    key={allergen}
                    variant="destructive"
                    className="pl-3 pr-1 py-1 gap-1"
                  >
                    {allergen}
                    <button
                      onClick={() => removeAllergen(allergen)}
                      className="ml-1 rounded-full hover:bg-red-700 p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </Card>

          {/* Dietary Restrictions Section */}
          <Card className="p-6 bg-zinc-900 border-zinc-800">
            <h2 className="text-white mb-4">Dietary Preferences</h2>
            <p className="text-gray-300 mb-4">
              Search and select your dietary preferences to see only items that match your lifestyle.
            </p>
            <div className="relative" ref={dietaryInputRef}>
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 z-10" />
              <Input
                type="text"
                placeholder="Search dietary preferences..."
                value={dietarySearch}
                onChange={(e) => {
                  setDietarySearch(e.target.value);
                  setShowDietarySuggestions(true);
                }}
                onFocus={() => setShowDietarySuggestions(true)}
                className="pl-10 bg-zinc-800 border-zinc-700 text-white placeholder:text-gray-500"
              />
              {showDietarySuggestions && dietarySearch && filteredDietaryRestrictions.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-zinc-800 border border-zinc-700 rounded-md shadow-lg max-h-48 overflow-y-auto z-20">
                  {filteredDietaryRestrictions.map((restriction) => (
                    <button
                      key={restriction}
                      onClick={() => addDietaryRestriction(restriction)}
                      className="w-full text-left px-4 py-2 hover:bg-zinc-700 text-sm text-white"
                    >
                      {restriction}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {dietaryRestrictions.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-4">
                {dietaryRestrictions.map((restriction) => (
                  <Badge
                    key={restriction}
                    variant="secondary"
                    className="pl-3 pr-1 py-1 gap-1"
                  >
                    {restriction}
                    <button
                      onClick={() => removeDietaryRestriction(restriction)}
                      className="ml-1 rounded-full hover:bg-gray-300 p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </Card>

          {/* Summary */}
          <Card className="p-6 bg-zinc-900 border-red-600">
            <h3 className="text-white mb-3">Your Selections</h3>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-300">Allergens to avoid: </span>
                <span className="text-white">
                  {allergens.length > 0 ? allergens.join(', ') : 'None selected'}
                </span>
              </div>
              <div>
                <span className="text-gray-300">Dietary preferences: </span>
                <span className="text-white">
                  {dietaryRestrictions.length > 0
                    ? dietaryRestrictions.join(', ')
                    : 'None selected'}
                </span>
              </div>
            </div>
          </Card>

          <div className="flex justify-center">
            <Button
              size="lg"
              onClick={handleSubmit}
              className="bg-red-600 hover:bg-red-700 text-white group"
            >
              View My Meal Options
              <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
