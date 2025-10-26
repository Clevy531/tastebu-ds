#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from restricted_ingredients import return_restricted_ingredients
from flask import Flask, request, jsonify
from flask_cors import CORS
import socket
import json
from json_extraction import load_foods_from_json

def is_food_safe(food_info, restricted_ingredients_lower):
    """
    Check if food is safe based on restricted ingredients.
    Remove any ingredient that matches a restricted word (singular/plural).
    Unsafe if any restricted ingredient is found.
    """
    food_ingredients = food_info.get("ingredients", [])
    safe = True  # Assume food is safe unless a restricted ingredient is found

    filtered_ingredients = []

    for ingredient in food_ingredients:
        ingredient_clean = ingredient.lower().replace(" ", "")
        remove_ingredient = False

        for restricted in restricted_ingredients_lower:
            restricted_clean = restricted.lower().replace(" ", "")
            # Match exact, or singular/plural forms
            if (restricted_clean in ingredient_clean or
                (restricted_clean + 's') in ingredient_clean or
                (restricted_clean.endswith('s') and restricted_clean[:-1] in ingredient_clean)):
                remove_ingredient = True
                safe = False
                break

        if not remove_ingredient:
            filtered_ingredients.append(ingredient)

    # Update the ingredients list to remove restricted items
    food_info["ingredients"] = filtered_ingredients
    return safe

def is_meal_allowed(meal, dietary_restrictions):
    """
    Check if a meal satisfies all of the user's dietary restrictions.
    
    meal: dict, must have "dietaryRestrictions" key (list of strings)
    dietary_restrictions: list of strings, e.g., ["Vegan", "Gluten-Free"]
    
    Returns True if the meal satisfies all dietary restrictions, False otherwise.
    """
    meal_tags = [tag.lower() for tag in meal.get("dietaryRestrictions", [])]

    # Disallow meals with no dietary restriction tags
    if not meal_tags:
        return False
    
    if not dietary_restrictions:
        return True  # No restrictions, everything allowed
    
    meal_tags = [tag.lower() for tag in meal.get("dietaryRestrictions", [])]

    for restriction in dietary_restrictions:
        restriction_lower = restriction.lower()

        if restriction_lower in ["vegan", "vegetarian"]:
            # Must explicitly include the tag
            if restriction_lower not in meal_tags:
                return False
        elif restriction_lower == "pescatarian":
            # Allow if meal is pescatarian or does not contain meat
            non_pescatarian_meat = ["beef", "chicken", "pork", "lamb"]
            ingredients_lower = [i.lower() for i in meal.get("ingredients", [])]
            has_meat = any(meat in ingredients_lower for meat in non_pescatarian_meat)
            if "pescatarian" not in meal_tags and has_meat:
                return False
        else:
            # Optional diets like Gluten-Free, Low-Carb
            if restriction_lower not in meal_tags:
                return False

    return True


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/filter_foods", methods=["POST"])
def filter_foods():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        print("📥 Raw data request:", data)
        
        # Convert to lowercase for case-insensitive matching
        allergies = [a.lower() if isinstance(a, str) else a for a in data.get("allergies", [])]
        restrictions = [r.lower() if isinstance(r, str) else r for r in data.get("dietaryRestrictions", [])]
        list_mealcards = data.get("foods", [])
        
        # Validate input types
        if not isinstance(data.get("allergies", []), list):
            return jsonify({"error": "allergies must be a list"}), 400
        if not isinstance(data.get("dietaryRestrictions", []), list):
            return jsonify({"error": "dietaryRestrictions must be a list"}), 400
        if not isinstance(list_mealcards, list):
            return jsonify({"error": "foods must be a list"}), 400
        
        # Get restricted ingredients
        all_restrict_ingredients = return_restricted_ingredients(allergies, restrictions)
        
        # Convert to lowercase set for efficient lookup
        restricted_ingredients_lower = {ing.lower() for ing in all_restrict_ingredients}
        
        print("🧩 Restricted ingredients:", all_restrict_ingredients)
        
        # If no foods provided, use example data (for testing)
        list_mealcards = []
        
        scraped_foods = load_foods_from_json("meals.with_ingredients.json")
        scraped_foods2 = load_foods_from_json("marci_meals.with_ingredients.json")
        scraped_foods3 = load_foods_from_json("warren_meals.with_ingredients.json")
        
        list_mealcards.extend(scraped_foods)
        list_mealcards.extend(scraped_foods2)
        list_mealcards.extend(scraped_foods3)        
        
        for meal in list_mealcards:
            if isinstance(meal.get("ingredients"), str):
        # Split by commas and strip whitespace
                meal["ingredients"] = [i.strip() for i in meal["ingredients"].split(",")]
        
        
        # Filter safe foods
        safe_foods = [
            food for food in list_mealcards
            if is_meal_allowed(food, restrictions) and is_food_safe(food, restricted_ingredients_lower)
        ]
        
        print(f"✅ Found {len(safe_foods)} safe foods out of {len(list_mealcards)}")
        
        return jsonify({
            "safe_foods": safe_foods,
            "total_filtered": len(list_mealcards) - len(safe_foods),
            "restricted_ingredients": list(all_restrict_ingredients)
        })
    
    except Exception as e:
        print(f"❌ Error processing request: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Create a socket and connect to an external address (doesn't actually send data)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 5001
    
    print("\n" + "="*60)
    print("🚀 Flask Backend Starting...")
    print("="*60)
    print(f"📍 Local access:   http://127.0.0.1:{port}")
    print(f"🌐 Network access: http://{local_ip}:{port}")
    print("="*60)
    print("💡 Use the Network URL to access from other devices")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=port)