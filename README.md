# 🚀 Steam 全球遊戲市場分析專題 (1997-2024)

![Project Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![Power BI](https://img.shields.io/badge/Visual-Power_BI-blue?style=for-the-badge&logo=powerbi)
![Python](https://img.shields.io/badge/ETL-Python-green?style=for-the-badge&logo=python)

本專題針對 Steam 平台 20 年間的 **89,618 筆** 遊戲數據進行深度解構，涵蓋資料清理 (ETL)、多維度建模與商業策略洞察。

---

## 📌 核心洞察 (Key Insights)
* **市場結構：** 獨立遊戲 (Indie) 佔比達 **48.44%**。
* **在地化價值：** 在地化流量倍數高達 **15.9 倍**。
* **特賣策略：** 秋季與黑五特賣為年度黃金發行檔期。
* **營收甜蜜點：** **$10 - $29.99** 定價搭配多語系支援具備最高潛力。

---

## 🛠️ 技術棧 (Technical Stack)
* **資料獲取：** Python (BeautifulSoup/Requests)
* **資料處理：** Python (Pandas), SQL Server
* **資料建模：** DAX, SQL
* **視覺化：** Power BI

---

## 🧹 資料處理細節 (Data Cleaning)
1. **語系規整：** 處理原始標籤為標準維度（繁中、簡中、雙語）。
2. **異常值剔除：** 處理價格異常與長尾無效數據。
3. **時間工程：** 提取年份、季節以進行「特賣週期」分析。
4. **COVID-19 標記：** 加入時間錨點觀察宅經濟效應。

---

## 👤 作者
* **鄭朝元** | 朝陽科技大學 資訊管理系