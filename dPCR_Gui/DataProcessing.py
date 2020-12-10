import pandas as pd


io = r'F:\PythonProject\dPCR_Gui\file\光照均匀性模拟数据.xlsx'

data = pd.read_excel(io, sheet_name = 0)
