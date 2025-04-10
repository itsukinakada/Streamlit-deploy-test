import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import yfinance as yf
import matplotlib.patches as mpatches
from datetime import datetime

# S&P500のデータをダウンロード（2000年から現在まで）
sp500 = yf.download('^GSPC', start='2000-01-01')

# 政権の期間を定義（大統領名と期間の開始日、終了日）
presidents = [
    {"name": "クリントン", "start": "2000-01-01", "end": "2001-01-20", "color": "lightblue"},
    {"name": "ブッシュ", "start": "2001-01-20", "end": "2009-01-20", "color": "lightcoral"},
    {"name": "オバマ", "start": "2009-01-20", "end": "2017-01-20", "color": "lightblue"},
    {"name": "トランプ", "start": "2017-01-20", "end": "2021-01-20", "color": "lightcoral"},
    {"name": "バイデン", "start": "2021-01-20", "end": "2025-01-20", "color": "lightblue"},
    {"name": "トランプ", "start": "2025-01-20", "end": "2025-04-10", "color": "lightcoral"}  # 現在日付まで
]

# 重要なイベントを定義
events = [
    {"date": "2001-09-11", "name": "9.11テロ事件", "color": "red"},
    {"date": "2008-09-15", "name": "リーマンショック", "color": "darkred"},
    {"date": "2020-03-11", "name": "WHOがCOVID-19のパンデミック宣言", "color": "purple"},
    {"date": "2022-02-24", "name": "ロシアのウクライナ侵攻", "color": "orange"},
    {"date": "2023-03-10", "name": "シリコンバレー銀行の破綻", "color": "brown"}
]

# プロットの設定
plt.figure(figsize=(15, 8))
ax = plt.subplot(111)

# S&P500の終値をプロット
ax.plot(sp500.index, sp500['Close'], color='black', linewidth=1.5)

# y軸のラベル
ax.set_ylabel('S&P500終値', fontsize=12)

# 政権ごとの背景色を設定
for president in presidents:
    start_date = pd.to_datetime(president["start"])
    end_date = pd.to_datetime(president["end"])
    
    # データの範囲内にある場合のみプロット
    if end_date >= sp500.index[0] and start_date <= sp500.index[-1]:
        # データの日付範囲に合わせて調整
        actual_start = max(start_date, sp500.index[0])
        actual_end = min(end_date, sp500.index[-1])
        
        # 網掛け（背景色）を追加
        ax.axvspan(actual_start, actual_end, alpha=0.3, color=president["color"])

# 重要なイベントを縦線で表示
for event in events:
    event_date = pd.to_datetime(event["date"])
    
    # データの範囲内にある場合のみプロット
    if event_date >= sp500.index[0] and event_date <= sp500.index[-1]:
        ax.axvline(event_date, color=event["color"], linestyle='--', linewidth=1.5)
        
        # イベント名のラベルを表示（y軸の高さを調整して重ならないようにする）
        y_pos = sp500['Close'].max() * (0.7 + events.index(event) * 0.05)
        ax.text(event_date, y_pos, event["name"], rotation=90, 
                verticalalignment='bottom', horizontalalignment='right', fontsize=10)

# x軸の日付フォーマットを設定
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))  # 2年ごとにメモリを設定
plt.xticks(rotation=45)

# グリッドの設定
ax.grid(True, linestyle='--', alpha=0.7)

# 凡例の作成
president_patches = []
for president in presidents:
    patch = mpatches.Patch(color=president["color"], alpha=0.3, label=f"{president['name']}政権")
    president_patches.append(patch)
    
# タイトルと凡例の設定
plt.title('S&P500と政権変化・重要イベント (2000年〜現在)', fontsize=14, fontweight='bold')
plt.legend(handles=president_patches, loc='upper left')

# レイアウトの調整
plt.tight_layout()

# プロットの表示
plt.show()

# ファイルに保存する場合
# plt.savefig('sp500_presidents_events.png', dpi=300, bbox_inches='tight')
