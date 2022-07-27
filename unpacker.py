# traverses through the root directory where game packages are stored and unpacks the .exe files
# after unpacking, takes from root_dir\vltc\games directory the list of games installed.

import time
import json
import os
from os import walk
import configparser


# unpacks the game package files
def traverse(root_dir):
    """
    traverses through a root directory where games packages are stored and unpacks the .exe files in the directory
    :param root_dir:
    :return: none
    """
    if os.path.exists(os.path.join(root_dir, 'vltc')):
        return
    else:
        for _path, _dirs, _files in walk(root_dir):
            for file in _files:
                if '.exe' in file:
                    print('unpacking file {}'.format(file))
                    os.startfile(os.path.join(_path, file))
                    time.sleep(0.5)


# takes the game names from vltc\games folder and saves in .json file
def get_game_names(root_dir):
    """
    gets the name of the games installed in vltc/games directory and saves them in game_names.json file
    :param root_dir:
    :return: none
    """
    module_names = []
    for _path, _dirs, _files in walk(os.path.join(root_dir, r'vltc\games')):
        for _dir in _dirs:
            module_names.append({
                'game_name': _dir
            })

    with open(r'internal\game_names.json', 'w') as f:
        json.dump(module_names, f, ensure_ascii=False, indent=4)


def execute():
    config = configparser.ConfigParser()
    config.read('resources/config.ini')
    working_subdir = config['RN']['release_note'].replace('Release ', '').replace('.pdf', '')

    # finds the directory in which the specified release note resides, and updates the config file
    for path, dirs, files in os.walk(config['APP']['root_dir']):
        for _dir in dirs:
            if working_subdir in _dir:
                config['APP']['working_dir'] = os.path.join(path, _dir)
                config['APP']['demo_dir'] = os.path.join(path, _dir, 'Demo\\Complete')
                config['APP']['production_dir'] = os.path.join(path, _dir, 'Production\\Complete')
                with open('resources/config.ini', 'w') as config_file:
                    config.write(config_file)

    traverse(config['APP']['demo_dir'])
    traverse(config['APP']['production_dir'])
    get_game_names(config['APP']['demo_dir'])
    get_game_names(config['APP']['production_dir'])
