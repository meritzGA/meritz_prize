import streamlit as st
import pandas as pd
import numpy as np
import os
import json

# 페이지 설정 (사이드바 제거)
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

# --- 🎨 커스텀 CSS (메리츠 브랜드 컬러 적용) ---
st.markdown("""
<style>
    /* 전체 배경을 밝은 회색으로 고정 */
    [data-testid="stAppViewContainer"] { background-color: #f2f4f6; color: #191f28; }
    
    /* 상단 메뉴(라디오 버튼) 탭 스타일로 변경 */
    div[data-testid="stRadio"] > div {
        display: flex; justify-content: center; background-color: #ffffff; 
        padding: 10px; border-radius: 15px; margin-bottom: 20px; margin-top: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #e5e8eb;
    }
    
    /* 🌟 메리츠 레드 타이틀 띠지 🌟 */
    .title-band {
        background-color: rgb(128, 0, 0);
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 800;
        text-align: center;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 24px;
        letter-spacing: -0.5px;
        box-shadow: 0 4px 10px rgba(128, 0, 0, 0.2);
    }

    /* 스트림릿 입력 폼(Form) 자체를 하얀색 카드로 만듦 */
    [data-testid="stForm"] {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 20px;
        border: 1px solid #e5e8eb;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 24px;
    }

    /* 🌟 요약 카드 (메리츠 레드 그라데이션) 🌟 */
    .summary-card { 
        background: linear-gradient(135deg, rgb(160, 20, 20) 0%, rgb(128, 0, 0) 100%); 
        border-radius: 20px; padding: 32px 24px; margin-bottom: 24px; border: none;
        box-shadow: 0 10px 25px rgba(128, 0, 0, 0.25);
    }
    .summary-label { color: rgba(255,255,255,0.85); font-size: 1.15rem; font-weight: 600; margin-bottom: 8px; }
    .summary-total { color: #ffffff; font-size: 3rem; font-weight: 800; letter-spacing: -1px; margin-bottom: 24px; }
    .summary-item-name { color: rgba(255,255,255,0.95); font-size: 1.15rem; }
    .summary-item-val { color: #ffffff; font-size: 1.3rem; font-weight: 800; }
    .summary-divider { height: 1px; background-color: rgba(255,255,255,0.2); margin: 16px 0; }
    
    /* 개별 시책 상세 카드 */
    .toss-card { 
        background: #ffffff; border-radius: 20px; padding: 28px 24px; 
        margin-bottom: 16px; border: 1px solid #e5e8eb; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
    }
    .toss-title { font-size: 1.6rem; font-weight: 700; color: #191f28; margin-bottom: 6px; letter-spacing: -0.5px; }
    .toss-desc { font-size: 1.1rem; color: #8b95a1; margin-bottom: 24px; }
    
    /* 데이터 행 */
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; }
    .data-label { color: #8b95a1; font-size: 1.1rem; }
    .data-value { color: #333d4b; font-size: 1.3rem; font-weight: 600; }
    
    /* 시상금 강조 행 (포인트 컬러: 메리츠 레드) */
    .prize-row { display: flex; justify-content: space-between; align-items: center; padding-top: 20px; margin-top: 12px; }
    .prize-label { color: #191f28; font-size: 1.4rem; font-weight: 700; }
    .prize-value { color: rgb(128, 0, 0); font-size: 2rem; font-weight: 800; } 
    
    /* 기본 구분선 */
    .toss-divider { height: 1px; background-color: #e5e8eb; margin: 16px 0; }
    .sub-data { font-size: 1rem; color: #8b95a1; margin-top: 4px; text-align: right; }
    
    /* 🌟 시니어 입력창 확대 및 메리츠 컬러 버튼 🌟 */
    div[data-testid="stTextInput"] input {
        font-size: 1.3rem !important; padding: 15px !important; height: 55px !important;
        background-color: #f9fafb !important; color: #191f28 !important;
        border: 1px solid #e5e8eb !important; border-radius: 12px !important;
    }
    div[data-testid="stFormSubmitButton"] button {
        font-size: 1.3rem !important; font-weight: 800 !important; height: 55px !important;
        border-radius: 12px !important; background-color: rgb(128, 0, 0) !important; /* 버튼 색상 변경 */
        color: white !important; border: none !important; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 📱 1. 최상단: 메뉴 선택 탭
# ==========================================
mode = st.radio("화면 선택", ["📊 내 실적 조회하기", "⚙️ 시스템 관리자 모드"], horizontal=True, label_visibility="collapsed")

# ==========================================
# 🔒 2. 관리자 모드
# ==========================================
if mode == "⚙️ 시스템 관리자 모드":
    st.markdown("<h2 style='color:#191f28; font-weight:800; font-size:1.8rem; margin-top: 20px;'>관리자 설정</h2>", unsafe_allow_html=True)
    
    admin_pw = st.text_input("관리자 비밀번호를 입력하세요", type="password")
    
    if admin_pw != "meritz0085":
        if admin_pw:
            st.error("비밀번호가 일치하지 않습니다.")
        st.stop()
        
    st.success("인증 성공! 변경 후 아래 [서버에 반영하기] 버튼을 눌러야 저장됩니다.")
    
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
        st.success(f"업로드 완료! (현재 {len(st.session_state['raw_data'])}개 파일 보유)")

    if st.session_state['raw_data']:
        st.divider()
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
            st.success("서버에 영구 반영되었습니다! 이제 조회 화면에서 확인 가능합니다.")

# ==========================================
# 🏆 3. 사용자 모드 (메리츠 스타일)
# ==========================================
else:
    # 🌟 메리츠 레드 띠지 🌟
    st.markdown('<div class="title-band">메리츠화재 시상 현황</div>', unsafe_allow_html=True)
    
    with st.form("search_form"):
        user_name = st.text_input("본인 이름을 입력하세요", placeholder="예: 홍길동")
        phone_last4 = st.text_input("비밀번호 (기본: 0000)", value="0000", max_chars=4, type="password")
        submit = st.form_submit_button("내 실적 확인하기")

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
                # 1) 요약표 렌더링
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
