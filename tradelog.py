import os
import io
import pandas as pd

df_init = pd.read_csv('python-finance/trades/U6277264_20210712.tlg', sep='|', header=None, skiprows=5, engine='python', skipfooter=1, parse_dates=[7, 8])
df_drop = df_init.drop(columns=[0,1,3,4,5,7,9,11,13,15])
#print(df_drop.head())
df_final = df_drop.rename(columns={2:'Symb', 6:'Code', 8:'Date Time', 10:'Shares', 12:'Price', 14:'Comm'})
#print(df_final.head(4))
#df_final.to_csv('Trade.csv')

# New DF to store the shares for each trade
df_open_trades = pd.DataFrame(columns=['Symb', 'Open Shares', 'Total Shares', 'Status'])
#print(df_open_trades)

# Loop for counting shares
for each_symb in df_final['Symb'].unique():
    print(each_symb)
    #for row in df_final.index:
    #    print(df_final['Symb'][row])

#print(df_final['Symb'].unique())