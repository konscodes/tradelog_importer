import os
import io
import pandas as pd

with open('tradelog_importer/trades/trade.txt', 'r') as f:
    data = f.read().replace('\n',';').replace(';;','\n')

hearer_list = ['Open Date', 'Open Time', 'Close Date', 'Close Time', 'Held', 'Symbol', 'Side', 'Avr Entry', 'Avr Exit', 'Shares', 'Gross', 'Comm'] 
df = pd.read_csv(io.StringIO(data), sep=";", header=None, names=hearer_list)
df['Open Date/Time'] = pd.to_datetime(df['Open Date'] + ' ' + df['Open Time'].str[4:]) # .str[4:] will cut first 3 char for the day of the week
df['Close Date/Time'] = pd.to_datetime(df['Close Date'] + ' ' + df['Close Time'].str[4:])
df = df.drop(columns=['Open Date', 'Open Time', 'Close Date', 'Close Time'])
columns_list = df.columns.tolist()
columns_sorted = columns_list[-2:] + columns_list[:-2] # takiing last two columns [-2:] and adding everything before that [:-2]
df = df[columns_sorted]
#print(df)

df['Diff'] = df['Avr Entry'] - df['Avr Exit']
# Condition with loc
# df.loc[df['column name'] condition, 'new column name'] = 'value if condition is met'
df.loc[(df['Side'] == 'LONG') & (df['Diff'] > 0), 'Gross'] = df['Gross'] * -1
df.loc[(df['Side'] == 'SHORT') & (df['Diff'] < 0), 'Gross'] = df['Gross'] * -1
df = df.drop(columns=['Diff'])
print(df)
df.to_csv('tradelog_importer/trade.csv')