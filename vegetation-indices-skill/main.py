#!/usr/bin/env python3
"""Entry point for vegetation-indices-skill"""
import sys
import os

# Add scripts directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "scripts"))

from vegetation_indices import main

if __name__ == "__main__":
    result = main()
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
