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

# 기존 데이터 호환성 보장
for c in st.session_state['config']:
    if 'category' not in c:
        c['category'] = 'weekly'

# 엑셀 사번(코드) 소수점(.0) 자동 제거용 안전 함수
def safe_str(val):
    if pd.isna(val): return ""
    s = str(val).strip()
    if s.endswith('.0'): s = s[:-2]
    return s

# --- 🎨 커스텀 CSS (라이트/다크모드 완벽 대응) ---
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

    .admin-title { color: #191f28; font-weight: 800; font-size: 1.8rem; margin-top: 20px; }
    .sub-title { color: #191f28; font-size: 1.4rem; margin-top: 30px; font-weight: 700; }
    .config-title { color: #191f28; font-size: 1.3rem; margin: 0; font-weight: 700; }
    .main-title { color: #191f28; font-weight: 800; font-size: 1.3rem; margin-bottom: 15px; }
    .blue-title { color: #1e3c72; font-size: 1.4rem; margin-top: 10px; font-weight: 800; }
    .agent-title { color: #3182f6; font-weight: 800; font-size: 1.5rem; margin-top: 0; text-align: center; }

    .config-box { background: #f9fafb; padding: 15px; border-radius: 15px; border: 1px solid #e5e8eb; margin-top: 15px; }
    .config-box-blue { background: #f0f4f8; padding: 15px; border-radius: 15px; border: 1px solid #c7d2fe; margin-top: 15px; }
    .detail-box { background: #ffffff; padding: 20px; border-radius: 20px; border: 2px solid #e5e8eb; margin-top: 10px; margin-bottom: 30px; }

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
    
    .toss-card { 
        background: #ffffff; border-radius: 20px; padding: 28px 24px; 
        margin-bottom: 16px; border: 1px solid #e5e8eb; box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
    }
    .toss-title { font-size: 1.6rem; font-weight: 700; color: #191f28; margin-bottom: 6px; letter-spacing: -0.5px; }
    .toss-desc { font-size: 1.15rem; color: rgb(128, 0, 0); font-weight: 800; margin-bottom: 24px; letter-spacing: -0.3px; line-height: 1.4; word-break: keep-all; }
    
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; flex-wrap: nowrap; }
    .data-label { color: #8b95a1; font-size: 1.1rem; word-break: keep-all; }
    .data-value { color: #333d4b; font-size: 1.3rem; font-weight: 600; white-space: nowrap; }
    
    .shortfall-row { background-color: #fff0f0; padding: 14px; border-radius: 12px; margin-top: 15px; margin-bottom: 5px; border: 2px dashed #ff4b4b; text-align: center; }
    .shortfall-text { color: #d9232e; font-size: 1.2rem; font-weight: 800; word-break: keep-all; }

    .prize-row { display: flex; justify-content: space-between; align-items: center; padding-top: 20px; margin-top: 12px; flex-wrap: nowrap; }
    .prize-label { color: #191f28; font-size: 1.3rem; font-weight: 700; word-break: keep-all; white-space: nowrap; }
    .prize-value { color: rgb(128, 0, 0); font-size: 1.8rem; font-weight: 800; white-space: nowrap; text-align: right; } 
    
    .toss-divider { height: 1px; background-color: #e5e8eb; margin: 16px 0; }
    .sub-data { font-size: 1rem; color: #8b95a1; margin-top: 4px; text-align: right; }
    
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
    
    div[data-testid="stTextInput"] input {
        font-size: 1.3rem !important; padding: 15px !important; height: 55px !important;
        background-color: #ffffff !important; color: #191f28 !important; border: 1px solid #e5e8eb !important; border-radius: 12px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    
    div.stButton > button[kind="primary"] {
        font-size: 1.4rem !important; font-weight: 800 !important; height: 60px !important;
        border-radius: 12px !important; background-color: rgb(128, 0, 0) !important; color: white !important; border: none !important; width: 100%; margin-top: 10px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(128, 0, 0, 0.2) !important;
    }
    
    div.stButton > button[kind="secondary"] {
        font-size: 1.2rem !important; font-weight: 700 !important; min-height: 60px !important; height: auto !important; padding: 10px !important;
        border-radius: 12px !important; background-color: #e8eaed !important; color: #191f28 !important; border: 1px solid #d1d6db !important; width: 100%; margin-top: 5px; margin-bottom: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important; white-space: normal !important; 
    }

    @media (prefers-color-scheme: dark) {
        [data-testid="stAppViewContainer"] { background-color: #121212 !important; color: #e0e0e0 !important; }
        div[data-testid="stRadio"] > div { background-color: #1e1e1e !important; border-color: #333 !important; }
        .admin-title, .sub-title, .config-title, .main-title { color: #ffffff !important; }
        .config-box { background-color: #1a1a1a !important; border-color: #333 !important; }
        .toss-card { background-color: #1e1e1e !important; border-color: #333 !important; }
        .toss-title, .data-value, .prize-label { color: #ffffff !important; }
        div[data-testid="stTextInput"] input { background-color: #1e1e1e !important; color: #ffffff !important; border-color: #444 !important; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# ⚙️ 공통 함수 (HTML UI 렌더링 및 계산)
# ==========================================
def calculate_agent_performance(target_code):
    calculated_results = []
    target_code_str = safe_str(target_code)
    
    for cfg in st.session_state['config']:
        df = st.session_state['raw_data'].get(cfg['file'])
        if df is None: continue
        col_code = cfg.get('col_code', '')
        if not col_code: continue
        
        # 사번 매칭 시 데이터 타입 불일치 방지
        match_df = df[df[col_code].apply(safe_str) == target_code_str]
        if match_df.empty: continue
        
        cat = cfg.get('category', 'weekly')
        p_type = cfg.get('type', '구간 시책')
        
        if cat == 'weekly':
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
                    "name": cfg['name'], "desc": cfg.get('desc', ''), "category": "weekly", "type": "브릿지1",
                    "val_prev": val_prev, "tier_prev": tier_prev,
                    "val_curr": val_curr, "curr_req": curr_req,
                    "rate": calc_rate, "prize": prize, "shortfall_curr": shortfall_curr
                })
                
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
                    "name": cfg['name'], "desc": cfg.get('desc', ''), "category": "weekly", "type": "브릿지2",
                    "val": val_curr, "tier": tier_achieved, "rate": calc_rate, "prize": prize, 
                    "curr_req": curr_req, "next_tier": next_tier, "shortfall": shortfall
                })

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
                    "name": cfg['name'], "desc": cfg.get('desc', ''), "category": "weekly", "type": "구간",
                    "val": val, "tier": tier_achieved, "rate": calc_rate, "prize": prize,
                    "next_tier": next_tier, "shortfall": shortfall
                })
        
        elif cat == 'cumulative':
            col_val = cfg.get('col_val', '')
            raw_val = match_df[col_val].values[0] if col_val and col_val in match_df.columns else 0
            try: val = float(str(raw_val).replace(',', ''))
            except: val = 0.0
            
            col_prize = cfg.get('col_prize', '')
            raw_prize = match_df[col_prize].values[0] if col_prize and col_prize in match_df.columns else 0
            try: prize = float(str(raw_prize).replace(',', ''))
            except: prize = 0.0
            
            calculated_results.append({
                "name": cfg['name'], "desc": cfg.get('desc', ''), "category": "cumulative", "type": "누계",
                "val": val, "prize": prize
            })
            
    total_prize_sum = sum(r['prize'] for r in calculated_results)
    return calculated_results, total_prize_sum

def render_ui_cards(user_name, calculated_results, total_prize_sum, show_share_text=False):
    if len(calculated_results) == 0: return

    weekly_res = [r for r in calculated_results if r['category'] == 'weekly']
    cumul_res = [r for r in calculated_results if r['category'] == 'cumulative']
    
    weekly_total = sum(r['prize'] for r in weekly_res)
    cumul_total = sum(r['prize'] for r in cumul_res)

    share_text = f"🎯 [{user_name} 팀장님 실적 현황]\n"
    share_text += f"💰 총 합산 시상금: {total_prize_sum:,.0f}원\n"
    share_text += "────────────────\n"

    if weekly_res:
        summary_html = (
            f"<div class='summary-card'>"
            f"<div class='summary-label'>{user_name} 팀장님의 진행 중인 시책 예상 시상</div>"
            f"<div class='summary-total'>{weekly_total:,.0f}원</div>"
            f"<div class='summary-divider'></div>"
        )
        share_text += f"📌 [진행 중인 시책]\n"
        
        for res in weekly_res:
            summary_html += f"<div class='data-row' style='padding: 6px 0;'><span class='summary-item-name'>{res['name']}</span><span class='summary-item-val'>{res['prize']:,.0f}원</span></div>"
            share_text += f"🔹 {res['name']}: {res['prize']:,.0f}원\n"
                
        summary_html += "</div>"
        st.markdown(summary_html, unsafe_allow_html=True)
        
        for res in weekly_res:
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
                    f"<div class='prize-row'><span class='prize-label'>확보한 시상금</span><span class='prize-value'>{res['prize']:,.0f}원</span></div>"
                    f"</div>"
                )
            elif "브릿지" in res['type']:
                v_curr = res.get('val_curr') if 'val_curr' in res else res.get('val', 0)
                card_html = (
                    f"<div class='toss-card'>"
                    f"<div class='toss-title'>{res['name']}</div>"
                    f"<div class='toss-desc'>{desc_html}</div>"
                    f"<div class='data-row'><span class='data-label'>당월 실적</span><span class='data-value'>{v_curr:,.0f}원</span></div>"
                    f"{shortfall_html}"
                    f"<div class='toss-divider'></div>"
                    f"<div class='prize-row'><span class='prize-label'>예상 시상금</span><span class='prize-value'>{res['prize']:,.0f}원</span></div>"
                    f"</div>"
                )
            st.markdown(card_html, unsafe_allow_html=True)

    if show_share_text:
        st.text_area("카카오톡 복사용 텍스트", value=share_text, height=200)

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
        with st.form("mgr_login"):
            mgr_code_input = st.text_input("지원매니저 사번(코드)를 입력하세요", type="password")
            if st.form_submit_button("로그인", type="primary"):
                if mgr_code_input:
                    st.session_state.mgr_logged_in = True
                    st.session_state.mgr_code = safe_str(mgr_code_input)
                    st.session_state.mgr_step = 'main'
                    st.rerun()
    else:
        if st.button("🚪 로그아웃"):
            st.session_state.mgr_logged_in = False
            st.rerun()
        
        step = st.session_state.get('mgr_step', 'main')
        
        if step == 'main':
            st.markdown("<h3 class='main-title'>어떤 실적을 확인하시겠습니까?</h3>", unsafe_allow_html=True)
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
            if st.button("⬅️ 뒤로가기"):
                st.session_state.mgr_step = 'main'
                st.rerun()
            
            cat_name = st.session_state.mgr_category
            st.markdown(f"<h3 class='main-title'>📁 {cat_name}실적 근접자 조회</h3>", unsafe_allow_html=True)
            
            # 매니저 소속 설계사 찾기
            agents = {}
            for cfg in st.session_state['config']:
                mgr_col = cfg.get('col_manager', '')
                if not mgr_col: continue
                df = st.session_state['raw_data'].get(cfg['file'])
                if df is None: continue
                
                # 매니저 사번 일치 여부를 safe_str로 엄격히 비교
                match_df = df[df[mgr_col].apply(safe_str) == st.session_state.mgr_code]
                for _, row in match_df.iterrows():
                    a_code = safe_str(row.get(cfg.get('col_code', '')))
                    if a_code: agents[a_code] = True
            
            ranges = {500000: (400000, 500000), 300000: (200000, 300000), 200000: (100000, 200000), 100000: (0, 100000)}
            counts = {500000: 0, 300000: 0, 200000: 0, 100000: 0}
            
            if agents:
                for a_code in agents.keys():
                    res_list, _ = calculate_agent_performance(a_code)
                    for r in res_list:
                        # 관리자 설정에 따른 타입 필터링
                        is_bridge = "브릿지" in r['type']
                        if cat_name == "구간" and is_bridge: continue
                        if cat_name == "브릿지" and not is_bridge: continue
                        if r['category'] == 'cumulative': continue
                        
                        val = r.get('val') if r['type'] in ['구간', '브릿지2'] else r.get('val_curr', 0)
                        for t, (min_v, max_v) in ranges.items():
                            if min_v <= val < max_v:
                                counts[t] += 1
                                break
            
            for t, (min_v, max_v) in ranges.items():
                if st.button(f"📁 {int(t//10000)}만 구간 근접자 ({int(min_v//10000)}만~{int(max_v//10000)}만) - 총 {counts[t]}명", use_container_width=True):
                    st.session_state.mgr_step = 'list'
                    st.session_state.mgr_target = t
                    st.session_state.mgr_min_v = min_v
                    st.session_state.mgr_max_v = max_v
                    st.rerun()

        elif step == 'list':
            if st.button("⬅️ 폴더로 돌아가기"):
                st.session_state.mgr_step = 'tiers'
                st.rerun()
            
            # 리스트 로직 (생략 없이 동일하게 보강)
            target = st.session_state.mgr_target
            st.markdown(f"### 👥 {int(target//10000)}만 구간 근접 명단")
            
            near_agents = []
            all_agents_info = {}
            for cfg in st.session_state['config']:
                mgr_col = cfg.get('col_manager', '')
                if not mgr_col: continue
                df = st.session_state['raw_data'].get(cfg['file'])
                if df is None: continue
                match_df = df[df[mgr_col].apply(safe_str) == st.session_state.mgr_code]
                for _, row in match_df.iterrows():
                    c = safe_str(row.get(cfg.get('col_code', '')))
                    n = safe_str(row.get(cfg.get('col_name', '')))
                    a = safe_str(row.get(cfg.get('col_agency', ''))) or safe_str(row.get(cfg.get('col_branch', '')))
                    if c: all_agents_info[c] = {"name": n, "agency": a}

            for c, info in all_agents_info.items():
                res_list, _ = calculate_agent_performance(c)
                for r in res_list:
                    is_bridge = "브릿지" in r['type']
                    if st.session_state.mgr_category == "구간" and is_bridge: continue
                    if st.session_state.mgr_category == "브릿지" and not is_bridge: continue
                    
                    val = r.get('val') if r['type'] in ['구간', '브릿지2'] else r.get('val_curr', 0)
                    if st.session_state.mgr_min_v <= val < st.session_state.mgr_max_v:
                        near_agents.append((c, info['name'], info['agency'], val))
                        break
            
            for c, n, a, v in near_agents:
                if st.button(f"👤 [{a}] {n} 설계사 (현재 {v:,.0f}원)", key=f"list_{c}", use_container_width=True):
                    st.session_state.mgr_selected_code = c
                    st.session_state.mgr_selected_name = f"[{a}] {n}"
                    st.session_state.mgr_step = 'detail'
                    st.rerun()

        elif step == 'detail':
            if st.button("⬅️ 명단으로 돌아가기"):
                st.session_state.mgr_step = 'list'
                st.rerun()
            code = st.session_state.mgr_selected_code
            name = st.session_state.mgr_selected_name
            calc_res, total = calculate_agent_performance(code)
            st.markdown(f"<div class='detail-box'><h4 class='agent-title'>{name}</h4>", unsafe_allow_html=True)
            render_ui_cards(name, calc_res, total, show_share_text=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 🔒 3. 시스템 관리자 모드
# ==========================================
elif mode == "⚙️ 시스템 관리자":
    st.markdown("<h2 class='admin-title'>관리자 설정</h2>", unsafe_allow_html=True)
    admin_pw = st.text_input("관리자 비밀번호", type="password")
    if admin_pw != "meritz0085":
        if admin_pw: st.error("비밀번호 불일치")
        st.stop()
        
    st.markdown("### 📂 파일 관리")
    uploaded = st.file_uploader("파일 업로드", accept_multiple_files=True)
    if uploaded:
        for f in uploaded:
            if f.name.endswith('.csv'): 
                try: df = pd.read_csv(f, encoding='cp949')
                except: df = pd.read_csv(f)
            else: df = pd.read_excel(f)
            st.session_state['raw_data'][f.name] = df
            df.to_pickle(os.path.join(DATA_DIR, f"{f.name}.pkl"))
        st.success("업로드 완료")
        st.rerun()

    # 시상 항목 설정 (관리자 화면 기존 로직 유지하되, 간단히 정리)
    if st.button("➕ 신규 주차/브릿지 시상 추가"):
        if st.session_state['raw_data']:
            st.session_state['config'].append({
                "name": "신규 시책", "category": "weekly", "type": "구간 시책",
                "file": list(st.session_state['raw_data'].keys())[0],
                "tiers": [(100000, 100)]
            })
            st.rerun()

    for i, cfg in enumerate(st.session_state['config']):
        with st.expander(f"📌 {cfg['name']} 설정"):
            cfg['name'] = st.text_input("시책명", value=cfg['name'], key=f"edit_nm_{i}")
            cfg['type'] = st.radio("종류", ["구간 시책", "브릿지 시책 (1기간)", "브릿지 시책 (2기간)"], key=f"edit_tp_{i}")
            file_opts = list(st.session_state['raw_data'].keys())
            cfg['file'] = st.selectbox("대상 파일", file_opts, key=f"edit_fl_{i}")
            cols = st.session_state['raw_data'][cfg['file']].columns.tolist()
            cfg['col_code'] = st.selectbox("설계사코드 열", cols, key=f"edit_co_{i}")
            cfg['col_name'] = st.selectbox("성명 열", cols, key=f"edit_na_{i}")
            cfg['col_manager'] = st.selectbox("매니저코드(비번) 열", cols, key=f"edit_mg_{i}")
            if "구간" in cfg['type']:
                cfg['col_val'] = st.selectbox("실적 열", cols, key=f"edit_v_{i}")
            else:
                cfg['col_val_curr'] = st.selectbox("당월실적 열", cols, key=f"edit_vc_{i}")
                cfg['col_val_prev'] = st.selectbox("전월실적 열", cols, key=f"edit_vp_{i}")

    if st.button("✅ 설정 저장하기", type="primary"):
        with open(os.path.join(DATA_DIR, 'config.json'), 'w', encoding='utf-8') as f:
            json.dump(st.session_state['config'], f, ensure_ascii=False)
        st.success("저장되었습니다.")

# ==========================================
# 🏆 4. 사용자 모드 (일반 설계사)
# ==========================================
else:
    st.markdown('<div class="title-band">메리츠화재 시상 현황</div>', unsafe_allow_html=True)
    user_name = st.text_input("이름")
    branch_code = st.text_input("지점코드 (숫자만)")
    
    if st.button("실적 확인", type="primary"):
        found_code = None
        for cfg in st.session_state['config']:
            df = st.session_state['raw_data'].get(cfg['file'])
            if df is not None:
                # 이름과 지점명 포함 여부로 사번 찾기
                tmp = df[df[cfg.get('col_name', '')].fillna('').astype(str).str.strip() == user_name.strip()]
                if not tmp.empty and branch_code:
                    # 지점명 열에 입력한 숫자가 포함되어 있는지 확인
                    br_col = cfg.get('col_branch', '')
                    tmp = tmp[tmp[br_col].astype(str).str.contains(branch_code)]
                    if not tmp.empty:
                        found_code = safe_str(tmp.iloc[0][cfg['col_code']])
                        break
        
        if found_code:
            res, total = calculate_agent_performance(found_code)
            render_ui_cards(user_name, res, total)
        else:
            st.error("정보를 찾을 수 없습니다.")
