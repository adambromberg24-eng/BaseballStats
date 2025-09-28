import importlib
import sys

# Clear any cached versions
if 'mlb_api_client' in sys.modules:
    del sys.modules['mlb_api_client']

# Fresh import
from mlb_api_client import MLBApiClient

# Create instance and test
client = MLBApiClient()
has_method = hasattr(client, 'get_game_options')

print(f"get_game_options method exists: {has_method}")

if has_method:
    print("Method signature:", client.get_game_options.__doc__)
else:
    print("Available methods:")
    for method in dir(client):
        if not method.startswith('_'):
            print(f"  - {method}")
