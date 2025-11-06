# 파일 위치: pages/1_simpleboard_maplestory.py

import pandas as pd
import plotly.express as px
import streamlit as st
import os # <-- os 모듈 추가

# --- load_and_preprocess_data 함수 정의 시작 ---
@st.cache_data
def load_and_preprocess_data(file_path):
    """
    데이터를 로드하고 모든 페이지에 필요한 공통 전처리를 수행하는 함수.
    """
    try:
        # 파일 경로를 절대적으로 지정하여 Key Error 및 경로 오류를 해결
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, '..', file_path) 
        
        df = pd.read_csv(data_path) 
        
        # --- 모든 페이지에 필요한 공통 전처리 ---
        
        # 1. 'user_status' 컬럼 생성 (Key Error를 유발했던 로직)
        df['user_status'] = df['character_name'].apply(
            lambda x: '월드 리프 유저' if pd.isna(x) else '챌린저스 잔류 유저'
        )
        
        # 2. 날짜 형식 변환
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['character_date_create'] = pd.to_datetime(df['character_date_create'], errors='coerce')

        # 3. 숫자 형식 변환
        df['전투력'] = pd.to_numeric(df['전투력'], errors='coerce')
        df['character_level'] = pd.to_numeric(df['character_level'], errors='coerce')
        
        # 4. 길드 가입 여부 컬럼 생성
        df['has_guild'] = df['길드명'].apply(lambda x: True if pd.notna(x) else False)
        
        return df
    except Exception as e:
        # 이제 오류가 발생하면 Streamlit에서 오류 메시지가 표시됩니다.
        st.error(f"데이터 로드 및 전처리 중 오류 발생: {e}") 
        return pd.DataFrame() 
# --- load_and_preprocess_data 함수 정의 끝 ---


# --- 데이터 불러오기 ---
df = load_and_preprocess_data('growth_log_v2_f_v2.csv')
# --- 대시보드 UI 구성 ---
st.title("🍁 챌린저스 서버 260+ 유저 기본 분석")
# ⭐ 요청하신 기준일 언급 추가 (작은 글씨)
st.markdown("##### *랭킹 KPI 기준일: 2025년 7월 3일 챌린저스 1서버 랭킹 자료 기준*")
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

# --- 4. 핵심 지표 (KPI) 표시 - 랭킹 파일 기반으로 수정 ---
if df_ranking is not None:
    # 1. 총 유저 수 (260레벨 이상)
    total_users_260_plus = len(df_ranking)
    
    # 2. 270~279 유저 수 (270 이상, 280 미만)
    users_270_to_279 = len(df_ranking[(df_ranking['level'] >= 270) & (df_ranking['level'] <= 279)])
    
    # 3. 280+ 유저 수 (280 이상)
    users_280_plus = len(df_ranking[df_ranking['level'] >= 280])

    col1, col2, col3 = st.columns(3)
    
    # 지표 표시
    col1.metric("📊 총 유저 수 (260+)", f"{total_users_260_plus:,} 명", help="20250703 챌린저스 랭킹 기준")
    # 레이블 최종 수정 반영
    col2.metric("✨ 270~279 유저 수", f"{users_270_to_279:,} 명", f"{users_270_to_279/total_users_260_plus:.1%}" if total_users_260_plus > 0 else "0%", help="20250703 챌린저스 랭킹 기준")
    col3.metric("🌟 280+ 유저 수", f"{users_280_plus:,} 명", f"{users_280_plus/total_users_260_plus:.1%}" if total_users_260_plus > 0 else "0%", help="20250703 챌린저스 랭킹 기준")
    st.markdown("---")
else:
    # 랭킹 파일 로드에 실패하면 경고 메시지 표시
    st.warning("⚠️ 랭킹 데이터 로드 실패로 핵심 지표를 표시할 수 없습니다. (아래 시각화는 기존 데이터 사용)")
    st.markdown("---")

# --- 5. 시각화 (기존 코드 유지) ---
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