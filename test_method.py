#!/usr/bin/env python3

import sys
import importlib

# Force reload of the module
if 'mlb_api_client' in sys.modules:
    importlib.reload(sys.modules['mlb_api_client'])

from mlb_api_client import MLBApiClient

client = MLBApiClient()

print("Methods available in MLBApiClient:")
methods = [method for method in dir(client) if not method.startswith('_')]
for method in sorted(methods):
    print(f"  - {method}")

print(f"\nget_game_options method exists: {hasattr(client, 'get_game_options')}")

if hasattr(client, 'get_game_options'):
    print("✅ get_game_options method is available!")
else:
    print("❌ get_game_options method is NOT available!")
