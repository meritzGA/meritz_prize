import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import re
import base64
import streamlit.components.v1 as components

# 페이지 설정
st.set_page_config(page_title="메리츠화재 시상 현황", layout="wide")

# --- 데이터 영구 저장을 위한 폴더 설정 ---
DATA_DIR = "app_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 데이터 불러오기 로직
if 'raw_data' not in st.session_state:
    st.session_state['raw_data'] = {}
    for file in os.listdir(DATA_DIR):
        if file.endswith('.pkl'):
            st.session_state['raw_data'][file.replace('.pkl', '')] = pd.read_pickle(os.path.join(DATA_DIR, file))

if 'config' not in st.session_state:
    config_path = os.path.join(DATA_DIR, 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            st.session_state['config'] = json.load(f)
    else:
        st.session_state['config'] = []

# 기존 데이터 호환성 보장
for c in st.session_state['config']:
    if 'category' not in c:
        c['category'] = 'weekly'

# 🌟 엑셀 외계어(_xHHHH_) 복원 및 정제 함수 🌟
def safe_str(val):
    if pd.isna(val) or val is None: return ""
    
    try:
        # 소수점으로 읽힌 사번 복구 (예: 12345.0 -> 12345)
        if isinstance(val, (int, float)) and float(val).is_integer():
            val = int(float(val))
    except:
        pass
        
    s = str(val)
    
    # 1. 엑셀의 숨겨진 16진수 외계어(_x0033_ 등)를 원래 문자(3 등)로 완벽 복원
    s = re.sub(r'_[xX]([0-9A-Fa-f]{4})_', lambda m: chr(int(m.group(1), 16)), s)
    
    # 2. 보이지 않는 띄어쓰기, 엔터, 탭 강제 삭제
    s = re.sub(r'\s+', '', s)
    
    # 3. 문자열에 남은 .0 잔재 제거
    if s.endswith('.0'): 
        s = s[:-2]
        
    # 4. 알파벳 대문자 통일 (매칭률 100% 보장)
    return s.upper()

# 🌟 정제된 데이터를 캐싱하여 중복 연산 완전 제거 🌟
def get_clean_series(df, col_name):
    clean_col_name = f"_clean_{col_name}"
    # 한 번 정제된 컬럼이 없다면 최초 1회만 정제 연산을 수행하여 데이터프레임에 저장
    if clean_col_name not in df.columns:
        df[clean_col_name] = df[col_name].apply(safe_str)
    return df[clean_col_name]

def safe_float(val):
    if pd.isna(val) or val is None: return 0.0
    s = str(val).replace(',', '').strip()
    try: return float(s)
    except: return 0.0

# --- 🎨 커스텀 CSS (라이트/다크모드 완벽 대응) ---
st.markdown("""
<style>
    /* ========================================= */
    /* ☀️ 기본 모드 (Light Mode) CSS             */
    /* ========================================= */
    [data-testid="stAppViewContainer"] { background-color: #f2f4f6; color: #191f28; }
    span.material-symbols-rounded, span[data-testid="stIconMaterial"] { display: none !important; }
    
    div[data-testid="stRadio"] > div {
        display: flex; justify-content: center; background-color: #ffffff; 
        padding: 10px; border-radius: 15px; margin-bottom: 20px; margin-top: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #e5e8eb;
    }
    
    .title-band {
        background-color: rgb(128, 0, 0); color: #ffffff; font-size: 1.4rem; font-weight: 800;
        text-align: center; padding: 16px; border-radius: 12px; margin-bottom: 24px;
        letter-spacing: -0.5px; box-shadow: 0 4px 10px rgba(128, 0, 0, 0.2);
    }

    [data-testid="stForm"] { background-color: transparent; border: none; padding: 0; margin-bottom: 24px; }

    /* 공통 텍스트 타이틀 클래스 */
    .admin-title { color: #191f28; font-weight: 800; font-size: 1.8rem; margin-top: 20px; }
    .sub-title { color: #191f28; font-size: 1.4rem; margin-top: 30px; font-weight: 700; }
    .config-title { color: #191f28; font-size: 1.3rem; margin: 0; font-weight: 700; }
    .main-title { color: #191f28; font-weight: 800; font-size: 1.3rem; margin-bottom: 15px; }
    .blue-title { color: #1e3c72; font-size: 1.4rem; margin-top: 10px; font-weight: 800; }
    .agent-title { color: #3182f6; font-weight: 800; font-size: 1.5rem; margin-top: 0; text-align: center; }

    /* 공통 박스 클래스 */
    .config-box { background: #f9fafb; padding: 15px; border-radius: 15px; border: 1px solid #e5e8eb; margin-top: 15px; }
    .config-box-blue { background: #f0f4f8; padding: 15px; border-radius: 15px; border: 1px solid #c7d2fe; margin-top: 15px; }
    .detail-box { background: #ffffff; padding: 20px; border-radius: 20px; border: 2px solid #e5e8eb; margin-top: 10px; margin-bottom: 30px; }

    /* 시책 요약 카드 (상단) */
    .summary-card { 
        background: linear-gradient(135deg, rgb(160, 20, 20) 0%, rgb(128, 0, 0) 100%); 
        border-radius: 20px; padding: 32px 24px; margin-bottom: 24px; border: none;
        box-shadow: 0 10px 25px rgba(128, 0, 0, 0.25);
    }
    .cumulative-card { 
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
        border-radius: 20px; padding: 32px 24px; margin-bottom: 24px; border: none;
        box-shadow: 0 10px 25px rgba(30, 60, 114, 0.25);
    }
    .summary-label { color: rgba(255,255,255,0.85); font-size: 1.15rem; font-weight: 600; margin-bottom: 8px; }
    .summary-total { color: #ffffff; font-size: 2.6rem; font-weight: 800; letter-spacing: -1px; margin-bottom: 24px; white-space: nowrap; word-break: keep-all; }
    .summary-item-name { color: rgba(255,255,255,0.95); font-size: 1.15rem; }
    .summary-item-val { color: #ffffff; font-size: 1.3rem; font-weight: 800; white-space: nowrap; }
    .summary-divider { height: 1px; background-color: rgba(255,255,255,0.2); margin: 16px 0; }
    
    /* 개별 상세 카드 */
    .toss-card { 
        background: #ffffff; border-radius: 20px; padding: 28px 24px; 
        margin-bottom: 16px; border: 1px solid #e5e8eb; box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
    }
    .toss-title { font-size: 1.6rem; font-weight: 700; color: #191f28; margin-bottom: 6px; letter-spacing: -0.5px; }
    .toss-desc { font-size: 1.15rem; color: rgb(128, 0, 0); font-weight: 800; margin-bottom: 24px; letter-spacing: -0.3px; line-height: 1.4; word-break: keep-all; }
    
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; flex-wrap: nowrap; }
    .data-label { color: #8b95a1; font-size: 1.1rem; word-break: keep-all; }
    .data-value { color: #333d4b; font-size: 1.3rem; font-weight: 600; white-space: nowrap; }
    
    /* 상위 구간 부족 금액 강조 디자인 */
    .shortfall-row { background-color: #fff0f0; padding: 14px; border-radius: 12px; margin-top: 15px; margin-bottom: 5px; border: 2px dashed #ff4b4b; text-align: center; }
    .shortfall-text { color: #d9232e; font-size: 1.2rem; font-weight: 800; word-break: keep-all; }

    .prize-row { display: flex; justify-content: space-between; align-items: center; padding-top: 20px; margin-top: 12px; flex-wrap: nowrap; }
    .prize-label { color: #191f28; font-size: 1.3rem; font-weight: 700; word-break: keep-all; white-space: nowrap; }
    .prize-value { color: rgb(128, 0, 0); font-size: 1.8rem; font-weight: 800; white-space: nowrap; text-align: right; } 
    
    .toss-divider { height: 1px; background-color: #e5e8eb; margin: 16px 0; }
    .sub-data { font-size: 1rem; color: #8b95a1; margin-top: 4px; text-align: right; }
    
    /* 누계 전용 세로 정렬 박스 */
    .cumul-stack-box {
        background: #ffffff; border: 1px solid #e5e8eb; border-left: 6px solid #2a5298; 
        border-radius: 16px; padding: 20px 24px; margin-bottom: 16px; 
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .cumul-stack-info { display: flex; flex-direction: column; gap: 4px; }
    .cumul-stack-title { font-size: 1.25rem; color: #1e3c72; font-weight: 800; word-break: keep-all; }
    .cumul-stack-val { font-size: 1.05rem; color: #8b95a1; }
    .cumul-stack-prize { font-size: 1.6rem; color: #d9232e; font-weight: 800; text-align: right; white-space: nowrap; }
    
    /* 입력 컴포넌트 */
    div[data-testid="stTextInput"] input {
        font-size: 1.3rem !important; padding: 15px !important; height: 55px !important;
        background-color: #ffffff !important; color: #191f28 !important; border: 1px solid #e5e8eb !important; border-radius: 12px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    div[data-testid="stSelectbox"] > div { background-color: #ffffff !important; border: 1px solid #e5e8eb !important; border-radius: 12px !important; }
    div[data-testid="stSelectbox"] * { font-size: 1.1rem !important; }
    
    /* 버튼 */
    div.stButton > button[kind="primary"] {
        font-size: 1.4rem !important; font-weight: 800 !important; height: 60px !important;
        border-radius: 12px !important; background-color: rgb(128, 0, 0) !important; color: white !important; border: none !important; width: 100%; margin-top: 10px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(128, 0, 0, 0.2) !important;
    }
    
    div.stButton > button[kind="secondary"] {
        font-size: 1.2rem !important; font-weight: 700 !important; min-height: 60px !important; height: auto !important; padding: 10px !important;
        border-radius: 12px !important; background-color: #e8eaed !important; color: #191f28 !important; border: 1px solid #d1d6db !important; width: 100%; margin-top: 5px; margin-bottom: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important; white-space: normal !important; 
    }

    .del-btn-container button {
        background-color: #f2f4f6 !important; color: #dc3545 !important; border: 1px solid #dc3545 !important;
        height: 40px !important; font-size: 1rem !important; margin-top: 0 !important; box-shadow: none !important;
    }

    /* ========================================= */
    /* 🌙 다크 모드 (Dark Mode) CSS              */
    /* ========================================= */
    @media (prefers-color-scheme: dark) {
        [data-testid="stAppViewContainer"] { background-color: #121212 !important; color: #e0e
