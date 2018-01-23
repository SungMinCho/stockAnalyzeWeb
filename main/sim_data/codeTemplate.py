import os, django, sys
sys.path.append('/var/www/stockAnalyzeWeb')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockAnalyzeWeb.settings")
django.setup()

from main.models import *
import main.Simulation as sm
from main.stuff import *
from random import shuffle

dfrom = MyDate('2012-12-03')
dto = MyDate('2017-12-03')

(sim,Sim) = sm.simInit(num=NUM,
        name='New strategy',
        detail = 'New strategy created',
        dfrom = dfrom,
        dto = dto)


def strategy(t, comps, wallet, context):
    sim.progress = (dfrom.gap(t) / dfrom.gap(dto)) * 100
    sim.save()
    return


Sim.run(strategy, startcash=1000000, modelSim=sim)

