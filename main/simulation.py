import pandas as pd
from crawl import *
from corp import *
from datetime import *
from collections import defaultdict
import random
import math
from logger import Logger
from stuff import human_readable_float

Log = Logger('log.txt')
temp = [] 

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

class Simulation:
    def __init__(self, universe_names_codes, _start, _end, _strategy, _wallet):
        #self.universe = [Corp(name, code, _start, _end) for (name, code) in universe_names_codes]
        self.universe = []
        univlen = len(universe_names_codes)
        i = 0
        for (name, code) in universe_names_codes:
            i += 1
            self.universe.append(Corp(name, code, _start, _end))
            print('\r                               ', end='')
            print('\rCorp Loading (' + str(i) + '/' + str(univlen) + ')', end='')
        print()
        self.universe = [corp for corp in self.universe if corp.loading_success]
        print('Loading Success (' + str(len(self.universe)) + '/' + str(univlen) + ')')
        self.start = _start
        self.end = _end
        self.strategy = _strategy
        self.wallet = _wallet
        self.contextForStrategy = {}

    def reset_with_strategy(self, _strategy):
        self.wallet.reset()
        self.strategy = _strategy
        self.contextForStrategy = {}

    def run_at(self, t):
        self.strategy(t, self.universe, self.wallet, self.contextForStrategy)

    def run(self):
        for t in daterange(self.start, self.end):
            self.run_at(t)


class Wallet:
    def __init__(self, _cash):
        self.original_cash = _cash
        self.cash = _cash
        self.stocks = defaultdict(lambda:0)  # dictionary from corp to amount of stocks
        self.history = pd.DataFrame()
        self.history['Corps'] = []

    def reset(self):
        self.cash = self.original_cash
        self.stocks = defaultdict(lambda:0)
        self.history = pd.DataFrame()
        self.history['Corps'] = []

    def can_buy(self, t, corp):
        assert(corp.can_trade(t))
        p = corp.get_buy_price(t)
        if math.isnan(self.cash / p):
            Log.writeline('debug nan', self.cash, p)
        ret = int(self.cash / p)
        return ret

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
        if not p:
            return
        self.cash -= p*amount
        self.stocks[corp] += amount

        t = str(t)
        if t not in list(self.history.columns):
            self.history[t] = ""
        name = corp.get_name()
        if name not in list(self.history['Corps']):
            self.history = self.history.append(pd.Series([name], index=['Corps']), ignore_index = True)
        s = "-" + str(amount) + "*" + str(p)
        self.history.loc[self.history['Corps'] == name, t] = s


    def sell(self, t, corp, amount):
        if amount > self.stocks[corp]:
            amount = self.stocks[corp]
        assert(amount <= self.stocks[corp])
        assert(corp.can_trade(t))
        p = corp.get_sell_price(t)
        if not p:
            return
        self.cash += p*amount
        self.stocks[corp] -= amount    

        t = str(t)
        if t not in list(self.history.columns):
            self.history[t] = ""
        name = corp.get_name()
        if name not in list(self.history['Corps']):
            self.history = self.history.append(pd.Series([name], index=['Corps']), ignore_index = True)
        s = str(amount) + "*" + str(p)
        self.history.loc[self.history['Corps'] == name, t] = s

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

    def log(self, t):
        tot = self.get_total(t)
        Log.writeline(str(t) + " total : " + str(tot) + " gain/loss : " + str( round((tot-self.original_cash)/self.original_cash * 100, 2) ) + "%")

    def log_final(self, t):
        self.log(t)
        self.liquidate(t)
        def earned(row):
            earned = 0
            for t in list(self.history.columns):
                if t == 'Corps':
                    continue
                try:
                    earned += eval(row[t])
                except Exception as e:
                    pass
            return human_readable_float(earned)

        self.history['earned'] = self.history.apply(lambda row : earned(row), axis=1)
        Log.writeline(self.history.to_string())

    def log_detail(self, t):
        self.log(t)
        tot = self.get_total(t)
        s = "cash " + str(round(self.cash / tot * 100, 2)) + "% "
        for corp in self.stocks:
            if self.stocks[corp] > 0:
                try:
                    s += corp.get_name() + " " + str( round(self.corp_value(t, corp) / tot * 100, 2) ) + "% "
                except Exception as e:
                    s += corp.get_name() + " " + "err% "
        Log.writeline(s)
        
        
        
################## Strategies #################

def RandomStrategy(t, universe, wallet, context):
    random.shuffle(universe)
    wallet.liquidate(t)
    target = universe[0]
    if target.can_trade(t):
        wallet.buy(t, universe[0], wallet.can_buy(t, universe[0]))
    wallet.log(t)

def IndexStrategyHelper(t, universe, wallet, context, index):
    if 'lastTradeDate' in context:
        if context['lastTradeDate'] + timedelta(days=365) > t: # hold for at least 365 days
            return

    #Log.writeline(t, 'candidate ', [(c.get_name(), c.get_recent_fund(t, index)) for c in universe])
    f = [c for c in universe if c.can_trade(t)]
    f = [c for c in f if c.get_recent_fund(t, index) and not math.isnan(c.get_recent_fund(t, index))]
    f.sort(key = lambda c : c.get_recent_fund(t,index))
    if len(f) > 0:
        #Log.writeline('among ', [(c.get_name(), c.get_recent_fund(t, index)) for c in f])
        wallet.liquidate(t)
        wallet.buy(t, f[0], wallet.can_buy(t, f[0]) // 2)
        Log.writeline('bought ', f[0].get_name(), ' at ', t, ' because ' + index + ' = ', f[0].get_recent_fund(t, index))
        wallet.log(t)
        context['lastTradeDate'] = t
    
def IndexStrategy(index):
    return lambda t, universe, wallet, context : IndexStrategyHelper(t, universe, wallet, context, index)


def RebalanceStrategyHelper(t, universe, wallet, context, portfolioBuilder, rebalancePeriod):
    if 'lastTradeDate' in context:
        if context['lastTradeDate'] + timedelta(days=rebalancePeriod) > t:
            return
    
    portfolio = portfolioBuilder(t, universe)
    if len(portfolio) == 0:
        return
    buying, _ = zip(*portfolio)
    for s in wallet.stocks:
        if wallet.stocks[s] > 0 and s not in buying:
            if not s.can_trade(t):
                return # can't get cash
    wallet.match_portfolio(t, portfolio)
    #wallet.log_detail(t)  # logging
    context['lastTradeDate'] = t

def RebalanceStrategy(portfolioBuilder, rebalancePeriod):
    return lambda t, universe, wallet, context: RebalanceStrategyHelper(t, universe, wallet, context, portfolioBuilder, rebalancePeriod)

def sortAndSelect(sortFunc, n, totalPercent):
    def ret(t, universe):
        f = [c for c in universe if c.can_trade(t)]
        f = [c for c in f if sortFunc(t, c) and not math.isnan(sortFunc(t, c))]
        f.sort(key = lambda c : sortFunc(t, c))
        if len(f) < n:
            return []
        f = f[:n]
        return [(c, totalPercent / n) for c in f]
    return ret


def sortAndSelectKth(sortFunc, k, n, totalPercent): # sort and divide into n even intervals. select the kth smallest interval
    def ret(t, universe):
        f = [c for c in universe if c.can_trade(t)]
        f = [c for c in f if sortFunc(t, c) and not math.isnan(sortFunc(t, c))]
        f.sort(key = lambda c : sortFunc(t, c))
        if len(f) < n:
            return []
        iLen = len(f) // n
        if k == n-1:
            f = f[iLen*k:]
        else:
            f = f[iLen*k:iLen*(k+1)] 
        return [(c, totalPercent / len(f)) for c in f]
    return ret

def IndexSort(index):
    global temp
    minus = False
    if index[0] == '-':
        index = index[1:]
        minus = True
    def ret(t, corp):
        res = corp.get_recent_fund(t, index)
        if isinstance(res, pd.Series):
            res = res.iat[0]
        if (res != None) and (math.isnan(res)):
                return None
        if minus and res != None:
            return -res
        return res
    return ret

#PERSort = IndexSort('PER')
#PERsortAndSelect = sortAndSelect(PERSort, 10, 0.7) # invest 70% in 10 lowest PER companies
#PRS = RebalanceStrategy(PERsortAndSelect, 365) # rebalance every year

def IndexRebalanceStrategy(index, n, totalPercent, rebalancePeriod):
    return RebalanceStrategy(sortAndSelect(IndexSort(index), n, totalPercent), rebalancePeriod)

def IndexKthRebalanceStrategy(index, k, n, totalPercent, rebalancePeriod):
    return RebalanceStrategy(sortAndSelectKth(IndexSort(index), k, n, totalPercent), rebalancePeriod)

PERRS = IndexRebalanceStrategy('PER', 10, 0.7, 365)
PBRRS = IndexRebalanceStrategy('PBR', 10, 0.7, 365)
    

################## Strategies #################

def Init():
    #start = date.fromordinal(date.today().toordinal()-365*5)
    end = datetime(2017,12,2) # fix date for faster corp loading
    end = datetime.date(end)
    start = date.fromordinal(end.toordinal()-365*5)
    wallet = Wallet(1000000000)

    ks = download_stock_codes('kospi')
    ks_names_codes = ks[['회사명','종목코드']]
    #universe_names_codes = [(name, code+".KS") for (name, code) in ks_names_codes.head(20).itertuples(index=False)]
    universe_names_codes = [(name, code+".KS") for (name, code) in ks_names_codes.itertuples(index=False)]

    sim = Simulation(universe_names_codes, start, end, PBRRS, wallet)
    return sim

def LowestNTest():
    sim = Init()
    def runWith(index, n, totalPercent, rebalancePeriod):
        sim.reset_with_strategy( IndexRebalanceStrategy(index, n, totalPercent, rebalancePeriod) )
        sim.run()
        #sim.wallet.log(end)

    results = {}
    df = pd.DataFrame([], columns=['index', 'n', 'totalPercent', 'earned'])

    i = 0
    nRange = 50
    simlen = 6 * nRange * 1
    startTime = datetime.now()
    for index in ['-ROE', 'EPS', 'BPS', 'DPS', 'PER', 'PBR']:
        for n in range(1, nRange + 1):
            for p in [0.7]:
                #Log.writeline('\n#### '+ index + ' test with n = ' + str(n) + ' totalPercent = ' + str(p) + ' rebalancePeriod = 365days ####')
                runWith(index, n, p, 365)
                earned = sim.wallet.earned(sim.end)
                earned = round(earned, 2)
                #results[(index,n,p)] = earned
                df = df.append({'index':index,'n':n,'totalPercent':p, 'earned':str(earned)+'%'}, ignore_index = True)
                
                i += 1
                print('\r                                       ', end='')
                print('\rSimulation : ' + str(round(i / simlen * 100, 2)) + '%   elapsed time : ' + str(datetime.now() - startTime).split('.')[0], end='')

    resultLog = Logger('result.txt')
    resultLog.writeline(df.to_string())
    resultLog.close()
    print()
    print('Finished')


def IntervalTest():
    sim = Init()
    def runWith(index, k, n, totalPercent, rebalancePeriod):
        sim.reset_with_strategy( IndexKthRebalanceStrategy(index, k, n, totalPercent, rebalancePeriod) )
        sim.run()

    df = pd.DataFrame([], columns=['index', 'k', 'n', 'earned'])

    i = 0
    n = 30
    p = 0.7
    #indexes = ['매출액', '영업이익', '당기순이익', '자산총계', '자본총계', '자본금', '영업이익률', 'ROA', 'ROE', 'EPS', 'BPS', 'DPS', 'PER', 'PBR', '배당수익률']
    indexes = ['DPS']
    simlen = len(indexes) * n 
    startTime = datetime.now()
    for index in indexes:
        for k in range(n):
            Log.writeline(index + ' ' + str(k) + '/' + str(n))
            runWith(index, k, n, p, 365)
            earned = sim.wallet.earned(sim.end)
            earned = round(earned, 2)
            df = df.append({'index':index, 'k':k, 'n':n, 'earned':str(earned)+'%'}, ignore_index = True)
            sim.wallet.log_final(sim.end)
            i += 1
            print('\r                                       ', end='')
            print('\rSimulation : ' + str(round(i / simlen * 100, 2)) + '%   elapsed time : ' + str(datetime.now() - startTime).split('.')[0], end='')

    resultLog = Logger('result.txt')
    resultLog.writeline(df.to_string())
    resultLog.close()
    print()
    print('Finished')



def main():
    IntervalTest()

    Log.close()

if __name__ == "__main__":
    main()
