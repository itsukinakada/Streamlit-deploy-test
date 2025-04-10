import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import yfinance as yf
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import time
import matplotlib as mpl
import platform
import os
import japanize_matplotlib

# 日本語フォントの設定（プラットフォームに応じて適切なフォントを設定）
def setup_japanese_fonts():
    try:
        # システムごとのフォント設定
        os_name = platform.system()
        if os_name == 'Windows':
            plt.rcParams['font.family'] = "MS Gothic"
        elif os_name == 'Darwin':  # Mac OS
            plt.rcParams['font.family'] = "Hiragino Sans GB"
        else:  # Linux その他
            plt.rcParams['font.family'] = "IPAGothic"
        
        # マイナス記号を正しく表示
        mpl.rcParams['axes.unicode_minus'] = False
        return True
    except Exception as e:
        st.warning(f"日本語フォント設定中にエラーが発生しました: {e}")
        return False

# 日本語フォントを設定
setup_japanese_fonts()

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

    # 重要なイベントを定義（より多くの正確なイベント）
    all_events = [
        # 2000年代
        {"date": "2000-03-10", "name": "ドットコムバブル崩壊", "color": "darkred", "category": "金融危機"},
        {"date": "2001-09-11", "name": "9.11テロ事件", "color": "red", "category": "地政学的事件"},
        {"date": "2002-07-30", "name": "サーベンス・オクスリー法成立", "color": "blue", "category": "金融規制"},
        {"date": "2003-03-20", "name": "イラク戦争開始", "color": "orange", "category": "地政学的事件"},
        {"date": "2004-05-10", "name": "原油価格40ドル突破", "color": "brown", "category": "コモディティ"},
        {"date": "2005-08-29", "name": "ハリケーン・カトリーナ", "color": "teal", "category": "自然災害"},
        {"date": "2006-02-01", "name": "バーナンキFRB議長就任", "color": "purple", "category": "金融政策"},
        {"date": "2007-02-27", "name": "上海ショック", "color": "darkred", "category": "金融危機"},
        {"date": "2007-08-09", "name": "サブプライム危機表面化", "color": "darkred", "category": "金融危機"},
        {"date": "2008-03-16", "name": "ベアー・スターンズ破綻", "color": "darkred", "category": "金融危機"},
        {"date": "2008-09-15", "name": "リーマン・ブラザーズ破綻", "color": "darkred", "category": "金融危機"},
        {"date": "2008-10-03", "name": "TARP法成立", "color": "blue", "category": "金融政策"},
        {"date": "2008-11-25", "name": "QE1開始", "color": "purple", "category": "金融政策"},
        {"date": "2009-03-09", "name": "金融危機最安値", "color": "green", "category": "金融危機"},
        
        # 2010年代前半
        {"date": "2010-05-06", "name": "フラッシュクラッシュ", "color": "darkred", "category": "金融危機"},
        {"date": "2010-05-09", "name": "欧州金融安定化基金設立", "color": "blue", "category": "金融政策"},
        {"date": "2010-11-03", "name": "QE2開始", "color": "purple", "category": "金融政策"},
        {"date": "2011-03-11", "name": "東日本大震災", "color": "teal", "category": "自然災害"},
        {"date": "2011-08-05", "name": "米国債格下げ（S&P）", "color": "brown", "category": "金融危機"},
        {"date": "2011-08-11", "name": "短期売り規制導入", "color": "blue", "category": "金融規制"},
        {"date": "2012-07-26", "name": "ドラギ「何でもする」演説", "color": "purple", "category": "金融政策"},
        {"date": "2012-09-13", "name": "QE3開始", "color": "purple", "category": "金融政策"},
        {"date": "2013-05-22", "name": "バーナンキ・テーパリング示唆", "color": "purple", "category": "金融政策"},
        {"date": "2014-10-29", "name": "QE3終了", "color": "purple", "category": "金融政策"},
        
        # 2010年代後半
        {"date": "2015-08-11", "name": "中国人民元切り下げ", "color": "red", "category": "金融危機"},
        {"date": "2015-12-16", "name": "FRB利上げ開始", "color": "purple", "category": "金融政策"},
        {"date": "2016-06-23", "name": "英国EU離脱投票", "color": "orange", "category": "地政学的事件"},
        {"date": "2016-11-08", "name": "トランプ大統領選出", "color": "orange", "category": "地政学的事件"},
        {"date": "2017-01-25", "name": "ダウ20000ドル突破", "color": "green", "category": "市場マイルストーン"},
        {"date": "2018-01-26", "name": "ダウ26616ドル最高値", "color": "green", "category": "市場マイルストーン"},
        {"date": "2018-02-05", "name": "ボラティリティショック", "color": "darkred", "category": "金融危機"},
        {"date": "2018-03-22", "name": "米中貿易戦争開始", "color": "orange", "category": "地政学的事件"},
        {"date": "2018-12-22", "name": "米政府機関閉鎖", "color": "red", "category": "地政学的事件"},
        {"date": "2019-07-31", "name": "FRB利下げ開始", "color": "purple", "category": "金融政策"},
        {"date": "2019-09-17", "name": "レポ市場危機", "color": "darkred", "category": "金融危機"},
        
        # 2020年代
        {"date": "2020-02-19", "name": "コロナ前最高値", "color": "green", "category": "市場マイルストーン"},
        {"date": "2020-03-11", "name": "WHOがCOVID-19のパンデミック宣言", "color": "red", "category": "健康危機"},
        {"date": "2020-03-15", "name": "FRBゼロ金利復帰・無制限QE", "color": "purple", "category": "金融政策"},
        {"date": "2020-03-23", "name": "コロナショック最安値", "color": "darkred", "category": "金融危機"},
        {"date": "2020-03-27", "name": "CARES法成立", "color": "blue", "category": "金融政策"},
        {"date": "2021-01-06", "name": "米国議会議事堂襲撃", "color": "red", "category": "地政学的事件"},
        {"date": "2021-11-08", "name": "S&P500最高値（当時）", "color": "green", "category": "市場マイルストーン"},
        {"date": "2022-02-24", "name": "ロシアのウクライナ侵攻", "color": "orange", "category": "地政学的事件"},
        {"date": "2022-03-16", "name": "FRB利上げ開始", "color": "purple", "category": "金融政策"},
        {"date": "2022-06-13", "name": "ベア市場入り宣言", "color": "darkred", "category": "金融危機"},
        {"date": "2022-09-28", "name": "英国債市場危機", "color": "darkred", "category": "金融危機"},
        {"date": "2023-03-10", "name": "シリコンバレー銀行の破綻", "color": "darkred", "category": "金融危機"},
        {"date": "2023-05-01", "name": "米地域銀行危機", "color": "darkred", "category": "金融危機"},
        {"date": "2023-07-31", "name": "日銀YCC政策修正", "color": "purple", "category": "金融政策"},
        {"date": "2023-12-13", "name": "FRBピボット示唆", "color": "purple", "category": "金融政策"},
        {"date": "2024-01-19", "name": "S&P500最高値更新", "color": "green", "category": "市場マイルストーン"},
        {"date": "2024-03-20", "name": "FRB金利据え置き継続", "color": "purple", "category": "金融政策"}
    ]

    # イベントカテゴリ選択
    event_categories = list(set(event["category"] for event in all_events))
    # カテゴリを特定の順序で並べる
    ordered_categories = ["金融危機", "金融政策", "金融規制", "地政学的事件", "健康危機", "自然災害", "コモディティ", "市場マイルストーン"]
    # リストの順序を保ちながら、ordered_categoriesに含まれる要素だけをフィルタリング
    sorted_categories = [category for category in ordered_categories if category in event_categories]
    # ordered_categoriesに含まれていないカテゴリも追加
    sorted_categories.extend([category for category in event_categories if category not in ordered_categories])
    
    # イベント数の制限オプション
    max_events = st.sidebar.slider("表示するイベントの最大数", 5, len(all_events), min(20, len(all_events)))
    
    selected_categories = st.sidebar.multiselect(
        "表示するイベントカテゴリ",
        options=sorted_categories,
        default=["金融危機", "金融政策", "地政学的事件"] if "金融危機" in sorted_categories else sorted_categories[:3]
    )

    # 選択されたカテゴリに基づいてイベントをフィルタリングし、日付でソート
    filtered_events = [event for event in all_events if event["category"] in selected_categories]
    # 日付でソート
    filtered_events.sort(key=lambda x: pd.to_datetime(x["date"]))
    
    # データの表示範囲に該当するイベントのみに絞り込む
    in_range_events = []
    for event in filtered_events:
        event_date = pd.to_datetime(event["date"])
        if event_date >= sp500.index[0] and event_date <= sp500.index[-1]:
            in_range_events.append(event)
    
    # 最大数に制限
    events = in_range_events[:max_events]

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
        # matplotlibスタイルの修正（バージョン間の互換性のためにtry-exceptで囲む）
        try:
            if graph_style == "ダークテーマ":
                plt.style.use('dark_background')
            elif graph_style == "科学論文風":
                # 新旧バージョン両方に対応
                try:
                    plt.style.use('seaborn-whitegrid')
                except:
                    plt.style.use('seaborn-v0_8-whitegrid')
            elif graph_style == "ミニマル":
                try:
                    plt.style.use('seaborn-minimal')
                except:
                    try:
                        plt.style.use('seaborn-v0_8-white')
                    except:
                        plt.style.use('default')
            else:
                plt.style.use('default')
        except Exception as e:
            st.warning(f"グラフスタイルの適用中にエラーが発生しました: {e}")
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

        # 政権の背景色を設定と大統領名の表示
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
                    
                    # 政権名をグラフ上部に表示
                    if actual_end > actual_start:  # 表示期間が存在する場合
                        # 期間の中央位置を計算
                        mid_date = actual_start + (actual_end - actual_start) / 2
                        
                        # y位置の調整（グラフの上部に配置）
                        y_pos = sp500['Close'].loc[sp500.index[0]:sp500.index[-1]].max() * 1.05
                        
                        # 大統領名を表示
                        ax.text(mid_date, y_pos, president["name"], 
                                horizontalalignment='center',
                                verticalalignment='bottom',
                                rotation=0,
                                fontsize=10,
                                color='black',
                                fontweight='bold',
                                bbox=dict(facecolor=president["color"], alpha=0.4, pad=2, boxstyle='round,pad=0.3'))

        # 重要なイベントを縦線で表示
        for event in events:
            event_date = pd.to_datetime(event["date"])
            
            # データの範囲内にある場合のみプロット
            if event_date >= sp500.index[0] and event_date <= sp500.index[-1]:
                ax.axvline(event_date, color=event["color"], linestyle='--', linewidth=1.5)
                
                # イベント名のラベルを表示（y軸の高さを調整して重ならないようにする）
                try:
                    # 重複を避けるため、イベントごとにy位置を調整
                    event_index = events.index(event)
                    # 循環的に5つの位置に分散させる（ラベルが多くなりすぎるのを防ぐ）
                    position_index = event_index % 5
                    y_pos = sp500['Close'].loc[sp500.index[0]:sp500.index[-1]].max() * (0.5 + position_index * 0.1)
                    
                    ax.text(event_date, y_pos, event["name"], rotation=90, 
                            verticalalignment='bottom', horizontalalignment='right', 
                            fontsize=8, color=event["color"], fontweight='bold',
                            bbox=dict(facecolor='white', alpha=0.7, edgecolor=event["color"], 
                                       pad=1, boxstyle='round,pad=0.2'))
                except Exception as e:
                    # エラーが発生した場合はスキップ（エラー解消のため）
                    st.warning(f"イベント表示中にエラーが発生しました: {e}")

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
