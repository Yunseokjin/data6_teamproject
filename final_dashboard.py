# --------------------------------------------------------------------------
# 🍁 메이플스토리 260+ 유저 성장 분석 대시보드 (최종 최적화 버전)
# --------------------------------------------------------------------------

import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st

# --- 0. 페이지 기본 설정 ---
st.set_page_config(
    page_title="메이플스토리 260+ 유저 성장 분석",
    page_icon="🍁",
    layout="wide"
)

# --- 1. 데이터 불러오기 및 전처리 (캐싱을 통해 성능 향상) ---
# ==================================================================
# ★★★ 바로 이 한 줄이 마법을 부립니다! ★★★
# 이 함수는 처음 한 번만 실행하고, 그 결과를 기억해 둡니다.
@st.cache_data
# ==================================================================
def load_and_process_data(file_path):
    # 이제 테스트용 .head(1000)는 필요 없으니, 전체 데이터를 모두 사용합니다.
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['ocid', 'date'])

    # 주간 경험치 성장량 계산
    df['weekly_exp_gain'] = df.groupby('ocid')['character_exp'].diff().fillna(0)
    
    # 활동 상태 정의 ('첫 주', '성장', '정체')
    df['activity_status'] = np.where(df.groupby('ocid').cumcount() == 0, '첫 주', 
                                     np.where(df['weekly_exp_gain'] > 0, '성장', '정체'))
    
    # 5레벨 단위 레벨 구간 생성
    bins = range(260, 301, 5)
    labels = [f"{i}~{i+4}" for i in bins[:-1]]
    df['level_range'] = pd.cut(df['character_level'], bins=bins, labels=labels, right=False)
    
    # 길드 가입 여부 생성
    df['has_guild'] = df['character_guild_name'].notna()
    
    return df

df = load_and_process_data('growth_log_v2_f_v2.csv')

# --- 2. 대시보드 제목 ---
st.title("🍁 메이플스토리 260+ 유저 성장 궤적 분석")
st.markdown("---")

# (이하 모든 그래프 코드는 이전과 동일)
# --- 3. 대시보드 레이아웃 구성 ---

# Row 1: 전체 활동 추이 (전체 너비 사용)
st.subheader("① 전체 유저 활동성 변화 추이")
analysis_df2 = df[df['activity_status'] != '첫 주'].copy()
activity_trend = analysis_df2.groupby('date')['activity_status'].value_counts(normalize=True).mul(100).rename('percentage').reset_index()
fig2 = px.line(activity_trend, x='date', y='percentage', color='activity_status', title='주차별 활동 유저 비율 변화 추이', labels={'date': '날짜', 'percentage': '유저 비율 (%)', 'activity_status': '활동 상태'}, markers=True)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Row 2: 정체 그룹 vs 성장 그룹 히트맵 (좌우 배치)
st.subheader("② 시간에 따른 유저 레벨 분포 변화")
col1, col2 = st.columns(2)

heatmap_source_df = df[df['activity_status'].isin(['성장', '정체'])].groupby(['date', 'activity_status', 'level_range'], observed=True).size().reset_index(name='user_count')
total_users_per_group = heatmap_source_df.groupby(['date', 'activity_status'])['user_count'].transform('sum')
heatmap_source_df['percentage'] = (heatmap_source_df['user_count'] / total_users_per_group) * 100

with col1:
    stagnation_heatmap_data = heatmap_source_df[heatmap_source_df['activity_status'] == '정체'].pivot_table(index='level_range', columns='date', values='percentage').sort_index(ascending=False)
    fig_stagnation_heatmap = px.imshow(stagnation_heatmap_data, labels=dict(x="날짜", y="레벨 구간", color="유저 비율 (%)"), title='<b>[정체 그룹]</b> 유저 분포', aspect="auto")
    st.plotly_chart(fig_stagnation_heatmap, use_container_width=True)

with col2:
    growth_heatmap_data = heatmap_source_df[heatmap_source_df['activity_status'] == '성장'].pivot_table(index='level_range', columns='date', values='percentage').sort_index(ascending=False)
    fig_growth_heatmap = px.imshow(growth_heatmap_data, labels=dict(x="날짜", y="레벨 구간", color="유저 비율 (%)"), title='<b>[성장 그룹]</b> 유저 분포', aspect="auto")
    st.plotly_chart(fig_growth_heatmap, use_container_width=True)

st.markdown("---")

# Row 3: 요약 및 원인 분석 (좌우 배치)
st.subheader("③ 성장 정체 구간 및 핵심 변수 분석")
col3, col4 = st.columns(2)

with col3:
    analysis_df1 = df[df['activity_status'] != '첫 주'].copy()
    stagnation_by_level = analysis_df1.groupby('level_range', observed=True)['activity_status'].value_counts(normalize=True).mul(100).rename('percentage').reset_index()
    stagnation_by_level_filtered = stagnation_by_level[stagnation_by_level['activity_status'] == '정체'].copy()
    stagnation_by_level_filtered['text'] = stagnation_by_level_filtered['percentage'].apply(lambda x: f'{x:.1f}%')
    fig1 = px.bar(stagnation_by_level_filtered, x='level_range', y='percentage', title='전체 기간의 레벨 구간별 "정체" 유저 비율', labels={'level_range': '레벨 구간', 'percentage': '정체 유저 비율 (%)'}, text='text')
    st.plotly_chart(fig1, use_container_width=True)

with col4:
    analysis_df3 = df[df['weekly_exp_gain'] > 0].copy()
    fig3 = px.box(analysis_df3, x='has_guild', y='weekly_exp_gain', color='has_guild', title='길드 가입 여부에 따른 주간 경험치 획득량 분포', labels={'has_guild': '길드 가입 여부', 'weekly_exp_gain': '주간 경험치 획득량'}, notched=True)
    st.plotly_chart(fig3, use_container_width=True)

# ==================================================================
# ★★★★★ 바로 이 부분이 추가된 애니메이션 차트입니다! ★★★★★
# ==================================================================
st.markdown("---")
st.subheader("④ [참고] 동적 시각화로 유저 여정 살펴보기")

# st.expander를 사용해 기본적으로는 내용을 숨겨둡니다.
with st.expander("▶️ 애니메이션으로 시간에 따른 레벨 분포 변화 보기 (클릭하여 펼치기)"):
    st.info("타임라인 슬라이더나 재생 버튼을 눌러 시간의 흐름에 따른 유저 분포의 변화를 동적으로 확인할 수 있습니다.")
    
    # 애니메이션을 위한 데이터 준비
    animation_df = heatmap_source_df.copy()
    animation_df['date_str'] = animation_df['date'].dt.strftime('%Y-%m-%d')
    level_order = [f"{i}~{i+4}" for i in range(260, 301, 5)[:-1]]

    # 애니메이션 바 차트 생성
    fig_animation = px.bar(
        animation_df.sort_values('date'),
        x='level_range',
        y='percentage',
        color='level_range',
        animation_frame='date_str',
        facet_row='activity_status',
        title='시간에 따른 활동 상태별 레벨 분포 변화 (애니메이션)',
        labels={'level_range': '레벨 구간', 'percentage': '해당 구간 유저 비율 (%)', 'date_str': '날짜'},
        range_y=[0, 100],
        category_orders={'level_range': level_order}
    )
    fig_animation.update_yaxes(title_text='유저 비율 (%)')
    fig_animation.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    # 대시보드에 애니메이션 차트 표시
    st.plotly_chart(fig_animation, use_container_width=True)

    # ... 기존 코드 맨 아래 ...

# 최종 배포를 위한 테스트 주석