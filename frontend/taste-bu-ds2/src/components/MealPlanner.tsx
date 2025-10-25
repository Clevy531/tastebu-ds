import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ChevronLeft } from "lucide-react";
import logo from "@/assets/taste-logo.png";
import mealsData from "@/data/meals.json";

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
    tags: string[];
    description: string;
}

const mockMeals: Meal[] = mealsData as Meal[];

const MealPlanner = ({ allergens, dietaryPrefs, onBack }: MealPlannerProps) => {
    const [selectedMeal, setSelectedMeal] = useState<Meal | null>(null);

    const filterMeals = (mealType: "breakfast" | "lunch" | "dinner") => {
        return mockMeals.filter(meal => {
            if (meal.mealType !== mealType) return false;

            const hasAllergen = meal.allergens.some(a =>
                allergens.some(userAllergen =>
                    a.toLowerCase().includes(userAllergen.toLowerCase())
                )
            );
            if (hasAllergen) return false;

            if (dietaryPrefs.length > 0) {
                const matchesDietary = dietaryPrefs.some(pref =>
                    meal.tags.some(tag =>
                        tag.toLowerCase().includes(pref.toLowerCase())
                    )
                );
                if (!matchesDietary) return false;
            }

            return true;
        });
    };

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
            {meal.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                    {meal.tags.map(tag => (
                        <span key={tag} className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded">
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
                        <img src={logo} alt="Taste BU-DS" className="h-12 w-auto hover:opacity-80 transition-opacity" />
                    </button>
                    <h1 className="text-xl font-bold text-foreground">Your Meal Plan</h1>
                </div>
            </header>

            <div className="container mx-auto p-6 max-w-6xl">
                {/* Breakfast */}
                <section className="mb-10">
                    <h2 className="text-2xl font-bold text-foreground mb-4">Breakfast</h2>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {filterMeals("breakfast").length > 0 ? (
                            filterMeals("breakfast").map(meal => (
                                <MealCard key={meal.id} meal={meal} />
                            ))
                        ) : (
                            <p className="text-muted-foreground col-span-full">No meals match your preferences</p>
                        )}
                    </div>
                </section>

                {/* Lunch */}
                <section className="mb-10">
                    <h2 className="text-2xl font-bold text-foreground mb-4">Lunch</h2>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {filterMeals("lunch").length > 0 ? (
                            filterMeals("lunch").map(meal => (
                                <MealCard key={meal.id} meal={meal} />
                            ))
                        ) : (
                            <p className="text-muted-foreground col-span-full">No meals match your preferences</p>
                        )}
                    </div>
                </section>

                {/* Dinner */}
                <section className="mb-10">
                    <h2 className="text-2xl font-bold text-foreground mb-4">Dinner</h2>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {filterMeals("dinner").length > 0 ? (
                            filterMeals("dinner").map(meal => (
                                <MealCard key={meal.id} meal={meal} />
                            ))
                        ) : (
                            <p className="text-muted-foreground col-span-full">No meals match your preferences</p>
                        )}
                    </div>
                </section>

                <Button
                    onClick={onBack}
                    variant="outline"
                    className="border-border hover:bg-muted"
                >
                    <ChevronLeft size={16} />
                    Update Preferences
                </Button>
            </div>

            {/* Nutrition Details Dialog */}
            <Dialog open={selectedMeal !== null} onOpenChange={() => setSelectedMeal(null)}>
                <DialogContent className="bg-card border-border">
                    <DialogHeader>
                        <DialogTitle className="text-foreground">{selectedMeal?.name}</DialogTitle>
                    </DialogHeader>

                    {selectedMeal && (
                        <div className="space-y-4">
                            <p className="text-muted-foreground">{selectedMeal.hall}</p>

                            {/* Nutrition Facts */}
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
                                        <span>Carbohydrates</span>
                                        <span>{selectedMeal.carbs}g</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span>Fat</span>
                                        <span>{selectedMeal.fat}g</span>
                                    </div>
                                </div>
                            </div>

                            {/* Allergens */}
                            {selectedMeal.allergens.length > 0 && (
                                <div className="border-t border-border pt-4">
                                    <h4 className="font-semibold text-foreground mb-2">Contains Allergens</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedMeal.allergens.map(allergen => (
                                            <span key={allergen} className="text-sm bg-destructive/20 text-destructive px-2 py-1 rounded">
                        {allergen}
                      </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Dietary Tags */}
                            {selectedMeal.tags.length > 0 && (
                                <div className="border-t border-border pt-4">
                                    <h4 className="font-semibold text-foreground mb-2">Dietary Tags</h4>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedMeal.tags.map(tag => (
                                            <span key={tag} className="text-sm bg-primary/20 text-primary px-2 py-1 rounded">
                        {tag}
                      </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Meal Description */}
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
