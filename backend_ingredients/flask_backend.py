#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from restricted_ingredients import return_restricted_ingredients
from flask import Flask, request, jsonify
from flask_cors import CORS
import socket

def is_food_safe(food_info, restricted_ingredients_lower):
    """Check if food is safe based on restricted ingredients."""
    food_ingredients = food_info.get("ingredients", [])
    
    for ingredient in food_ingredients:
        ingredient_lower = ingredient.lower()
        if ingredient_lower in restricted_ingredients_lower:
            return False
        for restricted in restricted_ingredients_lower:
            if restricted in ingredient_lower or ingredient_lower in restricted:
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
        restrictions = [r.lower() if isinstance(r, str) else r for r in data.get("dietary_restrictions", [])]
        scraped_foods = data.get("foods", [])
        
        # Validate input types
        if not isinstance(data.get("allergies", []), list):
            return jsonify({"error": "allergies must be a list"}), 400
        if not isinstance(data.get("dietary_restrictions", []), list):
            return jsonify({"error": "dietary_restrictions must be a list"}), 400
        if not isinstance(scraped_foods, list):
            return jsonify({"error": "foods must be a list"}), 400
        
        # Get restricted ingredients
        all_restrict_ingredients = return_restricted_ingredients(allergies, restrictions)
        
        # Convert to lowercase set for efficient lookup
        restricted_ingredients_lower = {ing.lower() for ing in all_restrict_ingredients}
        
        print("🧩 Restricted ingredients:", all_restrict_ingredients)
        
        # If no foods provided, use example data (for testing)
        if not scraped_foods:
            scraped_foods = [
                {
                    "id": "b1",
                    "name": "Pancakes",
                    "hall": "West Campus Dining",
                    "mealType": "breakfast",
                    "calories": 350,
                    "protein": 8,
                    "carbs": 60,
                    "fat": 10,
                    "allergens": ["Eggs", "Milk"],
                    "dietaryRestrictions": ["vegetarian"],
                    "description": "Fluffy pancakes served with syrup.",
                    "ingredients": ["Flour", "Eggs", "Milk"]
                },
                {
                    "id": "l1",
                    "name": "Salad",
                    "hall": "East Campus Dining",
                    "mealType": "lunch",
                    "calories": 250,
                    "protein": 5,
                    "carbs": 20,
                    "fat": 15,
                    "allergens": [],
                    "dietaryRestrictions": ["vegan", "gluten-free"],
                    "description": "Fresh romaine salad with dressing.",
                    "ingredients": ["Lettuce", "Tomato", "Cucumber"]
                }
            ]
        
        # Filter safe foods
        safe_foods = [
            food for food in scraped_foods 
            if is_food_safe(food, restricted_ingredients_lower)
        ]
        
        print(f"✅ Found {len(safe_foods)} safe foods out of {len(scraped_foods)}")
        
        return jsonify({
            "safe_foods": safe_foods,
            "total_filtered": len(scraped_foods) - len(safe_foods),
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