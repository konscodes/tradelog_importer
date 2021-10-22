import pandas as pd
from time import time
import random
import plotly.graph_objects as go
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
#path = 'tradelog_importer/trades/trades.csv'
path = filedialog.askopenfilename()
df = pd.read_csv(path)
range_df = pd.DataFrame(columns=['Upper', 'Lower', 'Rate'])
sim_df = pd.DataFrame(columns=['Data', 'Running'])

def performance(func):
    def wrapper(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Runtime is {round(t2 - t1, 2)}s\n')
        return result
    return wrapper


def user_input(option):
    if option == 'for trades':
        while True:
            trades_total = input('Input total number of trades for simulation (Def: 3000): ')
            try:
                trades_total = int(trades_total)
                break
            except ValueError:
                print('Error! Only int values can be used\n')
        return trades_total
    elif option == 'for split':
        while True:
            split_factor = input('Split your data into ranges to calculate the probabilities.\nInput a split factor: ')
            try:
                split_factor = int(split_factor)
                break
            except ValueError:
                print('Error! Only int values can be used\n')
        return split_factor


@performance
def my_data():
    global range_df
    trades_total = df.index.stop
    print(f'# Trades: {trades_total}')
    win_number = len(df[df['Data'] > 0].index)
    print(f'# Win: {win_number}')
    loss_number = len(df[df['Data'] < 0].index)
    print(f'# Loss: {loss_number}')
    win_rate = win_number/trades_total
    print(f'Win rate: {win_rate:.0%}')
    max_win = df['Data'].max()
    print(f'Max win: {max_win}')
    max_loss = df['Data'].min()
    print(f'Max loss: {max_loss}')
    print()
    split_factor = user_input('for split')
    print()
    split = (abs(max_loss) + max_win)/split_factor
    upper = max_win + 0.01
    for i in range(split_factor):
        lower = upper - split - 0.01
        trades_range = len(df[df['Data'].between(lower, upper)].index)
        occurrence = trades_range/trades_total
        print(f'Range from {round(upper, 4)} to {round(lower, 4)}, and {trades_range} trades')
        print(f'Occurrence: {occurrence}')
        range_data = {'Upper': upper, 'Lower': lower, 'Rate': occurrence}
        range_df = range_df.append(range_data, ignore_index=True)
        upper = lower


@performance
def sim_data():
    global range_df
    global sim_df
    trades_total = user_input('for trades')
    print()
    for i in range_df.index:
        upper = range_df.loc[i]['Upper']
        lower = range_df.loc[i]['Lower']
        rate = range_df.loc[i]['Rate']
        # Number of trades for each p/l range
        trades = int(trades_total * rate) 
        # For each trade generate random float p/l from corresponding range
        gross = list(map(lambda i: random.uniform(lower, upper), range(trades)))
        data = {'Data': gross}
        sim_df = sim_df.append(pd.DataFrame(data), ignore_index=True)
    
    sim_df = sim_df.sample(frac=1)
    sim_df.reset_index(inplace=True, drop=True)
    
    for i in sim_df.index:
        if i == 0:
            sim_df.at[i, 'Running'] = sim_df.loc[i]['Data']
        else:
            sim_df.at[i, 'Running'] = sim_df.loc[i]['Data'] + sim_df.loc[i-1]['Running']
    print(sim_df)


def plot_data():
    fig = go.Figure()
    scatter_plot = go.Scatter(x=sim_df.index, y=sim_df['Running'])
    fig.add_trace(scatter_plot)
    fig.update_layout(
        title={'text': "Simulated trading data over a number of trades", 'x':0.5},
        xaxis_title="Number of trades",
        yaxis_title="Data cumulative",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        )
    )
    fig.show()

print(df, '\n')
my_data()
sim_data()
plot_data()
