#!/usr/bin/env python3
"""Entry point for modis-product-skill"""
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "scripts"))

from modis_products import main

if __name__ == "__main__":
    result = main()
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
