# 파일 위치: pages/1_simpleboard_maplestory.py

import pandas as pd
import plotly.express as px
import streamlit as st
import os 
from utils import load_and_preprocess_data # <-- 루트 폴더의 utils.py를 다시 임포트

# --- 데이터 불러오기 ---
df = load_and_preprocess_data('growth_log_v2_f_v2.csv')

# --- 챌린저스 260+ 랭킹 데이터 로드 (KPI 계산용) ---
try:
    # pages/에서 상위 디렉토리의 파일에 접근 (이전에 잘 작동했던 경로)
    df_ranking = pd.read_csv('../candidates_챌린저스_lv260_and_above.csv') 
    df_ranking['level'] = pd.to_numeric(df_ranking['level'], errors='coerce')
    df_ranking.dropna(subset=['level'], inplace=True)
except FileNotFoundError:
    st.warning("⚠️ 랭킹 데이터 파일을 찾을 수 없어 KPI를 표시할 수 없습니다.")
    df_ranking = None
except Exception as e:
    st.error(f"🚨 랭킹 파일 처리 중 오류 발생: {e}")
    df_ranking = None


# --- 대시보드 UI 구성 ---
st.title("🍁 챌린저스 서버 260+ 유저 기본 분석")
st.markdown("##### *랭킹 KPI 기준일: 2025년 7월 3일 챌린저스 1서버 랭킹 자료 기준*")
st.markdown("---")

# ... (사이드바 및 filtered_df 생성 로직은 유지) ...

# --- 4. 핵심 지표 (KPI) 표시 - 랭킹 파일 기반 로직 (복구) ---
if df_ranking is not None:
    # 랭킹 KPI 로직 (이전에 잘 작동했던 로직)
    total_users_260_plus = len(df_ranking)
    users_270_to_279 = len(df_ranking[(df_ranking['level'] >= 270) & (df_ranking['level'] <= 279)])
    users_280_plus = len(df_ranking[df_ranking['level'] >= 280])

    col1, col2, col3 = st.columns(3)
    col1.metric("📊 총 유저 수 (260+)", f"{total_users_260_plus:,} 명")
    col2.metric("✨ 270~279 유저 수", f"{users_270_to_279:,} 명")
    col3.metric("🌟 280+ 유저 수", f"{users_280_plus:,} 명")
    st.markdown("---")
else:
    # 랭킹 파일 없을 때 임시 KPI (기존 로직 사용)
    total_users = len(filtered_df)
    remain_users = len(filtered_df[filtered_df['user_status'] == '챌린저스 잔류 유저'])
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 총 유저 수", f"{total_users:,} 명 (임시)")
    col3.metric("🌟 잔류 유저 수", f"{remain_users:,} 명 (임시)")
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