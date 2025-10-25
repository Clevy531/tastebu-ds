export interface NutritionInfo {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber?: number;
  sodium?: number;
  sugar?: number;
}

export interface MenuItem {
  id: string;
  name: string;
  diningHall: string;
  mealType: 'breakfast' | 'lunch' | 'dinner';
  category: string;
  nutrition: NutritionInfo;
  allergens: string[];
  dietaryTags: string[];
  description?: string;
}

export interface DietaryPreferences {
  allergens: string[];
  dietaryRestrictions: string[];
}
