from main.models import *
import main.Simulation as sm
from main.stuff import *
from random import shuffle

try:
    sim = Simulation.objects.get(num=2)
    sim.delete()
except Exception as e:
    pass

sim = Simulation()
sim.num = 2
sim.name = 'Naive strategy for testing'
sim.detail = 'Buy 5 random companies at each rebalancing period=365'
sim.progress = 0.0
sim.save()


dfrom = MyDate('2012-12-03')
dto = MyDate('2017-12-03')

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


Sim = sm.Sim(dfrom, dto, 'main/sim_data/f2', 2)
Sim.run(strategy, 1000000)
sim.progress = 100.0
sim.save()
