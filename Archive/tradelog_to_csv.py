import os
import io
import pandas as pd

with open('tradelog_importer/trades/trade.txt', 'r') as f:
    data = f.read().replace('\n',';').replace(';;','\n')

hearer_list = ['Open Date', 'Open Time', 'Close Date', 'Close Time', 'Held', 
                'Symbol', 'Side', 'Avr Entry', 'Avr Exit', 'Shares', 'Gross', 'Comm'] 
df = pd.read_csv(io.StringIO(data), sep=";", header=None, names=hearer_list)
df['Open Date/Time'] = pd.to_datetime(df['Open Date'] + ' ' + df['Open Time'].str[4:]) # .str[4:] will cut first 3 char for the day of the week
df['Close Date/Time'] = pd.to_datetime(df['Close Date'] + ' ' + df['Close Time'].str[4:])
df = df.drop(columns=['Open Date', 'Open Time', 'Close Date', 'Close Time'])
columns_list = df.columns.tolist()
columns_sorted = columns_list[-2:] + columns_list[:-2] # taking last two columns [-2:] and adding everything before that [:-2]
df = df[columns_sorted]
df['Shares'] = (df['Shares'] / 2).astype({'Shares': int})
df['Side'] = df['Side'].str.title()
# Condition with loc
# df.loc[df['column name'] condition, 'new column name'] = 'value if condition is met'
df['Diff'] = df['Avr Entry'] - df['Avr Exit']
df.loc[(df['Side'] == 'Long') & (df['Diff'] > 0), 'Gross'] = df['Gross'] * -1
df.loc[(df['Side'] == 'Short') & (df['Diff'] < 0), 'Gross'] = df['Gross'] * -1
df = df.drop(columns=['Diff'])
df = df.sort_values(by=['Close Date/Time'], ascending=True).reset_index(drop=True)
print(df)
df.to_csv('tradelog_importer/trades.csv')
