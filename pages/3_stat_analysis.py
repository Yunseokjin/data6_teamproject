# 파일 위치: pages/3_전투력_집중_분석.py

import pandas as pd
import plotly.express as px
import streamlit as st
from utils import load_and_preprocess_data # 1. 우리의 '공통 도우미'를 불러옵니다.

# --- 데이터 불러오기 ---
# 모든 전처리는 utils.py가 책임집니다.
df = load_and_preprocess_data('growth_log_v2_f_v2.csv')

# --- 대시보드 UI 구성 ---
st.title("⚔️ 챌린저스 서버 전투력 심층 분석")
st.markdown("---")

# --- 사이드바 (필터) ---
st.sidebar.header("🗓️ 기준 시점 선택")
# 날짜 목록을 내림차순으로 정렬하여 최신 날짜가 맨 위에 오도록 합니다.
date_options = sorted(df['date'].dt.strftime('%Y-%m-%d').unique(), reverse=True)
selected_date = st.sidebar.selectbox(
    "분석할 기준 날짜를 선택하세요:",
    options=date_options
)

# 선택된 날짜에 해당하는 데이터만 필터링합니다. (스냅샷 분석)
df_snapshot = df[df['date'] == selected_date].copy()

if df_snapshot.empty:
    st.warning("선택된 날짜에 해당하는 데이터가 없습니다.")
    st.stop()

# --- 1. 핵심 지표 (KPI) ---
st.subheader(f"📈 {selected_date} 기준 핵심 지표")
avg_power = df_snapshot['전투력'].mean()
max_power = df_snapshot['전투력'].max()
top_1_percent_power = df_snapshot['전투력'].quantile(0.99) # 상위 1% 전투력

col1, col2, col3 = st.columns(3)
col1.metric("평균 전투력", f"{avg_power:,.0f}")
col2.metric("최고 전투력", f"{max_power:,.0f}")
col3.metric("상위 1% 전투력", f"{top_1_percent_power:,.0f}")
st.markdown("---")


# --- 2. 시각화 (2x2 그리드 레이아웃) ---
col_left, col_right = st.columns(2)

with col_left:
    # --- 시각화 1: 전투력 분포 히스토그램 ---
    st.subheader("① 전투력 분포 현황")
    fig_hist = px.histogram(
        df_snapshot.dropna(subset=['전투력']),
        x='전투력',
        nbins=50,
        title=f"{selected_date} 기준 전투력 분포",
        labels={'전투력': '전투력'}
    )
    fig_hist.update_layout(bargap=0.1)
    st.plotly_chart(fig_hist, use_container_width=True)

    # --- 시각화 2: 직업별 전투력 분포 (상위 10개 직업) ---
    st.subheader("③ 직업별 전투력 분포 (상위 10개 직업)")
    
    # 데이터가 많은 상위 10개 직업만 필터링하여 시각화의 가독성을 높입니다.
    top_10_classes = df_snapshot['character_class'].value_counts().nlargest(10).index
    df_top_classes = df_snapshot[df_snapshot['character_class'].isin(top_10_classes)]

    fig_box = px.box(
        df_top_classes,
        x='character_class',
        y='전투력',
        color='character_class',
        title="직업별 전투력 중앙값 및 분포 비교",
        labels={'character_class': '직업', '전투력': '전투력'},
        points=False # 이상치(outlier) 점들을 숨겨서 깔끔하게 보여줍니다.
    )
    # X축 직업 이름을 정렬하지 않고 데이터 순서대로 보여줍니다.
    fig_box.update_xaxes(categoryorder='array', categoryarray=top_10_classes)
    st.plotly_chart(fig_box, use_container_width=True)

with col_right:
    # --- 시각화 3: 레벨과 전투력의 관계 (산점도) ---
    st.subheader("② 레벨과 전투력의 상관관계")
    fig_scatter = px.scatter(
        df_snapshot,
        x='character_level',
        y='전투력',
        hover_name='character_name', # 점 위에 마우스를 올리면 캐릭터 이름이 보입니다.
        title="레벨과 전투력 분포",
        labels={'character_level': '레벨', '전투력': '전투력'},
        opacity=0.6
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- 시각화 4: 전투력 TOP 20 랭킹 ---
    st.subheader("④ 전투력 랭킹 TOP 20")
    df_ranking = df_snapshot[['character_name', 'character_class', 'character_level', '전투력']] \
        .sort_values(by='전투력', ascending=False) \
        .head(20)
    
    # 인덱스를 1부터 시작하도록 설정하여 순위를 보여줍니다.
    df_ranking.index = range(1, len(df_ranking) + 1)
    st.dataframe(df_ranking)