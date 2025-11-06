# 파일 위치: pages/1_simpleboard_maplestory.py

import pandas as pd
import plotly.express as px
import streamlit as st
from utils import load_and_preprocess_data # 1. 공통 도우미 임포트

# --- 데이터 불러오기 ---
# 모든 전처리는 utils.py가 책임집니다.
# utils.py가 루트에 있으므로 파일명만 넘겨줍니다.
df = load_and_preprocess_data('growth_log_v2_f_v2.csv')

# --- 대시보드 UI 구성 ---
st.title("🍁 챌린저스 서버 260+ 유저 기본 분석")
st.markdown("---")

# 사이드바 (필터)
st.sidebar.header("🔎 필터")
status_filter = st.sidebar.multiselect(
    "유저 그룹 선택:",
    options=df['user_status'].unique(),
    default=df['user_status'].unique(),
    key='simpleboard_status_filter' 
)

# 필터링된 데이터
filtered_df = df[df['user_status'].isin(status_filter)]

if filtered_df.empty:
    st.warning("선택된 필터에 해당하는 데이터가 없습니다.")
    st.stop()

# --- 4. 핵심 지표 (KPI) 표시 (복구된 초기 KPI) ---
total_users = len(filtered_df)
leaf_users = len(filtered_df[filtered_df['user_status'] == '월드 리프 유저'])
remain_users = len(filtered_df[filtered_df['user_status'] == '챌린저스 잔류 유저'])

col1, col2, col3 = st.columns(3)

# 지표 표시
col1.metric("📊 총 유저 수", f"{total_users:,} 명")
col2.metric("✨ 월드 리프 유저 수", f"{leaf_users:,} 명", f"{leaf_users/total_users:.1%}" if total_users > 0 else "0%")
col3.metric("🌟 챌린저스 잔류 유저 수", f"{remain_users:,} 명", f"{remain_users/total_users:.1%}" if total_users > 0 else "0%")
st.markdown("---")

# --- 5. 시각화 (유지) ---
col_left, col_right = st.columns(2)

with col_left:
    # 1. 레벨 분포 (히스토그램)
    st.subheader("📊 레벨 분포")
    fig_level = px.histogram(
        filtered_df, 
        x='character_level', 
        color='user_status',
        title="유저 그룹별 레벨 분포",
        labels={'character_level': '캐릭터 레벨'}
    )
    st.plotly_chart(fig_level, use_container_width=True)

    # 2. 길드 가입률 (파이 차트)
    st.subheader("🤝 길드 가입률")
    guild_data = filtered_df[filtered_df['user_status'] == '챌린저스 잔류 유저']['has_guild'].value_counts()
    fig_guild = px.pie(
        guild_data, 
        values=guild_data.values, 
        names=guild_data.index.map({True: '길드 가입', False: '길드 미가입'}),
        title="챌린저스 잔류 유저 길드 가입 현황",
        hole=0.3
    )
    st.plotly_chart(fig_guild, use_container_width=True)

with col_right:
    # 3. 직업 분포 (막대 그래프)
    st.subheader("⚔️ 직업 분포")
    class_data = filtered_df[filtered_df['user_status'] == '챌린저스 잔류 유저']['character_class'].value_counts().nlargest(15)
    fig_class = px.bar(
        class_data,
        x=class_data.index,
        y=class_data.values,
        title="챌린저스 잔류 유저 직업 분포 (Top 15)",
        labels={'x': '직업', 'y': '유저 수'},
        color=class_data.index
    )
    st.plotly_chart(fig_class, use_container_width=True)
    
    # 4. 캐릭터 생성일 분포
    st.subheader("📅 캐릭터 생성일 분포")
    create_date_data = filtered_df.dropna(subset=['character_date_create'])
    fig_date = px.histogram(
        create_date_data,
        x='character_date_create',
        color='user_status',
        title="유저 그룹별 캐릭터 생성일 분포",
        labels={'character_date_create': '생성일'}
    )
    st.plotly_chart(fig_date, use_container_width=True)

# 원본 데이터 테이블 표시 (옵션)
if st.checkbox("데이터 원본 보기"):
    st.dataframe(filtered_df)