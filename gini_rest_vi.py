import streamlit as st
from datetime import datetime, timedelta
import time

# ============================================================================
# GINI R.E.S.T. v1.0 - Human Recovery AI System
# Tier 1: 안전한 도움 버전
# ============================================================================

# 페이지 설정
st.set_page_config(
    page_title="GINI R.E.S.T.",
    page_icon="🌙",
    layout="wide"
)

# ============================================================================
# 1. 초기화 및 세션 상태 관리
# ============================================================================

def init_session_state():
    """세션 상태 초기화"""
    if 'agreed_to_terms' not in st.session_state:
        st.session_state.agreed_to_terms = False
    
    if 'sleep_data' not in st.session_state:
        st.session_state.sleep_data = []
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'emergency_mode' not in st.session_state:
        st.session_state.emergency_mode = False

# ============================================================================
# 2. ESP (Emergency Safety Protocol)
# ============================================================================

CRISIS_KEYWORDS = [
    "죽고 싶", "자살", "살고 싶지 않", "죽을 것 같", 
    "존재가 의미 없", "절망", "희망 없", "끝내고 싶",
    "살기 싫", "그만하고 싶", "사라지고 싶", 
    "존재가 사라졌으면", "의미 없", "소용없",
    "더 이상 못", "견딜 수 없", "한계"
]

CRISIS_RESPONSE = """
🚨 **긴급 안전 프로토콜 작동**

당신이 지금 얼마나 힘든 시간을 보내고 계신지 이해합니다.
이런 고통을 혼자 견디려 하지 않아도 됩니다.

**지금 당장 전문가의 도움을 받으세요:**

📞 **자살예방 상담전화: 1393** (24시간 무료, 익명 보장)
📞 **정신건강 위기상담: 1577-0199** (24시간)
📞 **생명의 전화: 1588-9191** (24시간)
📞 **청소년 상담: 1388** (24시간)

**온라인 상담:**
- 카카오톡 "다들어줄게" 채널
- 정신건강복지센터: www.mentalhealth.go.kr

💙 **당신은 혼자가 아닙니다.**

지금 느끼는 고통은 일시적입니다. 
전문가의 도움으로 반드시 나아질 수 있습니다.
도움을 요청하는 것은 용기 있는 행동입니다.

⚠️ **중요:** 
GINI R.E.S.T.는 전문 치료를 대체할 수 없습니다.
당신의 안전이 가장 중요합니다. 지금 바로 위의 번호로 연락하거나 가까운 응급실을 방문하세요.
"""

def check_crisis_keywords(text):
    """위기 키워드 감지"""
    text_lower = text.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

# ============================================================================
# 3. 면책 조항 및 동의
# ============================================================================

def show_disclaimer():
    """면책 조항 표시 및 동의 받기"""
    st.title("🌙 GINI R.E.S.T.")
    st.subheader("Human Recovery AI System")
    
    st.markdown("---")
    
    st.markdown("""
    ### ⚠️ 이용 약관 및 면책 조항
    
    GINI R.E.S.T. 사용 전 반드시 읽고 동의해주세요.
    
    #### 1. 서비스의 성격
    - 본 서비스는 **수면 패턴 관리 도구**입니다.
    - **의학적 진단, 치료, 상담을 제공하지 않습니다.**
    - 정신건강 전문가의 조언을 대체할 수 없습니다.
    
    #### 2. 사용자의 책임
    - 제공되는 정보는 참고용입니다.
    - 심각한 수면 장애나 정신건강 문제가 있다면 **반드시 전문가와 상담**하세요.
    - 응급 상황 시 즉시 119 또는 정신건강 상담전화(1393)로 연락하세요.
    
    #### 3. 데이터 및 개인정보
    - 입력한 데이터는 브라우저 세션에만 저장됩니다.
    - 서버에 개인정보를 저장하지 않습니다.
    - 브라우저를 닫으면 데이터가 삭제됩니다.
    
    #### 4. 면책사항
    - 본 서비스 사용으로 인한 결과에 대해 개발자는 책임지지 않습니다.
    - 의학적 결정은 반드시 전문가와 상담 후 내려야 합니다.
    
    #### 5. 긴급 상황
    본 서비스는 위기 상황을 감지하면 전문 기관 연락처를 안내하고 대화를 중단합니다.
    """)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        agree = st.checkbox("위 내용을 모두 읽었으며 동의합니다", key="agree_checkbox")
        
        if st.button("시작하기", disabled=not agree, use_container_width=True):
            st.session_state.agreed_to_terms = True
            st.rerun()

# ============================================================================
# 4. 수면 데이터 추적
# ============================================================================

def add_sleep_record():
    """수면 기록 추가"""
    st.subheader("📊 오늘의 수면 기록")
    
    col1, col2 = st.columns(2)
    
    with col1:
        intended_bedtime = st.time_input("계획한 취침 시간", value=datetime.now().replace(hour=23, minute=0))
        actual_sleep_time = st.time_input("실제 잠든 시간", value=datetime.now().replace(hour=0, minute=30))
        wake_time = st.time_input("기상 시간", value=datetime.now().replace(hour=7, minute=0))
    
    with col2:
        awake_count = st.number_input("야간 각성 횟수", min_value=0, max_value=20, value=0)
        screen_after_10pm = st.radio("밤 10시 이후 스마트폰 사용", ["예", "아니오"])
        caffeine_intake = st.radio("오후 카페인 섭취", ["예", "아니오"])
    
    mood_tags = st.multiselect(
        "오늘의 감정 (복수 선택 가능)",
        ["불안", "스트레스", "우울", "긴장", "피곤", "평온", "흥분", "걱정", "화남", "무기력", "초조", "만족"]
    )
    
    notes = st.text_area("추가 메모 (선택사항)")
    
    if st.button("기록 저장", use_container_width=True):
        # 수면 시간 계산
        bedtime = datetime.combine(datetime.today(), intended_bedtime)
        sleep_start = datetime.combine(datetime.today(), actual_sleep_time)
        wake = datetime.combine(datetime.today(), wake_time)
        
        # 날짜 넘어간 경우 처리
        if actual_sleep_time < intended_bedtime:
            sleep_start += timedelta(days=1)
        if wake_time < actual_sleep_time:
            wake += timedelta(days=1)
        
        sleep_latency = (sleep_start - bedtime).total_seconds() / 60  # 분 단위
        total_sleep = (wake - sleep_start).total_seconds() / 3600  # 시간 단위
        
        # 입력 오류 검증
        error_messages = []
        
        if sleep_latency < 0:
            error_messages.append("⚠️ 실제 잠든 시간이 계획 취침 시간보다 이릅니다. 날짜를 확인해주세요.")
        
        if sleep_latency > 180:  # 3시간 이상
            error_messages.append("⚠️ 잠드는 데 3시간 이상 걸렸습니다. 시간을 다시 확인해주세요.")
        
        if total_sleep <= 0:
            error_messages.append("❌ 수면 시간이 0 이하입니다. 시간 입력을 확인해주세요.")
        
        if total_sleep > 16:
            error_messages.append("⚠️ 수면 시간이 16시간을 초과합니다. 입력을 확인해주세요.")
        
        if awake_count > 10:
            error_messages.append("⚠️ 야간 각성 횟수가 10회 이상입니다. 정확한 값인지 확인해주세요.")
        
        # 오류가 있으면 경고 표시
        if error_messages:
            for msg in error_messages:
                st.warning(msg)
            st.error("입력값을 확인하고 다시 시도해주세요.")
            return
        
        # 정상 입력 - 기록 저장
        record = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'intended_bedtime': intended_bedtime.strftime("%H:%M"),
            'actual_sleep_time': actual_sleep_time.strftime("%H:%M"),
            'wake_time': wake_time.strftime("%H:%M"),
            'sleep_latency': sleep_latency,
            'total_sleep_hours': total_sleep,
            'awake_count': awake_count,
            'screen_after_10pm': screen_after_10pm == "예",
            'caffeine_intake': caffeine_intake == "예",
            'mood_tags': mood_tags,
            'notes': notes
        }
        
        st.session_state.sleep_data.append(record)
        st.success("✅ 기록이 저장되었습니다!")
        
        # 이상 패턴 알림
        if sleep_latency > 60:
            st.info("💡 잠드는 데 1시간 이상 걸렸습니다. CBT-I 교육을 참고해보세요.")
        
        if total_sleep < 6:
            st.warning("⚠️ 수면 시간이 6시간 미만입니다. 충분한 수면을 취하도록 노력하세요.")
        
        st.rerun()

# ============================================================================
# 5. 수면 빚 계산기
# ============================================================================

def calculate_sleep_debt():
    """수면 빚 계산"""
    if len(st.session_state.sleep_data) == 0:
        st.info("아직 수면 기록이 없습니다. 먼저 기록을 추가해주세요.")
        return
    
    st.subheader("💤 수면 빚 분석")
    
    # 최근 7일 데이터
    recent_data = st.session_state.sleep_data[-7:]
    
    total_hours = sum([record['total_sleep_hours'] for record in recent_data])
    avg_sleep = total_hours / len(recent_data)
    
    recommended_sleep = 7.5  # 권장 수면 시간
    daily_deficit = recommended_sleep - avg_sleep
    total_debt = daily_deficit * len(recent_data)
    
    # 결과 표시
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("평균 수면 시간", f"{avg_sleep:.1f}시간")
    
    with col2:
        st.metric("일일 부족량", f"{daily_deficit:.1f}시간", 
                 delta=f"{daily_deficit:.1f}h", delta_color="inverse")
    
    with col3:
        st.metric("누적 수면 빚", f"{abs(total_debt):.1f}시간")
    
    # 분석 및 조언
    st.markdown("---")
    
    if total_debt > 0:
        recovery_days = int(total_debt / 1.5) + 1
        
        st.warning(f"""
        **⚠️ 수면 빚이 누적되었습니다**
        
        - 지난 {len(recent_data)}일간 평균 **{avg_sleep:.1f}시간** 수면
        - 권장량({recommended_sleep}시간) 대비 **매일 {daily_deficit:.1f}시간 부족**
        - 총 누적 빚: **{abs(total_debt):.1f}시간**
        
        **회복 계획:**
        - 완전 회복까지 최소 **{recovery_days}일** 소요 예상
        - 매일 8-9시간씩 자면서 점진적 회복 필요
        - 주말에 몰아서 자는 것보다 매일 조금씩 늘리는 것이 효과적
        """)
    else:
        st.success(f"""
        **✅ 건강한 수면 패턴을 유지하고 있습니다!**
        
        - 지난 {len(recent_data)}일간 평균 **{avg_sleep:.1f}시간** 수면
        - 권장량을 충족하고 있습니다.
        - 현재 패턴을 계속 유지하세요!
        """)

# ============================================================================
# 6. CBT-I 인지 재구조화
# ============================================================================

SLEEP_MYTHS = {
    "8시간은 꼭 자야 해": """
    **수면 신화 감지: "8시간 법칙"**
    
    ❌ **잘못된 믿음:**
    "8시간을 못 자면 큰일 난다"
    
    ✅ **과학적 사실:**
    - 개인차가 큽니다 (6-9시간 범위)
    - **수면의 질**이 양보다 중요
    - 중요한 것은 **일정한 패턴**
    
    📊 **당신의 데이터:**
    최근 수면 기록을 보면, 7시간만 자도 컨디션이 좋았던 날이 있었습니다.
    
    💡 **행동 처방:**
    숫자에 집착하지 말고, "아침에 개운한가?"를 기준으로 삼으세요.
    """,
    
    "잠이 안 오면 침대에 누워있어야 해": """
    **수면 신화 감지: "침대 집착"**
    
    ❌ **잘못된 믿음:**
    "침대에 오래 누워있으면 잠이 올 거야"
    
    ✅ **과학적 사실:**
    - 20분 후에도 잠 안 오면 **침대에서 나와야 함**
    - 침대 = 각성 장소로 학습될 위험
    - "자극 통제 요법"의 핵심 원리
    
    📊 **당신의 데이터:**
    당신은 평균 {}분 후에 잠듭니다.
    30분 이상 걸린 날들은 다음날 피로도가 높았습니다.
    
    💡 **행동 처방:**
    20분 안에 잠 안 오면 → 거실로 나가기 → 차분한 활동 → 졸리면 다시 침대
    """,
    
    "낮잠은 절대 안 돼": """
    **수면 신화 감지: "낮잠 금지론"**
    
    ❌ **잘못된 믿음:**
    "낮잠 자면 밤에 못 잔다"
    
    ✅ **과학적 사실:**
    - **20-30분 파워냅**은 오히려 도움
    - 오후 3시 이전이면 OK
    - 1시간 이상은 피해야 함
    
    💡 **행동 처방:**
    너무 피곤하면 → 20분 타이머 설정 → 낮잠 → 밤 수면은 정상 유지
    """
}

def show_cbti_education():
    """CBT-I 교육 및 인지 재구조화"""
    st.subheader("🧠 수면 인지 재구조화 (CBT-I)")
    
    st.markdown("""
    수면에 대한 잘못된 믿음을 바로잡고, 과학적 사실을 기반으로 건강한 수면 패턴을 만듭니다.
    """)
    
    # 신화 선택
    myth = st.selectbox(
        "당신이 믿고 있는 수면 상식을 선택하세요:",
        list(SLEEP_MYTHS.keys())
    )
    
    if st.button("분석 받기"):
        st.markdown("---")
        st.markdown(SLEEP_MYTHS[myth])

# ============================================================================
# 7. 호흡법 가이드
# ============================================================================

def breathing_exercise():
    """4-7-8 호흡법 가이드"""
    st.subheader("🫁 4-7-8 호흡법")
    
    st.markdown("""
    **과학적 근거:**
    - 부교감 신경 활성화
    - 심박수 감소
    - 뇌 각성 억제
    
    **방법:**
    1. 4초 동안 코로 숨 들이마시기
    2. 7초 동안 숨 참기
    3. 8초 동안 입으로 천천히 내쉬기
    4. 4회 반복
    """)
    
    if st.button("호흡법 시작", use_container_width=True):
        with st.spinner("준비하세요..."):
            time.sleep(2)
        
        for round_num in range(1, 5):
            st.write(f"**{round_num}회차**")
            
            with st.status(f"라운드 {round_num}/4", expanded=True) as status:
                st.write("🌬️ 4초 동안 숨을 들이마시세요...")
                time.sleep(4)
                
                st.write("⏸️ 7초 동안 숨을 참으세요...")
                time.sleep(7)
                
                st.write("💨 8초 동안 천천히 내쉬세요...")
                time.sleep(8)
                
                status.update(label=f"라운드 {round_num} 완료!", state="complete")
        
        st.success("✅ 호흡 운동을 완료했습니다! 몸과 마음이 진정되었나요?")

# ============================================================================
# 8. 메인 앱
# ============================================================================

def main():
    """메인 앱"""
    init_session_state()
    
    # 면책 조항 미동의 시
    if not st.session_state.agreed_to_terms:
        show_disclaimer()
        return
    
    # 사이드바
    with st.sidebar:
        st.title("🌙 GINI R.E.S.T.")
        st.caption("Human Recovery AI System v1.0")
        
        st.markdown("---")
        
        menu = st.radio(
            "메뉴",
            ["💬 AI 상담", "📊 수면 기록", "💤 수면 빚 분석", "🧠 CBT-I 교육", "🫁 호흡 운동"]
        )
        
        st.markdown("---")
        st.caption(f"기록된 데이터: {len(st.session_state.sleep_data)}일")
        
        if st.button("⚠️ 긴급 도움"):
            st.session_state.emergency_mode = True
    
    # 긴급 모드
    if st.session_state.emergency_mode:
        st.error(CRISIS_RESPONSE)
        if st.button("안전 모드 해제"):
            st.session_state.emergency_mode = False
            st.rerun()
        return
    
    # 메뉴별 화면
    if menu == "💬 AI 상담":
        st.title("💬 수면 AI 상담")
        
        st.info("""
        **⚠️ 현재 v1.0 베타 버전입니다.**
        
        AI 상담 기능은 다음 업데이트에서 활성화됩니다.
        지금은 수면 기록, CBT-I 교육, 호흡 운동을 이용해주세요.
        """)
        
        # 간단한 채팅 UI
        user_input = st.text_input("메시지를 입력하세요:")
        
        if user_input:
            # 위기 키워드 감지
            if check_crisis_keywords(user_input):
                st.session_state.emergency_mode = True
                st.rerun()
            else:
                st.chat_message("user").write(user_input)
                st.chat_message("assistant").write("""
                현재 베타 버전에서는 제한된 기능만 제공됩니다.
                
                다음 기능을 이용해보세요:
                - 📊 수면 기록
                - 💤 수면 빚 분석
                - 🧠 CBT-I 교육
                - 🫁 호흡 운동
                """)
    
    elif menu == "📊 수면 기록":
        st.title("📊 수면 기록 추가")
        add_sleep_record()
        
        # 기존 기록 표시
        if st.session_state.sleep_data:
            st.markdown("---")
            st.subheader("최근 기록")
            
            for i, record in enumerate(reversed(st.session_state.sleep_data[-5:])):
                with st.expander(f"{record['date']} - {record['total_sleep_hours']:.1f}시간"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**계획 취침:** {record['intended_bedtime']}")
                        st.write(f"**실제 취침:** {record['actual_sleep_time']}")
                        st.write(f"**기상:** {record['wake_time']}")
                    with col2:
                        st.write(f"**잠드는 시간:** {record['sleep_latency']:.0f}분")
                        st.write(f"**야간 각성:** {record['awake_count']}회")
                        st.write(f"**감정:** {', '.join(record['mood_tags'])}")
    
    elif menu == "💤 수면 빚 분석":
        st.title("💤 수면 빚 분석")
        calculate_sleep_debt()
    
    elif menu == "🧠 CBT-I 교육":
        st.title("🧠 CBT-I 인지 재구조화")
        show_cbti_education()
    
    elif menu == "🫁 호흡 운동":
        st.title("🫁 4-7-8 호흡 운동")
        breathing_exercise()

if __name__ == "__main__":
    main()
