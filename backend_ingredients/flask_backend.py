#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 25 15:28:54 2025

@author: matthewkim
"""

# This file contains the main backend which communicates with the 
# frontend. Uses Flask.

from restricted_ingredients import return_restricted_ingredients


from flask import Flask, request, jsonify


def is_food_safe(food_info, restricted_ingredients):
    for ingredient in food_info.get("ingredients", []):
        if ingredient.lower() in [r.lower() for r in restricted_ingredients]:
            return False
    return True


app = Flask(__name__)

@app.route("/filter_foods", methods=["POST"])
def filter_foods():
    data = request.get_json()
    
    allergies = data.get("allergies", [])
    restrictions = data.get("dietary_restrictions", [])
    
    all_restrict_ingredients = return_restricted_ingredients(allergies, restrictions)
    
    # Example scraped foods with full meal info
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
            "ingredients": ["Flour", "Eggs", "Milk"],
            "allergens": ["Eggs", "Milk"],
            "tags": ["vegetarian"],
            "description": "Fluffy pancakes served with syrup."
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
            "ingredients": ["Lettuce", "Tomato", "Cucumber"],
            "allergens": [],
            "tags": ["vegan", "gluten-free"],
            "description": "Fresh romaine salad with dressing."
        }
    ]
    
    # Filter safe foods
    safe_foods = [food for food in scraped_foods if is_food_safe(food, all_restrict_ingredients)]
    
    return jsonify(safe_foods)


    
    



    

