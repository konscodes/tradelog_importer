import os
import io
import pandas as pd

# Read the data from CSV
df = pd.read_csv('tradelog_importer/trades/U6277264_20210712.tlg', sep='|', header=None, skiprows=5, engine='python', skipfooter=1, parse_dates=[7, 8])
df = df.drop(columns=[0,1,3,4,5,7,9,11,13,15])
df = df.rename(columns={2:'Symb', 6:'Code', 8:'Date Time', 10:'Shares', 12:'Price', 14:'Comm'})
print(df.head())

# New DF to store the shares for each trade
open_trades = pd.DataFrame(columns=['Symb', 'Open Shares', 'Side', 'Status'])


# print(df['Symb'].unique())

# ''' Loop for counting shares
# 1) For each row update the open_trades df 
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

# selection = df[df['Symb'] == 'SEED']
# series = selection.loc[0]
# print(series['Shares'])
# print(selection.iterrows())
# for index, row in selection.iterrows():
#     print(row['Shares'])

# for symbol in df['Symb'].unique():
#     print(symbol)
#     selection = df[df['Symb'] == symbol]
#     print(selection)
#     for index, row in selection.iterrows():
#         #print(row['Symb'])
#         #print(row['Shares'])
#         if open_trades['Symb'] == symbol:
#             print('Match')
#         else:
#             print('none')

