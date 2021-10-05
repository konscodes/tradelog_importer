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

    def update(self, trade_index, shares):
        position_change = position.get(trade_index) + shares
        position.update(trade_index, position_change)

class Position:
    def get(self, trade_index):
        position_current = trades.df.at[trade_index, 'Position']
        return position_current
        
    def update(self, trade_index, position):
        trades.df.at[trade_index, 'Position'] = position


# Execution DataFrame - Read the data from CSV
path = 'tradelog_importer/trades/U6277264_20210712.tlg'
executions = Executions(path)
trades = Trades()
position = Position()

# Main loop
for symbol in executions.df['Symb'].unique():
    print(symbol)
    selection = executions.df[executions.df['Symb'] == symbol]
    print(selection)
    for index, row in selection.iterrows():
        shares = row['Shares']
        match = (trades.df['Symb'] == symbol).any()
        if match:
            print('Match, updating position')
            trade_index = max(trades.df.index)
            trades.update(trade_index, shares)
        else:
            print('No match, adding new entry')
            trades.add(symbol, shares)

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