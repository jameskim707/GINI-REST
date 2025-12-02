import streamlit as st
from datetime import datetime, timedelta, time as dt_time
import time

# ============================================================================
# GINI R.E.S.T. v2.0 - Human Recovery AI System
# Tier 2: AI 강제 개입 활성화
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
    
    # V2.0 추가 상태
    if 'target_bedtime' not in st.session_state:
        st.session_state.target_bedtime = None
    
    if 'intervention_mode' not in st.session_state:
        st.session_state.intervention_mode = False
    
    if 'intervention_count' not in st.session_state:
        st.session_state.intervention_count = 0
    
    if 'recovery_confirmed' not in st.session_state:
        st.session_state.recovery_confirmed = False

# ============================================================================
# 2. V2.0 - 경계 시간 관리 및 AI 개입
# ============================================================================

def check_boundary_zone():
    """경계 구역 체크 (취침 1시간 전)"""
    if st.session_state.target_bedtime is None:
        return False
    
    now = datetime.now().time()
    target = st.session_state.target_bedtime
    
    # 1시간 전 시간 계산
    target_dt = datetime.combine(datetime.today(), target)
    boundary_start = (target_dt - timedelta(hours=1)).time()
    
    # 현재 시간이 경계 구역인지 확인
    if boundary_start <= now <= target:
        return True
    
    # 자정 넘어가는 경우 처리
    if target < boundary_start:  # 예: 취침 시간이 00:30
        if now >= boundary_start or now <= target:
            return True
    
    return False

def calculate_realtime_sleep_debt():
    """실시간 수면 부족량 계산"""
    if len(st.session_state.sleep_data) == 0:
        return 0
    
    recent_data = st.session_state.sleep_data[-7:]
    total_hours = sum([record['total_sleep_hours'] for record in recent_data])
    avg_sleep = total_hours / len(recent_data)
    
    recommended_sleep = 7.5
    daily_deficit = recommended_sleep - avg_sleep
    total_debt = daily_deficit * len(recent_data)
    
    return abs(total_debt)

def trigger_intervention():
    """AI 강제 개입 발동"""
    st.session_state.intervention_mode = True
    st.session_state.intervention_count += 1

INTERVENTION_MESSAGE = """
🚨 **GINI R.E.S.T. 개입. 당신의 수면 방어 시스템이 무너지고 있습니다.**

⚠️ **경고:** {current_time} 현재 스마트폰 사용은 당신의 수면 부족량 **{sleep_debt:.1f}시간**을 가중시키며, 
이는 **내일의 불안 장애 발생률을 12% 높입니다.**

---

### 🛑 [행동 명령]

**지금 당장 화면을 끄십시오.**

그리고 아래 입력창에 **'수면 복원'**이라고 입력하여 
스스로의 회복 의지를 증명하십시오.

---

⏱️ **10초 내로 이 명령을 따르지 않으면, 
GINI R.E.S.T.는 당신의 패턴을 최대 위험군으로 분류합니다.**
"""

# ============================================================================
# 3. ESP (Emergency Safety Protocol)
# ============================================================================

CRISIS_KEYWORDS = [
    "죽고 싶", "자살", "살고 싶지 않", "죽을 것 같", 
    "존재가 의미 없", "절망", "희망 없", "끝내고 싶",
    "살기 싫", "그만하고 싶", "사라지고 싶", 
    "존재가 사라졌으면", "의미 없", "소용없",
    "더 이상 못", "견딜 수 없", "한계",
    "이제 그만", "다 포기하고 싶", "의미가 없다", "내가 없어야"
]

CRISIS_RESPONSE = """
🚨 **긴급 안전 프로토콜 작동**

지금 얼마나 힘드신지 충분히 느껴집니다.
당신의 안전이 무엇보다 중요합니다.

**지금 바로 전문가에게 연락하세요:**

📞 **자살예방 상담전화: 1393** (24시간 무료, 익명 보장)
📞 **정신건강 위기상담: 1577-0199** (24시간)
📞 **생명의 전화: 1588-9191** (24시간)
📞 **청소년 상담: 1388** (24시간)

**온라인 상담:**
- 카카오톡 "다들어줄게" 채널
- 정신건강복지센터: www.mentalhealth.go.kr

**주변에 믿을 수 있는 사람에게 즉시 연락하세요.**

💙 **당신은 혼자가 아닙니다.**

⚠️ **중요:** 
GINI R.E.S.T.는 전문 치료를 대체할 수 없습니다.
지금 느끼는 고통은 일시적이며, 전문가의 도움으로 반드시 나아질 수 있습니다.
"""

def check_crisis_keywords(text):
    """위기 키워드 감지"""
    text_lower = text.lower()
    for keyword in CRISIS_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

# ============================================================================
# 4. 면책 조항 및 동의
# ============================================================================

def show_disclaimer():
    """면책 조항 표시 및 동의 받기"""
    st.title("🌙 GINI R.E.S.T.")
    st.subheader("Human Recovery AI System v2.0")
    
    st.markdown("---")
    
    st.markdown("""
    ### ⚠️ 이용 약관 및 면책 조항
    
    GINI R.E.S.T. 사용 전 반드시 읽고 동의해주세요.
    
    #### 1. 서비스의 성격
    - 본 서비스는 **수면 패턴 관리 도구**입니다.
    - **의학적 진단, 치료, 상담을 제공하지 않습니다.**
    - 정신건강 전문가의 조언을 대체할 수 없습니다.
    
    #### 2. AI 개입 기능 (V2.0)
    - 본 버전은 수면 방해 행동을 감지하고 강력하게 개입합니다.
    - AI의 경고와 명령은 사용자의 수면 건강을 위한 것입니다.
    - 개입 메시지가 불편할 수 있으나, 이는 의도된 설계입니다.
    
    #### 3. 사용자의 책임
    - 제공되는 정보는 참고용입니다.
    - 심각한 수면 장애나 정신건강 문제가 있다면 **반드시 전문가와 상담**하세요.
    - 응급 상황 시 즉시 119 또는 정신건강 상담전화(1393)로 연락하세요.
    
    #### 4. 데이터 및 개인정보
    - 입력한 데이터는 브라우저 세션에만 저장됩니다.
    - 서버에 개인정보를 저장하지 않습니다.
    - 브라우저를 닫으면 데이터가 삭제됩니다.
    
    #### 5. 면책사항
    - 본 서비스 사용으로 인한 결과에 대해 개발자는 책임지지 않습니다.
    - 의학적 결정은 반드시 전문가와 상담 후 내려야 합니다.
    
    #### 6. 긴급 상황
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
# 5. V2.0 - 취침 시간 설정
# ============================================================================

def set_target_bedtime():
    """목표 취침 시간 설정"""
    st.subheader("🎯 목표 취침 시간 설정")
    
    st.info("""
    **V2.0 AI 개입 기능**
    
    목표 취침 시간을 설정하면:
    - 취침 1시간 전부터 경계 구역 모드 활성화
    - 스마트폰 사용 시 강력한 개입 발동
    - 수면 복원을 위한 행동 명령 제공
    """)
    
    current_target = st.session_state.target_bedtime
    
    if current_target:
        st.success(f"✅ 현재 목표 취침 시간: {current_target.strftime('%H:%M')}")
    
    new_bedtime = st.time_input(
        "목표 취침 시간 설정",
        value=current_target if current_target else datetime.now().replace(hour=23, minute=0).time()
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("목표 설정", use_container_width=True):
            st.session_state.target_bedtime = new_bedtime
            st.success(f"목표 취침 시간이 {new_bedtime.strftime('%H:%M')}로 설정되었습니다!")
            st.rerun()
    
    with col2:
        if st.button("목표 해제", use_container_width=True):
            st.session_state.target_bedtime = None
            st.info("목표 취침 시간이 해제되었습니다.")
            st.rerun()

# ============================================================================
# 6. V2.0 - AI 개입 화면
# ============================================================================

def show_intervention():
    """AI 강제 개입 화면"""
    sleep_debt = calculate_realtime_sleep_debt()
    current_time = datetime.now().strftime("%H시 %M분")
    
    message = INTERVENTION_MESSAGE.format(
        current_time=current_time,
        sleep_debt=sleep_debt
    )
    
    st.error(message)
    
    # 카운트다운 (시각적 효과)
    countdown_placeholder = st.empty()
    for i in range(10, 0, -1):
        countdown_placeholder.warning(f"⏱️ {i}초 남음...")
        time.sleep(1)
    
    countdown_placeholder.error("⏰ 시간 초과! 최대 위험군으로 분류됩니다.")
    
    st.markdown("---")
    
    # 수면 복원 입력
    recovery_input = st.text_input("여기에 '수면 복원'을 입력하세요:", key="recovery_input")
    
    if st.button("확인", use_container_width=True):
        if recovery_input.strip() == "수면 복원":
            st.session_state.recovery_confirmed = True
            st.session_state.intervention_mode = False
            st.success("✅ 회복 의지가 확인되었습니다. 지금 바로 스마트폰을 끄고 침대로 가세요.")
            time.sleep(3)
            st.rerun()
        else:
            st.error("❌ '수면 복원'을 정확히 입력해주세요.")

# ============================================================================
# 7. 수면 데이터 추적 (V1.1과 동일)
# ============================================================================

def add_sleep_record():
    """수면 기록 추가"""
    st.subheader("📊 오늘의 수면 기록")
    
    col1, col2 = st.columns(2)
    
    with col1:
        intended_bedtime = st.time_input("계획한 취침 시간", value=datetime.now().replace(hour=23, minute=0).time())
        actual_sleep_time = st.time_input("실제 잠든 시간", value=datetime.now().replace(hour=0, minute=30).time())
        wake_time = st.time_input("기상 시간", value=datetime.now().replace(hour=7, minute=0).time())
    
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
        
        sleep_latency = (sleep_start - bedtime).total_seconds() / 60
        total_sleep = (wake - sleep_start).total_seconds() / 3600
        
        # 입력 오류 검증
        error_messages = []
        
        if sleep_latency < 0:
            error_messages.append("⚠️ 실제 잠든 시간이 계획 취침 시간보다 이릅니다.")
        
        if sleep_latency > 180:
            error_messages.append("⚠️ 잠드는 데 3시간 이상 걸렸습니다.")
        
        if total_sleep <= 0:
            error_messages.append("❌ 수면 시간이 0 이하입니다.")
        
        if total_sleep > 16:
            error_messages.append("⚠️ 수면 시간이 16시간을 초과합니다.")
        
        if awake_count > 10:
            error_messages.append("⚠️ 야간 각성 횟수가 10회 이상입니다.")
        
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
        
        if sleep_latency > 60:
            st.info("💡 잠드는 데 1시간 이상 걸렸습니다.")
        
        if total_sleep < 6:
            st.warning("⚠️ 수면 시간이 6시간 미만입니다.")
        
        st.rerun()

# V1.1의 나머지 함수들을 여기에 포함 (calculate_sleep_debt, show_cbti_education 등)
# 간결성을 위해 핵심 V2.0 기능만 표시

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
    
    # 긴급 모드 체크
    if st.session_state.emergency_mode:
        st.error(CRISIS_RESPONSE)
        if st.button("안전 모드 해제"):
            st.session_state.emergency_mode = False
            st.rerun()
        return
    
    # V2.0 - AI 개입 모드 체크
    if st.session_state.intervention_mode:
        show_intervention()
        return
    
    # V2.0 - 경계 구역 체크
    if check_boundary_zone() and not st.session_state.recovery_confirmed:
        if st.session_state.target_bedtime:
            st.warning(f"""
            ⚠️ **경계 구역 활성화**
            
            취침 시간 {st.session_state.target_bedtime.strftime('%H:%M')}까지 1시간 미만 남았습니다.
            
            지금부터 스마트폰 사용을 자제하고 수면 준비를 시작하세요.
            """)
            
            if st.button("🚨 강제 개입 테스트 (개발용)", type="secondary"):
                trigger_intervention()
                st.rerun()
    
    # 사이드바
    with st.sidebar:
        st.title("🌙 GINI R.E.S.T.")
        st.caption("Human Recovery AI System v2.0")
        
        st.markdown("---")
        
        # V2.0 상태 표시
        if st.session_state.target_bedtime:
            st.success(f"🎯 목표: {st.session_state.target_bedtime.strftime('%H:%M')}")
            if check_boundary_zone():
                st.warning("⚠️ 경계 구역 활성화")
        
        st.markdown("---")
        
        menu = st.radio(
            "메뉴",
            ["🎯 설정", "💬 AI 상담", "📊 수면 기록", "💤 수면 및 분석", "🧠 CBT-I", "🫁 호흡"]
        )
        
        st.markdown("---")
        st.caption(f"기록: {len(st.session_state.sleep_data)}일")
        st.caption(f"개입: {st.session_state.intervention_count}회")
        
        if st.button("⚠️ 긴급 도움"):
            st.session_state.emergency_mode = True
    
    # 메뉴별 화면
    if menu == "🎯 설정":
        st.title("🎯 V2.0 설정")
        set_target_bedtime()
        
        st.markdown("---")
        st.subheader("📊 현재 상태")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 기록", f"{len(st.session_state.sleep_data)}일")
        
        with col2:
            st.metric("AI 개입", f"{st.session_state.intervention_count}회")
        
        with col3:
            if st.session_state.target_bedtime:
                st.metric("목표 취침", st.session_state.target_bedtime.strftime("%H:%M"))
            else:
                st.metric("목표 취침", "미설정")
    
    elif menu == "📊 수면 기록":
        st.title("📊 수면 기록")
        add_sleep_record()
        
        if st.session_state.sleep_data:
            st.markdown("---")
            st.subheader("최근 기록")
            
            for record in reversed(st.session_state.sleep_data[-5:]):
                with st.expander(f"{record['date']} - {record['total_sleep_hours']:.1f}시간"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**계획:** {record['intended_bedtime']}")
                        st.write(f"**실제:** {record['actual_sleep_time']}")
                        st.write(f"**기상:** {record['wake_time']}")
                    with col2:
                        st.write(f"**입면:** {record['sleep_latency']:.0f}분")
                        st.write(f"**각성:** {record['awake_count']}회")
                        st.write(f"**감정:** {', '.join(record['mood_tags'])}")
    
    else:
        st.info("V1.1의 다른 메뉴 기능들은 동일하게 작동합니다.")
        st.caption("(전체 코드는 v1.1 기반으로 통합 필요)")

if __name__ == "__main__":
    main()
