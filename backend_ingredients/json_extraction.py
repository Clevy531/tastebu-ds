#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 26 01:34:35 2025

@author: matthewkim
"""

# Extract data from a json file

import json

def load_foods_from_json(file_path):
    """
    Reads a JSON file and returns a list of food dictionaries.
    Each dictionary should have 'dietaryRestrictions', 'ingredients', etc.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        foods = json.load(f)
    return foods

