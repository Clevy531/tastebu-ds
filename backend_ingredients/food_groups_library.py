# food_groups.py

FOOD_DATABASE = {
    # Dairy Products
    'dairy': [
        'milk', 'whole milk', '2% milk', 'skim milk', 'almond milk',
        'cream', 'heavy cream', 'light cream', 'half and half',
        'cheese', 'cheddar', 'mozzarella', 'parmesan', 'swiss',
        'yogurt', 'greek yogurt', 'sour cream', 'cottage cheese',
        'butter', 'ice cream', 'whey', 'casein', 'buttermilk'
    ],
    
    
    # Seafood
    'seafood': [
        'salmon', 'tuna', 'cod', 'tilapia', 'halibut',
        'shrimp', 'crab', 'lobster', 'clams', 'mussels',
        'oysters', 'scallops', 'sardines', 'anchovies'
    ],

    
    # Nuts & Seeds
    'tree nuts': [
        'almonds', 'cashews', 'walnuts', 'pecans',
        'pistachios', 'hazelnuts', 'macadamia nuts',
    ],
    
    'seeds': [
        'sunflower seeds', 'pumpkin seeds', 'chia seeds',
        'flax seeds', 'sesame seeds',
        ],
    
    # Oils & Fats
    'oils or fats': [
        'olive oil', 'vegetable oil', 'canola oil', 'coconut oil',
        'butter', 'margarine', 'lard', 'shortening'
    ],
    
    # Eggs
    'eggs': [
        'eggs', 'egg whites', 'egg yolks', 'whole eggs'
    ]
}

def get_food_group(food_item):
    """Find which food group an item belongs to"""
    food_lower = food_item.lower().strip()
    
    for group, items in FOOD_DATABASE.items():
        if food_lower in items or any(food_lower in item for item in items):
            return group
    
    return 'unknown'

def get_all_in_group(group_name):
    """Get all foods in a specific group"""
    food_list = FOOD_DATABASE.get(group_name, [])
    
    if food_list is None:
        food_list = [group_name]
        
    return food_list


def exclude_group(food_list, excluded_groups):
    """Remove all foods from specified groups"""
    filtered = []
    for food in food_list:
        group = get_food_group(food)
        if group not in excluded_groups:
            filtered.append(food)
    return filtered