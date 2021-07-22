import os
import io
import pandas as pd

with open('python-finance/trades/trade.txt', 'r') as f:
    data = f.read().replace('\n',';').replace(';;','\n')
    #print(data)


df = pd.read_csv(io.StringIO(data), sep=";", header=None)
df[1] = df[1].str[4:]
df[3] = df[3].str[4:]
df['Open'] = pd.to_datetime(df[0] + ' ' + df[1])
df['Close'] = pd.to_datetime(df[2] + ' ' + df[3])
df = df.drop(columns=[0, 1, 2, 3])
cols = df.columns.tolist()
cols = cols[-2:] + cols[:-2]
df = df[cols]
print(df)
df.to_csv('trade.csv')