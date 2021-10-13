from numpy.lib.function_base import average
import pandas as pd
from time import time
import random
from datetime import datetime
import pdb

class Executions:
    def __init__(self, path):
        self.path = path
        self.df = pd.read_csv(path, sep='|', header=None, skiprows=5, engine='python', skipfooter=1)
        missing_check = pd.isnull(self.df[2])
        self.df = self.df[missing_check == False]
        self.df[7] = pd.to_datetime(self.df[7], format='%Y%m%d').dt.date
        self.df[8] = pd.to_datetime(self.df[8], format='%H:%M:%S').dt.time
        #self.df['DateTime'] = self.df[7].astype(str) + ' ' + self.df[8].astype(str)
        self.df[8] = self.df.apply(lambda r : datetime.combine(r[7],r[8]), 1)
        # self.df[8] = pd.to_datetime(self.df[7] + ' ' + self.df[8]) if type(self.df[7][0]) is str else self.df[8]
        self.df = self.df.drop(columns=[0,3,4,5,7,9,11,13,15])
        self.df = self.df.rename(columns={1:'ID', 2:'Symb', 6:'Code', 8:'Date Time', 10:'Shares', 12:'Price', 14:'Comm'})
        self.df = self.df.sort_values(by='Date Time')

class Trades:
    def __init__(self):
        headers = ['Open', 'Close', 'Held', 'Symb', 'Side', 'Avr Entry', 'Avr Exit', 'Qty', 'Gross', 'Comm', 'Net', 'Open Pos', 'Status', 'Trade ID']
        self.df = pd.DataFrame(columns=headers)

    def generate_id(self):
        trade_id = random.randint(100000, 999999)
        while (self.df['Trade ID'] == trade_id).any():
            trade_id = random.randint(100000, 999999)
        return trade_id
    
    def add(self, date, symbol, shares, trade_id):
        side = 'Long' if shares > 0 else 'Short'
        trade_data = {'Open': date, 'Symb': symbol, 'Open Pos': shares, 'Side': side, 'Status': 'Open', 'Trade ID': trade_id}
        self.df = self.df.append(trade_data, ignore_index=True)
    
    def update_status(self, trade_index, status):
        self.df.at[trade_index, 'Status'] = status

    def update_date(self, trade_index, date, stamp):
        if stamp == 'Open' or 'Close':
            self.df.at[trade_index, stamp] = date
        else:
            raise print('Not able to validate the Date stamp')
    
    def close(self, trade_index, close_date):
        self.update_date(trade_index, close_date, 'Close')
        self.update_status(trade_index, 'Closed')
    
    def get_id(self, trade_index):
        trade_id = self.df.at[trade_index, 'Trade ID']
        return trade_id
    
    def get_index(self, trade_id):
        filter_series = self.df['Trade ID'] == trade_id
        selection = self.df[filter_series]
        trade_index = selection.index[0]
        return trade_index
    
    def get_side(self, trade_index):
        side = self.df.at[trade_index, 'Side']
        return side

    def get_position(self, trade_index):
        position_current = self.df.at[trade_index, 'Open Pos']
        return position_current

    def get_details(self, trade_id):
        execution_list = key_dict[trade_id]
        filter_series = executions.df['ID'].isin(execution_list)
        execution_data = executions.df[filter_series]
        return execution_data
    
    def update_id(self, trade_index, trade_id):
        self.df.at[trade_index, 'Trade ID'] = trade_id

    def update_position(self, trade_index, position):
        self.df.at[trade_index, 'Open Pos'] = position


# Execution DataFrame - Read the data from CSV
path = 'tradelog_importer/trades/U6277264_20210712.tlg'
#path = 'tradelog_importer/trades/U6277264_20210101_20211008.tlg'
executions = Executions(path)
trades = Trades()

# Trade - Execution assignment dictionary
key_dict = {}

def performance(func):
    def wrapper(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Runtime is {round(t2 - t1, 2)}s')
        return result
    return wrapper

def define_status(new_position, side):
    if new_position == 0:
        return 'Closed'
    elif new_position < 0 and side == 'Long':
        print('Long -> flip to Short detected, adding new trade')
        return 'Flip'
    elif new_position > 0 and side == 'Short':
        print('Short -> flip to Long detected, adding new trade')
        return 'Flip'
    else:
        return 'Continue'

def calc_held_time():
    t1 = pd.to_datetime(trades.df['Close'])
    t2 = pd.to_datetime(trades.df['Open'])
    trades.df['Held'] = t1 - t2
    trades.df['Held'] = trades.df['Held'].astype(str).str[-8:]

def calc_price_avr():
    for trade_id in trades.df['Trade ID'].tolist():
        execution_data = trades.get_details(trade_id)
        filter_data = execution_data.query("Code == 'O'")
        price = average(filter_data['Price'])
        trade_index = trades.get_index(trade_id)
        trades.df.at[trade_index, 'Avr Entry'] = price
        filter_data = execution_data.query("Code == 'C' or Code == 'O,C'")
        price = average(filter_data['Price'])
        trades.df.at[trade_index, 'Avr Exit'] = price

@performance
def main_func():
    global key_dict
    for index, row in executions.df.iterrows():
        open_date = row['Date Time']
        symbol = row['Symb']
        shares = row['Shares']
        execution_id = [row['ID']]
        condition1 = trades.df['Symb'] == symbol
        condition2 = trades.df['Status'] == 'Open'
        match = trades.df[condition1 & condition2]
        if match.empty:
            print('No match in the DataFrame, adding new entry')
            trade_id = trades.generate_id()
            trades.add(open_date, symbol, shares, trade_id)
            key_dict.update({trade_id: execution_id})
        else:
            print('Match found, updating position') 
            trade_index = match.index[0]
            initial_position = trades.get_position(trade_index)
            new_position = initial_position + shares
            trades.update_position(trade_index, new_position)
            trade_id = trades.get_id(trade_index)
            key_dict[trade_id] = key_dict[trade_id] + execution_id
            side = trades.get_side(trade_index)
            status_check = define_status(new_position, side)
            if status_check == 'Closed':
                print('Position is closed, changing status to Closed')
                close_date = row['Date Time']
                trades.close(trade_index, close_date)
            elif status_check == 'Flip':
                close_date = row['Date Time']
                trades.update_position(trade_index, 0)
                trades.close(trade_index, close_date)
                open_date = close_date
                trade_id = trades.generate_id()
                trades.add(open_date, symbol, new_position, trade_id)
                key_dict.update({trade_id: execution_id})
            else:
                print('Trade is still open, continue')
    calc_held_time()
    calc_price_avr()

main_func()
print(trades.df[['Open', 'Symb', 'Side', 'Avr Entry', 'Avr Exit', 'Qty']])
pdb.set_trace()

''' 
Sort executions by Date
Loop for counting shares
1) For each row update the trade df
    a) If no Symb 
        add new entry, 
        add shares, 
        set status to Open
    b) Elseif there is Symb and status is Open
        add shares,
            If shares are 0
                change status to Closed
    c) Else there is Symb and status is Closed
        add new entry,
        add shares,
        set status to Open

Supporting position flip and taking missing executions into account
Existing execution df
Add new executions - keep IDs in memory
Sort by Date, select by symbol
For each ID from memory present in selection get min index
Recount from prev trade (delete all messed up trades that happened due to the missing execution?)
If no trade recount from 0th entry
'''