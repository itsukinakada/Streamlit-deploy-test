import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import yfinance as yf
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import time

# ページ設定
st.set_page_config(
    page_title="S&P500分析ダッシュボード",
    page_icon="📈",
    layout="wide"
)

# タイトルとイントロダクション
st.title("S&P500と政権変化・重要イベントの可視化")
st.markdown("""
このアプリでは、S&P500の日次終値の推移を表示し、米国の歴代政権と株価に影響を与えた重要イベントを
視覚的に確認できます。時間範囲やイベントの表示をカスタマイズしてみましょう。
""")

# サイドバー：パラメータ設定
st.sidebar.header("パラメータ設定")

# 日付範囲の選択
start_year = st.sidebar.slider("開始年", 1990, 2024, 2000)
start_date = f"{start_year}-01-01"
today = datetime.now().strftime("%Y-%m-%d")

# ローディングメッセージ
with st.spinner("S&P500のデータをダウンロード中..."):
    # データのキャッシュ機能
    @st.cache_data(ttl=3600)  # 1時間キャッシュ
    def load_sp500_data(start_date):
        try:
            sp500 = yf.download('^GSPC', start=start_date)
            return sp500
        except Exception as e:
            st.error(f"データのダウンロード中にエラーが発生しました: {e}")
            return None

    # データ取得
    sp500 = load_sp500_data(start_date)

if sp500 is not None and not sp500.empty:
    # 政権の期間を定義
    presidents = [
        {"name": "ブッシュ（父）", "start": "1989-01-20", "end": "1993-01-20", "color": "lightcoral", "party": "共和党"},
        {"name": "クリントン", "start": "1993-01-20", "end": "2001-01-20", "color": "lightblue", "party": "民主党"},
        {"name": "ブッシュ（子）", "start": "2001-01-20", "end": "2009-01-20", "color": "lightcoral", "party": "共和党"},
        {"name": "オバマ", "start": "2009-01-20", "end": "2017-01-20", "color": "lightblue", "party": "民主党"},
        {"name": "トランプ", "start": "2017-01-20", "end": "2021-01-20", "color": "lightcoral", "party": "共和党"},
        {"name": "バイデン", "start": "2021-01-20", "end": "2025-01-20", "color": "lightblue", "party": "民主党"},
        {"name": "トランプ", "start": "2025-01-20", "end": today, "color": "lightcoral", "party": "共和党"}
    ]

    # 重要なイベントを定義
    all_events = [
        {"date": "2001-09-11", "name": "9.11テロ事件", "color": "red", "category": "地政学的事件"},
        {"date": "2008-09-15", "name": "リーマンショック", "color": "darkred", "category": "金融危機"},
        {"date": "2010-05-06", "name": "フラッシュクラッシュ", "color": "orange", "category": "金融危機"},
        {"date": "2011-08-05", "name": "米国債格下げ", "color": "brown", "category": "金融危機"},
        {"date": "2016-06-23", "name": "英国EU離脱投票", "color": "green", "category": "地政学的事件"},
        {"date": "2018-02-05", "name": "ボラティリティショック", "color": "purple", "category": "金融危機"},
        {"date": "2020-03-11", "name": "WHOがCOVID-19のパンデミック宣言", "color": "purple", "category": "健康危機"},
        {"date": "2022-02-24", "name": "ロシアのウクライナ侵攻", "color": "orange", "category": "地政学的事件"},
        {"date": "2023-03-10", "name": "シリコンバレー銀行の破綻", "color": "brown", "category": "金融危機"}
    ]

    # イベントカテゴリ選択
    event_categories = list(set(event["category"] for event in all_events))
    selected_categories = st.sidebar.multiselect(
        "表示するイベントカテゴリ",
        options=event_categories,
        default=event_categories
    )

    # 選択されたカテゴリに基づいてイベントをフィルタリング
    events = [event for event in all_events if event["category"] in selected_categories]

    # 政権表示のオプション
    show_presidents = st.sidebar.checkbox("政権の期間を表示", value=True)
    
    # グラフのスタイル設定
    graph_style = st.sidebar.selectbox(
        "グラフスタイル",
        ["デフォルト", "ダークテーマ", "ミニマル", "科学論文風"]
    )

    # マーケット指標の追加オプション
    show_volume = st.sidebar.checkbox("出来高を表示", value=False)
    show_ma = st.sidebar.checkbox("移動平均線を表示", value=False)
    
    if show_ma:
        ma_period = st.sidebar.slider("移動平均の期間（日数）", 5, 200, 50)

    # プロット生成関数
    def generate_plot():
        if graph_style == "ダークテーマ":
            plt.style.use('dark_background')
        elif graph_style == "科学論文風":
            plt.style.use('seaborn-whitegrid')
        elif graph_style == "ミニマル":
            plt.style.use('seaborn-minimal')
        else:
            plt.style.use('default')

        fig, ax = plt.subplots(figsize=(12, 8))

        # メインプロット（S&P500の終値）
        ax.plot(sp500.index, sp500['Close'], color='black' if graph_style != "ダークテーマ" else 'white', 
                linewidth=1.5, label='S&P500終値')
        
        # 移動平均線を追加
        if show_ma:
            ma = sp500['Close'].rolling(window=ma_period).mean()
            ax.plot(sp500.index, ma, color='red', linewidth=1.2, 
                    label=f'{ma_period}日移動平均')

        # 出来高をサブプロットとして追加
        if show_volume:
            # メインのaxesのサイズを調整して下部に出来高のスペースを確保
            ax.set_position([0.1, 0.3, 0.8, 0.6])  # [left, bottom, width, height]
            
            # 出来高用のaxesを作成
            ax_volume = fig.add_axes([0.1, 0.1, 0.8, 0.15])  # [left, bottom, width, height]
            ax_volume.bar(sp500.index, sp500['Volume'], color='gray', alpha=0.5)
            ax_volume.set_ylabel('出来高', fontsize=10)
            ax_volume.tick_params(axis='x', labelsize=8)
            ax_volume.tick_params(axis='y', labelsize=8)
            
            # x軸の日付フォーマットを設定
            ax_volume.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax_volume.xaxis.set_major_locator(mdates.YearLocator(2))  # 2年ごとにメモリを設定
            plt.setp(ax_volume.get_xticklabels(), rotation=45)

        # 政権の背景色を設定
        if show_presidents:
            for president in presidents:
                start_date_p = pd.to_datetime(president["start"])
                end_date_p = pd.to_datetime(president["end"])
                
                # データの範囲内にある場合のみプロット
                if end_date_p >= sp500.index[0] and start_date_p <= sp500.index[-1]:
                    # データの日付範囲に合わせて調整
                    actual_start = max(start_date_p, sp500.index[0])
                    actual_end = min(end_date_p, sp500.index[-1])
                    
                    # 網掛け（背景色）を追加
                    ax.axvspan(actual_start, actual_end, alpha=0.3, color=president["color"])

        # 重要なイベントを縦線で表示
        for event in events:
            event_date = pd.to_datetime(event["date"])
            
            # データの範囲内にある場合のみプロット
            if event_date >= sp500.index[0] and event_date <= sp500.index[-1]:
                ax.axvline(event_date, color=event["color"], linestyle='--', linewidth=1.5)
                
                # イベント名のラベルを表示（y軸の高さを調整して重ならないようにする）
                y_pos = sp500['Close'].loc[sp500.index[0]:sp500.index[-1]].max() * (0.7 + events.index(event) * 0.05)
                
                ax.text(event_date, y_pos, event["name"], rotation=90, 
                        verticalalignment='bottom', horizontalalignment='right', 
                        fontsize=9, color=event["color"])

        # x軸の日付フォーマットを設定
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.YearLocator(2))  # 2年ごとにメモリを設定
        plt.xticks(rotation=45)

        # グリッドの設定
        ax.grid(True, linestyle='--', alpha=0.7)

        # 凡例の作成（政権）
        if show_presidents:
            president_patches = []
            shown_parties = set()  # 既に表示した政党を追跡
            
            for president in presidents:
                # 政党ごとに一度だけ凡例に追加
                if president['party'] not in shown_parties:
                    patch = mpatches.Patch(
                        color=president["color"], 
                        alpha=0.3, 
                        label=f"{president['party']}"
                    )
                    president_patches.append(patch)
                    shown_parties.add(president['party'])
            
            # 政権凡例を追加
            ax.legend(handles=president_patches, loc='upper left')
        else:
            ax.legend(loc='upper left')
            
        # y軸ラベル
        ax.set_ylabel('S&P500終値', fontsize=12)
        
        # タイトル
        plt.suptitle('S&P500と政権変化・重要イベント', fontsize=16, fontweight='bold')
        plt.title(f'{sp500.index[0].strftime("%Y-%m-%d")} から {sp500.index[-1].strftime("%Y-%m-%d")} まで', 
                  fontsize=12)

        plt.tight_layout()
        return fig

    # グラフを生成して表示
    fig = generate_plot()
    st.pyplot(fig)

    # データ統計の表示
    st.subheader("S&P500の統計情報")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_price = sp500['Close'].iloc[0]
        end_price = sp500['Close'].iloc[-1]
        percent_change = (end_price - start_price) / start_price * 100
        st.metric("価格変化", f"{end_price:.2f} USD", f"{percent_change:.2f}%")
    
    with col2:
        max_price = sp500['Close'].max()
        max_date = sp500['Close'].idxmax().strftime('%Y-%m-%d')
        st.metric("最高値", f"{max_price:.2f} USD", f"{max_date}に記録")
    
    with col3:
        volatility = sp500['Close'].pct_change().std() * 100 * (252 ** 0.5)  # 年率換算
        st.metric("ボラティリティ (年率)", f"{volatility:.2f}%")

    # 政権別のパフォーマンス表示
    if show_presidents:
        st.subheader("政権別のS&P500パフォーマンス")
        
        president_performance = []
        
        for president in presidents:
            start_date_p = pd.to_datetime(president["start"])
            end_date_p = pd.to_datetime(president["end"])
            
            # データの範囲内にある場合のみ計算
            if end_date_p >= sp500.index[0] and start_date_p <= sp500.index[-1]:
                # データの日付範囲に合わせて調整
                actual_start = max(start_date_p, sp500.index[0])
                actual_end = min(end_date_p, sp500.index[-1])
                
                # 該当期間のデータを取得
                period_data = sp500.loc[actual_start:actual_end]
                
                if not period_data.empty:
                    start_value = period_data['Close'].iloc[0]
                    end_value = period_data['Close'].iloc[-1]
                    percent_change = (end_value - start_value) / start_value * 100
                    annual_return = ((1 + percent_change/100) ** (365.25/(len(period_data) + 1)) - 1) * 100 if len(period_data) > 0 else 0
                    
                    president_performance.append({
                        "name": president["name"],
                        "party": president["party"],
                        "start": actual_start.strftime('%Y-%m-%d'),
                        "end": actual_end.strftime('%Y-%m-%d'),
                        "days": len(period_data),
                        "start_value": start_value,
                        "end_value": end_value,
                        "percent_change": percent_change,
                        "annual_return": annual_return
                    })
        
        # 表として表示
        df_performance = pd.DataFrame(president_performance)
        if not df_performance.empty:
            # 色分け用の関数
            def color_parties(val):
                if val == "民主党":
                    return 'background-color: lightblue'
                elif val == "共和党":
                    return 'background-color: lightcoral'
                return ''
            
            def color_percent(val):
                if val > 0:
                    return 'color: green'
                elif val < 0:
                    return 'color: red'
                return ''
            
            # 表示するカラムを選択
            display_df = df_performance[['name', 'party', 'start', 'end', 'percent_change', 'annual_return']]
            display_df.columns = ['大統領', '政党', '就任日', '退任日', '累積リターン(%)', '年率リターン(%)']
            
            # 数値を丸める
            display_df['累積リターン(%)'] = display_df['累積リターン(%)'].round(2)
            display_df['年率リターン(%)'] = display_df['年率リターン(%)'].round(2)
            
            # 条件付き書式でスタイル適用
            styled_df = display_df.style.applymap(color_parties, subset=['政党'])\
                                        .applymap(color_percent, subset=['累積リターン(%)', '年率リターン(%)'])
            
            st.dataframe(styled_df, height=400)

    # イベント一覧の表示
    if events:
        st.subheader("主要イベントリスト")
        
        event_df = pd.DataFrame([
            {"日付": pd.to_datetime(event["date"]).strftime('%Y-%m-%d'), 
             "イベント": event["name"], 
             "カテゴリ": event["category"]}
            for event in events if pd.to_datetime(event["date"]) >= sp500.index[0] 
                              and pd.to_datetime(event["date"]) <= sp500.index[-1]
        ])
        
        if not event_df.empty:
            st.dataframe(event_df, height=300)

    # ダウンロードセクション
    st.subheader("データダウンロード")
    
    csv = sp500.to_csv()
    st.download_button(
        label="CSVとしてS&P500データをダウンロード",
        data=csv,
        file_name='sp500_data.csv',
        mime='text/csv',
    )
    
    # フッター
    st.markdown("---")
    st.markdown("データソース: Yahoo Finance (yfinance)")
    st.markdown("最終更新: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
else:
    st.error("データを取得できませんでした。もう一度お試しください。")
