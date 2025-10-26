#Dietary Restrictions which INCLUDES ALLERGENS

DIETARY_RESTRICTIONS = {
    # Allergens (Medical)
    'dairy_free': {
        'type': 'allergy',
        'exclude': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'whey', 
                   'casein', 'lactose', 'ice cream', 'sour cream'],
        'description': 'No dairy products'
    },
    
    'egg_free': {
        'type': 'allergy',
        'exclude': ['eggs', 'egg whites', 'egg yolks', 'mayonnaise'],
        'description': 'No eggs'
    },
    
    'nut_free': {
        'type': 'allergy',
        'exclude': ['peanuts', 'almonds', 'walnuts', 'cashews', 'pecans',
                   'pistachios', 'hazelnuts', 'peanut butter'],
        'description': 'No nuts or peanuts'
    },
    
    'gluten_free': {
        'type': 'allergy',
        'exclude': ['wheat', 'barley', 'rye', 'bread', 'pasta', 'flour',
                   'couscous', 'bulgur', 'soy sauce', 'beer'],
        'description': 'No gluten'
    },
    
    'shellfish_free': {
        'type': 'allergy',
        'exclude': ['shrimp', 'crab', 'lobster', 'clams', 'mussels', 
                   'oysters', 'scallops'],
        'description': 'No shellfish'
    },
    
    'soy_free': {
        'type': 'allergy',
        'exclude': ['soy', 'tofu', 'soy milk', 'soy sauce', 'edamame', 
                   'tempeh', 'miso'],
        'description': 'No soy products'
    },
    
    # Religious/Cultural
    'halal': {
        'type': 'religious',
        'exclude': ['pork', 'bacon', 'ham', 'alcohol', 'wine', 'beer'],
        'description': 'Islamic dietary laws'
    },
    
    'kosher': {
        'type': 'religious',
        'exclude': ['pork', 'shellfish', 'bacon', 'ham'],
        'special_rules': 'No mixing meat and dairy',
        'description': 'Jewish dietary laws'
    },
    
    'hindu': {
        'type': 'religious',
        'exclude': ['beef', 'veal', 'steak'],
        'description': 'Hindu dietary practices'
    },
    
    # Lifestyle
    'vegetarian': {
        'type': 'lifestyle',
        'exclude': ['chicken', 'beef', 'pork', 'fish', 'turkey', 'lamb',
                   'salmon', 'tuna', 'shrimp', 'bacon', 'ham', 'sausage'],
        'description': 'No meat, poultry, or fish'
    },
    
    'vegan': {
        'type': 'lifestyle',
        'exclude': ['chicken', 'beef', 'pork', 'fish', 'turkey', 'lamb',
                   'salmon', 'tuna', 'shrimp', 'bacon', 'ham',
                   'milk', 'cheese', 'yogurt', 'butter', 'eggs', 
                   'honey', 'gelatin'],
        'description': 'No animal products'
    },
    
    'pescatarian': {
        'type': 'lifestyle',
        'exclude': ['chicken', 'beef', 'pork', 'turkey', 'lamb', 
                   'bacon', 'ham', 'sausage'],
        'description': 'No meat or poultry, fish okay'
    },
    
    # Health/Diet Plans
    'keto': {
        'type': 'health',
        'exclude': ['bread', 'pasta', 'rice', 'potatoes', 'sugar',
                   'banana', 'oats', 'cereal', 'corn'],
        'limit': {'carbs': 50},  # grams per day
        'description': 'Very low carb, high fat'
    },
    
    'paleo': {
        'type': 'health',
        'exclude': ['bread', 'pasta', 'rice', 'beans', 'lentils',
                   'dairy', 'cheese', 'yogurt', 'processed foods'],
        'description': 'No grains, legumes, or dairy'
    },
    
    'low_sodium': {
        'type': 'health',
        'exclude': ['canned soup', 'processed meats', 'soy sauce'],
        'limit': {'sodium': 2300},  # mg per day
        'description': 'Reduced salt intake'
    },
    
    'diabetic': {
        'type': 'health',
        'exclude': ['sugar', 'candy', 'soda', 'white bread', 'white rice'],
        'limit': {'sugar': 50, 'carbs': 200},  # grams per day
        'description': 'Blood sugar management'
    }
}

def filter_by_restrictions(ingredients, user_restrictions):
    """
    Filter ingredients based on user's dietary restrictions
    
    Args:
        ingredients: List of ingredient names
        user_restrictions: List of restriction keys (e.g., ['vegan', 'nut_free'])
    
    Returns:
        Dictionary with safe ingredients and violations
    """
    safe_ingredients = []
    violations = {}
    
    for ingredient in ingredients:
        ingredient_lower = ingredient.lower()
        is_safe = True
        ingredient_violations = []
        
        # Check against each restriction
        for restriction in user_restrictions:
            if restriction in DIETARY_RESTRICTIONS:
                excluded_items = DIETARY_RESTRICTIONS[restriction].get('exclude', [])
                
                # Check if ingredient matches any excluded item
                for excluded in excluded_items:
                    if excluded in ingredient_lower:
                        is_safe = False
                        ingredient_violations.append(restriction)
                        break
        
        if is_safe:
            safe_ingredients.append(ingredient)
        else:
            violations[ingredient] = ingredient_violations
    
    return {
        'safe': safe_ingredients,
        'violations': violations
    }

def get_restriction_info(restriction_key):
    """Get information about a specific dietary restriction"""
    if restriction_key in DIETARY_RESTRICTIONS:
        return DIETARY_RESTRICTIONS[restriction_key]
    return None