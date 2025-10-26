import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { ChevronLeft, AlertCircle } from "lucide-react";
import logo from "@/assets/taste-logo.png";

interface MealPlannerProps {
    allergens: string[];
    dietaryPrefs: string[];
    onBack: () => void;
}

interface Meal {
    id: string;
    name: string;
    hall: string;
    mealType: "breakfast" | "lunch" | "dinner";
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    allergens: string[];
    dietaryRestrictions: string[];
    description: string;
    ingredients: string[];
}

// Use environment variable for API URL, fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5001";

const MealPlanner = ({ allergens, dietaryPrefs, onBack }: MealPlannerProps) => {
    const [meals, setMeals] = useState<Meal[]>([]);
    const [selectedMeal, setSelectedMeal] = useState<Meal | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Fetch meals from Flask backend
    const fetchMeals = async () => {
        setLoading(true);
        setError(null);
        
        try {
            console.log(`🔌 Connecting to: ${API_BASE_URL}/filter_foods`);
            
            const response = await fetch(`${API_BASE_URL}/filter_foods`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    allergies: allergens, 
                    dietaryRestrictions: dietaryPrefs 
                })
            });

            if (!response.ok) {
                throw new Error(`Backend error: ${response.status}`);
            }

            const data = await response.json();
            console.log("Backend response:", data);

            // Handle the backend response structure
            let safeMeals: Meal[] = [];
            if (data.safe_foods) {
                safeMeals = data.safe_foods;
            } else if (Array.isArray(data)) {
                safeMeals = data;
            }

            setMeals(safeMeals);
        } catch (error) {
            console.error("Error fetching meals:", error);
            setError(error instanceof Error ? error.message : "Failed to fetch meals");
        } finally {
            setLoading(false);
        }
    };

    // Refetch meals whenever allergies or dietary preferences change
    useEffect(() => {
        fetchMeals();
    }, [allergens, dietaryPrefs]);

    const filterMealsByType = (mealType: Meal["mealType"]) =>
        meals.filter(meal => meal.mealType === mealType);

    const MealCard = ({ meal }: { meal: Meal }) => (
        <Card
            className="bg-card border-border p-4 hover:border-primary cursor-pointer transition-all"
            onClick={() => setSelectedMeal(meal)}
        >
            <h3 className="font-semibold text-foreground mb-1">{meal.name}</h3>
            <p className="text-sm text-muted-foreground mb-3">{meal.hall}</p>
            <div className="flex gap-4 text-sm text-foreground">
                <span>{meal.calories} cal</span>
                <span>{meal.protein}g protein</span>
                <span>{meal.carbs}g carbs</span>
                <span>{meal.fat}g fat</span>
            </div>
            {meal.dietaryRestrictions && meal.dietaryRestrictions.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                    {meal.dietaryRestrictions.map(tag => (
                        <span
                            key={tag}
                            className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded"
                        >
                            {tag}
                        </span>
                    ))}
                </div>
            )}
        </Card>
    );

    return (
        <div className="min-h-screen bg-background">
            <header className="bg-card border-b border-border p-4 sticky top-0 z-10">
                <div className="container mx-auto flex items-center gap-4">
                    <button onClick={onBack}>
                        <img
                            src={logo}
                            alt="Taste BU-DS"
                            className="h-12 w-auto hover:opacity-80 transition-opacity"
                        />
                    </button>
                    <h1 className="text-xl font-bold text-foreground">Your Meal Plan</h1>
                </div>
            </header>

            <div className="container mx-auto p-6 max-w-6xl">
                {/* Error state */}
                {error && (
                    <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 mb-6 flex items-center gap-3">
                        <AlertCircle className="text-destructive" size={20} />
                        <div className="flex-1">
                            <p className="text-destructive font-semibold">Error loading meals</p>
                            <p className="text-sm text-muted-foreground">{error}</p>
                            <p className="text-sm text-muted-foreground mt-1">
                                Backend URL: {API_BASE_URL}
                            </p>
                            <p className="text-sm text-muted-foreground">
                                Make sure your Flask backend is running
                            </p>
                        </div>
                        <Button 
                            onClick={fetchMeals} 
                            variant="outline" 
                            size="sm"
                        >
                            Retry
                        </Button>
                    </div>
                )}

                {/* Loading state */}
                {loading && (
                    <div className="text-center py-12">
                        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                        <p className="text-muted-foreground mt-4">Loading meals...</p>
                    </div>
                )}

                {/* Meals sections */}
                {!loading && !error && (
                    <>
                        {(["breakfast", "lunch", "dinner"] as Meal["mealType"][]).map(mealType => {
                            const mealsOfType = filterMealsByType(mealType);
                            return (
                                <section key={mealType} className="mb-10">
                                    <h2 className="text-2xl font-bold text-foreground mb-4 capitalize">
                                        {mealType}
                                    </h2>
                                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                                        {mealsOfType.length > 0 ? (
                                            mealsOfType.map(meal => <MealCard key={meal.id} meal={meal} />)
                                        ) : (
                                            <p className="text-muted-foreground col-span-full">
                                                No meals match your preferences
                                            </p>
                                        )}
                                    </div>
                                </section>
                            );
                        })}

                        <Button
                            onClick={onBack}
                            variant="outline"
                            className="border-border hover:bg-muted"
                        >
                            <ChevronLeft size={16} />
                            Update Preferences
                        </Button>
                    </>
                )}
            </div>

            {/* Nutrition Dialog */}
            <Dialog open={selectedMeal !== null} onOpenChange={() => setSelectedMeal(null)}>
                <DialogContent className="bg-card border-border">
                    <DialogHeader>
                        <DialogTitle className="text-foreground">{selectedMeal?.name}</DialogTitle>
                    </DialogHeader>

                    {selectedMeal && (
                        <div className="space-y-4">
                            <p className="text-muted-foreground">{selectedMeal.hall}</p>

                            <div className="border-t border-border pt-4">
                                <h4 className="font-semibold text-foreground mb-3">Nutrition Facts</h4>
                                <div className="space-y-2 text-foreground">
                                    <div className="flex justify-between">
                                        <span>Calories</span>
                                        <span className="font-semibold">{selectedMeal.calories}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Protein</span>
                                        <span>{selectedMeal.protein}g</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Carbs</span>
                                        <span>{selectedMeal.carbs}g</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Fat</span>
                                        <span>{selectedMeal.fat}g</span>
                                    </div>
                                </div>
                            </div>

                            {selectedMeal.allergens && selectedMeal.allergens.length > 0 && (
                                <div className="border-t border-border pt-4">
                                    <h4 className="font-semibold text-foreground mb-2">Contains Allergens</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedMeal.allergens.map(allergen => (
                                            <span
                                                key={allergen}
                                                className="text-sm bg-destructive/20 text-destructive px-2 py-1 rounded"
                                            >
                                                {allergen}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {selectedMeal.dietaryRestrictions && selectedMeal.dietaryRestrictions.length > 0 && (
                                <div className="border-t border-border pt-4">
                                    <h4 className="font-semibold text-foreground mb-2">Dietary Restrictions</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedMeal.dietaryRestrictions.map(tag => (
                                            <span
                                                key={tag}
                                                className="text-sm bg-primary/20 text-primary px-2 py-1 rounded"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {selectedMeal.ingredients && selectedMeal.ingredients.length > 0 && (
                                <div className="border-t border-border pt-4">
                                    <h4 className="font-semibold text-foreground mb-2">Ingredients</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedMeal.ingredients.map(ingredient => (
                                            <span
                                                key={ingredient}
                                                className="text-xs bg-muted text-foreground px-2 py-1 rounded"
                                            >
                                                {ingredient}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {selectedMeal.description && (
                                <div className="border-t border-border pt-4">
                                    <h4 className="font-semibold text-foreground mb-2">Description</h4>
                                    <p className="text-sm text-muted-foreground">{selectedMeal.description}</p>
                                </div>
                            )}
                        </div>
                    )}
                </DialogContent>
            </Dialog>
        </div>
    );
};

export default MealPlanner;