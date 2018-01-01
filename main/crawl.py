import urllib.parse
import pandas as pd
from pandas_datareader import data as pdr
from pandas_datareader.google.daily import GoogleDailyReader
#import fix_yahoo_finance as yf
from tabulate import tabulate
from datetime import *
from yahoo_finance import Share
import urllib.request
from bs4 import BeautifulSoup
import re

#yf.pdr_override()

MARKET_CODE_DICT = {
    'kospi': 'stockMkt',
    'kosdaq': 'kosdaqMkt',
    'konex': 'konexMkt'
}

DOWNLOAD_URL = 'kind.krx.co.kr/corpgeneral/corpList.do'

def download_stock_codes(market=None, delisted=False):
    params = {'method': 'download'}

    if market.lower() in MARKET_CODE_DICT:
        params['marketType'] = MARKET_CODE_DICT[market]

    if not delisted:
        params['searchType'] = 13

    params_string = urllib.parse.urlencode(params)
    request_url = urllib.parse.urlunsplit(['http', DOWNLOAD_URL, '', params_string, ''])

    df = pd.read_html(request_url, header=0)[0]
    df.종목코드 = df.종목코드.map('{:06d}'.format)

    return df

def snapshot_url(code):
    code = code.split('.')[0]
    return "http://comp.fnguide.com/SVO2/ASP/SVD_Main.asp?pGB=1&gicode=A"+ code + "&cID=&MenuYn=Y&ReportGB=&NewMenuID=101&stkGb=701"


def rowSplit(row, colLen):
    #for txt in row.findAll(text=True):
    try:
        head = row.find('span', {'class' : 'txt_acd'})
        head = head.text
    except Exception as e:
        head = row.find('th').find(text=True)
    head = str(head).strip()

    values = [head]
    for txt in row.findAll(text=True):
        pass
        if re.match(r'\d[\d,.]*', txt):
            values.append(float(str(txt).replace(',','')))
    #print(values, len(values))
    while len(values) < colLen:
        values.append(float('nan'))
    return values

def fnguideSoupToPandas(soup):
    trs = soup.find_all('tr')
    cols = [t for t in trs if t.find_all('th', {'scope' : 'col'})]
    rows = [t for t in trs if t.find_all('th', {'scope' : 'row'})]

    assert(len(cols) == 2)    

    cols = cols[1]
    columns = ['subject']

    for txt in cols.findAll(text=True):
        if re.match(r'^(19|20)\d\d[- /.](0[1-9]|1[012])(\(E\))?', txt):
            columns.append(str(txt))
     
    #print(columns, len(columns)) 
    #for row in rows:
    #    rowSplit(row)
    #res = pd.concat([pd.DataFrame(rowSplit(row), columns=columns) for row in rows], ignore_index=True)
    res = pd.DataFrame([rowSplit(row, len(columns)) for row in rows], columns=columns)
    #print(res)
    return res


def get_fund_helper(code, tableIndex):
    url = snapshot_url(code)
    f = urllib.request.urlopen(url).read()
    soup=BeautifulSoup(f, 'html.parser')
    tables = soup.find_all('table')
    ret = fnguideSoupToPandas(tables[tableIndex])
    ret = ret.set_index('subject')
    return ret

def get_fund_byYear(code):
    return get_fund_helper(code, 11)

def get_fund_byQuarter(code):
    return get_fund_helper(code, 12)

def get_stock(code, start=date.fromordinal(date.today().toordinal()-365*5), end=date.today()):
    return pdr.DataReader(code, "yahoo", start, end)

def get_kospi(code, start=date.fromordinal(date.today().toordinal()-365*5), end=date.today()):
    return get_stock(code+".KS", start, end)

#Fix this. can't get kosdaq from both google and yahoo.
def get_kosdaq(code, start=date.fromordinal(date.today().toordinal()-365*5), end=date.today()):
    #return get_stock(code+".KQ", start, end)
    return pdr.DataReader("KOSDAQ:"+code, "google", start, end)


def pp(s):
    print(tabulate(s))

def main():
    """
    ks_codes = download_stock_codes('kospi')

    results = {}

    for code in ks_codes.종목코드.head():
        try:
            results[code] = get_kospi(code)
        except Exception as e:
            pass

    df = pd.concat(results, axis=1)
    pp(df.loc[:,pd.IndexSlice[:, 'Adj Close']].tail()) 
    """
    print(get_fund_byQuarter('005930'))


if __name__ == "__main__":
   main()
