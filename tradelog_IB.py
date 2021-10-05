import pandas as pd
import pdb

class Executions:
    def __init__(self, path):
        self.path = path
        self.df = pd.read_csv(path, sep='|', header=None, skiprows=5, engine='python', skipfooter=1, parse_dates=[7, 8])
        self.df = self.df.drop(columns=[0,1,3,4,5,7,9,11,13,15])
        self.df = self.df.rename(columns={2:'Symb', 6:'Code', 8:'Date Time', 10:'Shares', 12:'Price', 14:'Comm'})

class Trades:
    def __init__(self):
        self.df = pd.DataFrame(columns=['Symb', 'Position', 'Side', 'Status'])

    def add(self, symbol, shares):
        side = 'Long' if shares > 0 else 'Short'
        trade_data = {'Symb': symbol, 'Position': shares, 'Side': side, 'Status': 'Open'}
        self.df = self.df.append(trade_data, ignore_index=True)

    def update_status(self, trade_index, status):
        trades.df.at[trade_index, 'Status'] = status

    def get_position(self, trade_index):
        position_current = trades.df.at[trade_index, 'Position']
        return position_current

    def update_position(self, trade_index, position):
        self.df.at[trade_index, 'Position'] = position
    
    def get_side(self, trade_index):
        side = trades.df.at[trade_index, 'Side']
        return side

# Execution DataFrame - Read the data from CSV
path = 'tradelog_importer/trades/U6277264_20210712.tlg'
executions = Executions(path)
trades = Trades()

# Main loop
for symbol in executions.df['Symb'].unique():
    print(symbol)
    selection = executions.df[executions.df['Symb'] == symbol]
    print(selection)
    for index, row in selection.iterrows():
        shares = row['Shares']
        condition1 = trades.df['Symb'] == symbol
        condition2 = trades.df['Status'] == 'Open'
        match = trades.df[condition1 & condition2]
        if match.empty:
            print('No match, adding new entry')
            trades.add(symbol, shares)
        else:
            print('Match, updating position')
            trade_index = max(trades.df.index)
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
                trades.add(symbol, new_position)
            elif new_position > 0 and side == 'Short':
                print('Short -> flip to Long detected, adding new trade')
                trades.update_position(trade_index, 0)
                trades.update_status(trade_index, 'Closed')
                trades.add(symbol, new_position)
            else:
                print('Trade is still open, continue')

print(trades.df)

# ''' Loop for counting shares
# 1) For each row update the open_df_trades df_executions 
#     a) If no Symb 
#         add new entry, 
#         add shares, 
#         set status to Open
#     b) Elseif there is Symb and status is Open
#         add shares,
#             If shares are 0
#                 change status to Closed
#     c) Else there is Symb and status is Closed
#         add new entry,
#         add shares,
#         set status to Open
# '''

# # add trade ID and create additional column with trade ID for execution - trade match