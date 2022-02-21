import pandas as pd
import requests, time
import matplotlib.pyplot as plt

#parametros de los gráficos
plt.style.use('seaborn-white')
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"
plt.rcParams["font.size"] = 15

# obtener apikey gratuita en https://fmpcloud.io/ (lleva 1 minuto)
apikey = 'acá_va_tu_APIkey_como_string'

#==============================================================================
# función para obtener el balance sheet, income statement y cashflow statement
def getFundamental(symbol, what, period):
    p = {'apikey' : apikey, 'period' : period} # annual (gratis) o quarter (pago)
    if what == 'balance_sheet':
        url = 'https://fmpcloud.io/api/v3/balance-sheet-statement/'+symbol
    elif what == 'income_st':
        url = 'https://fmpcloud.io/api/v3/income-statement/'+symbol
    elif what == 'cash_flow':
        url = 'https://fmpcloud.io/api/v3/cash-flow-statement/'+symbol       
        
    r = requests.get(url, params = p)
    js = r.json()
    df = pd.DataFrame(js)
    return df[::-1]
#==============================================================================

tickers = ['FB', 'AAPL', 'MSFT', 'AMZN', 'GOOGL']
for ticker in tickers:
    
    inc = getFundamental(symbol = ticker, what='income_st', period='annual')
    inc['r&d_to_revs'] = inc['researchAndDevelopmentExpenses'] / inc['revenue'] *100
    cf = getFundamental(symbol = ticker, what='cash_flow', period='annual')
    cf.set_index(pd.to_datetime(cf['date']), inplace=True)
    time.sleep(8)
    # gráfico
    fig, ax = plt.subplots(figsize=(12,6))
    ax.set_title(f'{ticker}', fontweight='bold')
    ax.set_facecolor('lightgray')
    ax.axhline(0, c='k', lw=0.8)
    revs = ax.bar([i.year for i in cf.index], inc['revenue']/1000000000, label='Revenue', align='center',
                  width=0.45, color='w', edgecolor='k')
    
    rd = ax.bar([i.year for i in cf.index], inc['researchAndDevelopmentExpenses']/1000000000,
                label='Research & Development', align='center',
                bottom=[max(cf['freeCashFlow'][i]/1000000000, 0) for i in range(len(cf))], width=0.45, color='lightsalmon', edgecolor='k')
    
    fcf = ax.bar([i.year for i in cf.index], cf['freeCashFlow']/1000000000, label='Free Cash Flow',
                 align='center', width=0.45, color='yellowgreen', edgecolor='k') 
    ax.set_ylabel('USD Bn')
    
    ax2 = ax.twinx()
    rd_revs = ax2.plot([i.year for i in cf.index], inc['r&d_to_revs'],
                       ls='--', c='k', lw=1.5, label='R&D to Revenue')
    ax2.set_ylabel('R&D / Revenue (%)')
    ax2.set_ylim(inc['r&d_to_revs'].min()*0.9 , inc['r&d_to_revs'].max()*1.1)
    
    lines_1, labels_1 = ax.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax.legend(lines_1 + lines_2, labels_1 + labels_2, loc=0)
    
    plt.show()
