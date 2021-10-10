import pandas as pd
from time import time
import random

class Executions:
    def __init__(self, path):
        self.path = path
        self.df = pd.read_csv(path, sep='|', header=None, skiprows=5, engine='python', skipfooter=1, parse_dates=[7,8])
        missing_check = pd.isnull(self.df[2])
        self.df = self.df[missing_check == False]
        self.df[8] = pd.to_datetime(self.df[7] + ' ' + self.df[8]) if type(self.df[7][0]) is str else self.df[8]
        self.df = self.df.drop(columns=[0,1,3,4,5,7,9,11,13,15])
        self.df = self.df.rename(columns={1:'ID', 2:'Symb', 6:'Code', 8:'Date Time', 10:'Shares', 12:'Price', 14:'Comm'})
        self.df = self.df.sort_values(by='Date Time')

class Trades:
    def __init__(self):
        headers = ['Open', 'Close', 'Held', 'Symb', 'Side', 'Entry', 'Exit', 'Qty', 'Gross', 'Comm', 'Net', 'Open Pos', 'Status', 'Trade ID']
        self.df = pd.DataFrame(columns=headers)

    def add(self, date, symbol, shares, trade_id):
        side = 'Long' if shares > 0 else 'Short'
        trade_data = {'Open': date, 'Symb': symbol, 'Open Pos': shares, 'Side': side, 'Status': 'Open', 'Trade ID': trade_id}
        self.df = self.df.append(trade_data, ignore_index=True)

    def close(self, trade_index, close_date):
        self.update_date(trade_index, close_date, 'Close')
        self.update_status(trade_index, 'Closed')
    
    def update_status(self, trade_index, status):
        self.df.at[trade_index, 'Status'] = status

    def get_position(self, trade_index):
        position_current = self.df.at[trade_index, 'Open Pos']
        return position_current

    def update_position(self, trade_index, position):
        self.df.at[trade_index, 'Open Pos'] = position

    def update_price(self, trade_index, state, price):
        if state == 'Entry':
            self.df.at[trade_index, 'Entry'] = price
        elif state == 'Exit':
            self.df.at[trade_index, 'Exit'] = price
    
    def get_side(self, trade_index):
        side = self.df.at[trade_index, 'Side']
        return side
    
    def update_date(self, trade_index, date, stamp):
        if stamp == 'Open' or 'Close':
            self.df.at[trade_index, stamp] = date
        else:
            raise print('Not able to validate the Date stamp')
    
    def generate_id(self):
        trade_id = random.randint(100000, 999999)
        while (self.df['Trade ID'] == trade_id).any():
            trade_id = random.randint(100000, 999999)
        return trade_id
    
    def update_id(self, trade_index, trade_id):
        self.df.at[trade_index, 'Trade ID'] = trade_id
            

# Execution DataFrame - Read the data from CSV
path = 'tradelog_importer/trades/U6277264_20210712.tlg'
#path = 'tradelog_importer/trades/U6277264_20210101_20211008.tlg'
executions = Executions(path)
trades = Trades()

def performance(func):
    def wrapper(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(f'Runtime is {round(t2 - t1, 2)}s')
        return result
    return wrapper

def trade_status(new_position, side):
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

def calculate_held():
    t1 = pd.to_datetime(trades.df['Close'])
    t2 = pd.to_datetime(trades.df['Open'])
    trades.df['Held'] = t1 - t2
    trades.df['Held'] = trades.df['Held'].astype(str).str[-8:]

@performance
def main_loop():
    for index, row in executions.df.iterrows():
        open_date = row['Date Time']
        symbol = row['Symb']
        shares = row['Shares']
        price = row['Price']
        condition1 = trades.df['Symb'] == symbol
        condition2 = trades.df['Status'] == 'Open'
        match = trades.df[condition1 & condition2]
        if match.empty:
            print('No match in the DataFrame, adding new entry')
            trade_id = trades.generate_id()
            # Add first exec ID to the key dict
            trades.add(open_date, symbol, shares, trade_id)
        else:
            print('Match found, updating position')
            # Add exec ID to key dict
            trade_index = match.index[0]
            initial_position = trades.get_position(trade_index)
            new_position = initial_position + shares
            trades.update_position(trade_index, new_position)
            side = trades.get_side(trade_index)
            status_check = trade_status(new_position, side)
            if status_check == 'Closed':
                print('Position is closed, changing status to Closed')
                close_date = row['Date Time']
                trades.close(trade_index, close_date)
            elif status_check == 'Flip':
                close_date = row['Date Time']
                trades.update_position(trade_index, 0)
                trades.close(trade_index, close_date)
                # Change current exec shares to fit to 0 total
                open_date = close_date
                trades.add(open_date, symbol, new_position)
                # Create exec ID and add to key dict
            else:
                print('Trade is still open, continue')


main_loop()
calculate_held()
print(trades.df)


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
'''

# add trade ID and create additional column with trade ID for execution - trade match

'''
Supporting position flip and taking missing executions into account
Existiong execution df
Add new executions - keep IDs in memory
Sort by Date, select by symbol
For each ID from memory present in selection get min index
Recount from prev trade (delete all messed up trades that happened due to the missing execution?)
If no trade recount from 0th entry
'''