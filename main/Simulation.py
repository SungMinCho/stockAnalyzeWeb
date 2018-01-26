from main.models import *
from main.stuff import *
from collections import defaultdict
import json
import pandas as pd
import os

class Logger:
    def __init__(self, path):
        self.path = path
        f = open(path, 'w')
        f.close() # erase file initially
        self.open = True
    def close(self):
        self.open = False
    def write(self,s):
        if self.open:
            with open(self.path, 'a', encoding='utf8') as f: 
                f.write(s)
    def writeline(self,s):
        self.write(s+'\n')

class Comp:
    slippage = 0.005
    tax = 0.003
    def __init__(self, code):
        self.code = code
        self.comp = Company.objects.get(code=code)
        self.prices = self.comp.price_set.all()
        self.fundy = self.comp.fund_y_set.all()
        self.fundq = self.comp.fund_q_set.all()

    def validate(self, dfrom, dto, market):
        print('\rvalidate ' + self.code, end='')
        if self.code == '^KS11':
            return False
        if self.prices.all().count() == 0:
            return False
        if MyDate(self.prices.earliest('date').date) > dfrom:
            return False
        if MyDate(self.prices.latest('date').date) < dto:
            return False
        return True
    
    def get_fund_related_data(self, t, dataname, freq):
        try:
            if dataname == 'eps':
                return self.get_eps(t, freq)
            elif dataname == 'bps':
                return self.get_bps(t, freq)
            elif dataname == 'per':
                return self.get_per(t, freq)
            elif dataname == 'pbr':
                return self.get_pbr(t, freq)
            return None
        except Exception as e:
            return -1
    
    def get_eps(self, t, freq):
        net_profit = self.get_recent_fund(t, 'net_profit', freq)
        shares = self.comp.shares
        return net_profit / shares
    
    def get_bps(self, t, freq):
        tot_capital = self.get_recent_fund(t, 'tot_capital', freq)
        shares = self.comp.shares
        return tot_capital / shares
    
    def get_per(self, t, freq):
        eps = self.get_eps(t, freq)
        per = self.get_recent_adjc(t) / eps
        return per
    
    def get_pbr(self, t, freq):
        bps = self.get_bps(t, freq)
        pbr = self.get_recent_adjc(t) / bps
        return pbr

    def get_recent_fund(self, t, index, freq):
        if freq == 'y' or freq == 'a':
            table = self.fundy
        else:
            table = self.fundq
        try:
            row = table.filter(date__lte=t).latest('date')
            ret = getattr(row, index)
            return ret * 100000000 # 단위가 억원
        except Exception as e:
            return None
    
    def get_adjc(self, t):
        try:
            return self.prices.get(date=t).adjclose
        except Exception as e:
            return None

    def get_recent_adjc(self, t):
        try:
            return self.prices.filter(date__lte=t).latest('date').adjclose
        except Exception as e:
            return None

    def get_buy_price(self, t):
        p = self.get_adjc(t)
        if p:
            return p*(1+Comp.slippage)
        return None

    def get_sell_price(self, t):
        p = self.get_adjc(t)
        if p:
            return p*(1-Comp.slippage-Comp.tax)
        return None

    def get_recent_sell_price(self, t):
        p = self.get_recent_adjc(t)
        if p:
            return p*(1-Comp.slippage-Comp.tax)
        return None

    def can_trade(self, t):
        return (self.get_adjc(t) != None)

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        return self.code == other.code

    def __ne__(self, other):
        return not(self == other)


class Wallet:
    def __init__(self, cash, log):
        self.original_cash = cash
        self.cash = cash
        self.log = log
        self.stocks = defaultdict(lambda:0)  # dictionary from corp to amount of stocks
        self.history = pd.DataFrame()
        self.history['Corps'] = []

    def can_buy(self, t, corp):
        assert(corp.can_trade(t))
        p = corp.get_buy_price(t)
        return int(self.cash / p)
    def corp_value(self, t, corp):
        return corp.get_recent_sell_price(t) * self.stocks[corp]
    def get_total(self, t):
        ret = self.cash
        for key, value in self.stocks.items():
            sp = key.get_recent_sell_price(t)
            if sp:
                ret += sp * value
        return ret
    def get_clean_total(self, t):
        ret = self.cash
        for key, value in self.stocks.items():
            sp = key.get_recent_adjc(t)
            if sp:
                ret += sp * value
        return ret
    def buy(self, t, corp, amount):
        if amount > self.can_buy(t, corp):
            amount = self.can_buy(t, corp) # naive fix
        assert(amount <= self.can_buy(t, corp))
        assert(corp.can_trade(t))
        p = corp.get_buy_price(t)
        self.cash -= p*amount
        self.stocks[corp] += amount
        if p*amount > 0:
            self.log.writeline(str(t) + ":buy " + str(amount) + " " + corp.comp.name + corp.comp.code + " at " + human_readable_float(p*amount))
        return # don't need to record history

        t = str(t)
        if t not in list(self.history.columns):
            self.history[t] = ""
        code = corp.code
        if code not in list(self.history['Corps']):
            self.history = self.history.append(pd.Series([code], index=['Corps']), ignore_index = True)
        if 'cash' not in list(self.history['Corps']):
            self.history = self.history.append(pd.Series(['cash'], index=['Corps']), ignore_index = True)
        s = str(self.stocks[corp])
        self.history.loc[self.history['Corps'] == code, t] = s
        self.history.loc[self.history['Corps'] == 'cash', t] = str(self.cash)
    def sell(self, t, corp, amount):
        if amount > self.stocks[corp]:
            amount = self.stocks[corp]
        assert(amount <= self.stocks[corp])
        assert(corp.can_trade(t))
        p = corp.get_sell_price(t)
        self.cash += p*amount
        self.stocks[corp] -= amount
        if p*amount > 0:
            self.log.writeline(str(t) + ":sell " + str(amount) + " " + corp.comp.name + corp.comp.code + " at " + human_readable_float(p*amount))
        return # don't need to record history

        t = str(t)
        if t not in list(self.history.columns):
            self.history[t] = ""
        code = corp.code
        if code not in list(self.history['Corps']):
            self.history = self.history.append(pd.Series([code], index=['Corps']), ignore_index = True)
        if 'cash' not in list(self.history['Corps']):
            self.history = self.history.append(pd.Series(['cash'], index=['Corps']), ignore_index = True)
        s = str(self.stocks[corp])
        self.history.loc[self.history['Corps'] == code, t] = s
        self.history.loc[self.history['Corps'] == 'cash', t] = str(self.cash)
    def sell_all(self, t, corp):
        self.sell(t, corp, self.stocks[corp])
    def buy_target(self, t, corp, target):
        assert(target >= self.stocks[corp])
        self.buy(t, corp, target - self.stocks[corp])
    def sell_target(self, t, corp, target):
        assert(target <= self.stocks[corp])
        self.sell(t, corp, self.stocks[corp] - target)
    def match_target(self, t, corp, target):
        if target > self.stocks[corp]:
            self.buy_target(t, corp, target)
        else:
            self.sell_target(t, corp, target)
    def match_portfolio(self, t, corpPercent): # invest total*p in corp. corpPercent : (corp * percent) list
        tot = 0
        buyCorps = []
        for (corp, p) in corpPercent:
            assert(corp.can_trade(t))
            assert(0 <= p and p <= 1)
            buyCorps.append(corp)
            tot += p
        assert(tot <= 1)
        # get cash first
        for corp in self.stocks:
            if corp not in buyCorps and corp.can_trade(t):
                self.sell_all(t, corp)
        for (corp, p) in corpPercent:
            target_cash = self.get_total(t)*p # is it right to use get_total()?
            target = int(target_cash / corp.get_buy_price(t))
            self.match_target(t, corp, target)
    def liquidate(self, t):
        for key, value in self.stocks.items():
            if key.can_trade(t):
                self.sell(t, key, value)
    def earned(self, t):
        tot = self.get_total(t)
        return round( (tot - self.original_cash) / self.original_cash * 100, 2 )
    def conclude(self):
        pass
    def record(self, t, chart):
        d = SfData()
        d.chart = chart
        d.x = t.__str__()
        d.y = self.get_clean_total(t)
        d.save()




class Sim:
    def __init__(self, dfrom, dto, simfolder, simnum):
        self.log = Logger(os.path.join(simfolder, 'log.txt'))
        self.dfrom = dfrom
        self.dto = dto
        self.comps = [Comp(c.code) for c in Company.objects.all()]
        self.log.writeline('Load ' + str(len(self.comps)))
        market = Comp('^KS11')
        self.comps = [c for c in self.comps if c.validate(dfrom, dto, market)]
        self.log.writeline('Valid ' + str(len(self.comps)))
        self.simfolder = simfolder
        self.simnum = simnum

    def run(self, strategy, startcash, modelSim, justResult=False):
        if not justResult:
            # write metadata
            metadata = {}
            metadata['from'] = self.dfrom.__str__()
            metadata['to'] = self.dto.__str__()
            metadata['startcash'] = startcash
            metadata['companyCodes'] = [c.code for c in self.comps]
            json.dump(metadata, open(os.path.join(self.simfolder, 'metadata.txt'), 'w'))

        wallet = Wallet(startcash, self.log)

        if justResult:
            log.close()

        context = {}
        if not justResult:
            chart = Chart()
            chart.sim = modelSim
            chart.name = 'simulation' # required
            chart.save()
        for d in mdrange(self.dfrom, self.dto+1):
            strategy(d, self.comps, wallet, context)
            if not justResult:
                wallet.record(d, chart)

        wallet.conclude()

        modelSim.progress = 100.0
        modelSim.save()

        return wallet.earned(self.dto)

def simInit(num, name, detail, dfrom, dto, progress=0.0):
    try:
        sim = Simulation.objects.get(num=num)
        sim.delete()
    except Exception as e:
        pass
    sim = Simulation()
    sim.num = num
    sim.name = name
    sim.detail = detail
    sim.progress = progress
    sim.save()
    SimInstance = Sim(dfrom, dto, '/var/www/stockAnalyzeWeb/main/sim_data/f'+str(num), num)
    return (sim, SimInstance)
