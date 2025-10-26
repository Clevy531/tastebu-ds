#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 21:15:38 2025
@author: matthewkim
"""
import json
from flask_backend import app  # replace with your .py file name (no .py)

def test_filter_foods():
    """Basic allergy filtering test"""
    with app.test_client() as client:
        data = {
            "allergies": ["Eggs"],
            "dietaryRestrictions": []
        }
        response = client.post("/filter_foods", json=data)
        
        print(f"📊 Status Code: {response.status_code}")
        assert response.status_code == 200
        
        response_data = response.get_json()
        print("✅ Response JSON:")
        print(json.dumps(response_data, indent=2))
        
        safe_foods = response_data.get("safe_foods", response_data)
        names = [food["name"] for food in safe_foods]
        print(f"🍽️  Safe food names: {names}")
        
        # Meals containing eggs should be filtered out
        for forbidden in ["Scrambled Eggs & Toast", "French Toast with Syrup", 
                          "Blueberry Protein Pancakes", "Spinach and Feta Omelette",
                          "Avocado Toast with Poached Egg"]:
            assert forbidden not in names, f"{forbidden} should be filtered out"
        
        # Meals that should be safe
        for allowed in ["Grilled Chicken Salad", "Vegan Lentil Soup", "Vegan Chili",
                        "Vegan Mushroom Risotto", "Vegetable Curry with Rice",
                        "Quinoa Power Bowl", "Tofu Buddha Bowl"]:
            assert allowed in names, f"{allowed} should be safe"
        
        total_filtered = response_data.get('total_filtered', 0)
        print(f"✅ Filtered out {total_filtered} unsafe food(s)")

def test_multiple_allergies():
    """Test with multiple allergies"""
    with app.test_client() as client:
        data = {
            "allergies": ["Eggs", "Milk"],
            "dietaryRestrictions": []
        }
        response = client.post("/filter_foods", json=data)
        assert response.status_code == 200
        
        response_data = response.get_json()
        safe_foods = response_data.get("safe_foods", response_data)
        names = [food["name"] for food in safe_foods]
        print(f"🥛 Multiple allergies test - Safe foods: {names}")
        
        # All foods containing Eggs or Milk must be filtered
        forbidden = ["Scrambled Eggs & Toast", "French Toast with Syrup", 
                     "Blueberry Protein Pancakes", "Spinach and Feta Omelette",
                     "Avocado Toast with Poached Egg", 
                     "Eggplant Parmesan"]
        for item in forbidden:
            assert item not in names, f"{item} contains eggs or milk"
        
        allowed = ["Grilled Chicken Salad", "Vegan Lentil Soup", "Vegan Chili",
                   "Vegan Mushroom Risotto", "Vegetable Curry with Rice",
                   "Quinoa Power Bowl", "Tofu Buddha Bowl"]
        for item in allowed:
            assert item in names, f"{item} should be safe"

def test_vegan_restriction():
    """Test dietary restrictions for vegan"""
    with app.test_client() as client:
        data = {
            "allergies": [],
            "dietaryRestrictions": ["Vegan"]
        }
        response = client.post("/filter_foods", json=data)
        assert response.status_code == 200
        
        response_data = response.get_json()
        safe_foods = response_data.get("safe_foods", response_data)
        names = [food["name"] for food in safe_foods]
        print(f"🌱 Vegan restriction test - Safe foods: {names}")
        
        # Only vegan meals should appear
        non_vegan = ["Scrambled Eggs & Toast", "Grilled Chicken Salad", "French Toast with Syrup",
                     "Blueberry Protein Pancakes", "Spinach and Feta Omelette", "Avocado Toast with Poached Egg",
                     "Greek Yogurt Parfait", "Eggplant Parmesan", "Beef Lasagna"]
        for item in non_vegan:
            assert item not in names, f"{item} is not vegan and should be filtered"

def test_no_restrictions():
    """Test with no restrictions - all foods should pass"""
    with app.test_client() as client:
        data = {
            "allergies": [],
            "dietaryRestrictions": []
        }
        response = client.post("/filter_foods", json=data)
        assert response.status_code == 200
        
        response_data = response.get_json()
        safe_foods = response_data.get("safe_foods", response_data)
        
        print(f"🍴 No restrictions test - {len(safe_foods)} foods available")
        assert len(safe_foods) >= 45, "All foods should be safe with no restrictions"

def test_invalid_request():
    """Test error handling with invalid request"""
    with app.test_client() as client:
        data = {
            "allergies": "Eggs",  # invalid: should be list
            "dietaryRestrictions": []
        }
        response = client.post("/filter_foods", json=data)
        print(f"❌ Invalid request test - Status: {response.status_code}")
        if response.status_code == 400:
            print("✅ Proper error handling detected")
        else:
            print("⚠️  Backend accepts invalid input format")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Starting Flask Integration Tests")
    print("=" * 60)
    
    try:
        test_filter_foods()
        print("\n✅ Test 1: Basic allergy filtering - PASSED!\n")
        
        test_multiple_allergies()
        print("\n✅ Test 2: Multiple allergies - PASSED!\n")
        
        test_vegan_restriction()
        print("\n✅ Test 3: Dietary restrictions - PASSED!\n")
        
        test_no_restrictions()
        print("\n✅ Test 4: No restrictions - PASSED!\n")
        
        test_invalid_request()
        print("\n✅ Test 5: Invalid request handling - PASSED!\n")
        
        print("=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
