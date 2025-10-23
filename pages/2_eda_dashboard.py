# 파일 위치: pages/2_EDA_Dashboard.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import font_manager, rc

# --- 1. 기본 설정 및 데이터 로딩 ---

st.set_page_config(layout="wide")

try:
    font_name = font_manager.FontProperties(fname='c:/Windows/Fonts/malgun.ttf').get_name()
    rc('font', family=font_name)
except FileNotFoundError:
    st.warning("한글 폰트(맑은 고딕)를 찾을 수 없어 그래프의 일부 글자가 깨질 수 있습니다.")
plt.rcParams['axes.unicode_minus'] = False

# ★★★ 프로젝트의 메인 데이터 파일을 정확히 가리키도록 경로 설정 ★★★
# (현재 파일은 pages 폴더 안에 있으므로, 상위 폴더의 파일을 가리키려면 '../'를 사용합니다.)
FILE_PATH = "../growth_log_v2_f_v2.csv" 

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    df['전투력'] = pd.to_numeric(df['전투력'], errors='coerce')
    df['character_level'] = pd.to_numeric(df['character_level'], errors='coerce')
    return df

try:
    df = load_data(FILE_PATH)
    latest_date = df['date'].max()
    df_latest = df[df['date'] == latest_date]

    # --- 2. 대시보드 UI 구성 ---
    st.title('챌린저스 월드 성장 데이터 EDA 대시보드 📊')
    st.sidebar.header('🔍 필터 및 검색')
    selected_class = st.sidebar.selectbox(
        '직업 선택 (전체 보기 가능)',
        options=['전체'] + sorted(df['character_class'].dropna().unique())
    )
    # --- 이하 코드는 이전과 동일 ---
    st.header('📈 서버 전체 동향')
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('주차별 평균 전투력 변화')
        avg_power_by_date = df.groupby('date')['전투력'].mean()
        st.line_chart(avg_power_by_date)
    with col2:
        st.subheader('주차별 평균 레벨 변화')
        avg_level_by_date = df.groupby('date')['character_level'].mean()
        st.line_chart(avg_level_by_date)

    st.header(f' snapshot ({latest_date.strftime("%Y-%m-%d")} 기준)')
    col3, col4 = st.columns(2)
    if selected_class != '전체':
        df_filtered_latest = df_latest[df_latest['character_class'] == selected_class]
    else:
        df_filtered_latest = df_latest
    with col3:
        st.subheader(f'{selected_class} 레벨 분포')
        fig, ax = plt.subplots()
        ax.hist(df_filtered_latest['character_level'].dropna(), bins=30, color='skyblue', edgecolor='black')
        st.pyplot(fig)
    with col4:
        st.subheader(f'{selected_class} 전투력 TOP 10')
        top_10 = df_filtered_latest[['character_name', 'character_level', '전투력']].sort_values(by='전투력', ascending=False).head(10)
        st.dataframe(top_10)

    st.header('👤 개별 캐릭터 성장 추적')
    search_name = st.text_input('캐릭터 이름을 입력하고 Enter를 누르세요', '당바나바')
    if search_name:
        char_data = df[df['character_name'] == search_name].sort_values('date')
        if not char_data.empty:
            st.subheader(f"'{search_name}'님의 성장 기록")
            col5, col6 = st.columns([1, 2])
            with col5:
                display_cols = ['date', 'character_level', '전투력', '보스_데미지']
                st.dataframe(char_data[display_cols].set_index('date'))
            with col6:
                st.line_chart(char_data.set_index('date')[['전투력']])
        else:
            st.warning(f"'{search_name}'님을 찾을 수 없습니다.")

except FileNotFoundError:
    st.error(f"데이터 파일을 찾을 수 없습니다. '{FILE_PATH}' 경로를 확인해주세요.")
except Exception as e:
    st.error(f"데이터를 로드하는 중 오류가 발생했습니다: {e}")