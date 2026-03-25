import pandas as pd

# 讀取檔案
df = pd.read_csv('dataset/games_march2025_cleaned.csv')

# 方法 1：只印出欄位清單
print(df.columns)

# 方法 2：查看欄位名稱、資料型態、以及是否有空值（推薦！）
print(df.info())
