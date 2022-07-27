import os
import json
import socket
import time
import configparser

with open('internal/extract_os.json', 'r') as f1, open('internal/extract_rn.json', 'r') as f2:
    data_1 = f1.read()
    data_2 = f2.read()

os_data = json.loads(data_1)
rn_data = json.loads(data_2)

prod_vs_rn = []
demo_vs_rn = []
file_names_in_rn = []
demo_vs_prod = []
ignore_list = ['GameMenu', 'GameMenuVertical', 'RechargeStation']

# PRODUCTION vs. RELEASE NOTES
for os_game, rn_game in zip(os_data, rn_data):
    temp_dict = {}
    for key, value in os_game.items():
        if key in rn_game.keys():
            if value != rn_game[key]:
                temp_dict['game_name'] = os_game['game_name']
                temp_dict[key] = value
    prod_vs_rn.append(temp_dict.copy())

# DEMO vs. RELEASE NOTES
for os_game, rn_game in zip(os_data, rn_data):
    try:
        temp_dict = {'DEMO_game_name': os_game['game_name']}
        if rn_game['game_dll'] != os_game['DEMO_game_dll']:
            temp_dict['DEMO_game_dll'] = os_game['DEMO_game_dll']
        if rn_game['engine_dll'] != os_game['DEMO_engine_dll']:
            temp_dict['DEMO_engine_dll'] = os_game['DEMO_engine_dll']
        if rn_game['game_version'] != os_game['DEMO_game_version']:
            temp_dict['DEMO_game_version'] = os_game['DEMO_game_version']
        if len(temp_dict) > 1:
            demo_vs_rn.append(temp_dict.copy())
    except:
        continue

# FILE_NAMES in RELEASE NOTES
for i in range(len(rn_data)):
    try:
        if rn_data[i]['file_name'][0] not in rn_data[i]['file_name'][1]:
            file_names_in_rn.append(rn_data[i]['file_name'][0])
    except IndexError:
        continue

# DEMO vs. PRODUCTION
for d in os_data:
    temp_dict = {}
    for key, value in d.items():
        temp_dict['game_name'] = d['game_name']
        if d['game_dll'] != d['DEMO_game_dll']:
            temp_dict['game_dll'] = d['game_dll']
        if d['engine_dll'] != d['DEMO_engine_dll']:
            temp_dict['engine_dll'] = d['engine_dll']
        if d['game_version'] != d['DEMO_game_version']:
            temp_dict['game_version'] = d['game_version']
    if len(temp_dict) > 1:
        demo_vs_prod.append(temp_dict.copy())


def print_report():
    """
    prints the report of potential differences found in the games versions across local machine and the release notes
    """
    config = configparser.ConfigParser()
    config.read('resources/config.ini')
    test_time = time.ctime()
    machine = socket.gethostname()

    print('Generating report...')

    with open('internal/files_os.json', 'r') as f_os, open('internal/files_rn.json', 'r') as f_rn:
        data_os = f_os.read()
        data_rn = f_rn.read()
    files_os = json.loads(data_os)
    files_rn = json.loads(data_rn)

    with open(os.path.join(os.path.expanduser('C:/Users/Tech/Documents'), 'report_{}.txt'
            .format(config['RN']['release_note']).replace('.pdf', '').replace(' ', '-')), 'w') as f:

        f.write('AUTOMATED VERSION VERIFICATION TEST\n'
                '-----------------------------------\n')
        f.write('Release Note: {:>31}\nTimestamp: {:>30}\nTest machine: {:>17}\n\n\n'
                .format(config['RN']['release_note'], test_time, machine))
        # writing production vs. release notes check results
        f.write('+ Production Difference with Release Notes\n'
                '------------------------------------------\n')
        for i in range(len(prod_vs_rn)):
            if len(prod_vs_rn[i]) > 1 and prod_vs_rn[i]['game_name'] not in str(ignore_list):
                for key, val in prod_vs_rn[i].items():
                    f.write(key + ':'.ljust(3) + val.ljust(20))
                f.write('\n')
        f.write('\n\n')
        # writing demo vs. release notes check results
        f.write('+ Demo Difference with Release Notes\n'
                '------------------------------------\n')
        for i in range(len(demo_vs_rn)):
            if len(demo_vs_rn[i]) > 1 and demo_vs_rn[i]['DEMO_game_name'] not in str(ignore_list):
                for key, val in demo_vs_rn[i].items():
                    f.write(key + ':'.ljust(3) + val.ljust(20))
                f.write('\n')
        f.write('\n\n')

        # writing demo vs. production check results
        f.write('+ Production Difference with Demo\n'
                '---------------------------------\n')
        for i in range(len(demo_vs_prod)):
            if len(demo_vs_prod[i]) > 1 and demo_vs_prod[i]['game_name'] not in str(ignore_list):
                for key, val in demo_vs_prod[i].items():
                    f.write(key + ':'.ljust(3) + val.ljust(20))
                f.write('\n')
        f.write('\n\n')

        # writing production vs. demo file name check results
        f.write('+ Production File Name Difference with Demo\n'
                '-------------------------------------------\n')
        for file in file_names_in_rn:
            f.write('- ' + file)
        f.write('\n\n')

        # writing os vs. release notes file check results
        os_missing_files = [item for item in files_rn if item not in files_os]
        rn_missing_files = [item for item in files_os if item not in files_rn]

        f.write('+ List of Missing Files\n'
                '-----------------------\n')
        if os_missing_files:
            f.write('OS Missing Files:\n')
            for fl in os_missing_files:
                f.write('- ' + fl + '\n')
        if rn_missing_files:
            f.write('\nRelease Notes Missing Files:\n')
            for fl in rn_missing_files:
                f.write('- ' + fl + '\n')
        f.write('\n\n')

        # writing ignore list check results
        f.write('+ Special Modules\n'
                '-----------------\n')
        for d in prod_vs_rn:
            for key, value in d.items():
                if value in ignore_list and 'game_dll' in d.keys():
                    f.write(key + ':'.ljust(3) + value.ljust(20) + '\n')
        for d in demo_vs_rn:
            for key, value in d.items():
                if value in ignore_list and 'DEMO_game_dll' in d.keys():
                    f.write(key + ':'.ljust(3) + value.ljust(20) + '\n')
        f.write('\n\n')
        f.write('EOF')
        print('Report successfully stored in My Documents folder.')


def execute():
    print_report()
