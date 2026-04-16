import pandas as pd
import numpy as np
import re
import ast

# 1. 讀取原始資料
# 確保路徑正確
df = pd.read_csv('dataset/games_march2025_cleaned.csv')

# 2. 日期清理與轉換
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df = df[df['release_date'] > '1997-01-01'] 
df['release_year'] = df['release_date'].dt.year
df['release_quarter'] = df['release_date'].dt.to_period('Q').astype(str)

# 3. 指標計算
# A. 好評率 (處理分母為 0 的情況)
df['total_reviews'] = df['positive'] + df['negative']
df['positive_rate'] = (df['positive'] / df['total_reviews']).replace(np.nan, 0)

# B. 語言數量統計
df['lang_count'] = df['supported_languages'].apply(lambda x: len(str(x).split(',')))

# C. 持有量轉換 (區間轉中位數)
def clean_owners(owner_str):
    if pd.isna(owner_str) or owner_str == '0 - 0': return 0
    parts = str(owner_str).replace(',', '').split(' - ')
    if len(parts) == 2:
        return (int(parts[0]) + int(parts[1])) / 2
    return 0
df['owners_midpoint'] = df['estimated_owners'].apply(clean_owners)

# D. 平均遊玩時間 (分轉小時)
df['average_playtime_hours'] = df['average_playtime_forever'] / 60

# 4. 價格區間與排序邏輯
def price_category(price):
    if price == 0: return 'Free', 1
    elif price < 10: return '< $10', 2
    elif price < 30: return '$10 - $30', 3
    elif price < 60: return '$30 - $60', 4
    else: return 'AAA ($60+)', 5
df['price_tier'], df['price_sort'] = zip(*df['price'].apply(price_category))

# 5. 標籤維度表 (Tags Dimension)
# 使用 ast.literal_eval 精準解析字典，避免正則表達式導致的資料位移
def safe_parse_tags(tags_str):
    try:
        tag_dict = ast.literal_eval(tags_str)
        if isinstance(tag_dict, dict):
            return list(tag_dict.keys())
        return ["Uncategorized"]
    except:
        return ["Uncategorized"]

tags_df = df[['appid', 'tags']].copy()
tags_df['tags_list'] = tags_df['tags'].apply(safe_parse_tags)
tags_df = tags_df.explode('tags_list')
tags_df = tags_df.rename(columns={'tags_list': '遊戲風格標籤(tags)'})
tags_df = tags_df[tags_df['遊戲風格標籤(tags)'] != "Uncategorized"].dropna()

# 6. 開發商維度表 (包含無效名稱過濾)
devs_df = df[['appid', 'developers']].copy()
devs_df['developers'] = devs_df['developers'].astype(str).replace("[]", "Unknown Developer")
devs_df['developers'] = devs_df['developers'].str.replace(r"[\[\]{}'\"]", "", regex=True)
devs_df['developers'] = devs_df['developers'].str.split(',').explode('developers').str.strip()

invalid_names = ['Ltd', 'Inc', 'LLC', 'Corp', 'Corporation', 'Co', 'Llc', 'Ltd.', 'ltd', 'inc']
devs_df.loc[devs_df['developers'].isin(invalid_names), 'developers'] = "Unknown Developer"
devs_df.loc[devs_df['developers'].str.len() < 2, 'developers'] = "Unknown Developer"
devs_df = devs_df[devs_df['developers'] != ""].dropna()

# 7. 語言維度表 (中文化與脫殼優化)
langs_df = df[['appid', 'supported_languages']].copy()

def extra_clean_language(text):
    text = str(text).strip()
    if text in ["[]", "nan", "", "None"]: return "Unknown"
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[\r\n\t]', ' ', text)
    return text.strip("[]'\" ")

langs_df['clean_langs'] = langs_df['supported_languages'].apply(extra_clean_language)
langs_df = langs_df.assign(language_name=langs_df['clean_langs'].str.split(',')).explode('language_name')
langs_df['language_name'] = langs_df['language_name'].str.strip("[]'\" ")

lang_map = {
    'English': '英文', 'Traditional Chinese': '繁體中文', 'Simplified Chinese': '簡體中文',
    'Japanese': '日文', 'Korean': '韓文', 'French': '法文', 'German': '德文',
    'Spanish - Spain': '西班牙文', 'Spanish - Latin America': '西班牙文(拉丁美洲)',
    'Russian': '俄文', 'Portuguese - Brazil': '葡萄牙文(巴西)', 'Italian': '義大利文',
    'Turkish': '土耳其文', 'Polish': '波蘭文', 'Thai': '泰文', 'Unknown': '未知語言'
}
langs_df['支援語言 (Language)'] = langs_df['language_name'].map(lang_map)
langs_df = langs_df.dropna(subset=['支援語言 (Language)'])

# 8. 儲存結果 (強制轉換 AppID 型別並使用 utf-8-sig 避免亂碼)
# A. 整理 Main 表欄位
cols_to_keep = [
    'appid', 'name', 'release_date', 'release_year', 'release_quarter', 
    'price', 'price_tier', 'price_sort', 'positive', 'negative', 'total_reviews', 
    'positive_rate', 'owners_midpoint', 'lang_count', 'peak_ccu','average_playtime_hours'
]
df_final = df[cols_to_keep].copy()

# B. 強制轉換所有 AppID 為整數型別 (解決 Power BI Integer/Text 衝突)
df_final['appid'] = df_final['appid'].astype(int)
tags_df['appid'] = tags_df['appid'].astype(int)
devs_df['appid'] = devs_df['appid'].astype(int)
langs_df['appid'] = langs_df['appid'].astype(int)

# C. 輸出 CSV
df_final.to_csv('games_20year_main.csv', index=False, encoding='utf-8-sig')
tags_df[['appid', '遊戲風格標籤(tags)']].to_csv('games_tags_dimension.csv', index=False, encoding='utf-8-sig')
devs_df.to_csv('games_developers_dimension.csv', index=False, encoding='utf-8-sig')
langs_df[['appid', '支援語言 (Language)']].to_csv('games_languages_dimension.csv', index=False, encoding='utf-8-sig')

print("--- 數據清洗整理完成 ---")
print(f"1. Main表: {len(df_final)} 筆")
print(f"2. Tags維度表: {len(tags_df)} 筆")
print(f"3. Developers維度表: {len(devs_df)} 筆")
print(f"4. Languages維度表: {len(langs_df)} 筆")