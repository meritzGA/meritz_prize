import streamlit as st
import pandas as pd
import numpy as np
import os
import json

# 페이지 설정
st.set_page_config(page_title="메리츠화재 시상 현황", layout="wide", initial_sidebar_state="collapsed")

# --- 데이터 영구 저장을 위한 폴더 설정 ---
DATA_DIR = "app_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# 데이터 불러오기 로직 (앱이 새로고침 되어도 서버 폴더에서 읽어옴)
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

# --- 공통 커스텀 CSS (아이콘 충돌 방지 및 다크 테마 유지) ---
st.markdown("""
<style>
    /* 전체 배경을 완전한 다크톤으로 설정 */
    [data-testid="stAppViewContainer"] { background-color: #0b0b0d; color: #f2f2f2; }
    [data-testid="stSidebar"] { background-color: #131315; }
    
    /* 검색 컨테이너 */
    .search-container {
        background: #19191b; padding: 24px; border-radius: 20px;
        margin-bottom: 24px; border: 1px solid #262628;
    }
    
    /* 🌟 요약 카드 (토스 스타일 포인트 컬러 박스) 🌟 */
    .summary-card { 
        background: linear-gradient(135deg, #3182f6 0%, #1b64da 100%); /* 토스 블루 그라데이션 */
        border-radius: 20px; padding: 32px 24px; margin-bottom: 24px; border: none;
        box-shadow: 0 10px 25px rgba(49, 130, 246, 0.25);
    }
    .summary-label { color: rgba(255,255,255,0.85); font-size: 1.15rem; font-weight: 600; margin-bottom: 8px; }
    .summary-total { color: #ffffff; font-size: 3rem; font-weight: 800; letter-spacing: -1px; margin-bottom: 24px; }
    .summary-item-name { color: rgba(255,255,255,0.95); font-size: 1.15rem; }
    .summary-item-val { color: #ffffff; font-size: 1.3rem; font-weight: 800; }
    .summary-divider { height: 1px; background-color: rgba(255,255,255,0.2); margin: 16px 0; }
    
    /* 개별 시책 상세 카드 */
    .toss-card { background: #19191b; border-radius: 20px; padding: 28px 24px; margin-bottom: 16px; border: 1px solid #262628; }
    .toss-title { font-size: 1.6rem; font-weight: 700; color: #ffffff; margin-bottom: 6px; }
    .toss-desc { font-size: 1.1rem; color: #8e8e93; margin-bottom: 24px; }
    
    /* 데이터 행 */
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; }
    .data-label { color: #8e8e93; font-size: 1.1rem; }
    .data-value { color: #ffffff; font-size: 1.3rem; font-weight: 600; }
    
    /* 시상금 강조 행 */
    .prize-row { display: flex; justify-content: space-between; align-items: center; padding-top: 20px; margin-top: 12px; }
    .prize-label { color: #ffffff; font-size: 1.4rem; font-weight: 700; }
    .prize-value { color: #3182f6; font-size: 2rem; font-weight: 800; } 
    
    /* 기본 구분선 */
    .toss-divider { height: 1px; background-color: #262628; margin: 16px 0; }
    .sub-data { font-size: 1rem; color: #636366; margin-top: 4px; text-align: right; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# ⚙️ 사이드바 & 접속 모드 관리
# ==========================================
st.sidebar.title("설정 메뉴")
mode = st.sidebar.radio("접속 화면 선택", ["사용자 (실적 조회)", "관리자 (데이터 업로드 및 설정)"], index=0)

# ==========================================
# 🔒 관리자 모드
# ==========================================
if mode == "관리자 (데이터 업로드 및 설정)":
    st.title("⚙️ 시스템 관리자 설정")
    
    admin_pw = st.text_input("관리자 비밀번호를 입력하세요", type="password")
    
    if admin_pw != "meritz0085":
        if admin_pw:
            st.error("비밀번호가 일치하지 않습니다.")
        st.stop()
        
    st.success("관리자 인증 성공!")
    st.info("💡 이곳에서 변경하고 [설정 완료 및 서버에 반영하기]를 누르면 서버에 영구 반영되어 사용자 화면이 업데이트됩니다.")
    
    uploaded_files = st.file_uploader("CSV/엑셀 파일 업로드", accept_multiple_files=True, type=['csv', 'xlsx'])
    
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state['raw_data']:
                if file.name.endswith('.csv'):
                    try: df = pd.read_csv(file)
                    except Exception:
                        file.seek(0)
                        try: df = pd.read_csv(file, sep='\t')
                        except Exception:
                            file.seek(0)
                            try: df = pd.read_csv(file, encoding='cp949')
                            except Exception:
                                file.seek(0)
                                df = pd.read_csv(file, sep='\t', encoding='cp949')
                else:
                    df = pd.read_excel(file)
                st.session_state['raw_data'][file.name] = df
        st.success(f"업로드 완료! (현재 메모리에 {len(st.session_state['raw_data'])}개 유지 중)")

    if st.session_state['raw_data']:
        st.divider()
        st.subheader("2. 시책 항목 상세 설정")
        if st.button("➕ 시책 항목 추가"):
            first_file = list(st.session_state['raw_data'].keys())[0]
            st.session_state['config'].append({
                "name": f"신규 시책 {len(st.session_state['config'])+1}",
                "desc": "", "type": "구간 시책", 
                "file": first_file, "col_name": "", "col_phone": "", 
                "col_val": "", "col_val_prev": "", "col_val_curr": "", "curr_req": 100000.0,
                "tiers": [(100000, 100), (200000, 200), (300000, 200), (500000, 300)]
            })

        for i, cfg in enumerate(st.session_state['config']):
            if 'desc' not in cfg: cfg['desc'] = ""
            if 'type' not in cfg: cfg['type'] = "구간 시책"
            if 'col_val_prev' not in cfg: cfg['col_val_prev'] = ""
            if 'col_val_curr' not in cfg: cfg['col_val_curr'] = ""
            if 'curr_req' not in cfg: cfg['curr_req'] = 100000.0

            with st.expander(f"📌 {cfg['name']} 설정", expanded=True):
                cfg['name'] = st.text_input(f"시책명", value=cfg['name'], key=f"name_{i}")
                cfg['desc'] = st.text_input("시책 설명 (적용 기간 등)", value=cfg.get('desc', ''), placeholder="예: 2/1 ~ 2/15 인보험 적용", key=f"desc_{i}")
                cfg['type'] = st.radio("시책 종류 선택", ["구간 시책", "브릿지 시책"], index=0 if cfg['type']=="구간 시책" else 1, horizontal=True, key=f"type_{i}")
                
                col1, col2 = st.columns(2)
                with col1:
                    file_opts = list(st.session_state['raw_data'].keys())
                    cfg['file'] = st.selectbox(f"대상 파일", file_opts, index=file_opts.index(cfg['file']) if cfg['file'] in file_opts else 0, key=f"file_{i}")
                    cols = st.session_state['raw_data'][cfg['file']].columns.tolist()
                    def get_idx(val, opts): return opts.index(val) if val in opts else 0

                    cfg['col_name'] = st.selectbox("성명 컬럼", cols, index=get_idx(cfg['col_name'], cols), key=f"cname_{i}")
                    cfg['col_phone'] = st.selectbox("식별번호(비밀번호) 컬럼", cols, index=get_idx(cfg['col_phone'], cols), key=f"cphone_{i}")
                    
                    if cfg['type'] == "구간 시책":
                        cfg['col_val'] = st.selectbox("실적 수치 컬럼", cols, index=get_idx(cfg['col_val'], cols), key=f"cval_{i}")
                    else:
                        cfg['col_val_prev'] = st.selectbox("전월 실적 컬럼", cols, index=get_idx(cfg['col_val_prev'], cols), key=f"cvalp_{i}")
                        cfg['col_val_curr'] = st.selectbox("당월 실적 컬럼", cols, index=get_idx(cfg['col_val_curr'], cols), key=f"cvalc_{i}")
                        cfg['curr_req'] = st.number_input("당월 필수 달성 조건 금액", value=float(cfg['curr_req']), step=10000.0, key=f"creq_{i}")

                with col2:
                    st.write("📈 구간 설정 (구간금액,지급률%)")
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
                        
        if st.button("✅ 설정 완료 및 서버에 반영하기", type="primary"):
            for k, v in st.session_state['raw_data'].items():
                v.to_pickle(os.path.join(DATA_DIR, f"{k}.pkl"))
            with open(os.path.join(DATA_DIR, 'config.json'), 'w', encoding='utf-8') as f:
                json.dump(st.session_state['config'], f, ensure_ascii=False)
            st.success("서버에 영구적으로 반영되었습니다! 이제 누구나 조회가 가능합니다.")

# ==========================================
# 🏆 사용자 모드 (Toss UI & 시니어 입력창 확대)
# ==========================================
else:
    # 사용자 모드일 때만 입력창과 버튼을 큼직하게 만드는 CSS
    st.markdown("""
    <style>
        input[type="text"], input[type="password"] {
            font-size: 1.4rem !important; 
            padding: 18px !important;
            height: 60px !important;
        }
        .stButton > button {
            font-size: 1.4rem !important;
            font-weight: 800 !important;
            height: 60px !important;
            border-radius: 12px !important;
            background-color: #3182f6 !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 상단 타이틀 추가 (메리츠화재 시상 현황)
    st.markdown("""
    <div style='padding: 20px 0 10px 0;'>
        <p style='color:#3182f6; font-weight:800; font-size:1.1rem; margin-bottom: 0;'>메리츠화재 시상 현황</p>
        <h2 style='color:#ffffff; font-weight:800; font-size:2.2rem; margin-top: 5px;'>내 실적 현황 조회</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='search-container'>", unsafe_allow_html=True)
        with st.form("search_form"):
            user_name = st.text_input("본인 이름을 입력하세요", placeholder="예: 홍길동")
            phone_last4 = st.text_input("비밀번호 (전화번호 뒷 4자리)", value="0000", max_chars=4, type="password")
            submit = st.form_submit_button("내 실적 조회하기", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if submit:
        if not user_name:
            st.warning("이름을 입력해주세요.")
        elif not st.session_state['config']:
            st.warning("현재 진행 중인 시책 데이터가 없습니다.")
        else:
            calculated_results = []
            total_prize_sum = 0
            
            for cfg in st.session_state['config']:
                if cfg['file'] in st.session_state['raw_data']:
                    df = st.session_state['raw_data'][cfg['file']]
                    try:
                        search_phone = df[cfg['col_phone']].fillna('').astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
                        search_name = df[cfg['col_name']].fillna('').astype(str).str.strip()
                        
                        name_match_condition = (search_name == user_name.strip())
                        if phone_last4 == "0000": match = df[name_match_condition]
                        else: match = df[name_match_condition & (search_phone.str.endswith(phone_last4))]
                        
                        if not match.empty:
                            p_type = cfg.get('type', '구간 시책')
                            
                            if p_type == "구간 시책":
                                raw_val = match[cfg['col_val']].values[0]
                                try: val = float(str(raw_val).replace(',', ''))
                                except: val = 0.0
                                
                                calc_rate, tier_achieved, prize = 0, 0, 0
                                for amt, rate in cfg['tiers']:
                                    if val >= amt:
                                        tier_achieved = amt
                                        calc_rate = rate
                                        prize = tier_achieved * (calc_rate / 100) 
                                        break
                                
                                calculated_results.append({
                                    "name": cfg['name'], "desc": cfg.get('desc', ''), "type": "구간",
                                    "val": val, "tier": tier_achieved, "rate": calc_rate, "prize": prize
                                })
                                total_prize_sum += prize
                                
                            else: 
                                raw_prev = match[cfg['col_val_prev']].values[0]
                                raw_curr = match[cfg['col_val_curr']].values[0]
                                try: val_prev = float(str(raw_prev).replace(',', ''))
                                except: val_prev = 0.0
                                try: val_curr = float(str(raw_curr).replace(',', ''))
                                except: val_curr = 0.0
                                
                                curr_req = float(cfg['curr_req'])
                                calc_rate, tier_prev, prize = 0, 0, 0
                                
                                if val_curr >= curr_req:
                                    for amt, rate in cfg['tiers']:
                                        if val_prev >= amt:
                                            tier_prev = amt
                                            calc_rate = rate
                                            prize = (tier_prev + curr_req) * (calc_rate / 100)
                                            break
                                            
                                calculated_results.append({
                                    "name": cfg['name'], "desc": cfg.get('desc', ''), "type": "브릿지",
                                    "val_prev": val_prev, "tier_prev": tier_prev,
                                    "val_curr": val_curr, "curr_req": curr_req,
                                    "rate": calc_rate, "prize": prize
                                })
                                total_prize_sum += prize
                    except Exception as e:
                        pass 

            if len(calculated_results) > 0:
                # 1) 요약표 렌더링 (블루 그라데이션 적용)
                summary_html = f"""<div class="summary-card">
<div class="summary-label">{user_name} 팀장님의 확보한 총 시상금</div>
<div class="summary-total">{total_prize_sum:,.0f}원</div>
<div class="summary-divider"></div>"""
                
                for res in calculated_results:
                    summary_html += f"""<div class="data-row" style="padding: 6px 0;">
<span class="summary-item-name">{res['name']}</span>
<span class="summary-item-val">{res['prize']:,.0f}원</span>
</div>"""
                summary_html += "</div>"
                st.markdown(summary_html, unsafe_allow_html=True)
                
                # 2) 개별 상세 카드 렌더링
                for res in calculated_results:
                    if res['type'] == "구간":
                        card_html = f"""<div class="toss-card">
<div class="toss-title">{res['name']}</div>
<div class="toss-desc">{res['desc']}</div>
<div class="data-row"><span class="data-label">현재 누적 실적</span><span class="data-value">{res['val']:,.0f}원</span></div>
<div class="data-row"><span class="data-label">도달한 구간 기준</span><span class="data-value">{res['tier']:,.0f}원</span></div>
<div class="data-row"><span class="data-label">적용 지급률</span><span class="data-value">{res['rate']:g}%</span></div>
<div class="toss-divider"></div>
<div class="prize-row">
<span class="prize-label">확보한 시상금</span>
<span class="prize-value">{res['prize']:,.0f}원</span>
</div>
</div>"""
                    else:
                        card_html = f"""<div class="toss-card">
<div class="toss-title">{res['name']}</div>
<div class="toss-desc">{res['desc']}</div>
<div class="data-row">
<span class="data-label">전월 실적 (인정구간)</span>
<div style="text-align:right;">
<div class="data-value">{res['val_prev']:,.0f}원</div>
<div class="sub-data">({res['tier_prev']:,.0f}원 구간)</div>
</div>
</div>
<div class="data-row">
<span class="data-label">당월 실적 (목표 {res['curr_req']:,.0f}원)</span>
<span class="data-value">{res['val_curr']:,.0f}원</span>
</div>
<div class="data-row"><span class="data-label">적용 지급률</span><span class="data-value">{res['rate']:g}%</span></div>
<div class="toss-divider"></div>
<div class="prize-row">
<span class="prize-label">확보한 시상금</span>
<span class="prize-value">{res['prize']:,.0f}원</span>
</div>
</div>"""
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.error("일치하는 정보가 없습니다. 이름을 다시 확인해주세요.")
