# this file extracts the following data from game files on the local machine:
# 1- game_name
# 2- game_dll version
# 3- engine_dll version
# 4- game_version
from win32api import GetFileVersionInfo, LOWORD, HIWORD
import os
import json
import re
import configparser


# returns the FileVersion attribute of file in a directory if available
def get_version_number(_file):
    try:
        info = GetFileVersionInfo(_file, "\\")
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        return HIWORD(ms), LOWORD(ms), HIWORD(ls), LOWORD(ls)
    except 'Version information not found.':
        return 0, 0, 0, 0


# takes a sub-directory as an argument -> returns game_name, game_dll, and engine_dll
def get_game_dir_info(_root_dir):
    game_dir_info = {}
    for path, dirs, files in os.walk(_root_dir):

        # get game_name
        game_name = path.split('\\')
        if game_name[-1].lower() == 'jewelsjungle':
            game_dir_info['game_name'] = 'JewelsOfTheJungle'
        elif game_name[-1].lower() == 'kingtut':
            game_dir_info['game_name'] = 'KingTutsTreasure'
        elif game_name[-1].lower() == 'kingtut2':
            game_dir_info['game_name'] = 'KingTutsTreasure2'
        else:
            game_dir_info['game_name'] = game_name[-1]

        for file in files:
            # check for prod game_dll
            if 'dll' in file and 'Engine' not in file:
                version = ".".join([str(i) for i in get_version_number(os.path.join(path, file))])
                game_dir_info['game_dll'] = version
            # check for prod engine_dll
            elif 'dll' in file and 'Engine' in file:
                version = ".".join([str(i) for i in get_version_number(os.path.join(path, file))])
                game_dir_info['engine_dll'] = version
    return game_dir_info


# takes the directory where game packages are as an argument -> returns a dict of game_names and game_versions
def get_game_version(root_dir, game_name):
    with open(r'internal\game_names.json', 'r') as f:
        data = f.read()
    game_names = json.loads(data)

    game_version = {}
    # traverse through packages' directory
    for path, dirs, files in os.walk(root_dir):
        for file in files:
            if '.exe' in file:  # look for game packages in .exe files
                if (game_name + '_') in file:  # game_name:game_version pair
                    game_version[game_name] = re.search(r'([0-9]+(\.[0-9]+)+)', file).group(0)
    return game_version


# aggregates the data collected by get_game_dir_info and get_game_version methods to extract_os.json file
def aggregator(production_path, demo_path, qa_releases):
    print('Collecting information from the local machine...')
    with open(r'internal\game_names.json', 'r') as f:
        data = f.read()
    games = json.loads(data)
    game_info = []
    game_dict = {}

    for i in range(len(games)):
        try:
            game_dict['game_name'] = get_game_dir_info(os.path.join(production_path, games[i]['game_name']))['game_name']
            game_dict['DEMO_game_dll'] = get_game_dir_info(os.path.join(demo_path, games[i]['game_name']))['game_dll']
            game_dict['game_dll'] = get_game_dir_info(os.path.join(production_path, games[i]['game_name']))['game_dll']
            game_dict['DEMO_engine_dll'] = get_game_dir_info(os.path.join(demo_path, games[i]['game_name']))['engine_dll']
            game_dict['engine_dll'] = get_game_dir_info(os.path.join(production_path, games[i]['game_name']))['engine_dll']
            game_dict['DEMO_game_version'] = get_game_version(qa_releases[0], games[i]['game_name'])[games[i]['game_name']]
            game_dict['game_version'] = get_game_version(qa_releases[1], games[i]['game_name'])[games[i]['game_name']]
        except:
            pass
        game_info.append(game_dict.copy())
    with open('internal/extract_os.json', 'w') as f:
        json.dump(game_info, f, ensure_ascii=False, indent=4)

    with open('internal/files_os.json', 'w') as files_os:  # gets list of all .exe files in prod and demo directories
        files_demo = [f for f in os.listdir(qa_releases[0]) if '.exe' in f]
        files_prod = [f for f in os.listdir(qa_releases[1]) if '.exe' in f]
        files = set(files_prod + files_demo)
        files = sorted(list(files))
        json.dump(files, files_os, ensure_ascii=False, indent=4)
    print('Local machine information collection successful...')

def execute():
    config = configparser.ConfigParser()
    config.read('resources/config.ini')

    demo_path = os.path.join(config['APP']['demo_dir'], 'vltc\\games')
    production_path = os.path.join(config['APP']['production_dir'], 'vltc\\games')
    qa_releases = [config['APP']['demo_dir'], config['APP']['production_dir']]
    aggregator(production_path, demo_path, qa_releases)
