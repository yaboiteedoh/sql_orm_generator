import json
from pathlib import Path


def save_config(config, fs):
    print(json.dumps(config, indent=4))
    with open(fs['config'], 'w') as f:
        json.dump(config, f)
