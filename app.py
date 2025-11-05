"""
LLM 기반 가짜 미술품 검증 시뮬레이션 Streamlit 앱
"""

import streamlit as st
from llm_simulator import LLMArtworkSimulator
import json
from datetime import datetime
import time

# 페이지 설정
st.set_page_config(
    page_title="LLM 기반 미술품 검증 시뮬레이터",
    page_icon="🤖",
    layout="wide"
)

# API 키 로드
openai_api_key = None

try:
    if hasattr(st, 'secrets') and st.secrets:
        if 'openai' in st.secrets and hasattr(st.secrets.openai, 'api_key') and st.secrets.openai.api_key:
            openai_api_key = st.secrets.openai.api_key
        elif 'OPENAI_API_KEY' in st.secrets and st.secrets['OPENAI_API_KEY']:
            openai_api_key = st.secrets['OPENAI_API_KEY']
except:
    pass

if not openai_api_key and 'openai_api_key' in st.session_state and st.session_state.openai_api_key:
    openai_api_key = st.session_state.openai_api_key

# 탭 설정
tab1, tab2 = st.tabs(["시뮬레이션", "설정"])

with tab1:
    st.title("🤖 LLM 기반 미술품 검증 시뮬레이터")
    st.markdown("---")
    
    if not openai_api_key:
        st.warning("⚠️ 설정 탭에서 Open API Key를 입력해주세요.")
    else:
        st.success("✅ API Key가 설정되었습니다.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_turns = st.number_input(
                "대화 횟수",
                min_value=1,
                max_value=1000,
                value=100,
                step=10,
                help="검증 봇과 고객 봇이 진행할 대화 횟수"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            start_button = st.button("🚀 시뮬레이션 시작", type="primary", use_container_width=True)
        
        if start_button:
            if 'simulator' not in st.session_state:
                st.session_state.simulator = LLMArtworkSimulator(openai_api_key, num_turns)
            
            # 진행 상황 표시 영역
            progress_bar = st.progress(0)
            status_text = st.empty()
            conversation_area = st.empty()
            
            # 결과 저장 영역
            results_container = st.container()
            
            # 시뮬레이션 실행
            conversations_list = []
            
            def progress_callback(turn, total, conversation):
                progress = turn / total
                progress_bar.progress(progress)
                status_text.text(f"진행 중: {turn}/{total} 턴 완료")
                
                # 대화 표시
                with conversation_area.container():
                    st.markdown(f"### [턴 {turn}]")
                    st.markdown(f"**👤 고객 봇:** {conversation.customer_message}")
                    st.markdown(f"**🤖 검증 전문가:** {conversation.verification_message}")
                    st.markdown("---")
                
                conversations_list.append({
                    "turn": turn,
                    "customer": conversation.customer_message,
                    "verification": conversation.verification_message
                })
            
            try:
                with st.spinner("시뮬레이션 실행 중..."):
                    results = st.session_state.simulator.run_simulation(progress_callback)
                
                progress_bar.progress(1.0)
                status_text.success(f"✅ 시뮬레이션 완료! 총 {num_turns}턴 완료")
                
                # 통계 표시
                stats = st.session_state.simulator.get_statistics()
                
                with results_container:
                    st.markdown("### 📊 시뮬레이션 결과")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("총 대화 횟수", stats.get("total_turns", 0))
                    with col_b:
                        verdicts = stats.get("verdict_breakdown", {})
                        st.metric("진품 판정", verdicts.get("진품", 0))
                    with col_c:
                        st.metric("가품 판정", verdicts.get("가품", 0))
                    
                    # 판정 분포
                    if verdicts:
                        st.markdown("#### 판정 분포")
                        for verdict, count in verdicts.items():
                            st.progress(count / stats.get("total_turns", 1), text=f"{verdict}: {count}개")
                    
                    # 최근 대화 기록
                    st.markdown("#### 최근 대화 기록")
                    with st.expander("대화 기록 보기", expanded=False):
                        for result in results[-10:]:  # 최근 10개만 표시
                            st.markdown(f"**턴 {result['turn']}**")
                            st.markdown(f"👤 **고객:** {result['customer']}")
                            st.markdown(f"🤖 **검증:** {result['verification']}")
                            if result.get('customer_response'):
                                st.markdown(f"👤 **고객 반응:** {result['customer_response']}")
                            st.markdown("---")
                
                # 결과 다운로드
                results_json = json.dumps(results, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 결과 다운로드 (JSON)",
                    data=results_json,
                    file_name=f"simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
                st.exception(e)

with tab2:
    st.title("⚙️ 설정")
    st.markdown("---")
    
    # Open API Key 설정
    st.subheader("🔑 Open API Key 설정")
    
    # Streamlit Secrets 확인
    secrets_loaded = False
    try:
        if hasattr(st, 'secrets') and st.secrets:
            if 'openai' in st.secrets and hasattr(st.secrets.openai, 'api_key') and st.secrets.openai.api_key:
                secrets_loaded = True
            elif 'OPENAI_API_KEY' in st.secrets and st.secrets['OPENAI_API_KEY']:
                secrets_loaded = True
    except:
        pass
    
    if secrets_loaded or openai_api_key:
        st.success("✅ API Key가 Streamlit Secrets에 설정되어 있습니다.")
        st.info("💡 Streamlit Cloud에서는 대시보드의 'Secrets' 탭에서 관리할 수 있습니다.")
        
        # 디버깅 정보
        with st.expander("🔍 Secrets 확인"):
            try:
                if hasattr(st, 'secrets') and st.secrets:
                    st.json({"secrets_available": True, "openai_in_secrets": 'openai' in st.secrets})
                else:
                    st.json({"secrets_available": False})
            except:
                st.json({"secrets_available": False, "error": "Cannot access secrets"})
    else:
        # 세션 상태에서 API Key 입력
        api_key = st.text_input(
            "Open API Key",
            type="password",
            value=st.session_state.get('openai_api_key', ''),
            help="OpenAI API Key를 입력하세요. (예: sk-...)"
        )
        
        if st.button("💾 API Key 저장", type="primary"):
            if api_key:
                st.session_state.openai_api_key = api_key
                st.success("✅ API Key가 세션 상태에 저장되었습니다!")
                st.rerun()
            else:
                st.warning("⚠️ API Key를 입력해주세요.")
        
        if st.session_state.get('openai_api_key'):
            st.info("✅ API Key가 세션 상태에 설정되어 있습니다.")
            if st.button("🗑️ API Key 삭제"):
                del st.session_state.openai_api_key
                st.success("✅ API Key가 삭제되었습니다!")
                st.rerun()
    
    st.markdown("---")
    st.subheader("📝 Streamlit Cloud Secrets 설정")
    st.markdown("""
    **Streamlit Cloud에서 Secrets를 설정하는 방법:**
    
    1. Streamlit Cloud 대시보드에서 앱을 선택합니다.
    2. 'Settings' 또는 '⚙️' 아이콘을 클릭합니다.
    3. 'Secrets' 탭을 선택합니다.
    4. 아래 형식으로 입력합니다:
    
    ```toml
    [openai]
    api_key = "sk-your-api-key-here"
    ```
    
    5. 'Save' 버튼을 클릭하여 저장합니다.
    """)
    
    st.markdown("---")
    st.subheader("ℹ️ 시스템 정보")
    st.markdown("""
    ### LLM 기반 미술품 검증 시뮬레이터
    
    이 시스템은 OpenAI API를 사용하여 검증 봇과 고객 봇이 대화하며 미술품 검증을 시뮬레이션합니다.
    
    **주요 기능:**
    - 🤖 LLM 기반 검증 봇과 고객 봇
    - 💬 자연스러운 대화 시뮬레이션
    - 📊 실시간 진행 상황 및 통계
    - 💾 결과 다운로드
    
    **사용 방법:**
    1. 설정 탭에서 Open API Key를 입력합니다.
    2. 시뮬레이션 탭에서 대화 횟수를 설정합니다.
    3. '시뮬레이션 시작' 버튼을 클릭합니다.
    4. 결과를 확인하고 다운로드합니다.
    """)

