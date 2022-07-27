import json
import re
import tabula
import configparser

pages = []  # has game_name, game_dll, engine_dll, game_id
tables = []  # has game_version and file_name
extracts = []  # aggregation of all data unified

config = configparser.ConfigParser()
config.read('resources/config.ini')

# read game pages
read_pages_rn = [tabula.read_pdf(str('resources/' + config['RN']['release_note']), output_format='json',
                                 pages=config['RN']['game_pages'], area=[80, 0, 200, 450]),
                 tabula.read_pdf(str('resources/' + config['RN']['release_note']), output_format='json',
                                 pages=config['RN']['special_module_pages'], area=[80, 0, 180, 450])]
# reduce one level of nested lists in game pages
for item in range(len(read_pages_rn)):
    for jtem in range(len(read_pages_rn[item])):
        pages.append(read_pages_rn[item][jtem])


# read tables, contains game_version and file_name
tabula.convert_into(str('resources/' + config['RN']['release_note']), 'internal/temp_tables.json',
                    output_format='json', pages='all')

# reading temp_tables file for formatting
with open('internal/temp_tables.json', 'r') as f:
    raw_file = f.read()
temp_tables = json.loads(raw_file)

# formatting tables data
for i in range(len(temp_tables)):
    for j in range(len(temp_tables[i]['data'])):
        tables.append({
            'game_name': ''.join(
                [i if ord(i) < 128 else '' for i in re.sub(r'\[[^)]*]', '', temp_tables[i]['data'][j][0]['text'])
                    .replace(' ', '').replace('*', '').replace('\'', '')]),
            'version': temp_tables[i]['data'][j][1]['text'].replace('V', '')
        })


with open('internal/game_names.json', 'r') as f:
    data = f.read()
games = json.loads(data)


# get game_name from release notes
def get_game_name(game):
    for i in range(len(tables)):
        if game.lower() == tables[i]['game_name'].lower():
            return tables[i]['game_name']
        elif game.lower() == 'jewelsjungle':
            return 'JewelsOfTheJungle'
        elif game.lower() == 'kingtut':
            return 'KingTutsTreasure'
        elif game.lower() == 'kingtut2':
            return 'KingTutsTreasure2'


# get game_dll version from release notes
def get_game_dll(game):

    # accounting for discrepancies in the naming of the games across directories and documents by original developers
    if game.lower() == 'jewelsjungle':
        game = 'jewelsofthejungle'
    elif game.lower() == 'kingtut':
        game = 'kingtutstreasure'
    elif game.lower() == 'kingtut2':
        game = 'kingtutstreasure2'

    for i in range(len(pages)):
        try:
            if game.lower() in pages[i]['data'][0][1]['text'].replace('’', '').replace('\'', '').replace(' ', '').lower():
                return pages[i]['data'][1][1]['text']
        except IndexError:
            continue


# get engine_dll version from release notes
def get_engine_dll(game):

    # accounting for discrepancies in the naming of the games across directories and documents by original developers
    if game.lower() == 'jewelsjungle':
        game = 'jewelsofthejungle'
    elif game.lower() == 'kingtut':
        game = 'kingtutstreasure'
    elif game.lower() == 'kingtut2':
        game = 'kingtutstreasure2'

    for i in range(len(pages)):
        try:
            if game.lower() in pages[i]['data'][0][1]['text'].replace('’', '').replace('\'', '').replace(' ', '').lower():
                return pages[i]['data'][2][1]['text']
        except IndexError:
            continue


# get game_id from release notes
def get_game_id(_data, game):
    game_id = re.search(r'\[([A-Za-z0-9_]+)\]', _data[game]['data'][0][1]['text']).group(1)
    return game_id


# get game_version from release notes
def get_game_version(game):

    # accounting for discrepancies in the naming of the games across directories and documents by original developers
    if game.lower() == 'jewelsjungle':
        game = 'jewelsofthejungle'
    elif game.lower() == 'kingtut':
        game = 'kingtutstreasure'
    elif game.lower() == 'kingtut2':
        game = 'kingtutstreasure2'

    for i in range(len(tables)):
        if game.lower() == tables[i]['game_name'].lower():
            return tables[i]['version']


# get file_name from release notes
def get_file_name(game):
    file_names = []

    # accounting for discrepancies in the naming of the games across directories and documents by original developers
    if game == 'JewelsOfTheJungle':
        game = 'JewelsJungle'
    elif game == 'KingTutsTreasure':
        game = 'KingTut'
    elif game == 'KingTutsTreasure2':
        game = 'KingTut2'

    game = game + '_'  # preventing misinterpretation of similar games names that differ by only a number at the end

    for i in range(len(tables)):
        if game.lower() in tables[i]['game_name'].lower() and '.exe' in tables[i]['game_name']:
            file_names.append(tables[i]['game_name'])
    return file_names


# extract_rn.json should be created here. the function will aggregate the values from the methods above
# the loop should happen 29 times equal to the number of PT games.
def aggregator():
    print('Collecting information from release notes...')
    for game in range(len(games)):
        extracts.append({
            'game_name': get_game_name(games[game]['game_name']),
            'game_dll': get_game_dll(games[game]['game_name']),
            'engine_dll': get_engine_dll(games[game]['game_name']),
            'game_version': get_game_version(games[game]['game_name']),
            # 'game_id': get_game_id(pages, game),
            'file_name': get_file_name(games[game]['game_name'])
        })
    with open('internal/extract_rn.json', 'w') as extract_file:
        json.dump(extracts, extract_file, ensure_ascii=False, indent=4)

    with open('internal/files_rn.json', 'w') as files_rn:
        files = []
        for d in tables:
            for key, value in d.items():
                if '.exe' in value:
                    files.append(value)
        files = sorted(files)
        json.dump(files, files_rn, ensure_ascii=False, indent=4)
    print('Release notes information collection successful...')


def execute():
    aggregator()
