import os, django, sys
sys.path.append('/var/www/stockAnalyzeWeb')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockAnalyzeWeb.settings")
django.setup()

from main.models import *
import main.Simulation as sm
from main.stuff import *
from main.sejong import *
from main.models import *
import pandas as pd
import os
from bs4 import BeautifulSoup
import urllib.request

#dfrom = MyDate('2012-12-03')
#dto = MyDate('2017-12-03')

sim = Simulation.objects.get(num=3)

try:
    def getSharesOutstanding(code):
        url = 'http://www.sejongdata.com/business/fin_fr_01.html?&no=' + code
        r = urllib.request.urlopen(url).read()
        soup=BeautifulSoup(r, 'html.parser')
        tds = soup.find_all('td', {"class": "bus_board_txt"})
        
        return tds[2].string

    with open('/var/www/stockAnalyzeWeb/main/sim_data/f3/log.txt', 'w', encoding='utf-8') as f:
        f.write('Start\n')
    cnt = Company.objects.all().count()
    i = 0
    for comp in Company.objects.all():
        i += 1
        sim.progress = (i / cnt) * 100
        sim.save()
        code = comp.code
        if code == "^KS11":
            continue
        ret = str(getSharesOutstanding(code))
        shares = int(ret.split(' ')[0].replace(',',''))*1000
        with open('/var/www/stockAnalyzeWeb/main/sim_data/f3/log.txt', 'a', encoding='utf-8') as f:
            f.write(str(code) + ' ' + str(ret) + ' ' + str(comp.shares) + ' -> ' + str(shares) + '\n')
        comp.shares = shares
        comp.save()

except Exception as e:
    with open('/var/www/stockAnalyzeWeb/main/sim_data/f3/log.txt', 'w', encoding='utf-8') as f:
        f.write(str(e))
