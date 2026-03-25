import pandas as pd
import numpy as np

# 1. 讀取資料
df = pd.read_csv('dataset/games_march2025_cleaned.csv')

# 2. 日期清理：轉換為標準日期，並提取年份與季度
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
# 刪除日期無效或太早的資料
df = df[df['release_date'] > '1997-01-01'] 
df['release_year'] = df['release_date'].dt.year
df['release_quarter'] = df['release_date'].dt.to_period('Q').astype(str)

# 3. 計算關鍵指標 (好評率、語言數、持有量中位數)
# A. 好評率
df['total_reviews'] = df['positive'] + df['negative']
df['positive_rate'] = (df['positive'] / df['total_reviews']).replace(np.nan, 0)

# B. 語言數量統計 (支援幾種語言)
df['lang_count'] = df['supported_languages'].apply(lambda x: len(str(x).split(',')))

# C. 持有量轉換 (將 "10,000 - 20,000" 轉為 15000)
def clean_owners(owner_str):
    if pd.isna(owner_str) or owner_str == '0 - 0': return 0
    parts = str(owner_str).replace(',', '').split(' - ')
    if len(parts) == 2:
        return (int(parts[0]) + int(parts[1])) / 2
    return 0

df['owners_midpoint'] = df['estimated_owners'].apply(clean_owners)

# 4. 價格區間分類 (含排序索引)
def price_category(price):
    if price == 0: return 'Free', 1
    elif price < 10: return '< $10', 2
    elif price < 30: return '$10 - $30', 3
    elif price < 60: return '$30 - $60', 4
    else: return 'AAA ($60+)', 5

# 使用 zip(*...) 同時產生名稱與排序欄位
df['price_tier'], df['price_sort'] = zip(*df['price'].apply(price_category))

# 5. 標籤與類型拆解 (維度表：處理多對多關係與清理髒資料)
tags_expanded = df[['appid', 'tags']].copy()
# 處理 [] 並移除所有括號、引號
tags_expanded['tags'] = tags_expanded['tags'].astype(str).replace("[]", "Uncategorized")
tags_expanded['tags'] = tags_expanded['tags'].str.replace(r"[\[\]{}'\"]", "", regex=True)
# 拆分、展開、去空格
tags_expanded['tags'] = tags_expanded['tags'].str.split(',').explode('tags').str.strip()
# 過濾空字串
tags_expanded = tags_expanded[tags_expanded['tags'] != ""].dropna()

# 6. 儲存結果 (只保留 Power BI 需要的精簡欄位)
cols_to_keep = [
    'appid', 'name', 'release_date', 'release_year', 'release_quarter', 
    'price', 'price_tier', 'price_sort', 'positive', 'negative', 'total_reviews', 
    'positive_rate', 'owners_midpoint', 'average_playtime_forever', 
    'developers', 'publishers', 'lang_count', 'peak_ccu'
]
df_final = df[cols_to_keep]

# 儲存 CSV
df_final.to_csv('games_20year_main.csv', index=False)
tags_expanded.to_csv('games_tags_dimension.csv', index=False)

print("--- 整理完成 ---")
print(f"資料筆數：{len(df_final)}")
print(f"生成的檔案：games_20year_main.csv, games_tags_dimension.csv")