#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 25 14:33:32 2025

@author: matthewkim
"""


#Getting the required functions from the libraries
from food_groups_library import get_all_in_group
from DIETARY_groups_library import  get_all_diet_in_group

#This file will return the list of all foods related.

def return_restricted_ingredients(allergens, dietary_restriction):
    
    #Returns list of all related ingredients to the allergens
    all_restricted_ingredients = []
    for i in allergens:
        ext_allergens = get_all_in_group(i)
        all_restricted_ingredients += ext_allergens
    
    for i in dietary_restriction:
        ext_dietary = get_all_diet_in_group(i)
        all_restricted_ingredients += ext_dietary
    
    
    #all_restricted_ingredients now has all the ingredients we do NOT want

    return all_restricted_ingredients

    
    
    
        