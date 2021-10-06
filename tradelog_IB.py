import pandas as pd
import pdb

class Executions:
    def __init__(self, path):
        self.path = path
        self.df = pd.read_csv(path, sep='|', header=None, skiprows=5, engine='python', skipfooter=1, parse_dates=[7, 8])
        self.df = self.df.drop(columns=[0,1,3,4,5,7,9,11,13,15])
        self.df = self.df.rename(columns={1:'ID', 2:'Symb', 6:'Code', 8:'Date Time', 10:'Shares', 12:'Price', 14:'Comm'})
        self.df = self.df.sort_values(by='Date Time')

class Trades:
    def __init__(self):
        headers = ['Open', 'Close', 'Held', 'Symb', 'Side', 'Entry', 'Exit', 'Qty', 'Gross', 'Comm', 'Net', 'Open Pos', 'Status', 'Trade ID']
        self.df = pd.DataFrame(columns=headers)

    def add(self, symbol, shares):
        side = 'Long' if shares > 0 else 'Short'
        trade_data = {'Symb': symbol, 'Open Pos': shares, 'Side': side, 'Status': 'Open'}
        self.df = self.df.append(trade_data, ignore_index=True)

    def update_status(self, trade_index, status):
        trades.df.at[trade_index, 'Status'] = status

    def get_position(self, trade_index):
        position_current = trades.df.at[trade_index, 'Open Pos']
        return position_current

    def update_position(self, trade_index, position):
        self.df.at[trade_index, 'Open Pos'] = position
    
    def get_side(self, trade_index):
        side = trades.df.at[trade_index, 'Side']
        return side

# Execution DataFrame - Read the data from CSV
path = 'tradelog_importer/trades/U6277264_20210712.tlg'
executions = Executions(path)
trades = Trades()

# Main loop
for index, row in executions.df.iterrows():
    symbol = row['Symb']
    shares = row['Shares']
    condition1 = trades.df['Symb'] == symbol
    condition2 = trades.df['Status'] == 'Open'
    match = trades.df[condition1 & condition2]
    if match.empty:
        print('No match in the DataFrame, adding new entry')
        # Create trade ID
        # Add first exec ID to the key dict
        trades.add(symbol, shares)
    else:
        print('Match found, updating position')
        # Add exec ID to key dict
        trade_index = match.index[0]
        initial_position = trades.get_position(trade_index)
        new_position = initial_position + shares
        trades.update_position(trade_index, new_position)
        side = trades.get_side(trade_index)
        if new_position == 0:
            print('Position is closed, changing status to Closed')
            trades.update_status(trade_index, 'Closed')
        elif new_position < 0 and side == 'Long':
            print('Long -> flip to Short detected, adding new trade')
            trades.update_position(trade_index, 0)
            trades.update_status(trade_index, 'Closed')
            # Change current exec shares to fit to 0 total
            trades.add(symbol, new_position)
            # Create exec ID and add to key dict
        elif new_position > 0 and side == 'Short':
            print('Short -> flip to Long detected, adding new trade')
            trades.update_position(trade_index, 0)
            trades.update_status(trade_index, 'Closed')
            trades.add(symbol, new_position)
        else:
            print('Trade is still open, continue')

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
# sort the data by date before iteration 

'''
Supporting position flip and taking missing executions into account
Existiong execution df
Add new executions - keep IDs in memory
Sort by Date, select by symbol
For each ID from memory present in selection get min index
Recount from prev trade (delete all messed up trades that happened due to the missing execution?)
If no trade recount from 0th entry
'''