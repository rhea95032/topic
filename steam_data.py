import pandas as pd
import numpy as np
import re
# 1. 讀取資料
df = pd.read_csv('dataset/games_march2025_cleaned.csv')

# 2. 日期清理
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df = df[df['release_date'] > '1997-01-01'] 
df['release_year'] = df['release_date'].dt.year
df['release_quarter'] = df['release_date'].dt.to_period('Q').astype(str)

# 3. 指標計算 (好評率、語言數、持有量)
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

# D. 平均遊玩時間 (將分鐘轉為小時)
df['average_playtime_hours'] = df['average_playtime_forever'] / 60

# 4. 價格區間與排序
def price_category(price):
    if price == 0: return 'Free', 1
    elif price < 10: return '< $10', 2
    elif price < 30: return '$10 - $30', 3
    elif price < 60: return '$30 - $60', 4
    else: return 'AAA ($60+)', 5
df['price_tier'], df['price_sort'] = zip(*df['price'].apply(price_category))

# 5. 標籤維度表 (Tags Dimension)
tags_df = df[['appid', 'tags']].copy()
tags_df['tags'] = tags_df['tags'].astype(str).replace("[]", "Uncategorized")
tags_df['tags'] = tags_df['tags'].str.replace(r"[\[\]{}'\"]", "", regex=True)
tags_df['tags'] = tags_df['tags'].str.split(',').explode('tags').str.strip()
tags_df = tags_df[tags_df['tags'] != ""].dropna()

# 6. 開發商維度表 (優化版：過濾無效名稱)
devs_df = df[['appid', 'developers']].copy()
devs_df['developers'] = devs_df['developers'].astype(str).replace("[]", "Unknown Developer")
devs_df['developers'] = devs_df['developers'].str.replace(r"[\[\]{}'\"]", "", regex=True)
devs_df['developers'] = devs_df['developers'].str.split(',').explode('developers').str.strip()

# --- 新增：過濾掉只有法律縮寫的無效名稱 ---
# 定義無效名稱黑名單
invalid_names = ['Ltd', 'Inc', 'LLC', 'Corp', 'Corporation', 'Co', 'Llc', 'Ltd.']

# 如果名稱在黑名單內，或者長度小於 2 個字，就設為 Unknown
devs_df.loc[devs_df['developers'].isin(invalid_names), 'developers'] = "Unknown Developer"
devs_df.loc[devs_df['developers'].str.len() < 2, 'developers'] = "Unknown Developer"

# 過濾空值
devs_df = devs_df[devs_df['developers'] != ""].dropna()

# 7. 語言維度表 (Languages Dimension) - 強化脫殼與中文化版
langs_df = df[['appid', 'supported_languages']].copy()

def extra_clean_language(text):
    text = str(text).strip()
    
    # 1. 處理常見的空值或空列表字串
    if text in ["[]", "nan", "", "None"]:
        return "Unknown"
    
    # 2. 移除所有 HTML 標籤 (如 <b>, </b>)
    text = re.sub(r'<[^>]+>', '', text)
    
    # 3. 移除 \r, \n, \t
    text = re.sub(r'[\r\n\t]', ' ', text)
    
    # 4. 重要：移除最外層可能殘留的 [ ] ' " 符號 (處理 ['English'] 這種字串)
    # 我們針對整個長字串先做一次清理
    text = text.strip("[]'\" ")
    
    return text

# 執行初步清理
langs_df['clean_langs'] = langs_df['supported_languages'].apply(extra_clean_language)

# 拆分並展開 (Explode)
langs_df = langs_df.assign(language_name=langs_df['clean_langs'].str.split(',')).explode('language_name')

# 5. 針對展開後的每個個別語言「再次脫殼」
# 這是為了解決 ['English', 'French'] 展開後變成 ' 'English'' 的問題
langs_df['language_name'] = langs_df['language_name'].str.strip("[]'\" ")

# 定義語言翻譯字典 (維持不變)
lang_map = {
    'English': '英文',
    'Traditional Chinese': '繁體中文',
    'Simplified Chinese': '簡體中文',
    'Japanese': '日文',
    'Korean': '韓文',
    'French': '法文',
    'German': '德文',
    'Spanish - Spain': '西班牙文',
    'Spanish - Latin America': '西班牙文(拉丁美洲)',
    'Russian': '俄文',
    'Portuguese - Brazil': '葡萄牙文(巴西)',
    'Italian': '義大利文',
    'Turkish': '土耳其文',
    'Polish': '波蘭文',
    'Thai': '泰文',
    'Unknown': '未知語言'
}

# 執行翻譯
langs_df['支援語言 (Language)'] = langs_df['language_name'].map(lang_map).fillna(langs_df['language_name'])

# 最後過濾無效列
langs_df = langs_df[langs_df['支援語言 (Language)'].str.strip() != ""]

# 儲存
langs_df[['appid', '支援語言 (Language)']].to_csv('games_languages_dimension.csv', index=False, encoding='utf-8-sig')


# 8. 儲存結果
cols_to_keep = [
    'appid', 'name', 'release_date', 'release_year', 'release_quarter', 
    'price', 'price_tier', 'price_sort', 'positive', 'negative', 'total_reviews', 
    'positive_rate', 'owners_midpoint', 'lang_count', 'peak_ccu','average_playtime_hours'
]
df_final = df[cols_to_keep]

#df_final.to_csv('games_20year_main.csv', index=False)
#tags_df.to_csv('games_tags_dimension.csv', index=False)
#devs_df.to_csv('games_developers_dimension.csv', index=False)
langs_df.to_csv('games_languages_dimension.csv', index=False)

print("--- 整理完成 ---")
print(f"生成的檔案：main表, tags維度表, developers維度表, languages維度表")