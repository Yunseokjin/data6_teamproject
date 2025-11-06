# 파일 위치: pages/1_simpleboard_maplestory.py

import pandas as pd
import plotly.express as px
import streamlit as st
import os 
import sys

# --- 1. 데이터 로드 및 전처리 함수 (utils.py 역할) ---
# 이 함수는 KPI와 시각화 모두에 사용되는 메인 데이터(growth_log)를 로드합니다.
@st.cache_data
def load_and_preprocess_data(file_path):
    try:
        # 파일 경로를 절대적으로 지정하여 Key Error 및 경로 오류를 해결합니다.
        # pages 폴더 안에 있으므로 '..'를 붙여 루트 폴더의 파일을 찾습니다.
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, '..', file_path) 
        
        df = pd.read_csv(data_path) 
        
        # --- 전처리 로직 ---
        df['user_status'] = df['character_name'].apply(
            lambda x: '월드 리프 유저' if pd.isna(x) else '챌린저스 잔류 유저'
        )
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['character_date_create'] = pd.to_datetime(df['character_date_create'], errors='coerce')
        df['전투력'] = pd.to_numeric(df['전투력'], errors='coerce')
        df['character_level'] = pd.to_numeric(df['character_level'], errors='coerce')
        df['has_guild'] = df['길드명'].apply(lambda x: True if pd.notna(x) else False)
        
        return df
    except Exception as e:
        # 파일 경로 오류 시 경고를 띄웁니다.
        st.error(f"메인 데이터 로드 중 오류 발생: {e}. 파일을 찾을 수 없거나 데이터 컬럼이 유효하지 않습니다.") 
        return pd.DataFrame() 

# --- 2. 데이터 불러오기 ---
df = load_and_preprocess_data('growth_log_v2_f_v2.csv')

# --- 3. 챌린저스 260+ 랭킹 데이터 로드 (KPI 계산용) ---
df_ranking = None # NameError 방지를 위해 미리 선언
try:
    # 랭킹 파일 로드: pages/에서 상위 디렉토리의 파일을 찾습니다.
    ranking_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'candidates_챌린저스_lv260_and_above.csv')
    df_ranking = pd.read_csv(ranking_path) 
    df_ranking['level'] = pd.to_numeric(df_ranking['level'], errors='coerce')
    df_ranking.dropna(subset=['level'], inplace=True)
except Exception:
    # 랭킹 파일 로드 실패 시 무시하고 df_ranking은 None으로 유지
    pass 

# --- 4. 대시보드 UI 구성 ---
st.title("🍁 챌린저스 서버 260+ 유저 기본 분석")
st.markdown("##### *랭킹 KPI 기준: 2025년 7월 3일 챌린저스 1서버 랭킹 자료*")
st.markdown("---")

# --- 5. 사이드바 (필터) ---
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

# --- 6. 핵심 지표 (KPI) 표시 (최종 목표) ---
if df_ranking is not None:
    # 🌟 랭킹 파일이 존재할 경우: 목표 KPI 표시 🌟
    total_users_260_plus = len(df_ranking)
    users_270_to_279 = len(df_ranking[(df_ranking['level'] >= 270) & (df_ranking['level'] <= 279)])
    users_280_plus = len(df_ranking[df_ranking['level'] >= 280])

    col1, col2, col3 = st.columns(3)
    
    col1.metric("📊 총 유저 수 (260+)", f"{total_users_260_plus:,} 명")
    col2.metric("✨ 270~279 유저 수", f"{users_270_to_279:,} 명")
    col3.metric("🌟 280+ 유저 수", f"{users_280_plus:,} 명")
    
else:
    # 랭킹 파일 없을 때: 유의미한 임시 KPI 표시
    st.warning("⚠️ 랭킹 데이터 로드 실패. 임시 KPI 표시 중.")
    total_users = len(filtered_df)
    remain_users = len(filtered_df[filtered_df['user_status'] == '챌린저스 잔류 유저'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 총 유저 수", f"{total_users:,} 명")
    col3.metric("🌟 잔류 유저 수", f"{remain_users:,} 명")

st.markdown("---")
    
# --- 7. 시각화 ---
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