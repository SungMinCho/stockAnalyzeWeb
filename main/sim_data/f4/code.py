import os, django, sys
sys.path.append('/var/www/stockAnalyzeWeb')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockAnalyzeWeb.settings")
django.setup()

from main.models import *
import main.Simulation as sm
from main.stuff import *
from random import shuffle
import main.crawl as cw

dfrom = MyDate('2007-11-30')
dto = MyDate('2018-01-26')

sim = Simulation.objects.get(num=4)
if sim.name == 'New strategy':
    sim.name = 'Price getter'
    sim.detail = 'Get prices'
    sim.save()

log = sm.Logger('/var/www/stockAnalyzeWeb/main/sim_data/f4/log.txt')

try:
    def save(comp):
        #earliest = comp.price_set.earliest('date').date
        #latest = comp.price_set.latest('date').date
        new_data = None
        for trying in range(5):
            try:
                #to = MyDate(earliest)
                log.writeline(comp.name)
                #og.writeline(str(dfrom) + '~' + str(dto))
                new_data = cw.get_kospi(comp.code, start=dfrom.date, end=dto.date)
                break
            except Exception as e:
                pass
        if new_data is None:
            return
        
        #log.writeline(earliest + ' ~ ' + latest)
        #log.writeline(new_data.to_string())
        
        for index, row in new_data.iterrows():
                d = str(index).split(' ')[0]
                
                if Price.objects.filter(company=comp).filter(date=d).count() > 0:
                    #log.writeline(d + ' exists')
                    continue
                try:
                    pt = Price(company=comp,
                            date=d,
                            open = row['Open'],
                            close = row['Close'],
                            high = row['High'],
                            low = row['Low'],
                            adjclose = row['Adj Close'],
                            volume = row['Volume'])
                    pt.save()
                    #log.writeline(d + ' saved')
                except Exception as e:
                    pass
        
        

    log.writeline('Start')
    cnt = Company.objects.all().count()
    i = 0
    for comp in Company.objects.all():
        i += 1
        sim.progress = (i / cnt) * 100
        sim.save()
        code = comp.code
        save(comp)
        
        #if i > 1:
            #break
    log.writeline('End')

except Exception as e:
    log.writeline(str(e))
