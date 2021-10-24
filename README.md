# Interactive Brokers TradeLog Importer
[![Visitors](https://visitor-badge.glitch.me/badge?page_id=tradelog_importer.visitor-badge)](https://github.com/tradelog_importer)
### What and Why

Python script that converts IB Third-Party TradeLog into .csv format.

![2021-10-24 18_54_11](https://user-images.githubusercontent.com/6221944/138589055-9f353496-9be6-43ba-aa66-1ad172ba1a93.png)

IB .tlg file turns into two dataframes with trades and executions 👇

![image](https://user-images.githubusercontent.com/6221944/138589112-efa4a501-5d8b-4fbe-9def-2be875999cdd.png)

The output can be further used to analize your trades or use trade data with other tools like excel and google docs. </br>
I use the script to convert executions into trades to use in other scripts for per-trade analytics.

### Libraries used

- [`pandas`](https://pypi.org/project/pandas/) for creating table-like dataframes to store executions and trades
- [`tkinter`](https://docs.python.org/3/library/tkinter.html) for simple file dialog
- [`pathlib`](https://pypi.org/project/pathlib/) for cross-platform file path detection

### Try the script

Download the TradeLog .tlg file from IB. </br>
Run the script `tradelog_IB.py` and choose the file. On the output you get two dataframes with with data and .csv file with trades. </br>
CSV will be created in the same folder the script is ran from. </br>
