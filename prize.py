import streamlit as st
import pandas as pd
import numpy as np
import os
import json

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

# 엑셀 사번(코드) 소수점(.0) 자동 제거용 안전 함수
def safe_str(val):
    if pd.isna(val): return ""
    s = str(val).strip()
    if s.endswith('.0'): s = s[:-2]
    return s

# --- 🎨 커스텀 CSS (버튼 색상 분리, 누계 디자인 및 모바일 최적화) ---
st.markdown("""
<style>
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

    /* 기본 구간 시책 요약 카드 (레드) */
    .summary-card { 
        background: linear-gradient(135deg, rgb(160, 20, 20) 0%, rgb(128, 0, 0) 100%); 
        border-radius: 20px; padding: 32px 24px; margin-bottom: 24px; border: none;
        box-shadow: 0 10px 25px rgba(128, 0, 0, 0.25);
    }
    
    /* 🌟 월간 누계 전용 요약 카드 (딥 네이비 파란색) 🌟 */
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
    
    .toss-card { 
        background: #ffffff; border-radius: 20px; padding: 28px 24px; 
        margin-bottom: 16px; border: 1px solid #e5e8eb; box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
    }
    .toss-title { font-size: 1.6rem; font-weight: 700; color: #191f28; margin-bottom: 6px; letter-spacing: -0.5px; }
    
    /* 시책 설명란 (설계사 화면) */
    .toss-desc { font-size: 1.15rem; color: rgb(128, 0, 0); font-weight: 800; margin-bottom: 24px; letter-spacing: -0.3px; line-height: 1.5; }
    .toss-desc-cumul { font-size: 1.15rem; color: #2a5298; font-weight: 800; margin-bottom: 24px; letter-spacing: -0.3px; line-height: 1.5; }
    
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; flex-wrap: nowrap; }
    .data-label { color: #8b95a1; font-size: 1.1rem; word-break: keep-all; }
    .data-value { color: #333d4b; font-size: 1.3rem; font-weight: 600; white-space: nowrap; }
    
    /* 상위 구간 부족 금액 강조 디자인 */
    .shortfall-row { background-color: #fff0f0; padding: 14px; border-radius: 12px; margin-top: 15px; margin-bottom: 5px; border: 2px dashed #ff4b4b; text-align: center; }
    .shortfall-text { color: #d9232e; font-size: 1.2rem; font-weight: 800; word-break: keep-all; }

    .prize-row { display: flex; justify-content: space-between; align-items: center; padding-top: 20px; margin-top: 12px; flex-wrap: nowrap; }
    .prize-label { color: #191f28; font-size: 1.3rem; font-weight: 700; word-break: keep-all; }
    .prize-value { color: rgb(128, 0, 0); font-size: 1.8rem; font-weight: 800; white-space: nowrap; text-align: right; } 
    .prize-value-cumul { color: #2a5298; font-size: 1.8rem; font-weight: 800; white-space: nowrap; text-align: right; } 
    
    .toss-divider { height: 1px; background-color: #e5e8eb; margin: 16px 0; }
    .sub-data { font-size: 1rem; color: #8b95a1; margin-top: 4px; text-align: right; }
    
    @media (max-width: 450px) {
        .summary-total { font-size: 2.1rem !important; }
        .summary-label { font-size: 1.05rem !important; }
        .prize-label { font-size: 1.1rem !important; }
        .prize-value, .prize-value-cumul { font-size: 1.45rem !important; }
        .data-label { font-size: 1rem !important; }
        .data-value { font-size: 1.15rem !important; }
        .toss-title { font-size: 1.4rem !important; }
        .shortfall-text { font-size: 1.05rem !important; }
    }
    
    div[data-testid="stTextInput"] input {
        font-size: 1.3rem !important; padding: 15px !important; height: 55px !important;
        background-color: #ffffff !important; color: #191f28 !important; border: 1px solid #e5e8eb !important; border-radius: 12px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    div[data-testid="stSelectbox"] > div { background-color: #ffffff !important; border: 1px solid #e5e8eb !important; border-radius: 12px !important; }
    div[data-testid="stSelectbox"] * { font-size: 1.1rem !important; }
    
    /* 🔴 메인 동작 버튼 (Primary) */
    div.stButton > button[kind="primary"] {
        font-size: 1.4rem !important; font-weight: 800 !important; height: 60px !important;
        border-radius: 12px !important; background-color: rgb(128, 0, 0) !important; color: white !important; border: none !important; width: 100%; margin-top: 10px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(128, 0, 0, 0.2) !important;
    }
    
    /* 📁 폴더 및 보조 버튼 (Secondary) */
    div.stButton > button[kind="secondary"] {
        font-size: 1.2rem !important; font-weight: 700 !important; min-height: 60px !important; height: auto !important; padding: 10px !important;
        border-radius: 12px !important; background-color: #e8eaed !important; color: #191f28 !important; border: 1px solid #d1d6db !important; width: 100%; margin-top: 5px; margin-bottom: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important; white-space: normal !important; 
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# ⚙️ 공통 함수 (HTML UI 렌더링 및 계산)
# ==========================================
def calculate_agent_performance(target_code):
    """설계사 코드를 기반으로 실적을 계산합니다."""
    calculated_results = []
    total_prize_sum = 0
    
    for cfg in st.session_state['config']:
        df = st.session_state['raw_data'].get(cfg['file'])
        if df is None: continue
        col_code = cfg.get('col_code', '')
        if not col_code: continue
        
        match_df = df[df[col_code].apply(safe_str) == safe_str(target_code)]
        if match_df.empty: continue
        
        p_type = cfg.get('type', '구간 시책')
        
        if "1기간" in p_type: 
            raw_prev = match_df[cfg['col_val_prev']].values[0]
            raw_curr = match_df[cfg['col_val_curr']].values[0]
            try: val_prev = float(str(raw_prev).replace(',', ''))
            except: val_prev = 0.0
            try: val_curr = float(str(raw_curr).replace(',', ''))
            except: val_curr = 0.0
            
            curr_req = float(cfg.get('curr_req', 100000.0))
            calc_rate, tier_prev, prize = 0, 0, 0
            
            if val_curr >= curr_req:
                for amt, rate in cfg['tiers']:
                    if val_prev >= amt:
                        tier_prev = amt
                        calc_rate = rate
                        prize = (tier_prev + curr_req) * (calc_rate / 100)
                        break
                        
            shortfall_curr = curr_req - val_curr if val_curr < curr_req else 0
                        
            calculated_results.append({
                "name": cfg['name'], "desc": cfg.get('desc', ''), "type": "브릿지1",
                "val_prev": val_prev, "tier_prev": tier_prev,
                "val_curr": val_curr, "curr_req": curr_req,
                "rate": calc_rate, "prize": prize, "shortfall_curr": shortfall_curr
            })
            total_prize_sum += prize
            
        elif "2기간" in p_type:
            raw_curr = match_df[cfg['col_val_curr']].values[0]
            try: val_curr = float(str(raw_curr).replace(',', ''))
            except: val_curr = 0.0
            
            curr_req = float(cfg.get('curr_req', 100000.0))
            calc_rate, tier_achieved, prize = 0, 0, 0
            
            for amt, rate in cfg['tiers']:
                if val_curr >= amt:
                    tier_achieved = amt
                    calc_rate = rate
                    break
                    
            if tier_achieved > 0:
                prize = (tier_achieved + curr_req) * (calc_rate / 100)
                
            next_tier = None
            for amt, rate in reversed(cfg['tiers']):
                if val_curr < amt:
                    next_tier = amt
                    break
            shortfall = next_tier - val_curr if next_tier else 0
            
            calculated_results.append({
                "name": cfg['name'], "desc": cfg.get('desc', ''), "type": "브릿지2",
                "val": val_curr, "tier": tier_achieved, "rate": calc_rate, "prize": prize, 
                "curr_req": curr_req, "next_tier": next_tier, "shortfall": shortfall
            })
            total_prize_sum += prize

        # 🌟 누계 데이터 처리 로직 🌟
        elif "누계" in p_type:
            col_val = cfg.get('col_val', '')
            raw_val = match_df[col_val].values[0] if col_val and col_val in match_df.columns else 0
            try: val = float(str(raw_val).replace(',', ''))
            except: val = 0.0
            
            col_prize = cfg.get('col_prize', '')
            raw_prize = match_df[col_prize].values[0] if col_prize and col_prize in match_df.columns else 0
            try: prize = float(str(raw_prize).replace(',', ''))
            except: prize = 0.0
            
            calculated_results.append({
                "name": cfg['name'], "desc": cfg.get('desc', ''), "type": "누계",
                "val": val, "prize": prize
            })
            total_prize_sum += prize

        else: 
            raw_val = match_df[cfg['col_val']].values[0]
            try: val = float(str(raw_val).replace(',', ''))
            except: val = 0.0
            
            calc_rate, tier_achieved, prize = 0, 0, 0
            for amt, rate in cfg['tiers']:
                if val >= amt:
                    tier_achieved = amt
                    calc_rate = rate
                    prize = tier_achieved * (calc_rate / 100) 
                    break
                    
            next_tier = None
            for amt, rate in reversed(cfg['tiers']):
                if val < amt:
                    next_tier = amt
                    break
            shortfall = next_tier - val if next_tier else 0
            
            calculated_results.append({
                "name": cfg['name'], "desc": cfg.get('desc', ''), "type": "구간",
                "val": val, "tier": tier_achieved, "rate": calc_rate, "prize": prize,
                "next_tier": next_tier, "shortfall": shortfall
            })
            total_prize_sum += prize
            
    return calculated_results, total_prize_sum

def render_ui_cards(user_name, calculated_results, total_prize_sum, show_share_text=False):
    """실적을 카드 형태로 예쁘게 출력하고, 카톡 복사용 텍스트를 제공합니다."""
    if len(calculated_results) == 0: return

    normal_results = [r for r in calculated_results if r['type'] != '누계']
    cumul_results = [r for r in calculated_results if r['type'] == '누계']
    
    total_normal = sum(r['prize'] for r in normal_results)
    total_cumul = sum(r['prize'] for r in cumul_results)

    share_text = f"🎯 [{user_name} 팀장님 실적 현황]\n"
    share_text += f"💰 총 합산 시상금: {total_prize_sum:,.0f}원\n"
    share_text += "────────────────\n"

    # --- 🔴 1. 진행중인 구간/브릿지 시책 요약 및 렌더링 ---
    if normal_results:
        summary_html = (
            f"<div class='summary-card'>"
            f"<div class='summary-label'>{user_name} 팀장님의 진행 중인 시책 예상 시상</div>"
            f"<div class='summary-total'>{total_normal:,.0f}원</div>"
            f"<div class='summary-divider'></div>"
        )
        
        share_text += f"📌 [진행 중인 시책]\n"
        for res in normal_results:
            if res['type'] in ["구간", "브릿지1"]:
                summary_html += (
                    f"<div class='data-row' style='padding: 6px 0;'>"
                    f"<span class='summary-item-name'>{res['name']}</span>"
                    f"<span class='summary-item-val'>{res['prize']:,.0f}원</span>"
                    f"</div>"
                )
                share_text += f"🔹 {res['name']}: {res['prize']:,.0f}원\n"
            else: 
                # 🌟 요구사항 1: 줄바꿈 및 문구 변경 (다음 달 10만 가동 조건)
                summary_html += (
                    f"<div class='data-row' style='padding: 6px 0; align-items:flex-start;'>"
                    f"<span class='summary-item-name'>{res['name']}<br><span style='font-size:0.95rem; color:rgba(255,255,255,0.7);'>(다음 달 {int(res['curr_req']//10000)}만 가동 조건)</span></span>"
                    f"<span class='summary-item-val'>{res['prize']:,.0f}원</span>"
                    f"</div>"
                )
                share_text += f"🔹 {res['name']}: {res['prize']:,.0f}원 (다음 달 {int(res['curr_req']//10000)}만 가동 조건)\n"
                
        summary_html += "</div>"
        st.markdown(summary_html, unsafe_allow_html=True)
        
        # 개별 카드 렌더링
        for res in normal_results:
            desc_html = res['desc'].replace('\n', '<br>')
            shortfall_html = ""
            
            if res.get('shortfall', 0) > 0 and res.get('next_tier'):
                shortfall_html = f"<div class='shortfall-row'><span class='shortfall-text'>🚀 다음 {int(res['next_tier']//10000)}만 구간까지 {res['shortfall']:,.0f}원 남음!</span></div>"
            elif res.get('shortfall_curr', 0) > 0 and res.get('curr_req'):
                shortfall_html = f"<div class='shortfall-row'><span class='shortfall-text'>🚨 당월 필수목표({int(res['curr_req']//10000)}만)까지 {res['shortfall_curr']:,.0f}원 부족!</span></div>"
            
            if res['type'] == "구간":
                card_html = (
                    f"<div class='toss-card'>"
                    f"<div class='toss-title'>{res['name']}</div>"
                    f"<div class='toss-desc'>{desc_html}</div>"
                    f"<div class='data-row'><span class='data-label'>현재 누적 실적</span><span class='data-value'>{res['val']:,.0f}원</span></div>"
                    f"<div class='data-row'><span class='data-label'>도달한 구간 기준</span><span class='data-value'>{res['tier']:,.0f}원</span></div>"
                    f"<div class='data-row'><span class='data-label'>적용 지급률</span><span class='data-value'>{res['rate']:g}%</span></div>"
                    f"{shortfall_html}"
                    f"<div class='toss-divider'></div>"
                    f"<div class='prize-row'>"
                    f"<span class='prize-label'>확보한 시상금</span>"
                    f"<span class='prize-value'>{res['prize']:,.0f}원</span>"
                    f"</div></div>"
                )
                share_text += f"\n[{res['name']}]\n- 현재실적: {res['val']:,.0f}원\n- 확보금액: {res['prize']:,.0f}원\n"
                if res.get('shortfall', 0) > 0: share_text += f"🚀 다음 {int(res['next_tier']//10000)}만 구간까지 {res['shortfall']:,.0f}원 남음!\n"
                
            elif res['type'] == "브릿지1":
                card_html = (
                    f"<div class='toss-card'>"
                    f"<div class='toss-title'>{res['name']}</div>"
                    f"<div class='toss-desc'>{desc_html}</div>"
                    f"<div class='data-row'>"
                    f"<span class='data-label'>전월 실적 (인정구간)</span>"
                    f"<div style='text-align:right;'>"
                    f"<div class='data-value'>{res['val_prev']:,.0f}원</div>"
                    f"<div class='sub-data'>({res['tier_prev']:,.0f}원 구간)</div>"
                    f"</div></div>"
                    f"<div class='data-row'>"
                    f"<span class='data-label'>당월 실적 (목표 {res['curr_req']:,.0f}원)</span>"
                    f"<span class='data-value'>{res['val_curr']:,.0f}원</span>"
                    f"</div>"
                    f"<div class='data-row'><span class='data-label'>적용 지급률</span><span class='data-value'>{res['rate']:g}%</span></div>"
                    f"{shortfall_html}"
                    f"<div class='toss-divider'></div>"
                    f"<div class='prize-row'>"
                    f"<span class='prize-label'>확보한 시상금</span>"
                    f"<span class='prize-value'>{res['prize']:,.0f}원</span>"
                    f"</div></div>"
                )
                share_text += f"\n[{res['name']}]\n- 당월실적: {res['val_curr']:,.0f}원\n- 확보금액: {res['prize']:,.0f}원\n"
                if res.get('shortfall_curr', 0) > 0: share_text += f"🚨 당월 목표까지 {res['shortfall_curr']:,.0f}원 부족!\n"
                
            elif res['type'] == "브릿지2":
                card_html = (
                    f"<div class='toss-card'>"
                    f"<div class='toss-title'>{res['name']}</div>"
                    f"<div class='toss-desc'>{desc_html}</div>"
                    f"<div class='data-row'><span class='data-label'>당월 누적 실적</span><span class='data-value'>{res['val']:,.0f}원</span></div>"
                    f"<div class='data-row'><span class='data-label'>확보한 구간 기준</span><span class='data-value'>{res['tier']:,.0f}원</span></div>"
                    f"<div class='data-row'><span class='data-label'>예상 적용 지급률</span><span class='data-value'>{res['rate']:g}%</span></div>"
                    f"{shortfall_html}"
                    f"<div class='toss-divider'></div>"
                    f"<div class='prize-row'>"
                    f"<span class='prize-label'>다음 달 {int(res['curr_req']//10000)}만 가동 시<br>시상금</span>"
                    f"<span class='prize-value'>{res['prize']:,.0f}원</span>"
                    f"</div></div>"
                )
                share_text += f"\n[{res['name']}]\n- 당월실적: {res['val']:,.0f}원\n- 예상시상: {res['prize']:,.0f}원 (다음 달 가동 조건)\n"
                if res.get('shortfall', 0) > 0: share_text += f"🚀 다음 {int(res['next_tier']//10000)}만 구간까지 {res['shortfall']:,.0f}원 남음!\n"
                
            st.markdown(card_html, unsafe_allow_html=True)

    # --- 🔵 2. 월간 누계 시상금 요약 및 렌더링 (파란색 섹션) ---
    if cumul_results:
        cumul_html = (
            f"<div class='cumulative-card'>"
            f"<div class='summary-label'>{user_name} 팀장님의 월간 확정(누계) 시상</div>"
            f"<div class='summary-total'>{total_cumul:,.0f}원</div>"
            f"<div class='summary-divider'></div>"
        )
        
        share_text += f"\n🏆 [월간 확정 누계 시상]\n"
        for res in cumul_results:
            cumul_html += (
                f"<div class='data-row' style='padding: 6px 0;'>"
                f"<span class='summary-item-name'>{res['name']}</span>"
                f"<span class='summary-item-val'>{res['prize']:,.0f}원</span>"
                f"</div>"
            )
            share_text += f"🔹 {res['name']}: {res['prize']:,.0f}원\n"
        cumul_html += "</div>"
        st.markdown(cumul_html, unsafe_allow_html=True)
        
        for res in cumul_results:
            desc_html = res['desc'].replace('\n', '<br>')
            val_html = f"<div class='data-row'><span class='data-label'>해당 항목 실적</span><span class='data-value'>{res['val']:,.0f}원</span></div>" if res['val'] > 0 else ""
            
            card_html = (
                f"<div class='toss-card' style='border-left: 5px solid #2a5298;'>"
                f"<div class='toss-title'>{res['name']}</div>"
                f"<div class='toss-desc-cumul'>{desc_html}</div>"
                f"{val_html}"
                f"<div class='toss-divider'></div>"
                f"<div class='prize-row'>"
                f"<span class='prize-label'>확정 누계 시상금</span>"
                f"<span class='prize-value-cumul'>{res['prize']:,.0f}원</span>"
                f"</div></div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)

    if show_share_text:
        st.markdown("<h4 style='color:#191f28; font-weight:700; margin-top:10px;'>💬 카카오톡 바로 공유하기</h4>", unsafe_allow_html=True)
        st.info("💡 아래 텍스트 박스 안의 글자를 복사해서, 해당 설계사의 카톡 창에 붙여넣기 하시면 바로 시상 내용을 보여줄 수 있습니다.")
        st.text_area("카카오톡 복사용 텍스트", value=share_text, height=350)


# ==========================================
# 📱 1. 최상단: 메뉴 선택 탭
# ==========================================
mode = st.radio("화면 선택", ["📊 내 실적 조회", "👥 매니저 관리", "⚙️ 시스템 관리자"], horizontal=True, label_visibility="collapsed")

# ==========================================
# 👥 2. 매니저 관리 페이지 
# ==========================================
if mode == "👥 매니저 관리":
    st.markdown('<div class="title-band">매니저 소속 실적 관리</div>', unsafe_allow_html=True)
    
    if 'mgr_logged_in' not in st.session_state: st.session_state.mgr_logged_in = False
    
    if not st.session_state.mgr_logged_in:
        mgr_code = st.text_input("지원매니저 사번(코드) 또는 이름을 입력하세요", type="password", placeholder="예: 12345 또는 홍길동")
        if st.button("로그인", type="primary"):
            st.session_state.mgr_logged_in = True
            st.session_state.mgr_code = mgr_code
            st.session_state.mgr_step = 'main'
            st.rerun()
    else:
        if st.button("🚪 로그아웃"):
            st.session_state.mgr_logged_in = False
            st.rerun()
        st.markdown('<br>', unsafe_allow_html=True)
        
        step = st.session_state.get('mgr_step', 'main')
        
        if step == 'main':
            st.markdown("<h3 style='color:#191f28; font-weight:800; font-size:1.3rem; margin-bottom: 15px;'>어떤 실적을 확인하시겠습니까?</h3>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📁 구간실적 관리", use_container_width=True):
                    st.session_state.mgr_step = 'tiers'
                    st.session_state.mgr_category = '구간'
                    st.rerun()
            with col2:
                if st.button("📁 브릿지실적 관리", use_container_width=True):
                    st.session_state.mgr_step = 'tiers'
                    st.session_state.mgr_category = '브릿지'
                    st.rerun()
                
        elif step == 'tiers':
            if st.button("⬅️ 뒤로가기", use_container_width=False):
                st.session_state.mgr_step = 'main'
                st.rerun()
            
            cat = st.session_state.mgr_category
            st.markdown(f"<h3 style='color:#191f28; font-weight:800; font-size:1.3rem; margin-bottom: 15px;'>📁 {cat}실적 근접자 조회</h3>", unsafe_allow_html=True)
            
            agents = {}
            for cfg in st.session_state['config']:
                mgr_col = cfg.get('col_manager', '')
                if not mgr_col: continue
                df = st.session_state['raw_data'].get(cfg['file'])
                if df is None: continue
                
                match_df = df[df[mgr_col].apply(safe_str) == safe_str(st.session_state.mgr_code)]
                for _, row in match_df.iterrows():
                    code = safe_str(row.get(cfg.get('col_code', '')))
                    if code: agents[code] = True
            
            ranges = {
                500000: (400000, 500000),
                300000: (200000, 300000),
                200000: (100000, 200000),
                100000: (0, 100000)
            }
            counts = {500000: 0, 300000: 0, 200000: 0, 100000: 0}
            
            if agents:
                for code in agents.keys():
                    calc_results, _ = calculate_agent_performance(code)
                    for res in calc_results:
                        if cat == "구간" and res['type'] != "구간": continue
                        if cat == "브릿지" and "브릿지" not in res['type']: continue
                        if res['type'] == "누계": continue
                        
                        val = res.get('val') if res['type'] in ['구간', '브릿지2'] else res.get('val_curr')
                        for t, (min_v, max_v) in ranges.items():
                            if min_v <= val < max_v:
                                counts[t] += 1
                                break
            
            for t, (min_v, max_v) in ranges.items():
                count = counts[t]
                if st.button(f"📁 {int(t//10000)}만 구간 근접자 ({int(min_v//10000)}만 이상 ~ {int(max_v//10000)}만 미만) - 총 {count}명", use_container_width=True, key=f"t_{t}"):
                    st.session_state.mgr_step = 'list'
                    st.session_state.mgr_target = t
                    st.session_state.mgr_min_v = min_v
                    st.session_state.mgr_max_v = max_v
                    st.rerun()
                
        elif step == 'list':
            if st.button("⬅️ 폴더로 돌아가기", use_container_width=False):
                st.session_state.mgr_step = 'tiers'
                st.rerun()
            
            cat = st.session_state.mgr_category
            target = st.session_state.mgr_target
            min_v = st.session_state.mgr_min_v
            max_v = st.session_state.mgr_max_v
            
            st.markdown(f"<h3 style='color:#191f28; font-weight:800; font-size:1.3rem;'>👥 {int(target//10000)}만 구간 근접자 명단</h3>", unsafe_allow_html=True)
            st.info("💡 이름을 클릭하면 상세 실적을 확인하고 카톡으로 전송할 수 있습니다.")
            
            agents = {}
            for cfg in st.session_state['config']:
                mgr_col = cfg.get('col_manager', '')
                if not mgr_col: continue
                df = st.session_state['raw_data'].get(cfg['file'])
                if df is None: continue
                
                match_df = df[df[mgr_col].apply(safe_str) == safe_str(st.session_state.mgr_code)]
                for _, row in match_df.iterrows():
                    code = safe_str(row.get(cfg.get('col_code', '')))
                    name = safe_str(row.get(cfg.get('col_name', '')))
                    agency = safe_str(row.get(cfg.get('col_agency', '')))
                    if not agency: agency = safe_str(row.get(cfg.get('col_branch', '')))
                    if code and name: agents[code] = {"name": name, "agency": agency}
            
            if not agents:
                st.error("⚠️ 소속된 설계사가 없거나 매니저 정보가 일치하지 않습니다.")
            else:
                near_agents = []
                for code, info in agents.items():
                    name = info['name']
                    agency = info['agency']
                    calc_results, _ = calculate_agent_performance(code)
                    
                    for res in calc_results:
                        if cat == "구간" and res['type'] != "구간": continue
                        if cat == "브릿지" and "브릿지" not in res['type']: continue
                        if res['type'] == "누계": continue
                        
                        val = res.get('val') if res['type'] in ['구간', '브릿지2'] else res.get('val_curr')
                        if min_v <= val < max_v:
                            near_agents.append((code, name, agency, val))
                            break
                
                if not near_agents:
                    st.info(f"해당 구간({int(target//10000)}만)에 근접한 소속 설계사가 없습니다.")
                else:
                    near_agents.sort(key=lambda x: (x[2], x[1]))
                    for code, name, agency, val in near_agents:
                        display_text = f"👤 [{agency}] {name} 설계사님 (현재 {val:,.0f}원)"
                        if st.button(display_text, use_container_width=True, key=f"btn_{code}"):
                            st.session_state.mgr_selected_code = code
                            st.session_state.mgr_selected_name = f"[{agency}] {name}"
                            st.session_state.mgr_step = 'detail'
                            st.rerun()

        elif step == 'detail':
            if st.button("⬅️ 명단으로 돌아가기", use_container_width=False):
                st.session_state.mgr_step = 'list'
                st.rerun()
            
            code = st.session_state.mgr_selected_code
            name = st.session_state.mgr_selected_name
            cat = st.session_state.mgr_category
            
            st.markdown(f"<div style='background:#ffffff; padding:20px; border-radius:20px; border:2px solid #e5e8eb; margin-top:10px; margin-bottom:30px;'>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color:#3182f6; font-weight:800; font-size:1.5rem; margin-top:0; text-align:center;'>👤 {name} 설계사님 ({cat} 상세)</h4>", unsafe_allow_html=True)
            
            calc_results, total_prize = calculate_agent_performance(code)
            render_ui_cards(name, calc_results, total_prize, show_share_text=True)
            
            user_leaflet_path = os.path.join(DATA_DIR, "leaflet.png")
            if os.path.exists(user_leaflet_path):
                st.image(user_leaflet_path, use_container_width=True)
                
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 🔒 3. 시스템 관리자 모드
# ==========================================
elif mode == "⚙️ 시스템 관리자":
    st.markdown("<h2 style='color:#191f28; font-weight:800; font-size:1.8rem; margin-top: 20px;'>관리자 설정</h2>", unsafe_allow_html=True)
    
    admin_pw = st.text_input("관리자 비밀번호를 입력하세요", type="password")
    if admin_pw != "meritz0085":
        if admin_pw: st.error("비밀번호가 일치하지 않습니다.")
        st.stop()
        
    st.success("인증 성공! 변경 사항은 가장 아래 [서버에 반영하기] 버튼을 눌러야 저장됩니다.")
    
    st.markdown("<h3 style='color:#191f28; font-size:1.4rem; margin-top:30px;'>📂 1. 실적 파일 업로드 및 관리</h3>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("CSV/엑셀 파일 업로드", accept_multiple_files=True, type=['csv', 'xlsx'])
    
    if uploaded_files:
        new_upload = False
        for file in uploaded_files:
            if file.name not in st.session_state['raw_data']:
                if file.name.endswith('.csv'):
                    try: df = pd.read_csv(file)
                    except:
                        file.seek(0)
                        try: df = pd.read_csv(file, sep='\t')
                        except:
                            file.seek(0)
                            try: df = pd.read_csv(file, encoding='cp949')
                            except:
                                file.seek(0)
                                df = pd.read_csv(file, sep='\t', encoding='cp949')
                else: df = pd.read_excel(file)
                
                st.session_state['raw_data'][file.name] = df
                df.to_pickle(os.path.join(DATA_DIR, f"{file.name}.pkl"))
                new_upload = True
                
        if new_upload:
            st.success("✅ 파일 업로드 및 저장이 완료되었습니다.")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([7, 3])
    with col1:
        st.markdown(f"**현재 저장된 파일 ({len(st.session_state['raw_data'])}개)**")
    with col2:
        if st.button("🗑️ 전체 파일 삭제", use_container_width=True):
            st.session_state['raw_data'].clear()
            for f in os.listdir(DATA_DIR):
                if f.endswith('.pkl'): os.remove(os.path.join(DATA_DIR, f))
            st.rerun()
        
    st.divider()
    
    if not st.session_state['raw_data']:
        st.info("현재 업로드된 파일이 없습니다. 위에 파일을 추가해주세요.")
    else:
        for file_name in list(st.session_state['raw_data'].keys()):
            col_name, col_btn = st.columns([8, 2])
            with col_name: st.write(f"📄 {file_name}")
            with col_btn:
                if st.button("개별 삭제", key=f"del_file_{file_name}", use_container_width=True):
                    del st.session_state['raw_data'][file_name]
                    pkl_path = os.path.join(DATA_DIR, f"{file_name}.pkl")
                    if os.path.exists(pkl_path): os.remove(pkl_path)
                    st.rerun()
            st.markdown("<hr style='margin:10px 0; opacity:0.3;'>", unsafe_allow_html=True)

    st.markdown("<h3 style='color:#191f28; font-size:1.4rem; margin-top:30px;'>🏆 2. 시상(시책) 항목 추가 및 관리</h3>", unsafe_allow_html=True)
    
    col_add, col_del_all = st.columns(2)
    with col_add:
        if st.button("➕ 신규 시상 항목 추가", type="primary", use_container_width=True):
            if not st.session_state['raw_data']:
                st.error("⚠️ 먼저 실적 파일을 1개 이상 업로드해야 시상을 추가할 수 있습니다.")
            else:
                first_file = list(st.session_state['raw_data'].keys())[0]
                st.session_state['config'].append({
                    "name": f"신규 시책 {len(st.session_state['config'])+1}",
                    "desc": "", "type": "구간 시책", 
                    "file": first_file, "col_name": "", "col_code": "", "col_branch": "", "col_agency": "", "col_manager": "",
                    "col_val": "", "col_val_prev": "", "col_val_curr": "", "col_prize": "", "curr_req": 100000.0,
                    "tiers": [(100000, 100), (200000, 200), (300000, 200), (500000, 300)]
                })
                st.rerun()
                
    with col_del_all:
        if st.button("🗑️ 모든 시상 항목 일괄 삭제", use_container_width=True):
            st.session_state['config'].clear()
            with open(os.path.join(DATA_DIR, 'config.json'), 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
            st.rerun()

    if not st.session_state['config']:
        st.info("현재 설정된 시상 항목이 없습니다. [➕ 신규 시상 항목 추가] 버튼을 눌러주세요.")

    for i, cfg in enumerate(st.session_state['config']):
        if 'desc' not in cfg: cfg['desc'] = ""
        if 'type' not in cfg: cfg['type'] = "구간 시책"
        if 'col_code' not in cfg: cfg['col_code'] = ""
        if 'col_branch' not in cfg: cfg['col_branch'] = cfg.get('col_phone', '') 
        if 'col_agency' not in cfg: cfg['col_agency'] = ""
        if 'col_manager' not in cfg: cfg['col_manager'] = ""
        if 'col_val_prev' not in cfg: cfg['col_val_prev'] = ""
        if 'col_val_curr' not in cfg: cfg['col_val_curr'] = ""
        if 'col_prize' not in cfg: cfg['col_prize'] = ""
        if 'curr_req' not in cfg: cfg['curr_req'] = 100000.0

        st.divider()
        
        c_title, c_del = st.columns([8, 2])
        with c_title:
            st.markdown(f"<h3 style='color:#191f28; font-size:1.3rem; margin:0;'>📌 {cfg['name']} 설정</h3>", unsafe_allow_html=True)
        with c_del:
            if st.button("개별 삭제", key=f"del_cfg_{i}", use_container_width=True):
                st.session_state['config'].pop(i)
                with open(os.path.join(DATA_DIR, 'config.json'), 'w', encoding='utf-8') as f:
                    json.dump(st.session_state['config'], f, ensure_ascii=False)
                st.rerun()
        
        cfg['name'] = st.text_input(f"시책명", value=cfg['name'], key=f"name_{i}")
        
        # 🌟 요구사항 2: 시책 설명란 다중 줄바꿈 지원 🌟
        cfg['desc'] = st.text_area("시책 설명 (적용 기간 등)", value=cfg.get('desc', ''), placeholder="예: 2/1 ~ 2/15 인보험 적용\n(엔터를 쳐서 문단을 나눌 수 있습니다)", key=f"desc_{i}", height=100)
        
        idx = 0
        if "1기간" in cfg['type']: idx = 1
        elif "2기간" in cfg['type']: idx = 2
        elif "누계" in cfg['type']: idx = 3
            
        # 🌟 요구사항 3: 누계 시상 항목 라디오 버튼 추가 🌟
        cfg['type'] = st.radio("시책 종류 선택", ["구간 시책", "브릿지 시책 (1기간: 시상 확정)", "브릿지 시책 (2기간: 차월 달성 조건)", "월간 누계 (확정 시상 불러오기)"], 
                               index=idx, horizontal=True, key=f"type_{i}")
        
        col1, col2 = st.columns(2)
        with col1:
            file_opts = list(st.session_state['raw_data'].keys())
            if not file_opts:
                st.error("파일이 모두 삭제되어 항목을 설정할 수 없습니다. 파일을 다시 업로드해주세요.")
                continue
                
            cfg['file'] = st.selectbox(f"대상 파일", file_opts, index=file_opts.index(cfg['file']) if cfg['file'] in file_opts else 0, key=f"file_{i}")
            cols = st.session_state['raw_data'][cfg['file']].columns.tolist()
            def get_idx(val, opts): return opts.index(val) if val in opts else 0

            st.info("💡 식별을 위해 아래 5개 컬럼을 정확히 지정해주세요.")
            cfg['col_name'] = st.selectbox("성명 컬럼", cols, index=get_idx(cfg['col_name'], cols), key=f"cname_{i}")
            cfg['col_branch'] = st.selectbox("지점명(조직) 컬럼", cols, index=get_idx(cfg['col_branch'], cols), key=f"cbranch_{i}")
            cfg['col_agency'] = st.selectbox("대리점/지사명 컬럼 (명단 표시용)", cols, index=get_idx(cfg['col_agency'], cols), key=f"cagency_{i}")
            cfg['col_code'] = st.selectbox("설계사코드(사번) 컬럼", cols, index=get_idx(cfg['col_code'], cols), key=f"ccode_{i}")
            cfg['col_manager'] = st.selectbox("매니저코드(비번) 컬럼 (매니저 화면용)", cols, index=get_idx(cfg['col_manager'], cols), key=f"cmgr_{i}")
            
            if "1기간" in cfg['type']:
                cfg['col_val_prev'] = st.selectbox("전월 실적 컬럼", cols, index=get_idx(cfg['col_val_prev'], cols), key=f"cvalp_{i}")
                cfg['col_val_curr'] = st.selectbox("당월 실적 컬럼", cols, index=get_idx(cfg['col_val_curr'], cols), key=f"cvalc_{i}")
                cfg['curr_req'] = st.number_input("당월 필수 달성 조건 금액", value=float(cfg['curr_req']), step=10000.0, key=f"creq_{i}")
            elif "2기간" in cfg['type']:
                col_key = 'col_val_curr'
                cfg[col_key] = st.selectbox("당월 실적 수치 컬럼", cols, index=get_idx(cfg.get(col_key, ''), cols), key=f"cval_{i}")
                cfg['curr_req'] = st.number_input("차월 필수 달성 조건 금액 (합산용)", value=float(cfg.get('curr_req', 100000.0)), step=10000.0, key=f"creq_{i}")
            elif "누계" in cfg['type']:
                cfg['col_val'] = st.selectbox("해당 항목 실적 컬럼 (선택사항, 금액이 없으면 성명 컬럼 지정)", cols, index=get_idx(cfg.get('col_val', ''), cols), key=f"cval_{i}")
                cfg['col_prize'] = st.selectbox("해당 항목 확정 시상금(금액) 컬럼", cols, index=get_idx(cfg.get('col_prize', ''), cols), key=f"cprize_{i}")
            else: 
                col_key = 'col_val'
                cfg[col_key] = st.selectbox("실적 수치 컬럼", cols, index=get_idx(cfg.get(col_key, ''), cols), key=f"cval_{i}")

        with col2:
            if "1기간" in cfg['type']: st.write("📈 전월 구간 설정 (전월구간금액,지급률%)")
            elif "누계" in cfg['type']: st.write("✅ 누계 확정 항목은 구간 설정이 필요 없습니다.")
            else: st.write("📈 당월 구간 설정 (달성구간금액,지급률%)")
            
            if "누계" not in cfg['type']:
                tier_str = "\n".join([f"{int(t[0])},{int(t[1])}" for t in cfg['tiers']])
                tier_input = st.text_area("엔터로 줄바꿈", value=tier_str, height=150, key=f"tier_{i}")
                try:
                    new_tiers = []
                    for line in tier_input.strip().split('\n'):
                        if ',' in line:
                            parts = line.split(',')
                            new_tiers.append((float(parts[0].strip()), float(parts[1].strip())))
                    cfg['tiers'] = sorted(new_tiers, key=lambda x: x[0], reverse=True)
                except:
                    st.error("형식이 올바르지 않습니다.")

    st.divider()
    st.markdown("<h3 style='color:#191f28; font-size:1.4rem; margin-top:10px;'>🖼️ 3. 안내 리플렛(이미지) 등록</h3>", unsafe_allow_html=True)
    st.info("💡 실적 조회 결과 맨 아래에 보여줄 상품 안내장이나 리플렛 이미지를 등록할 수 있습니다.")
    
    leaflet_file = st.file_uploader("리플렛 이미지 업로드 (JPG, PNG)", type=['jpg', 'jpeg', 'png'])
    if leaflet_file:
        with open(os.path.join(DATA_DIR, "leaflet.png"), "wb") as f:
            f.write(leaflet_file.getbuffer())
        st.success("✅ 리플렛 이미지가 저장되었습니다!")
        st.rerun()

    leaflet_path = os.path.join(DATA_DIR, "leaflet.png")
    if os.path.exists(leaflet_path):
        st.markdown("<p style='color:#333d4b; font-weight:600;'>현재 등록된 리플렛 이미지:</p>", unsafe_allow_html=True)
        st.image(leaflet_path, width=250)
        
        if st.button("🗑️ 등록된 리플렛 삭제", use_container_width=False):
            os.remove(leaflet_path)
            st.rerun()

    if st.session_state['config']:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ 모든 설정 완료 및 서버에 반영하기", type="primary", use_container_width=True):
            with open(os.path.join(DATA_DIR, 'config.json'), 'w', encoding='utf-8') as f:
                json.dump(st.session_state['config'], f, ensure_ascii=False)
            st.success("✅ 서버에 영구 반영되었습니다! 이제 조회 화면에서 확인 가능합니다.")

# ==========================================
# 🏆 4. 사용자 모드 (일반 설계사)
# ==========================================
else:
    st.markdown('<div class="title-band">메리츠화재 시상 현황</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#191f28; font-weight:800; font-size:1.3rem; margin-bottom: 15px;'>이름과 지점별 코드를 입력하세요.</h3>", unsafe_allow_html=True)
    
    user_name = st.text_input("본인 이름을 입력하세요", placeholder="예: 홍길동")
    branch_code_input = st.text_input("지점별 코드", placeholder="예: 1지점은 1, 11지점은 11 입력")

    codes_found = set()
    needs_disambiguation = False

    if user_name and branch_code_input:
        for i, cfg in enumerate(st.session_state['config']):
            df = st.session_state['raw_data'].get(cfg['file'])
            if df is not None:
                search_name = df[cfg['col_name']].fillna('').astype(str).str.strip()
                name_match_condition = (search_name == user_name.strip())
                
                if branch_code_input.strip() == "0000": 
                    match = df[name_match_condition]
                else:
                    clean_code = branch_code_input.replace("지점", "").strip()
                    if clean_code:
                        search_branch = df[cfg['col_branch']].fillna('').astype(str)
                        regex_pattern = rf"(?<!\d){clean_code}\s*지점"
                        match = df[name_match_condition & search_branch.str.contains(regex_pattern, regex=True)]
                    else:
                        match = pd.DataFrame()
                
                if not match.empty:
                    if 'col_code' in cfg and cfg['col_code']:
                        for _, row in match.iterrows():
                            agent_code = safe_str(row[cfg['col_code']])
                            if agent_code: codes_found.add(agent_code)

    codes_found = {c for c in codes_found if c}
    
    selected_code = None
    if len(codes_found) > 1:
        st.warning("⚠️ 동일한 이름과 지점을 가진 분이 존재합니다. 본인의 설계사코드(사번)를 선택해주세요.")
        selected_code = st.selectbox("나의 설계사코드 선택", sorted(list(codes_found)))
        needs_disambiguation = True

    if st.button("내 실적 확인하기", type="primary"):
        if not user_name or not branch_code_input:
            st.warning("이름과 지점코드를 입력해주세요.")
        elif not st.session_state['config']:
            st.warning("현재 진행 중인 시책 데이터가 없습니다.")
        elif not codes_found:
            st.error("일치하는 정보가 없습니다. 이름과 지점코드를 다시 확인해주세요.")
        else:
            final_target_code = selected_code if needs_disambiguation else list(codes_found)[0]
            
            calc_results, total_prize = calculate_agent_performance(final_target_code)
            
            if calc_results:
                render_ui_cards(user_name, calc_results, total_prize, show_share_text=False)
                
                user_leaflet_path = os.path.join(DATA_DIR, "leaflet.png")
                if os.path.exists(user_leaflet_path):
                    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
                    st.image(user_leaflet_path, use_container_width=True)
            else:
                st.error("해당 조건의 실적 데이터가 없습니다.")
