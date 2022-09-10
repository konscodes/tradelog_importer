import pandas as pd
from time import time
import random
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

script_path = Path(__file__).resolve()
script_parent = script_path.parent

try:
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename()
except:
    print('\nError providing window dialog with tkinter, default path is used\n')
    path = script_parent / 'files' / 'example_20210712.tlg'

class Executions:
    def __init__(self, path):
        self.path = path
        self.df = pd.read_csv(path, sep='|', header=None, skiprows=5, engine='python', skipfooter=1)
        missing_check = pd.isnull(self.df[2])
        self.df = self.df[missing_check == False]
        self.df[7] = pd.to_datetime(self.df[7], format='%Y%m%d').dt.date
        self.df[8] = pd.to_datetime(self.df[8], format='%H:%M:%S').dt.time
        self.df[8] = self.df.apply(lambda r : datetime.combine(r[7],r[8]), 1)
        self.df = self.df.drop(columns=[0,3,4,5,7,9,11,15])
        self.df = self.df.rename(columns={1:'ID', 2:'Symb', 6:'Code', 8:'DateTime', 10:'Shares', 12:'Price', 13:'Pos', 14:'Comm'})
        self.df = self.df.sort_values(['Symb', 'DateTime'], ascending=[True, True])
    
    def add(self, execution_id, symbol, code, date, shares, price, pos, comm):
        execution_data = {'ID': execution_id, 'Symb': symbol, 'Code': code, 'DateTime': date, 'Shares': shares, 'Price': price, 'Pos': pos, 'Comm': comm}
        self.df = self.df.append(execution_data, ignore_index=True)
    
    def update_shares(self, execution_index, shares):
        self.df.at[execution_index, 'Shares'] = shares

    def update_position(self, execution_index, pos):
        self.df.at[execution_index, 'Pos'] = pos

class Trades:
    def __init__(self):
        headers = ['Open', 'Close', 'Held', 'Symb', 'Side', 'Avr Entry', 'Avr Exit', 'Qty', 'Gross', 'Comm', 'Net', 'Open Qty', 'Status', 'Trade ID']
        self.df = pd.DataFrame(columns=headers)

    def generate_id(self):
        trade_id = random.randint(100000, 999999)
        while (self.df['Trade ID'] == trade_id).any():
            trade_id = random.randint(100000, 999999)
        return trade_id
    
    def add(self, date, symbol, shares, trade_id):
        side = 'Long' if shares > 0 else 'Short'
        trade_data = {'Open': date, 'Symb': symbol, 'Open Qty': shares, 'Side': side, 'Status': 'Open', 'Trade ID': trade_id}
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
        position_current = self.df.at[trade_index, 'Open Qty']
        return position_current

    def get_details(self, trade_id):
        execution_list = key_dict[trade_id]
        filter_series = executions.df['ID'].isin(execution_list)
        execution_data = executions.df[filter_series].copy()
        return execution_data
    
    def update_id(self, trade_index, trade_id):
        self.df.at[trade_index, 'Trade ID'] = trade_id

    def update_position(self, trade_index, position):
        self.df.at[trade_index, 'Open Qty'] = position

# Execution DataFrame - Read the data from CSV
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

def define_status(new_position, side, symbol):
    if new_position == 0:
        return 'Closed'
    elif new_position < 0 and side == 'Long':
        print(f'Long -> flip to Short detected on {symbol}, adding new trade')
        return 'Flip'
    elif new_position > 0 and side == 'Short':
        print(f'Short -> flip to Long detected on {symbol}, adding new trade')
        return 'Flip'
    else:
        return 'Continue'

def calc_time():
    t1 = pd.to_datetime(trades.df['Close'])
    t2 = pd.to_datetime(trades.df['Open'])
    trades.df['Held'] = t1 - t2
    trades.df['Held'] = trades.df['Held'].astype(str).str[-8:]

def calc_price():
    for trade_id in trades.df['Trade ID'].tolist():
        trade_index = trades.get_index(trade_id)
        execution_data = trades.get_details(trade_id)
        execution_data['Shares'] = execution_data['Shares'].abs()
        execution_data['Pos'] = execution_data['Pos'].abs()
        if not execution_data['Code'].any():
            print(execution_data)
            print('Missing Code?')
            continue
        # Updating avr entry price
        open_data = execution_data.query("Code == 'O'")
        entry_pos = sum(open_data['Pos'])
        qty = sum(open_data['Shares'])
        trades.df.at[trade_index, 'Qty'] = qty
        price = entry_pos/qty
        trades.df.at[trade_index, 'Avr Entry'] = round(price, 2)
        # Updating avr exit price
        close_data = execution_data.query("Code == 'C' or Code == 'C;O'")
        exit_pos = sum(close_data['Pos'])
        price = exit_pos/qty
        trades.df.at[trade_index, 'Avr Exit'] = round(price, 2)
        # Updating Gross/Net
        gross = exit_pos - entry_pos if (trades.df.at[trade_index, 'Side'] == 'Long') else entry_pos - exit_pos
        trades.df.at[trade_index, 'Gross'] = round(gross, 2)
        comm = sum(execution_data['Comm'])
        trades.df.at[trade_index, 'Comm'] = round(comm, 4)
        trades.df.at[trade_index, 'Net'] = round(gross + comm, 2)

@performance
def main_func():
    global key_dict
    for index, row in executions.df.iterrows():
        open_date = row['DateTime']
        symbol = row['Symb']
        shares = row['Shares']
        price = row['Price']
        execution_id = int(row['ID'])
        condition1 = trades.df['Symb'] == symbol
        condition2 = trades.df['Status'] == 'Open'
        match = trades.df[condition1 & condition2]
        # !!! this logic doesn't include the situation when the log only includes partial trade information
        # such as ony closed portion of a trade - this will result in an error
        # ideally this script should keep a log of previously imported trades to check for Open trades etc.
        if match.empty:
            #print('No match in the DataFrame, adding new entry')
            trade_id = trades.generate_id()
            trades.add(open_date, symbol, shares, trade_id)
            key_dict.update({trade_id: [execution_id]})
        else:
            #print('Match found, updating position') 
            trade_index = match.index[0]
            initial_position = trades.get_position(trade_index)
            new_position = initial_position + shares
            trades.update_position(trade_index, new_position)
            trade_id = trades.get_id(trade_index)
            key_dict[trade_id] = key_dict[trade_id] + [execution_id]
            side = trades.get_side(trade_index)
            status_check = define_status(new_position, side, symbol)
            if status_check == 'Closed':
                #print('Position is closed, changing status to Closed')
                close_date = row['DateTime']
                trades.close(trade_index, close_date)
            elif status_check == 'Flip':
                # Close existing trade
                close_date = row['DateTime']
                trades.update_position(trade_index, 0)
                trades.close(trade_index, close_date)
                # Open new trade
                open_date = close_date
                trade_id = trades.generate_id()
                trades.add(open_date, symbol, new_position, trade_id)
                # Update existing execution
                executions.update_shares(index, -initial_position)
                #pdb.set_trace()
                pos = (-initial_position) * price
                executions.update_position(index, pos)
                # Add new execution
                #print(execution_id)
                execution_id = int(str(execution_id)[::-1])
                pos = new_position * price
                executions.add(execution_id, symbol, 'O', open_date, new_position, price, pos, 0)
                key_dict.update({trade_id: [execution_id]})
            else:
                #print('Trade is still open, continue')
                pass
    calc_time()
    print(trades.df)
    calc_price()

main_func()
print(trades.df[['Close', 'Symb', 'Side', 'Avr Entry', 'Avr Exit', 'Qty', 'Gross', 'Comm', 'Net', 'Status']].sort_values(by='Close', ascending=False))
#print(trades.df)
export = trades.df.sort_values(by='Close').copy()
csv_path = script_parent / 'trades.csv'
export.to_csv(csv_path, index=False)


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

- Supporting position flip and taking missing executions into account
Existing execution df
Add new executions - keep IDs in memory
Sort by Date, select by symbol
For each ID from memory present in selection get min index
Recount from prev trade (delete all messed up trades that happened due to the missing execution?)
If no trade recount from 0th entry
'''