# 파일 위치: final_dashboard.py

import streamlit as st

# --- 페이지 기본 설정 ---
# st.set_page_config()는 가장 먼저 실행되는 메인 파일에 한 번만 둡니다.
st.set_page_config(
    page_title="메이플스토리 260+ 유저 분석",
    page_icon="🍁",
    layout="wide",
    initial_sidebar_state="expanded" # 사이드바를 기본으로 열어둡니다.
)

# --- 메인 페이지 내용 ---
st.title("🍁 챌린저스 서버 260+ 유저 성장 분석 대시보드")
st.markdown("---")

st.header("프로젝트 개요")
st.write(
    """
    본 대시보드는 넥슨 Open API를 통해 수집된 챌린저스 서버 260레벨 이상 유저들의
    16주간 성장 데이터를 기반으로 제작되었습니다.
    
    왼쪽 사이드바에서 분석 페이지를 선택하여 다양한 인사이트를 확인해 보세요.
    """
)

st.subheader("페이지 안내")
st.markdown(
    """
    - **1_simpleboard_maplestory**: 서버 유저들의 기본적인 분포(레벨, 직업, 길드 등)와 월드 리프 현황을 분석합니다.
    - **2_Activity_Analysis**: 유저를 '성장'과 '정체' 그룹으로 나누어, 성장을 이끌거나 저해하는 요인을 심층적으로 분석합니다.
    - **(EDA Dashboard)**: 서버 전체의 성장 동향과 개별 캐릭터의 성장 과정을 추적합니다. (이 페이지는 아직 통합 전이라면 추가 설명)
    - **4_cody_fashion_analysis**: 10/16 스냅샷 기준 코디/뷰티 소비 유형과 라벨·믹스염색 활용도를 살펴봅니다.
    """
)

st.info("👈 왼쪽 사이드바에서 메뉴를 클릭하여 분석을 시작하세요.")