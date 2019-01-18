import re
import os.path
import time
import urllib.request
from bs4 import BeautifulSoup

# Time in minutes to update
UPD_MINUTES = 60

# ROGuard Endless Tower URL
URL = 'http://www.roguard.net/game/endless-tower/'

#-------------------------------------------------------------------

UPD_SEC = UPD_MINUTES * 60
CACHE_FNAME = 'ET_dump.txt'
IDMAP_FNAME = 'roguard_mon_id.txt'

def is_valid_channel(channel):
    # check for valid channels ourselves because ROGuard doesn't
    #TODO
    return True

def check_cache():
    # get new data if cached one is older than desired
    # update time; create a cache if necessary
    if not os.path.isfile(CACHE_FNAME) or \
        time.time() - os.path.getmtime(CACHE_FNAME) > UPD_SEC:

        with urllib.request.urlopen(URL) as response:
            webpage = response.read()
            with open(CACHE_FNAME, 'w') as f:
                print(webpage, file=f)
                print('---UPDATED ENDLESS TOWER DATA---\n')

def parse_monster_id_map():
    id_map = {}
    with open(IDMAP_FNAME) as file:
        for line in file:
            num, monster = line.strip().split(': ')
            id_map[int(num)] = monster
    return id_map

def get_floor(monster, soup):
    matches = []

    for target in soup.find_all('a', title=re.compile(monster)):
        p = target.find_parent('td')
        i = 1
        channel = p.find_previous_sibling('td').string
        while channel is None:
            p = p.find_previous_sibling('td')
            channel = p.find_previous_sibling('td').string
            i += 1

            #TOREMOVE
            if i > 100:
               assert False, 'Bug in the program'

        floor = i*10
        if is_valid_channel(channel):
            matches.append((floor, channel))

    matches.sort(key=lambda x: x[0])

    for floor, channel in matches:
        print(channel, 'Floor', floor)

def test(soup):
    monster_tables = soup.find_all('table')

    mvp_table = monster_tables[0].find('tbody')
    mini_table = monster_tables[0].find('tbody')

    parse_table(mvp_table)

def monster_id_mapper(soup):
    id_map = {}

    # pattern = re.compile(r'"(\d*)"\s*>\s*(\S*)\s*<')
    # for v in soup.find_all('option'):
    #     match = pattern.search(str(v))
    #     if match:
    #         id_map[int(match.group(1))] = match.group(2)

    # for k, v in id_map.items():
    #     print("%s: '%s'" % (k, v))

    pattern = re.compile(r'\/db\/monsters\/(\d*)\/.*title="(\S*)')
    for v in soup.find_all('a'):
        match = pattern.search(str(v))
        if match:
            id_map[int(match.group(1))] = match.group(2)

    for k in sorted(id_map):
        d = id_map[k]
        print("%s: %s" % (k, d))

def parse_table(table):

    channel_id_pattern = re.compile(r'.*>\s*(\d)\s*<.*')
    monster_id_pattern = re.compile(r'href\s*=\s*"\/db\/monsters\/(\d.*)\/"')

    def get_channel_id(columns):
        # get channel ID on the leftmost column
        return int(channel_id_pattern.match(str(columns[0])).group(1))

    def parse_columns(columns):
        pass

    contents = []
    for i, channel in enumerate(table.children):
        if i % 2 == 1: # useful data are on odd indices

            columns = channel.find_all('td')
            
            channel_id = get_channel_id(columns)

            print(channel_id)
            assert False

            contents.append(channel)
    return contents


def read_et_list(targets):

    check_cache()

    with open(CACHE_FNAME) as cached_response:
        webpage = cached_response.read()
        soup = BeautifulSoup(webpage, 'html.parser')

        # TESTING
        #test(soup)
        
        matches = []

        for target in soup.find_all('a', title=re.compile('Mistress')):
            p = target.find_parent('td')
            i = 1
            channel = p.find_previous_sibling('td').string
            while channel is None:
                p = p.find_previous_sibling('td')
                channel = p.find_previous_sibling('td').string
                i += 1
                if i > 100:
                   assert False, 'Bug in the program'

            floor = i*10
            if is_valid_channel(channel):
                matches.append((floor, channel))

        matches.sort(key=lambda x: x[0])

        for floor, channel in matches:
            print(channel, 'Floor', floor)

read_et_list([])
    