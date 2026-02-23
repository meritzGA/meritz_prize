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

# --- 🎨 커스텀 CSS (하얀 빈 박스 버그 완벽 제거) ---
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
    
    .toss-card { 
        background: #ffffff; border-radius: 20px; padding: 28px 24px; 
        margin-bottom: 16px; border: 1px solid #e5e8eb; box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
    }
    
    /* 누계 전용 황금색 카드 */
    .toss-card-gold { 
        background: linear-gradient(135deg, #fff9e6 0%, #ffffff 100%); border-radius: 20px; padding: 28px 24px; 
        margin-bottom: 16px; border: 1px solid #ffe599; box-shadow: 0 4px 20px rgba(255,200,0,0.1); 
    }
    
    .toss-title { font-size: 1.6rem; font-weight: 700; color: #191f28; margin-bottom: 6px; letter-spacing: -0.5px; }
    .toss-desc { font-size: 1.15rem; color: rgb(128, 0, 0); font-weight: 800; margin-bottom: 24px; letter-spacing: -0.3px; }
    
    .data-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; }
    .data-label { color: #8b95a1; font-size: 1.1rem; }
    .data-value { color: #333d4b; font-size: 1.3rem; font-weight: 600; }
    
    .prize-row { display: flex; justify-content: space-between; align-items: center; padding-top: 20px; margin-top: 12px; }
    .prize-label { color: #191f28; font-size: 1.4rem; font-weight: 700; }
    .prize-value { color: rgb(128, 0, 0); font-size: 2rem; font-weight: 800; } 
    
    .toss-divider { height: 1px; background-color: #e5e8eb; margin: 16px 0; }
    .sub-data { font-size: 1rem; color: #8b95a1; margin-top: 4px; text-align: right; }
    
    div[data-testid="stTextInput"] input {
        font-size: 1.3rem !important; padding: 15px !important; height: 55px !important;
        background-color: #ffffff !important; color: #191f28 !important;
        border: 1px solid #e5e8eb !important; border-radius: 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }
    div[data-testid="stSelectbox"] > div {
        background-color: #ffffff !important; border: 1px solid #e5e8eb !important; border-radius: 12px !important;
    }
    div[data-testid="stSelectbox"] * { font-size: 1.1rem !important; }
    
    div.stButton > button {
        font-size: 1.4rem !important; font-weight: 800 !important; height: 60px !important;
        border-radius: 12px !important; background-color: rgb(128, 0, 0) !important;
        color: white !important; border: none !important; width: 100%; margin-top: 15px; margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(128, 0, 0, 0.2);
    }
    
    .del-btn-container button {
        background-color: #f2f4f6 !important; color: #dc3545 !important; border: 1px solid #dc3545 !important;
        height: 40px !important; font-size: 1rem !important; margin-top: 0 !important; box-shadow: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 📱 1. 최상단: 메뉴 선택 탭
# ==========================================
mode = st.radio("화면 선택", ["📊 내 실적 조회", "👥 매니저 관리", "⚙️ 관리자 모드"], horizontal=True, label_visibility="collapsed")

# ==========================================
# 🔒 2. 관리자 모드
# ==========================================
if mode == "⚙️ 관리자 모드":
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
            st.success("✅ 파일 업로드 완료")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([7, 3])
    with col1: st.markdown(f"**현재 저장된 파일 ({len(st.session_state['raw_data'])}개)**")
    with col2:
        st.markdown('<div class="del-btn-container">', unsafe_allow_html=True)
        if st.button("🗑️ 전체 파일 삭제", use_container_width=True):
            st.session_state['raw_data'].clear()
            for f in os.listdir(DATA_DIR):
                if f.endswith('.pkl'): os.remove(os.path.join(DATA_DIR, f))
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.divider()
    if not st.session_state['raw_data']:
        st.info("현재 업로드된 파일이 없습니다.")
    else:
        for file_name in list(st.session_state['raw_data'].keys()):
            col_name, col_btn = st.columns([8, 2])
            with col_name: st.write(f"📄 {file_name}")
            with col_btn:
                st.markdown('<div class="del-btn-container">', unsafe_allow_html=True)
                if st.button("개별 삭제", key=f"del_file_{file_name}", use_container_width=True):
                    del st.session_state['raw_data'][file_name]
                    pkl_path = os.path.join(DATA_DIR, f"{file_name}.pkl")
                    if os.path.exists(pkl_path): os.remove(pkl_path)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<hr style='margin:10px 0; opacity:0.3;'>", unsafe_allow_html=True)

    st.markdown("<h3 style='color:#191f28; font-size:1.4rem; margin-top:30px;'>🏆 2. 시상(시책) 항목 추가 및 관리</h3>", unsafe_allow_html=True)
    col_add, col_del_all = st.columns(2)
    with col_add:
        st.markdown('<style>div.row-widget.stButton > button[kind="primary"] { background-color: #3182f6 !important; }</style>', unsafe_allow_html=True)
        if st.button("➕ 신규 시상 항목 추가", type="primary", use_container_width=True):
            if not st.session_state['raw_data']: st.error("⚠️ 파일을 먼저 업로드해주세요.")
            else:
                first_file = list(st.session_state['raw_data'].keys())[0]
                st.session_state['config'].append({
                    "name": f"신규 시책 {len(st.session_state['config'])+1}", "desc": "", "type": "구간 시책", "file": first_file, 
                    "col_name": "", "col_code": "", "col_branch": "", "col_manager_code": "",
                    "col_val": "", "col_val_prev": "", "col_val_curr": "", "curr_req": 100000.0, "tiers": [(100000, 100), (200000, 200)]
                })
                st.rerun()
                
    with col_del_all:
        st.markdown('<div class="del-btn-container">', unsafe_allow_html=True)
        if st.button("🗑️ 모든 시상 항목 삭제", use_container_width=True):
            st.session_state['config'].clear()
            with open(os.path.join(DATA_DIR, 'config.json'), 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    for i, cfg in enumerate(st.session_state['config']):
        for k in ['desc','col_code','col_branch','col_manager_code','col_val_prev','col_val_curr']:
            if k not in cfg: cfg[k] = ""
        if 'curr_req' not in cfg: cfg['curr_req'] = 100000.0

        st.divider()
        c_title, c_del = st.columns([8, 2])
        with c_title: st.markdown(f"<h3 style='color:#191f28; font-size:1.3rem; margin:0;'>📌 {cfg['name']} 설정</h3>", unsafe_allow_html=True)
        with c_del:
            st.markdown('<div class="del-btn-container">', unsafe_allow_html=True)
            if st.button("개별 삭제", key=f"del_cfg_{i}", use_container_width=True):
                st.session_state['config'].pop(i)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        cfg['name'] = st.text_input(f"시책명", value=cfg['name'], key=f"name_{i}")
        cfg['desc'] = st.text_input("시책 설명 (적용 기간 등)", value=cfg.get('desc', ''), placeholder="예: 2/1 ~ 2/15 인보험 적용", key=f"desc_{i}")
        
        # 🌟 누계 시상 옵션 4번째로 부활 🌟
        idx = 0
        if "1기간" in cfg['type']: idx = 1
        elif "2기간" in cfg['type']: idx = 2
        elif "누계" in cfg['type']: idx = 3
        
        cfg['type'] = st.radio("시책 종류 선택", ["구간 시책", "브릿지 시책 (1기간: 시상 확정)", "브릿지 시책 (2기간: 차월 달성 조건)", "누계 시상 (총 실적 및 시상금 단순 조회)"], index=idx, horizontal=True, key=f"type_{i}")
        
        col1, col2 = st.columns(2)
        with col1:
            file_opts = list(st.session_state['raw_data'].keys())
            if not file_opts: continue
            cfg['file'] = st.selectbox(f"대상 파일", file_opts, index=file_opts.index(cfg['file']) if cfg['file'] in file_opts else 0, key=f"file_{i}")
            cols = st.session_state['raw_data'][cfg['file']].columns.tolist()
            def get_idx(val, opts): return opts.index(val) if val in opts else 0

            st.info("💡 식별을 위해 아래 컬럼들을 지정해주세요.")
            cfg['col_name'] = st.selectbox("성명 컬럼", cols, index=get_idx(cfg['col_name'], cols), key=f"cname_{i}")
            cfg['col_branch'] = st.selectbox("지점명(조직) 컬럼", cols, index=get_idx(cfg['col_branch'], cols), key=f"cbranch_{i}")
            cfg['col_code'] = st.selectbox("설계사코드(사번) 컬럼", cols, index=get_idx(cfg['col_code'], cols), key=f"ccode_{i}")
            cfg['col_manager_code'] = st.selectbox("지원매니저코드 컬럼", cols, index=get_idx(cfg['col_manager_code'], cols), key=f"cmgrcode_{i}")
            
            # 🌟 누계 시상일 경우 컬럼 설정 🌟
            if "누계" in cfg['type']:
                cfg['col_val_prev'] = st.selectbox("총 실적계 컬럼 (보여주기용)", cols, index=get_idx(cfg['col_val_prev'], cols), key=f"cvalp_{i}")
                cfg['col_val_curr'] = st.selectbox("총 시상금계 컬럼 (보여주기용)", cols, index=get_idx(cfg['col_val_curr'], cols), key=f"cvalc_{i}")
            elif "1기간" in cfg['type']:
                cfg['col_val_prev'] = st.selectbox("전월 실적 컬럼", cols, index=get_idx(cfg['col_val_prev'], cols), key=f"cvalp_{i}")
                cfg['col_val_curr'] = st.selectbox("당월 실적 컬럼", cols, index=get_idx(cfg['col_val_curr'], cols), key=f"cvalc_{i}")
                cfg['curr_req'] = st.number_input("당월 필수 달성 금액", value=float(cfg['curr_req']), step=10000.0, key=f"creq_{i}")
            elif "2기간" in cfg['type']:
                cfg['col_val_curr'] = st.selectbox("당월 실적 수치 컬럼", cols, index=get_idx(cfg.get('col_val_curr', ''), cols), key=f"cvalc2_{i}")
                cfg['curr_req'] = st.number_input("차월 필수 달성 금액 (합산용)", value=float(cfg.get('curr_req', 100000.0)), step=10000.0, key=f"creq2_{i}")
            else: 
                cfg['col_val'] = st.selectbox("실적 수치 컬럼", cols, index=get_idx(cfg.get('col_val', ''), cols), key=f"cval_{i}")

        with col2:
            if "누계" in cfg['type']:
                st.info("💡 누계 시상은 별도의 구간/지급률 설정이 필요 없습니다. 업로드된 파일의 합산 수치를 그대로 보여줍니다.")
            else:
                st.write("📈 구간 설정 (달성구간금액,지급률%)")
                tier_str = "\n".join([f"{int(t[0])},{int(t[1])}" for t in cfg['tiers']])
                tier_input = st.text_area("엔터로 줄바꿈", value=tier_str, height=150, key=f"tier_{i}")
                try:
                    new_tiers = []
                    for line in tier_input.strip().split('\n'):
                        if ',' in line:
                            parts = line.split(',')
                            new_tiers.append((float(parts[0].strip()), float(parts[1].strip())))
                    cfg['tiers'] = sorted(new_tiers, key=lambda x: x[0], reverse=True)
                except: st.error("형식이 올바르지 않습니다.")

    st.divider()
    st.markdown("<h3 style='color:#191f28; font-size:1.4rem; margin-top:10px;'>🖼️ 3. 안내 리플렛(이미지) 등록</h3>", unsafe_allow_html=True)
    leaflet_file = st.file_uploader("리플렛 업로드 (JPG, PNG)", type=['jpg', 'jpeg', 'png'])
    if leaflet_file:
        with open(os.path.join(DATA_DIR, "leaflet.png"), "wb") as f:
            f.write(leaflet_file.getbuffer())
        st.success("✅ 리플렛 이미지가 저장되었습니다!")
        st.rerun()

    leaflet_path = os.path.join(DATA_DIR, "leaflet.png")
    if os.path.exists(leaflet_path):
        st.image(leaflet_path, width=250)
        st.markdown('<div class="del-btn-container">', unsafe_allow_html=True)
        if st.button("🗑️ 등록된 리플렛 삭제", use_container_width=False):
            os.remove(leaflet_path)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state['config']:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<style>div.row-widget.stButton > button[kind="secondary"] { background-color: rgb(128, 0, 0) !important; color: white !important; font-size: 1.5rem !important; height: 70px !important; }</style>', unsafe_allow_html=True)
        if st.button("✅ 모든 설정 완료 및 서버에 반영하기", use_container_width=True):
            with open(os.path.join(DATA_DIR, 'config.json'), 'w', encoding='utf-8') as f:
                json.dump(st.session_state['config'], f, ensure_ascii=False)
            st.success("✅ 서버에 영구 반영되었습니다!")

# ==========================================
# 👥 3. 매니저 관리 화면 (이름 제외, 코드만)
# ==========================================
elif mode == "👥 매니저 관리":
    st.markdown('<div class="title-band">매니저 산하 근접자 조회</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#191f28; font-weight:800; font-size:1.3rem; margin-bottom: 15px;'>지원매니저 코드(사번)를 입력하세요.</h3>", unsafe_allow_html=True)
    
    manager_code = st.text_input("매니저 코드(사번)", placeholder="예: 123456")
    submit_manager = st.button("산하 근접자 확인하기")

    if submit_manager:
        if not manager_code:
            st.warning("매니저 코드를 입력해주세요.")
        elif not st.session_state['config']:
            st.warning("진행 중인 시책이 없습니다.")
        else:
            has_data = False
            for i, cfg in enumerate(st.session_state['config']):
                if not cfg.get('col_manager_code'):
                    continue
                if "누계" in cfg.get('type', ''): # 누계 시상은 근접자 조회에서 제외
                    continue
                    
                df = st.session_state['raw_data'].get(cfg['file'])
                if df is not None:
                    search_mgr_code = df[cfg['col_manager_code']].fillna('').astype(str).str.strip()
                    match_df = df[search_mgr_code == manager_code.strip()]
                    
                    if not match_df.empty:
                        has_data = True
                        st.markdown(f"<h4 style='color:rgb(128, 0, 0); font-weight:800; margin-top:30px;'>🏆 {cfg['name']}</h4>", unsafe_allow_html=True)
                        
                        agent_list = []
                        for _, row in match_df.iterrows():
                            agent_name = str(row.get(cfg['col_name'], '')).strip()
                            agent_branch = str(row.get(cfg['col_branch'], '')).strip()
                            p_type = cfg.get('type', '구간 시책')
                            
                            val = 0.0
                            try:
                                if "1기간" in p_type or "2기간" in p_type: val = float(str(row[cfg['col_val_curr']]).replace(',', ''))
                                else: val = float(str(row[cfg['col_val']]).replace(',', ''))
                            except: pass
                                
                            tier_achieved, next_tier = 0, None
                            for amt, rate in cfg['tiers']:
                                if val >= amt:
                                    tier_achieved = amt
                                    break
                            for amt, rate in reversed(cfg['tiers']):
                                if val < amt:
                                    next_tier = amt
                                    break
                                    
                            shortfall = (next_tier - val) if next_tier else 0
                            if shortfall > 0:
                                agent_list.append({
                                    '소속지점': agent_branch, '설계사명': agent_name,
                                    '현재실적': int(val), '도달구간': int(tier_achieved),
                                    '다음구간': int(next_tier) if next_tier else 0, '부족금액': int(shortfall)
                                })
                        
                        if agent_list:
                            res_df = pd.DataFrame(agent_list).sort_values(by='부족금액')
                            res_df['현재실적'] = res_df['현재실적'].apply(lambda x: f"{x:,.0f}원")
                            res_df['도달구간'] = res_df['도달구간'].apply(lambda x: f"{x:,.0f}원")
                            res_df['다음구간'] = res_df['다음구간'].apply(lambda x: f"{x:,.0f}원")
                            res_df['부족금액'] = res_df['부족금액'].apply(lambda x: f"🚨 {x:,.0f}원 부족" if x <= 150000 else f"{x:,.0f}원")
                            st.dataframe(res_df, use_container_width=True, hide_index=True)
                        else:
                            st.info("산하 설계사 모두 최고 구간을 달성했습니다.")
                            
            if not has_data:
                st.error("일치하는 정보가 없거나, '지원매니저코드 컬럼'이 지정되지 않았습니다.")

# ==========================================
# 📊 4. 사용자 모드 (설계사 실적 조회)
# ==========================================
elif mode == "📊 내 실적 조회":
    st.markdown('<div class="title-band">메리츠화재 시상 현황</div>', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#191f28; font-weight:800; font-size:1.3rem; margin-bottom: 15px;'>이름과 지점별 코드를 입력하세요.</h3>", unsafe_allow_html=True)
    
    user_name = st.text_input("본인 이름을 입력하세요", placeholder="예: 홍길동")
    branch_code_input = st.text_input("지점별 코드", placeholder="예: 1지점은 1, 11지점은 11 입력")

    matched_configs = {}
    codes_found = set()
    needs_disambiguation = False

    if user_name and branch_code_input:
        for i, cfg in enumerate(st.session_state['config']):
            df = st.session_state['raw_data'].get(cfg['file'])
            if df is not None:
                search_name = df[cfg['col_name']].fillna('').astype(str).str.strip()
                name_match_condition = (search_name == user_name.strip())
                
                if branch_code_input.strip() == "0000": match = df[name_match_condition]
                else:
                    clean_code = branch_code_input.replace("지점", "").strip()
                    if clean_code:
                        search_branch = df[cfg['col_branch']].fillna('').astype(str)
                        regex_pattern = rf"(?<!\d){clean_code}\s*지점"
                        match = df[name_match_condition & search_branch.str.contains(regex_pattern, regex=True)]
                    else: match = pd.DataFrame()
                
                if not match.empty:
                    matched_configs[i] = match
                    if 'col_code' in cfg and cfg['col_code']:
                        for _, row in match.iterrows():
                            agent_code = str(row[cfg['col_code']]).strip()
                            if agent_code: codes_found.add(agent_code)

    codes_found = {c for c in codes_found if c}
    selected_code = None
    if len(codes_found) > 1:
        st.warning("⚠️ 동일한 이름과 지점을 가진 분이 존재합니다. 본인의 설계사코드(사번)를 선택해주세요.")
        selected_code = st.selectbox("나의 설계사코드 선택", sorted(list(codes_found)))
        needs_disambiguation = True

    submit = st.button("내 실적 확인하기")

    if submit:
        if not user_name or not branch_code_input: st.warning("이름과 지점코드를 입력해주세요.")
        elif not st.session_state['config']: st.warning("현재 진행 중인 시책 데이터가 없습니다.")
        elif not matched_configs: st.error("일치하는 정보가 없습니다. 이름과 지점코드를 다시 확인해주세요.")
        else:
            calculated_results = []
            total_prize_sum = 0
            
            for i, match_df in matched_configs.items():
                cfg = st.session_state['config'][i]
                if needs_disambiguation and selected_code and 'col_code' in cfg and cfg['col_code']:
                    match_df = match_df[match_df[cfg['col_code']].fillna('').astype(str).str.strip() == selected_code]
                if match_df.empty: continue
                
                p_type = cfg.get('type', '구간 시책')
                
                # 🌟 누계 시상 로직 🌟
                if "누계" in p_type:
                    raw_perf = match_df[cfg['col_val_prev']].values[0]
                    raw_prize = match_df[cfg['col_val_curr']].values[0]
                    try: val_perf = float(str(raw_perf).replace(',', ''))
                    except: val_perf = 0.0
                    try: val_prize = float(str(raw_prize).replace(',', ''))
                    except: val_prize = 0.0
                    
                    calculated_results.append({ "name": cfg['name'], "desc": cfg.get('desc', ''), "type": "누계", "val_perf": val_perf, "prize": val_prize })
                
                elif "1기간" in p_type: 
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
                    calculated_results.append({ "name": cfg['name'], "desc": cfg.get('desc', ''), "type": "브릿지1", "val_prev": val_prev, "tier_prev": tier_prev, "val_curr": val_curr, "curr_req": curr_req, "rate": calc_rate, "prize": prize })
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
                    if tier_achieved > 0: prize = (tier_achieved + curr_req) * (calc_rate / 100)
                    calculated_results.append({ "name": cfg['name'], "desc": cfg.get('desc', ''), "type": "브릿지2", "val": val_curr, "tier": tier_achieved, "rate": calc_rate, "prize": prize, "curr_req": curr_req })
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
                    calculated_results.append({ "name": cfg['name'], "desc": cfg.get('desc', ''), "type": "구간", "val": val, "tier": tier_achieved, "rate": calc_rate, "prize": prize })
                    total_prize_sum += prize

            if len(calculated_results) > 0:
                summary_html = (
                    f"<div class='summary-card'><div class='summary-label'>{user_name} 팀장님의 확보한 총 시상금</div>"
                    f"<div class='summary-total'>{total_prize_sum:,.0f}원</div><div class='summary-divider'></div>"
                )
                for res in calculated_results:
                    if res['type'] in ["구간", "브릿지1"]:
                        summary_html += f"<div class='data-row' style='padding: 6px 0;'><span class='summary-item-name'>{res['name']}</span><span class='summary-item-val'>{res['prize']:,.0f}원</span></div>"
                    elif res['type'] == "브릿지2": 
                        summary_html += f"<div class='data-row' style='padding: 6px 0;'><span class='summary-item-name'>{res['name']} <span style='font-size:0.9rem; color:rgba(255,255,255,0.7);'>(차월 {int(res['curr_req']//10000)}만 달성조건)</span></span><span class='summary-item-val'>{res['prize']:,.0f}원</span></div>"
                summary_html += "</div>"
                st.markdown(summary_html, unsafe_allow_html=True)
                
                for res in calculated_results:
                    if res['type'] == "구간":
                        st.markdown(f"<div class='toss-card'><div class='toss-title'>{res['name']}</div><div class='toss-desc'>{res['desc']}</div><div class='data-row'><span class='data-label'>현재 누적 실적</span><span class='data-value'>{res['val']:,.0f}원</span></div><div class='data-row'><span class='data-label'>도달한 구간 기준</span><span class='data-value'>{res['tier']:,.0f}원</span></div><div class='data-row'><span class='data-label'>적용 지급률</span><span class='data-value'>{res['rate']:g}%</span></div><div class='toss-divider'></div><div class='prize-row'><span class='prize-label'>확보한 시상금</span><span class='prize-value'>{res['prize']:,.0f}원</span></div></div>", unsafe_allow_html=True)
                    elif res['type'] == "브릿지1":
                        st.markdown(f"<div class='toss-card'><div class='toss-title'>{res['name']}</div><div class='toss-desc'>{res['desc']}</div><div class='data-row'><span class='data-label'>전월 실적 (인정구간)</span><div style='text-align:right;'><div class='data-value'>{res['val_prev']:,.0f}원</div><div class='sub-data'>({res['tier_prev']:,.0f}원 구간)</div></div></div><div class='data-row'><span class='data-label'>당월 실적 (목표 {res['curr_req']:,.0f}원)</span><span class='data-value'>{res['val_curr']:,.0f}원</span></div><div class='data-row'><span class='data-label'>적용 지급률</span><span class='data-value'>{res['rate']:g}%</span></div><div class='toss-divider'></div><div class='prize-row'><span class='prize-label'>확보한 시상금</span><span class='prize-value'>{res['prize']:,.0f}원</span></div></div>", unsafe_allow_html=True)
                    elif res['type'] == "브릿지2":
                        st.markdown(f"<div class='toss-card'><div class='toss-title'>{res['name']}</div><div class='toss-desc'>{res['desc']}</div><div class='data-row'><span class='data-label'>당월 누적 실적</span><span class='data-value'>{res['val']:,.0f}원</span></div><div class='data-row'><span class='data-label'>확보한 구간 기준</span><span class='data-value'>{res['tier']:,.0f}원</span></div><div class='data-row'><span class='data-label'>예상 적용 지급률</span><span class='data-value'>{res['rate']:g}%</span></div><div class='toss-divider'></div><div class='prize-row'><span class='prize-label'>차월 {int(res['curr_req']//10000)}만원 달성시 시상금</span><span class='prize-value'>{res['prize']:,.0f}원</span></div></div>", unsafe_allow_html=True)
                    # 🌟 누계 시상 전용 카드 (스페셜 테마 적용) 🌟
                    elif res['type'] == "누계":
                        st.markdown(f"<div class='toss-card-gold'><div class='toss-title'>{res['name']}</div><div class='toss-desc'>{res['desc']}</div><div class='data-row'><span class='data-label'>총 합산 실적 (누계)</span><span class='data-value'>{res['val_perf']:,.0f}원</span></div><div class='toss-divider'></div><div class='prize-row'><span class='prize-label'>총 누계 시상금</span><span class='prize-value' style='color:#b38600;'>{res['prize']:,.0f}원</span></div></div>", unsafe_allow_html=True)
                
                user_leaflet_path = os.path.join(DATA_DIR, "leaflet.png")
                if os.path.exists(user_leaflet_path):
                    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
                    st.image(user_leaflet_path, use_container_width=True)
