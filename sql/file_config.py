import json
from pathlib import Path
from tkinter import filedialog


def save_config(config, fs):
    print(json.dumps(config, indent=4))
    config_path = filedialog.askdirectory(title='Where to Save DB Config?')
    for db_name in config.keys():
        with open(Path(config_path, f'{db_name}_config.json'), 'w') as f:
            json.dump(config, f)


def load_config():
    config_path = filedialog.askopenfilename(title='Select DB Config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    print(json.dumps(config, indent=4))
    return config

