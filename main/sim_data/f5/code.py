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

(sim,Sim) = sm.simInit(num=5,
        name='10 years naive strategy',
        detail = 'Do naive strategy for 10 years',
        dfrom = dfrom,
        dto = dto)


def strategy(t, comps, wallet, context):
    sim.progress = (dfrom.gap(t) / dfrom.gap(dto)) * 100
    sim.save()

    print('\r' + str(sim.progress)+'%', end='')

    if 'lastTrade' in context and context['lastTrade'] + 364 > t:
        return

    tradable = [c for c in comps if c.can_trade(t)]
    if len(tradable) < 5:
        return

    shuffle(tradable)

    portfolio = [(c,0.2) for c in tradable[:5]]

    wallet.match_portfolio(t, portfolio)

    context['lastTrade'] = t


Sim.run(strategy, startcash=1000000, modelSim=sim)

