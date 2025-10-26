#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 25 14:19:25 2025

@author: matthewkim
"""

DIETARY_DATABASE = {
    # Dietary restrictions
    'halal': [
        'pork', 'bacon', 'ham', 'alcohol', 'wine', 'beer'
    ],
    
    'kosher': [
        'pork', 'shellfish', 'bacon', 'ham', 'sausage', 
    ],
    
    
    'vegetarian': [
        'chicken', 'beef', 'pork', 'fish', 'turkey', 'lamb',
        'salmon', 'tuna', 'shrimp', 'bacon', 'ham', 'sausage'],
    
    'vegan': [
        'chicken', 'beef', 'pork', 'fish', 'turkey', 'lamb',
        'salmon', 'tuna', 'shrimp', 'bacon', 'ham',
        'milk', 'cheese', 'yogurt', 'butter', 'eggs', 
        'honey', 'gelatin'],
    
    'pescatarian': [
        'chicken', 'beef', 'pork', 'turkey', 'lamb', 
        'bacon', 'ham', 'sausage'],
    
    'gluten-free': [
        'pasta', 'bread', 'flour', 'wheat'
        ],
    #'low-fat':[]
    
    #'high-protein':[]
    
    #'low-carb':[]
    
    'low-sodium': [
        'canned soup', 'processed meats', 'soy sauce'],
    
    'diabetic': [
        'sugar', 'candy', 'soda', 'white bread', 'white rice'],
    
}


def get_restricted_group(restriction):
    """Find which food group an item belongs to"""
    restriction_lower = restriction.lower().strip()
    
    for group, items in DIETARY_DATABASE.items():
        if restriction_lower in items or any(restriction_lower in item for item in items):
            return group
    
    return 'unknown'

def get_all_diet_in_group(DIET_NAME):
    """Get all foods in a specific group"""
    return DIETARY_DATABASE.get(DIET_NAME, [])






