import os, django, sys
sys.path.append('/var/www/stockAnalyzeWeb')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockAnalyzeWeb.settings")
django.setup()

from main.models import *
import main.Simulation as sm
from main.stuff import *
from random import shuffle

dfrom = MyDate('2007-12-03')
dto = MyDate('2017-12-03')

(sim,Sim) = sm.simInit(num=6,
        name='10 years buy 5 lowest PER every year',
        detail = 'Buy 5 companies with lowest PER every 365 days for 10 years',
        dfrom = dfrom,
        dto = dto)


def strategy(t, comps, wallet, context):
    sim.progress = (dfrom.gap(t) / dfrom.gap(dto)) * 100
    sim.save()

    if 'lastTrade' in context and context['lastTrade'] + 365 > t:
        return

    tradable = [c for c in comps if c.can_trade(t)]

    tradable = [c for c in tradable if c.get_fund_related_data(t, 'per', 'y') is not None]
    if len(tradable) < 5:
        return
    
    tradable = sorted(tradable, key = lambda c : c.get_fund_related_data(t, 'per', 'y'))

    portfolio = [(c,0.2) for c in tradable[:5]]

    wallet.match_portfolio(t, portfolio)

    context['lastTrade'] = t

try:
    Sim.run(strategy, startcash=1000000, modelSim=sim)
except Exception as e:
    with open('/var/www/stockAnalyzeWeb/main/sim_data/f6/error.txt', 'w', encoding='utf-8') as f:
        f.write(str(e))

