import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ページ設定
st.set_page_config(
    page_title="DeepSeek収益分析：AIサービスの高収益ビジネスモデル",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: white;
        background-color: #1E88E5;
        padding: 10px;
        border-radius: 5px;
    }
    .sub-header {
        font-size: 18px;
        font-weight: bold;
        color: white;
        background-color: #1E88E5;
        padding: 8px;
        border-radius: 5px;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .highlight {
        color: #FF6347;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown('<div class="main-header">DeepSeek収益分析：AIサービスの高収益ビジネスモデル</div>', unsafe_allow_html=True)

# サイドバーで日付を選択できるようにする
st.sidebar.header("分析期間設定")
start_date = st.sidebar.date_input("開始日", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("終了日", datetime.now())

# サイドバーでフィルタ設定
st.sidebar.header("フィルタ設定")
service_type = st.sidebar.multiselect(
    "サービスタイプ",
    ["API提供", "SaaS", "オンプレミス", "コンサルティング"],
    default=["API提供", "SaaS"]
)

# メインコンテンツを3列に分割
col1, col2, col3 = st.columns([1, 2, 1])

# 1列目：高収益ビジネスモデル概要
with col1:
    st.markdown('<div class="sub-header">1. 高収益ビジネスモデル概要</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="metric-container">
        <b>収益性指標:</b><br>
        • 売上率: わずか<span class="highlight">20%以下</span><br>
        • 利益上の成長率: <span class="highlight">約245%</span><br>
        • 投資効率性: 1円で<span class="highlight">45円</span>を創出<br>
        • 実質収益率: <span class="highlight">2~3倍</span> (他業種比較時)
        </div>
        """, unsafe_allow_html=True)
    
    # 2. 日次収益分析
    st.markdown('<div class="sub-header">2. 日次収益分析</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="metric-container">
        <b>1日あたりの数値 (円):</b><br>
        コスト: <span class="highlight">870万円</span><br>
        利益上の収入: <span class="highlight">5,620万円</span><br>
        純利益(利益上): <span class="highlight">4,750万円</span><br>
        <small>※GPTの料金レンジを参考値に設定 (推定200 GPU/日)</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 3. 実際の収益実績
    st.markdown('<div class="sub-header">3. 実際の収益実績</div>', unsafe_allow_html=True)
    
    # 日米比較のテーブル
    data = {
        "地域": ["米国", "日本への展開"],
        "詳細": [
            "V3は価格が半分。\n需要拡大 (75%)で\n利益率が向上。",
            "言語特化サービスで\nアジアのチャット需要が\n人気でさらに利益率\n向上する可能性あり。"
        ]
    }
    
    df = pd.DataFrame(data)
    st.dataframe(df, hide_index=True, use_container_width=True)

# 2列目：時間帯別収益・コスト分析 + 重要な背景情報
with col2:
    st.markdown('<div class="sub-header">4. 時間帯別収益・コスト分析</div>', unsafe_allow_html=True)
    
    # 時間帯データの作成
    hours = list(range(0, 24))
    revenue_data = [25, 20, 15, 10, 15, 25, 40, 55, 65, 70, 72, 70, 65, 63, 60, 62, 65, 68, 60, 55, 50, 45, 40, 30]
    cost_data = [40, 38, 35, 30, 32, 35, 40, 45, 50, 50, 48, 45, 42, 40, 38, 40, 42, 45, 43, 40, 38, 35, 32, 30]
    
    # プロットのための準備
    fig = go.Figure()
    
    # 午前中（4時から12時）の範囲を指定
    fig.add_vrect(
        x0=4, x1=12,
        fillcolor="yellow", opacity=0.2,
        layer="below", line_width=0,
    )
    
    # 午後（12時から18時）の範囲を指定
    fig.add_vrect(
        x0=12, x1=18,
        fillcolor="orange", opacity=0.2,
        layer="below", line_width=0,
    )
    

    # 夜間（18時から4時）の範囲を指定
    fig.add_vrect(
        x0=18, x1=24,
        fillcolor="blue", opacity=0.2,
        layer="below", line_width=0,
    )
    fig.add_vrect(
        x0=0, x1=4,
        fillcolor="blue", opacity=0.2,
        layer="below", line_width=0,
    )
    
    # 収益と費用のプロット
    fig.add_trace(go.Scatter(x=hours, y=revenue_data, mode='lines', name='収入 (百万円)', line=dict(color='blue', width=2)))
    fig.add_trace(go.Scatter(x=hours, y=cost_data, mode='lines', name='コスト (百万円)', line=dict(color='orange', width=2), fill='tozeroy'))
    
    fig.update_layout(
        xaxis_title="時間帯",
        yaxis_title="金額 (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=30, b=20),
        height=400
    )
    
    # 時間帯のラベルを設定
    fig.update_xaxes(
        tickvals=list(range(0, 24, 4)),
        ticktext=['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 重要な背景情報
    st.markdown('<div class="sub-header">5. 重要な背景</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="metric-container">
        • 高収益ビジネスモデル: どの時間帯でもコストを上回る収益を確保<br>
        • 収益効率が高い時間帯: 昼間 (12:00-22:00) の時間帯が特に効率的<br>
        • チャレンジ課題: 価格設定、競合サービス、夜間帯引き収益性を改善<br>
        • リソース活用: GPU利用の最適化が収益向上との鍵
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-container">
        <small>※注記: DeepSeekのビジネスモデルは、同じくAIサービスを提供している他社と比較しても、
        インフラ整備に優れており、AIサービスの利用料金が他社と比較して安価になっています。</small>
        </div>
        """, unsafe_allow_html=True)
    
# 3列目：KPI概要 + コスト内訳
with col3:
    st.markdown('<div class="sub-header">KPI概要</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="metric-container">
        <b>目標上の収益</b><br>
        <span style="font-size:24px; font-weight:bold;">205億円</span><br>
        * 日常単価 5,620万円 × 365日で計算
        </div>
        """, unsafe_allow_html=True)
    
    # 経営効率比較
    st.markdown('<div class="sub-header">経営効率比較</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="metric-container">
        <b>利益上の効率性</b><br>
        <span style="font-size:24px; font-weight:bold;">546%</span><br>
        <small>既存サービス比: 125%</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 円グラフでコスト内訳を表示
    st.markdown('<div class="sub-header">コスト内訳</div>', unsafe_allow_html=True)
    
    labels = ['GPU利用', '人件費', 'その他']
    values = [75, 15, 10]
    colors = ['#FFD700', '#1E88E5', '#43A047']
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, marker_colors=colors)])
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300)
    
    st.plotly_chart(fig, use_container_width=True)

# 注釈
st.caption("2023年3月3日 | プロフェッショナル分析レポート")

# オプション：ダウンロードボタン
csv = pd.DataFrame({
    '時間帯': hours,
    '収益': revenue_data,
    'コスト': cost_data
}).to_csv(index=False)

st.download_button(
    label="CSVデータをダウンロード",
    data=csv,
    file_name='time_analysis_data.csv',
    mime='text/csv',
)
