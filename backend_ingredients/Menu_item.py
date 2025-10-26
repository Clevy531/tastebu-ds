#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 25 15:11:54 2025

@author: matthewkim
"""

#This is the file which shows the class for our food obj which is 
#extracted from whatever beautiful soup has given us. 


class Menu_item:
    def __init__ (self, name, ingredients, nutrients):
        self.name = name
        self.ingredients = ingredients
        self.nutrients = nutrients
        
    def display(self):
        print(f"Menu_item: {self.name}")
        print(f"Ingredients: {', '.join(self.ingredients)}")
        print(f"Nutrients: {', '.join(self.nutrients)}")
        
        
