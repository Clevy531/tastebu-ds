import { useState, useEffect } from 'react';
import { PreferencesSetup } from './components/PreferencesSetup';
import { MealPlanner } from './components/MealPlanner';
import { DietaryPreferences } from './types';

export default function App() {
  const [preferences, setPreferences] = useState<DietaryPreferences | null>(null);
  const [showSetup, setShowSetup] = useState(true);

  // Load preferences from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('dietaryPreferences');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setPreferences(parsed);
        setShowSetup(false);
      } catch (e) {
        console.error('Failed to parse saved preferences', e);
      }
    }
  }, []);

  const handlePreferencesComplete = (newPreferences: DietaryPreferences) => {
    setPreferences(newPreferences);
    setShowSetup(false);
    // Save to localStorage
    localStorage.setItem('dietaryPreferences', JSON.stringify(newPreferences));
  };

  const handleEditPreferences = () => {
    setShowSetup(true);
  };

  if (showSetup || !preferences) {
    return (
      <PreferencesSetup
        onComplete={handlePreferencesComplete}
        initialPreferences={preferences || undefined}
      />
    );
  }

  return (
    <MealPlanner
      preferences={preferences}
      onEditPreferences={handleEditPreferences}
    />
  );
}
