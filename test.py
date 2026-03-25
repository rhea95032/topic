import pandas as pd
import numpy as np

# 1. 讀取資料
df = pd.read_csv('dataset/games_march2025_cleaned.csv')

# 2. 日期清理：轉換為標準日期，並提取年份與季度
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
# 刪除日期無效或太早的資料（例如 1970 年之前的異常值）
df = df[df['release_date'] > '1997-01-01'] 
df['release_year'] = df['release_date'].dt.year
df['release_quarter'] = df['release_date'].dt.to_period('Q').astype(str)

# 3. 計算關鍵指標
# 好評率 (用清單中的 positive 和 negative)
df['total_reviews'] = df['positive'] + df['negative']
df['positive_rate'] = (df['positive'] / df['total_reviews']).replace(np.nan, 0)

# 4. 價格區間分類 (不含數字編號，但新增一個排序用的索引欄位)
def price_category(price):
    if price == 0: return 'Free', 1
    elif price < 10: return '< $10', 2
    elif price < 30: return '$10 - $30', 3
    elif price < 60: return '$30 - $60', 4
    else: return 'AAA ($60+)', 5

# 同時產生「名稱」與「順序」兩個欄位
df['price_tier'], df['price_sort'] = zip(*df['price'].apply(price_category))

# 5. 標籤與類型拆解 (修正版)
tags_expanded = df[['appid', 'tags']].copy()
# 處理 [] 並移除所有括號與引號
tags_expanded['tags'] = tags_expanded['tags'].astype(str).replace("[]", "Uncategorized")
tags_expanded['tags'] = tags_expanded['tags'].str.replace(r"[\[\]{}'\"]", "", regex=True)
# 拆分、展開、去空格
tags_expanded['tags'] = tags_expanded['tags'].str.split(',').explode('tags').str.strip()
# 過濾空字串
tags_expanded = tags_expanded[tags_expanded['tags'] != ""].dropna()

# 6. 儲存結果
# 儲存主表 (移除掉太長的描述欄位以節省空間)
cols_to_keep = ['appid', 'name', 'release_date', 'release_year', 'release_quarter', 
                'price', 'price_tier', 'positive', 'negative', 'total_reviews', 
                'positive_rate', 'estimated_owners', 'average_playtime_forever', 
                'developers', 'publishers','price_sort']
df_final = df[cols_to_keep]

df_final.to_csv('games_20year_main.csv', index=False)
tags_expanded.to_csv('games_tags_dimension.csv', index=False)

print(f"整理完成！")
print(f"資料時間跨度：{df_final['release_year'].min()} - {df_final['release_year'].max()}")
print(f"總遊戲筆數：{len(df_final)}")