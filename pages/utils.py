# 파일 위치: utils.py

import pandas as pd
import streamlit as st

# @st.cache_data 데코레이터를 사용하여 데이터 로딩을 캐싱합니다.
@st.cache_data
def load_and_preprocess_data(file_path):
    """
    데이터를 로드하고 모든 페이지에 필요한 공통 전처리를 수행하는 함수.
    이 함수가 이제 '데이터의 유일한 진실 공급원'이 됩니다.
    """
    try:
        df = pd.read_csv(file_path)
        
        # --- 모든 페이지에 필요한 공통 전처리 ---
        
        # 1. 'user_status' 컬럼 생성
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
        df['has_guild'] = df['character_guild_name'].notna()

        # 5. 데이터 정제
        df.dropna(subset=['ocid'], inplace=True)
        
        return df

    except FileNotFoundError:
        st.error(f"데이터 파일을 찾을 수 없습니다. '{file_path}' 경로를 확인해주세요.")
        return pd.DataFrame() # 오류 발생 시 빈 데이터프레임 반환
    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")
        return pd.DataFrame()