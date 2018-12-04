import re
import os.path
import time
import urllib.request
from bs4 import BeautifulSoup

# ROGuard Endless Tower URL
URL = 'http://www.roguard.net/game/endless-tower/'
# Time in minutes to update
UPD_MINUTES = 15

#-------------------------------------------------------------------

UPD_SEC = UPD_MINUTES * 60

# get new data if cached one is older than
# desired update time
if not os.path.isfile('ET_dump.txt') or \
    time.time() - os.path.getmtime('ET_dump.txt') > UPD_SEC:

    with urllib.request.urlopen(URL) as response:
        webpage = response.read()
        with open('ET_dump.txt', 'w') as f:
            print(webpage, file=f)
            print('UPDATED ENDLESS TOWER DATA')

with open('ET_dump.txt') as cached_response:
    webpage = cached_response.read()
    soup = BeautifulSoup(webpage, 'html.parser')
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
    	if i == 1:
    		print(channel, i*10)
    	