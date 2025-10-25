import { useState, useEffect } from "react";
import PreferencesSetup from "@/components/PreferencesSetup";
import MealPlanner from "@/components/MealPlanner";

const Index = () => {
  const [showPreferences, setShowPreferences] = useState(true);
  const [allergens, setAllergens] = useState<string[]>([]);
  const [dietaryPrefs, setDietaryPrefs] = useState<string[]>([]);

  useEffect(() => {
    const savedAllergens = localStorage.getItem("allergens");
    const savedDietary = localStorage.getItem("dietaryPrefs");
    
    if (savedAllergens && savedDietary) {
      setAllergens(JSON.parse(savedAllergens));
      setDietaryPrefs(JSON.parse(savedDietary));
      setShowPreferences(false);
    }
  }, []);

  const handlePreferencesComplete = (newAllergens: string[], newDietary: string[]) => {
    setAllergens(newAllergens);
    setDietaryPrefs(newDietary);
    setShowPreferences(false);
  };

  const handleBackToPreferences = () => {
    setShowPreferences(true);
  };

  return showPreferences ? (
    <PreferencesSetup onComplete={handlePreferencesComplete} />
  ) : (
    <MealPlanner 
      allergens={allergens} 
      dietaryPrefs={dietaryPrefs}
      onBack={handleBackToPreferences}
    />
  );
};

export default Index;
