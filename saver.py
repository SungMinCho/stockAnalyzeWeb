from stockAnalyzeWeb.wsgi import *
from pandas import *
from main.models import * 

def saver(ks):
    for index, r in ks.iterrows():

        code = r['종목코드']

        pwd = '/var/www/stockAnalyzeWeb/main/data'

        c = Company(market='kospi', name=r['회사명'], code=r['종목코드'], category=r['업종'], products=r['주요제품'], listedDate=r['상장일'], settlementMonth=r['결산월'], representative=r['대표자명'], homepage=r['홈페이지'], area=r['지역'], prices=os.path.join(pwd, code+'.KS_prices'), fundY=os.path.join(pwd, code+'.KS_fundByYear'), fundQ=os.path.join(pwd, code+'.KS_fundByQuarter'))
        c.save()


def pricestablesaver():
    counter = 0
    for c in Company.objects.all():
        counter += 1
        print('\r       ', end='')
        print(counter, end='')
        try:
            p = read_pickle('/var/www/stockAnalyzeWeb/main/data/' + c.code + '.KS_prices')
            for index, row in p.iterrows():
                pt = Price(company=c,
                        date=str(index).split(' ')[0],
                        open = row['Open'],
                        close = row['Close'],
                        high = row['High'],
                        low = row['Low'],
                        adjclose = row['Adj Close'],
                        volume = row['Volume'])
                pt.save()
        except Exception as e:
            print(e, end='')

def main():
    pricestablesaver()

