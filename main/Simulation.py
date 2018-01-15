from main.models import *
from main.stuff import *
from collections import defaultdict
import json
import pandas as pd
import os

class Logger:
    def __init__(self, path):
        self.path = path
        self.f = open(path, 'a')
        self.open = True
    def close(self):
        if self.open:
            self.f.close()
            self.open = False
    def write(self,s):
        if self.open:
            self.f.write(s)
    def writeline(self,s):
        if self.open:
            self.f.write(s+'\n')

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

    def get_recent_fund(self, t, index):
        # using fundy for now
        try:
            row = self.fundy.filter(date__lte=t).latest('date')
            ret = getattr(row, index)
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
        if self.log.open:
            self.history.to_pickle(self.log.path)
    def record(self, t, chart):
        d = SfData()
        d.chart = chart
        d.x = t.__str__()
        d.y = self.get_clean_total(t)
        d.save()




class Sim:
    def __init__(self, dfrom, dto, simfolder, simnum):
        self.dfrom = dfrom
        self.dto = dto
        self.comps = [Comp(c.code) for c in Company.objects.all()]
        print('Load ' + str(len(self.comps)))
        market = Comp('^KS11')
        self.comps = [c for c in self.comps if c.validate(dfrom, dto, market)]
        print('Valid ' + str(len(self.comps)))
        self.simfolder = simfolder
        self.simnum = simnum

    def run(self, strategy, startcash, justResult=False):
        if not justResult:
            # write metadata
            metadata = {}
            metadata['from'] = self.dfrom.__str__()
            metadata['to'] = self.dto.__str__()
            metadata['startcash'] = startcash
            metadata['companyCodes'] = [c.code for c in self.comps]
            json.dump(metadata, open(os.path.join(self.simfolder, 'metadata.txt'), 'w'))

        result = Logger(os.path.join(self.simfolder, 'result.txt'))
        wallet = Wallet(startcash, result)

        if justResult:
            result.close()

        context = {}
        sim = Simulation.objects.get(num=self.simnum)
        if not justResult:
            chart = Chart()
            chart.sim = sim
            chart.name = 'simulation'
            chart.save()
        for d in mdrange(self.dfrom, self.dto+1):
            strategy(d, self.comps, wallet, context)
            if not justResult:
                wallet.record(d, chart)

        wallet.conclude()

        return wallet.earned(self.dto)
