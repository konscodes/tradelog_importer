import os
import io
import pandas as pd

df = pd.read_csv('tradelog_importer/trades/U6277264_20210712.tlg', sep='|', header=None, skiprows=5, engine='python', skipfooter=1, parse_dates=[7, 8])
df = df.drop(columns=[0,1,3,4,5,7,9,11,13,15])
df = df.rename(columns={2:'Symb', 6:'Code', 8:'Date Time', 10:'Shares', 12:'Price', 14:'Comm'})
print(df)
# New DF to store the shares for each trade
open_trades = pd.DataFrame(columns=['Symb', 'Open Shares', 'Status'])
#print(df_open_trades)

''' Loop for counting shares
1) For each row update the open_trades df 
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
# df.loc[df['Symb'] == open_trades['Symb'], open_trades['Symb']] = df['Symb']
# for each_symb in df['Symb'].unique():
#     print(each_symb)
#     #for row in df.index:
#     #    print(df['Symb'][row])

print(df['Symb'].unique())