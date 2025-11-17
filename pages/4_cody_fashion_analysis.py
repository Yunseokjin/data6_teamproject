# 파일 위치: pages/4_cody_fashion_analysis.py

import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

st.title("🧥 10/16 코디 아이템 집중 분석")
st.markdown(
    """
    10월 16일 스냅샷으로 정리된 코디 아이템 데이터를 활용해
    코디/뷰티 소비 패턴과 믹스 염색 활용도를 한눈에 살펴볼 수 있습니다.
    """
)

DATA_CANDIDATES = [
    Path("코디_분석_결과.csv"),
    Path(r"C:\Users\MSG\Desktop\DAB6기\윤석진_데이터톤파일 정리\7팀_데이터톤_사용데이터프레임\코디_분석_결과.csv"),
]

COLUMN_MAP = {
    "유료아이템착용 개수": "paid_item_count",
    "총 코디금액(원)": "total_cody_amount",
    "착용코디금액(원)": "equipped_cody_amount",
    "스페셜라벨 개수": "special_label_cnt",
    "레드라벨 개수": "red_label_cnt",
    "마스터라벨 개수": "master_label_cnt",
    "일루전 링 개수": "illusion_ring_cnt",
    "비싼 헤어(부티크, 마스터라벨) 유무": "premium_hair_flag",
    "헤어 믹스염색 여부": "mix_hair_flag",
    "헤어 믹스염색 비율": "mix_hair_ratio",
    "성형 믹스염색 여부": "mix_face_flag",
    "성형 믹스염색 비율": "mix_face_ratio",
    "착용 아이템 리스트": "equipped_items",
    "착용 헤어,성형,피부": "equipped_beauty",
    "세분화 유저 그룹": "user_segment",
}

SEGMENT_ALIAS = {
    "1. 유료 유저 (아이템 구매 지출)": "코디 유저",
    "2. 무료/이벤트 유저 (뷰티 컨텐츠 지출)": "헤어/성형 유저",
    "3. 순수 무료 유저 (지출 0원)": "무과금 유저",
}


@st.cache_data
def load_cody_dataframe():
    for path in DATA_CANDIDATES:
        if path.exists():
            df = pd.read_csv(path, encoding="utf-8").rename(columns=COLUMN_MAP)
            df["user_segment"] = df["user_segment"].astype(str).str.strip()
            df["segment_simple"] = df["user_segment"].map(SEGMENT_ALIAS).fillna("기타")

            numeric_cols = [
                "paid_item_count",
                "total_cody_amount",
                "equipped_cody_amount",
                "special_label_cnt",
                "red_label_cnt",
                "master_label_cnt",
                "illusion_ring_cnt",
                "premium_hair_flag",
                "mix_hair_flag",
                "mix_hair_ratio",
                "mix_face_flag",
                "mix_face_ratio",
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            return df
    st.error("코디 분석용 CSV 파일을 찾을 수 없습니다. 경로를 다시 확인해주세요.")
    return pd.DataFrame()


df = load_cody_dataframe()

if df.empty:
    st.stop()

# --- 사이드바 필터 ---
st.sidebar.header("🎛️ 뷰티 소비 필터")
segment_filter = st.sidebar.multiselect(
    "유저 타입",
    options=df["segment_simple"].unique(),
    default=df["segment_simple"].unique(),
    key="cody_segment_filter",
)

filtered_df = df[df["segment_simple"].isin(segment_filter)].copy()

if filtered_df.empty:
    st.warning("선택된 조건에 해당하는 유저가 없습니다.")
    st.stop()

st.markdown("---")
st.subheader("1️⃣ 코디·뷰티 소비 타입 분포 (10/16)")
segment_summary = (
    filtered_df["segment_simple"]
    .value_counts()
    .rename_axis("세그먼트")
    .reset_index(name="user_count")
)
segment_summary["비중(%)"] = (
    segment_summary["user_count"] / segment_summary["user_count"].sum() * 100
)

col_a, col_b = st.columns([2, 1])
with col_a:
    fig_segment = px.bar(
        segment_summary,
        x="세그먼트",
        y="user_count",
        color="세그먼트",
        text=segment_summary["비중(%)"].apply(lambda v: f"{v:.1f}%"),
        title="코디 유저 vs 헤어/성형 유저 vs 무과금 유저 분포",
        labels={"user_count": "유저 수"},
    )
    fig_segment.update_traces(textposition="outside")
    st.plotly_chart(fig_segment, use_container_width=True)
with col_b:
    st.dataframe(segment_summary, hide_index=True)

st.markdown("---")
st.subheader("2️⃣ 착용 코디 금액 분포")
amount_metric = st.radio(
    "분석 지표 선택",
    options=["총 코디 금액", "현재 착용 금액"],
    horizontal=True,
    key="cody_amount_metric",
)
amount_col = (
    "total_cody_amount" if amount_metric == "총 코디 금액" else "equipped_cody_amount"
)

fig_amount = px.histogram(
    filtered_df,
    x=amount_col,
    nbins=40,
    color="segment_simple",
    title=f"{amount_metric} 분포",
    labels={amount_col: f"{amount_metric} (원)", "segment_simple": "세그먼트"},
)
fig_amount.update_layout(bargap=0.05)
st.plotly_chart(fig_amount, use_container_width=True)

amount_stats = filtered_df[amount_col].agg(
    평균="mean", 중앙값="median", 최대="max", 상위10퍼센타일=lambda s: s.quantile(0.9)
)
st.caption("요약 통계 (원)")
st.write(amount_stats.to_frame(name=amount_metric).style.format("{:,.0f}"))

st.markdown("---")
st.subheader("3️⃣ 코디 유저 라벨 아이템 착용 비율")
cody_users = filtered_df[filtered_df["segment_simple"] == "코디 유저"]
if cody_users.empty:
    st.info("선택한 조건에 코디 유저가 없습니다.")
else:
    label_metrics = pd.DataFrame(
        {
            "라벨 유형": [
                "마스터라벨",
                "레드+블랙라벨",
                "스페셜라벨",
            ],
            "착용 비율(%)": [
                (cody_users["master_label_cnt"] > 0).mean() * 100,
                (cody_users["red_label_cnt"] > 0).mean() * 100,
                (cody_users["special_label_cnt"] > 0).mean() * 100,
            ],
        }
    )
    fig_labels = px.bar(
        label_metrics,
        x="라벨 유형",
        y="착용 비율(%)",
        text=label_metrics["착용 비율(%)"].map(lambda v: f"{v:.1f}%"),
        color="라벨 유형",
        range_y=[0, 100],
        title="코디 유저 라벨별 착용 침투율",
    )
    fig_labels.update_traces(textposition="outside")
    st.plotly_chart(fig_labels, use_container_width=True)
    st.caption("※ 블랙라벨 컬럼이 분리되어 있지 않아 레드라벨 수치를 대표값으로 사용했습니다.")

st.markdown("---")
st.subheader("4️⃣ 믹스 염색 · 렌즈 활용 및 커스텀 강도")
mix_stats = {
    "헤어 믹스염색 적용률": (filtered_df["mix_hair_flag"] > 0).mean() * 100,
    "믹스렌즈(성형) 적용률": (filtered_df["mix_face_flag"] > 0).mean() * 100,
    "평균 헤어 커스텀 강도": filtered_df.loc[
        filtered_df["mix_hair_flag"] > 0, "mix_hair_ratio"
    ].mean()
    if (filtered_df["mix_hair_flag"] > 0).any()
    else 0,
    "평균 렌즈 커스텀 강도": filtered_df.loc[
        filtered_df["mix_face_flag"] > 0, "mix_face_ratio"
    ].mean()
    if (filtered_df["mix_face_flag"] > 0).any()
    else 0,
}

metric_cols = st.columns(4)
metric_labels = list(mix_stats.keys())
for idx, col in enumerate(metric_cols):
    value = mix_stats[metric_labels[idx]]
    col.metric(metric_labels[idx], f"{value:.1f}%")

mix_detail = pd.DataFrame(
    {
        "구분": ["헤어 믹스염색", "성형 믹스렌즈"],
        "적용률(%)": [
            mix_stats["헤어 믹스염색 적용률"],
            mix_stats["믹스렌즈(성형) 적용률"],
        ],
        "평균 커스텀 강도(%)": [
            mix_stats["평균 헤어 커스텀 강도"],
            mix_stats["평균 렌즈 커스텀 강도"],
        ],
    }
).round(1)
st.dataframe(mix_detail, hide_index=True)

st.markdown(
    """
    - 믹스염색/믹스렌즈 적용률은 해당 기능을 사용한 유저 비중입니다.
    - 커스텀 강도는 믹스 기능을 사용한 유저들의 평균 색상 가중치(%)를 의미합니다.
    """
)

