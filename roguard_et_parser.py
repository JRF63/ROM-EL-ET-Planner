import re
import pickle
import os.path
import time
import urllib.request
from bs4 import BeautifulSoup

# Time in minutes to update
UPD_MINUTES = 600

# ROGuard Endless Tower URL
URL = 'http://www.roguard.net/game/endless-tower/'

#-------------------------------------------------------------------

UPD_SEC = UPD_MINUTES * 60
CACHE_FNAME = 'ET_dump.pickle'
IDMAP_FNAME = 'roguard_mon_id.txt'


def parse_monster_id_map():
    id_map = {}
    with open(IDMAP_FNAME) as file:
        for line in file:
            num, monster = line.strip().split(': ')
            id_map[int(num)] = monster
    return id_map

def monster_id_utility(soup):
    # Prints out monster ID to monster name mapping
    id_map = {}

    pattern = re.compile(r'\/db\/monsters\/(\d*)\/.*title.*"(.*) -')
    for v in soup.find_all('a'):
        match = pattern.search(str(v))
        if match:
            id_map[int(match.group(1))] = match.group(2)

    for k in sorted(id_map):
        d = id_map[k]
        print("%s: %s" % (k, d))

def parse_data(soup):

    pattern = re.compile(r'(\d{1,3})F')
    et_data = {}

    def get_floors(table):
        floors = []
        for data in table.find_all('th')[1:]: # first entry is empty
            match = pattern.search(str(data))
            floors.append(int(match.group(1)))
        return floors


    def build_data(mob_list, floors):
        for channel_id, channel_mobs in mob_list.items():
            for floor, floor_mobs in zip(floors, channel_mobs):
                if floor not in et_data:
                    et_data[floor] = {}
                et_data[floor][channel_id] = floor_mobs
        return et_data

    monster_tables = soup.find_all('table')

    mvp_floors = get_floors(monster_tables[0])
    mvp_list = parse_table(monster_tables[0].find('tbody'))
    build_data(mvp_list, mvp_floors)

    mini_list = parse_table(monster_tables[1].find('tbody'))
    mini_floors = get_floors(monster_tables[1])
    build_data(mini_list, mini_floors)

    return et_data

def parse_table(table):

    channel_id_pattern = re.compile(r'.*>\s*(\d)\s*<.*')
    monster_id_pattern = re.compile(r'\/db\/monsters\/(\d*)\/')

    id_map = parse_monster_id_map()

    def get_channel_id(columns):
        # get channel ID on the leftmost column
        return int(channel_id_pattern.match(str(columns[0])).group(1))

    def parse_columns(columns):
        floors = []
        for column in columns[1:]: # skip first column
            mons_in_floor = []
            for match in monster_id_pattern.finditer(str(column)):
                mons_in_floor.append(id_map[int(match.group(1))])
            floors.append(mons_in_floor)
        return floors
            

    contents = {i: None for i in range(10)}
    for i, channel in enumerate(table.children):
        if i % 2 == 1: # useful data are on odd indices

            columns = channel.find_all('td')
            
            channel_id = get_channel_id(columns)

            floors = parse_columns(columns)
            contents[channel_id] = floors
            
    return contents

def check_cache():
    # get new data if cached one is older than desired
    # update time; create a cache if necessary
    if not os.path.isfile(CACHE_FNAME) or \
        time.time() - os.path.getmtime(CACHE_FNAME) > UPD_SEC:

        with urllib.request.urlopen(URL) as response:
            webpage = response.read()
            soup = BeautifulSoup(webpage, 'html.parser')
            et_data = parse_data(soup)

            with open(CACHE_FNAME, 'wb') as f:
                pickle.dump(et_data, f)
                print('---UPDATED ENDLESS TOWER DATA---\n')


def read_et_list(targets):
    check_cache()

    with open(CACHE_FNAME, 'rb') as f:
        et_data = pickle.load(f)


read_et_list([])
    