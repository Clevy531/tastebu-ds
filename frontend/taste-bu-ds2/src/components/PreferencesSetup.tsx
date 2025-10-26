import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { X } from "lucide-react";
import logo from "@/assets/taste-logo.png";

interface PreferencesSetupProps {
    onComplete: (allergens: string[], dietaryPrefs: string[]) => void;
}

const commonAllergens = [
    "Peanuts", "Tree Nuts", "Almonds", "Walnuts", "Cashews", "Pecans", "Pistachios",
    "Eggs", "Fish", "Shellfish", "Shrimp", "Crab", "Lobster",
    "Soy", "Wheat", "Gluten", "Sesame", "Mustard", "Celery",
    "Corn", "Coconut", "Pine Nuts", "Sunflower Seeds", "Poppy Seeds",
    "Fennel", "Peach", "Banana", "Avocado", "Kiwi", "Passion Fruit",
    "Papaya", "Chickpeas", "Lentils", "Dairy", "Seeds", "Seafood", 
];

const dietaryOptions = [
    "Vegan", "Vegetarian", "Pescatarian", "Halal", "Kosher",
    "Gluten-Free", "Low-Carb", "Low-Sodium", "Low-Fat", "High-Protein"
];

const PreferencesSetup = ({ onComplete }: PreferencesSetupProps) => {
    const [allergenSearch, setAllergenSearch] = useState("");
    const [dietarySearch, setDietarySearch] = useState("");
    const [selectedAllergens, setSelectedAllergens] = useState<string[]>([]);
    const [selectedDietary, setSelectedDietary] = useState<string[]>([]);

    const filteredAllergens = commonAllergens.filter(a =>
        a.toLowerCase().includes(allergenSearch.toLowerCase()) &&
        !selectedAllergens.includes(a)
    );

    const filteredDietary = dietaryOptions.filter(d =>
        d.toLowerCase().includes(dietarySearch.toLowerCase()) &&
        !selectedDietary.includes(d)
    );

    const addAllergen = (allergen: string) => {
        setSelectedAllergens([...selectedAllergens, allergen]);
        setAllergenSearch("");
    };

    const addDietary = (dietary: string) => {
        setSelectedDietary([...selectedDietary, dietary]);
        setDietarySearch("");
    };

    const removeAllergen = (allergen: string) => {
        setSelectedAllergens(selectedAllergens.filter(a => a !== allergen));
    };

    const removeDietary = (dietary: string) => {
        setSelectedDietary(selectedDietary.filter(d => d !== dietary));
    };

    const handleSave = () => {
        localStorage.setItem("allergens", JSON.stringify(selectedAllergens));
        localStorage.setItem("dietaryPrefs", JSON.stringify(selectedDietary));
        onComplete(selectedAllergens, selectedDietary);
    };

    return (
        <div className="min-h-screen bg-background">
            <div className="max-w-2xl mx-auto">
                {/* Logo */}
                <div className="flex justify-center mt-4 mb-2">
                    <img
                        src={logo}
                        alt="Taste BU-DS"
                        className="w-auto h-44 md:h-60 lg:h-72"
                    />
                </div>

                {/* Heading */}
                <h1 className="text-3xl md:text-4xl font-bold text-foreground text-center mb-1 leading-tight">
                    Set Your Preferences
                </h1>
                <p className="text-muted-foreground text-center mb-4 leading-tight">
                    Tell us about your dietary needs so we can personalize your meal options
                </p>

                {/* Allergens Section */}
                <div className="mb-8">
                    <label className="block text-foreground font-semibold mb-2">
                        Allergens to Avoid
                    </label>
                    <div className="relative">
                        <Input
                            type="text"
                            placeholder="Search allergens..."
                            value={allergenSearch}
                            onChange={(e) => setAllergenSearch(e.target.value)}
                            className="bg-card border-border text-foreground"
                        />
                        {allergenSearch && filteredAllergens.length > 0 && (
                            <div className="absolute z-10 w-full mt-1 bg-card border border-border rounded-md shadow-lg max-h-60 overflow-auto">
                                {filteredAllergens.map((allergen) => (
                                    <button
                                        key={allergen}
                                        onClick={() => addAllergen(allergen)}
                                        className="w-full text-left px-4 py-2 hover:bg-muted text-foreground transition-colors"
                                    >
                                        {allergen}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                        {selectedAllergens.map((allergen) => (
                            <span
                                key={allergen}
                                className="inline-flex items-center gap-1 bg-primary text-primary-foreground px-3 py-1 rounded-full text-sm"
                            >
                {allergen}
                                <button onClick={() => removeAllergen(allergen)} className="hover:opacity-70">
                  <X size={14} />
                </button>
              </span>
                        ))}
                    </div>
                </div>

                {/* Dietary Preferences Section */}
                <div className="mb-8">
                    <label className="block text-foreground font-semibold mb-2">
                        Dietary Preferences
                    </label>
                    <div className="relative">
                        <Input
                            type="text"
                            placeholder="Search dietary preferences..."
                            value={dietarySearch}
                            onChange={(e) => setDietarySearch(e.target.value)}
                            className="bg-card border-border text-foreground"
                        />
                        {dietarySearch && filteredDietary.length > 0 && (
                            <div className="absolute z-10 w-full mt-1 bg-card border border-border rounded-md shadow-lg max-h-60 overflow-auto">
                                {filteredDietary.map((dietary) => (
                                    <button
                                        key={dietary}
                                        onClick={() => addDietary(dietary)}
                                        className="w-full text-left px-4 py-2 hover:bg-muted text-foreground transition-colors"
                                    >
                                        {dietary}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                    <div className="flex flex-wrap gap-2 mt-2">
                        {selectedDietary.map((dietary) => (
                            <span
                                key={dietary}
                                className="inline-flex items-center gap-1 bg-primary text-primary-foreground px-3 py-1 rounded-full text-sm"
                            >
                {dietary}
                                <button onClick={() => removeDietary(dietary)} className="hover:opacity-70">
                  <X size={14} />
                </button>
              </span>
                        ))}
                    </div>
                </div>

                {/* Save Button */}
                <Button
                    onClick={handleSave}
                    className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
                    size="lg"
                >
                    Save Preferences & Continue
                </Button>
            </div>
        </div>
    );
};

export default PreferencesSetup;
