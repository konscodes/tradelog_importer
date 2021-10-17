import pandas as pd
from time import time
import random
from datetime import datetime

from pandas.core import series

path = 'tradelog_importer/trades/trades.csv'
df = pd.read_csv(path, sep=',', header=0, engine='python')

range_df = pd.DataFrame(columns=['Upper', 'Lower', 'Rate'])
sim_df = pd.DataFrame(columns=['Gross'])

def performance(func):
    def wrapper(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Runtime is {round(t2 - t1, 2)}s\n')
        return result
    return wrapper

@performance
def my_data():
    global range_df
    trades_total = df.index.stop
    print(f'# Trades: {trades_total}')
    win_number = len(df[df['Gross'] > 0].index)
    print(f'# Win: {win_number}')
    loss_number = len(df[df['Gross'] < 0].index)
    print(f'# Loss: {loss_number}')
    win_rate = win_number/trades_total
    print(f'Win rate: {win_rate:.0%}')
    max_win = df['Gross'].max()
    print(f'Max win: {max_win}')
    max_loss = df['Gross'].min()
    print(f'Max loss: {max_loss}')
    print()
    split_factor = 5
    split = (abs(max_loss) + max_win)/split_factor
    upper = max_win
    for i in range(split_factor):
        lower = upper - split
        trades_range = len(df[df['Gross'].between(lower, upper)].index)
        occurrence = trades_range/trades_total
        print(f'Range from {round(upper, 2)} to {round(lower, 2)}: {occurrence:.0%}')
        range_data = {'Upper': upper, 'Lower': lower, 'Rate': occurrence}
        range_df = range_df.append(range_data, ignore_index=True)
        upper = lower

@performance
def sim_data():
    global range_df
    global sim_df
    trades_total = 100
    for i in range_df.index:
        upper = range_df.loc[i]['Upper']
        lower = range_df.loc[i]['Lower']
        rate = range_df.loc[i]['Rate']
        trades = int(trades_total * rate)
        print(trades)
        gross = list(map(lambda i: random.uniform(lower, upper), range(trades)))
        print(gross)

my_data()
sim_data()
#print(range_df)


