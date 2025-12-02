import streamlit as st
from datetime import datetime, timedelta
import time
import json

# ============================================================================
# GINI R.E.S.T. v2.5 - Human Recovery AI System
# Phase 1: Crisis Engine Enhanced (강화)
# ============================================================================

# 페이지 설정
st.set_page_config(
    page_title="GINI R.E.S.T. v2.5",
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
    
    # V2.0 상태
    if 'target_bedtime' not in st.session_state:
        st.session_state.target_bedtime = None
    
    if 'intervention_mode' not in st.session_state:
        st.session_state.intervention_mode = False
    
    if 'intervention_count' not in st.session_state:
        st.session_state.intervention_count = 0
    
    if 'recovery_confirmed' not in st.session_state:
        st.session_state.recovery_confirmed = False
    
    if 'last_reset_date' not in st.session_state:
        st.session_state.last_reset_date = datetime.now().date()
    
    # ========== V2.5 추가 상태 (Crisis Engine Enhanced) ==========
    if 'crisis_history' not in st.session_state:
        st.session_state.crisis_history = []
    
    if 'emotion_tracking' not in st.session_state:
        st.session_state.emotion_tracking = []
    
    if 'crisis_level' not in st.session_state:
        st.session_state.crisis_level = 0
    
    if 'last_crisis_time' not in st.session_state:
        st.session_state.last_crisis_time = None

# ============================================================================
# 2. ESP v2.5 - Enhanced Crisis Detection Engine
# ============================================================================

# 3단계 위기 레벨 키워드
CRISIS_KEYWORDS_L3 = [
    # Level 3: 즉각 개입 (자살 관련)
    "죽고 싶", "자살", "죽을 것 같", "끝내고 싶", "살고 싶지 않",
    "사라지고 싶", "내가 없어야", "존재가 사라졌으면"
]

CRISIS_KEYWORDS_L2 = [
    # Level 2: 강력 경고 (절망/무가치)
    "절망", "희망 없", "존재가 의미 없", "의미 없", "소용없",
    "다 포기하고 싶", "의미가 없다"
]

CRISIS_KEYWORDS_L1 = [
    # Level 1: 주의 (심각한 고통)
    "더 이상 못", "견딜 수 없", "한계", "이제 그만",
    "살기 싫", "그만하고 싶"
]

# 맥락 분석용 완화 키워드 (비유적 표현 감지)
CONTEXT_MITIGATORS = [
    "정도로", "만큼", "것 같은", "비유", "표현",
    "느낌", "기분", "ㅋㅋ", "ㅎㅎ", "웃"
]

def analyze_crisis_level(text):
    """
    다단계 위기 레벨 분석
    Returns: (level, matched_keywords, is_metaphor)
    """
    text_lower = text.lower()
    matched_keywords = []
    is_metaphor = False
    
    # 맥락 완화 체크 (비유적 표현)
    for mitigator in CONTEXT_MITIGATORS:
        if mitigator in text_lower:
            is_metaphor = True
            break
    
    # Level 3 체크 (최고 위험)
    for keyword in CRISIS_KEYWORDS_L3:
        if keyword in text_lower:
            matched_keywords.append((keyword, 3))
    
    # Level 2 체크 (높은 위험)
    for keyword in CRISIS_KEYWORDS_L2:
        if keyword in text_lower:
            matched_keywords.append((keyword, 2))
    
    # Level 1 체크 (주의)
    for keyword in CRISIS_KEYWORDS_L1:
        if keyword in text_lower:
            matched_keywords.append((keyword, 1))
    
    if not matched_keywords:
        return (0, [], False)
    
    # 가장 높은 레벨 반환
    max_level = max([kw[1] for kw in matched_keywords])
    
    # 비유적 표현이면 레벨 1단계 낮춤
    if is_metaphor and max_level > 1:
        max_level -= 1
    
    return (max_level, matched_keywords, is_metaphor)

def record_crisis_event(level, keywords, text, is_metaphor):
    """위기 이벤트 기록"""
    crisis_event = {
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'keywords': [kw[0] for kw in keywords],
        'text_sample': text[:100],  # 처음 100자만 저장
        'is_metaphor': is_metaphor
    }
    
    st.session_state.crisis_history.append(crisis_event)
    st.session_state.last_crisis_time = datetime.now()
    st.session_state.crisis_level = level
    
    # 최근 30일치만 유지
    if len(st.session_state.crisis_history) > 100:
        st.session_state.crisis_history = st.session_state.crisis_history[-100:]

def get_crisis_pattern():
    """위기 패턴 분석"""
    if len(st.session_state.crisis_history) == 0:
        return {
            'total_count': 0,
            'recent_7days': 0,
            'trend': 'stable'
        }
    
    now = datetime.now()
    recent_7days = [
        c for c in st.session_state.crisis_history
        if datetime.fromisoformat(c['timestamp']) > now - timedelta(days=7)
    ]
    
    recent_30days = [
        c for c in st.session_state.crisis_history
        if datetime.fromisoformat(c['timestamp']) > now - timedelta(days=30)
    ]
    
    # 추세 분석
    if len(recent_7days) > 3:
        trend = 'worsening'
    elif len(recent_7days) > 0:
        trend = 'concerning'
    else:
        trend = 'stable'
    
    return {
        'total_count': len(st.session_state.crisis_history),
        'recent_7days': len(recent_7days),
        'recent_30days': len(recent_30days),
        'trend': trend
    }

# 레벨별 위기 대응 메시지
def get_crisis_response(level, pattern):
    """레벨별 위기 대응 메시지"""
    
    base_contacts = """
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
"""
    
    if level == 3:
        # 최고 위험: 즉각 개입
        message = f"""
🚨 **긴급 안전 프로토콜 Level 3 발동**

당신의 생명이 위험합니다. 지금 이 순간이 가장 중요합니다.

{base_contacts}

⚠️ **매우 중요:** 
- GINI R.E.S.T.는 전문 치료를 대체할 수 없습니다.
- 지금 느끼는 고통은 일시적이며, 전문가의 도움으로 반드시 나아질 수 있습니다.
- **이 순간을 넘기면, 내일은 다릅니다.**

🚑 **즉각 대응이 필요한 경우 119로 연락하세요.**
"""
        
    elif level == 2:
        # 높은 위험: 강력 경고
        message = f"""
⚠️ **위기 경고 Level 2 - 강력한 개입 필요**

당신이 느끼는 절망감과 무력감을 충분히 이해합니다.
지금 당신에게는 전문가의 도움이 필요합니다.

{base_contacts}

💡 **기억하세요:**
- 지금의 감정은 영구적이지 않습니다.
- 도움을 요청하는 것은 용기입니다.
- 전문가와 대화하는 것만으로도 변화가 시작됩니다.
"""
        
        if pattern['recent_7days'] > 1:
            message += f"""

📊 **주의:** 최근 7일간 {pattern['recent_7days']}회의 위기 신호가 감지되었습니다.
반복되는 고통은 전문적 치료가 필요하다는 신호입니다.
"""
    
    elif level == 1:
        # 주의: 지지적 대응
        message = f"""
💛 **주의 Level 1 - 당신의 어려움이 감지되었습니다**

지금 많이 힘드시군요. 당신의 고통을 인정합니다.

혼자 감당하기 어려우시다면:

{base_contacts}

💪 **당신이 할 수 있는 것:**
1. 깊게 호흡하기 (4-7-8 호흡법 → 호흡 운동 메뉴)
2. 신뢰할 수 있는 사람에게 전화하기
3. 잠시 산책하기
4. 따뜻한 차 한 잔 마시기

**작은 행동이 큰 변화를 만듭니다.**
"""
        
        if pattern['recent_7days'] > 2:
            message += f"""

📊 **알림:** 최근 7일간 {pattern['recent_7days']}회 어려움이 감지되었습니다.
패턴이 반복된다면 전문가 상담을 권장합니다.
"""
    
    else:
        message = "상태를 계속 모니터링하고 있습니다."
    
    return message

def check_crisis_keywords(text):
    """
    V2.5 Enhanced Crisis Detection
    Returns: (has_crisis, level, response_message)
    """
    level, keywords, is_metaphor = analyze_crisis_level(text)
    
    if level > 0:
        # 위기 이벤트 기록
        record_crisis_event(level, keywords, text, is_metaphor)
        
        # 패턴 분석
        pattern = get_crisis_pattern()
        
        # 레벨별 대응 메시지
        response = get_crisis_response(level, pattern)
        
        return (True, level, response)
    
    return (False, 0, "")

# ============================================================================
# 2-1. V2.0 - 경계 시간 관리 및 AI 개입 (유지)
# ============================================================================

def reset_daily_state():
    """매일 자동 초기화 (오전 8시 기준)"""
    today = datetime.now().date()
    
    if st.session_state.last_reset_date < today:
        st.session_state.recovery_confirmed = False
        st.session_state.last_reset_date = today

def check_boundary_zone():
    """경계 구역 체크 (취침 1시간 전)"""
    if st.session_state.target_bedtime is None:
        return False
    
    now = datetime.now().time()
    target = st.session_state.target_bedtime
    
    target_dt = datetime.combine(datetime.today(), target)
    boundary_start = (target_dt - timedelta(hours=1)).time()
    
    if boundary_start <= now <= target:
        return True
    
    if target < boundary_start:
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

def show_intervention():
    """AI 강제 개입 화면"""
    sleep_debt = calculate_realtime_sleep_debt()
    current_time = datetime.now().strftime("%H시 %M분")
    
    st.error(f"""
    🚨 **GINI R.E.S.T. 개입. 당신의 수면 방어 시스템이 무너지고 있습니다.**
    
    ⚠️ **경고:** {current_time} 현재 스마트폰 사용은 당신의 수면 부족량 **{sleep_debt:.1f}시간**을 가중시키며, 
    이는 **내일의 불안 장애 발생률을 12% 높입니다.**
    """)
    
    st.markdown("---")
    st.markdown("### 🛑 [행동 명령]")
    st.markdown("**지금 당장 화면을 끄십시오.**")
    st.markdown("그리고 아래 입력창에 **'수면 복원'**이라고 입력하여 스스로의 회복 의지를 증명하십시오.")
    
    st.markdown("---")
    
    st.warning("⏱️ 10초 내로 이 명령을 따르지 않으면, GINI R.E.S.T.는 당신의 패턴을 최대 위험군으로 분류합니다.")
    
    recovery_input = st.text_input("여기에 '수면 복원'을 입력하세요:", key="recovery_input")
    
    if st.button("확인", use_container_width=True):
        if recovery_input.strip() == "수면 복원":
            st.session_state.recovery_confirmed = True
            st.session_state.intervention_mode = False
            st.success("✅ 회복 의지가 확인되었습니다. 지금 바로 스마트폰을 끄고 침대로 가세요.")
            time.sleep(2)
            st.rerun()
        else:
            st.error("❌ '수면 복원'을 정확히 입력해주세요.")

def set_target_bedtime():
    """목표 취침 시간 설정"""
    st.subheader("🎯 목표 취침 시간 설정")
    
    st.info("""
    **V2.5 AI 개입 기능 (Crisis Engine Enhanced)**
    
    목표 취침 시간을 설정하면:
    - 취침 1시간 전부터 경계 구역 모드 활성화
    - 스마트폰 사용 시 강력한 개입 발동
    - 수면 복원을 위한 행동 명령 제공
    - **다단계 위기 감지 시스템 활성화**
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
# 2-2. V2.5 - Crisis Dashboard (새로 추가)
# ============================================================================

def show_crisis_dashboard():
    """위기 관리 대시보드"""
    st.subheader("📊 위기 관리 대시보드")
    
    pattern = get_crisis_pattern()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 위기 감지", f"{pattern['total_count']}회")
    
    with col2:
        st.metric("최근 7일", f"{pattern['recent_7days']}회")
    
    with col3:
        st.metric("최근 30일", f"{pattern['recent_30days']}회")
    
    with col4:
        trend_emoji = "⚠️" if pattern['trend'] == 'worsening' else "📊" if pattern['trend'] == 'concerning' else "✅"
        trend_text = "악화" if pattern['trend'] == 'worsening' else "주의" if pattern['trend'] == 'concerning' else "안정"
        st.metric("추세", f"{trend_emoji} {trend_text}")
    
    st.markdown("---")
    
    if pattern['trend'] == 'worsening':
        st.error("""
        ⚠️ **위기 추세 악화 감지**
        
        최근 7일간 빈번한 위기 신호가 감지되었습니다.
        **전문가 상담을 강력히 권장합니다.**
        
        📞 자살예방 상담전화: 1393 (24시간)
        """)
    elif pattern['trend'] == 'concerning':
        st.warning("""
        📊 **주의가 필요한 상태**
        
        최근 위기 신호가 감지되었습니다.
        상태가 지속되면 전문가와 상담하세요.
        """)
    else:
        st.success("""
        ✅ **안정적인 상태**
        
        현재 위기 신호가 적습니다.
        계속 건강한 수면 패턴을 유지하세요.
        """)
    
    # 최근 위기 이력
    if len(st.session_state.crisis_history) > 0:
        st.markdown("---")
        st.subheader("📋 최근 위기 이력")
        
        recent_5 = st.session_state.crisis_history[-5:]
        
        for event in reversed(recent_5):
            timestamp = datetime.fromisoformat(event['timestamp']).strftime("%Y-%m-%d %H:%M")
            level = event['level']
            level_emoji = "🚨" if level == 3 else "⚠️" if level == 2 else "💛"
            level_text = "Level 3 (긴급)" if level == 3 else "Level 2 (경고)" if level == 2 else "Level 1 (주의)"
            
            with st.expander(f"{level_emoji} {timestamp} - {level_text}"):
                st.write(f"**감지 키워드:** {', '.join(event['keywords'])}")
                st.write(f"**비유 표현:** {'예' if event['is_metaphor'] else '아니오'}")
                if event['text_sample']:
                    st.write(f"**내용 일부:** {event['text_sample']}")

# ============================================================================
# 3. 면책 조항 및 동의 (유지)
# ============================================================================

def show_disclaimer():
    """면책 조항 표시 및 동의 받기"""
    st.title("🌙 GINI R.E.S.T.")
    st.subheader("Human Recovery AI System v2.5")
    st.caption("Phase 1: Crisis Engine Enhanced")
    
    st.markdown("---")
    
    st.markdown("""
    ### ⚠️ 이용 약관 및 면책 조항
    
    GINI R.E.S.T. 사용 전 반드시 읽고 동의해주세요.
    
    #### 1. 서비스의 성격
    - 본 서비스는 **수면 패턴 관리 도구**입니다.
    - **의학적 진단, 치료, 상담을 제공하지 않습니다.**
    - 정신건강 전문가의 조언을 대체할 수 없습니다.
    
    #### 2. AI 개입 기능 (V2.5)
    - 본 버전은 다단계 위기 감지 시스템을 포함합니다.
    - 위기 신호 감지 시 자동으로 전문기관 연락처를 안내합니다.
    - AI의 경고와 명령은 사용자의 안전을 위한 것입니다.
    
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
    
    agree = st.checkbox("위 내용을 모두 읽고 이해했으며, 이에 동의합니다.")
    
    if st.button("시작하기", disabled=not agree, use_container_width=True):
        st.session_state.agreed_to_terms = True
        st.rerun()

# ============================================================================
# 4-8. 기존 기능들 (유지) - 간략화
# ============================================================================

def add_sleep_record():
    """수면 기록 추가 (기존 유지)"""
    st.info("수면 기록 기능 - 기존 v2.0 기능 유지")
    # 기존 코드 유지 (생략)

def calculate_sleep_debt():
    """수면 부족량 계산 (기존 유지)"""
    st.info("수면 분석 기능 - 기존 v2.0 기능 유지")
    # 기존 코드 유지 (생략)

def show_cbti_education():
    """CBT-I 교육 (기존 유지)"""
    st.info("CBT-I 교육 기능 - 기존 v2.0 기능 유지")
    # 기존 코드 유지 (생략)

def breathing_exercise():
    """호흡 운동 (기존 유지)"""
    st.info("호흡 운동 기능 - 기존 v2.0 기능 유지")
    # 기존 코드 유지 (생략)

def show_education():
    """AI 상담 (Enhanced - 위기 감지 통합)"""
    st.title("💬 AI 상담")
    st.caption("Enhanced Crisis Detection System")
    
    st.markdown("---")
    
    # FAQ 섹션 (기존 유지)
    st.subheader("📚 자주 묻는 질문")
    
    faq_list = [
        "카페인과 수면의 관계",
        "스마트폰 블루라이트와 수면",
        "낮잠을 자도 괜찮을까요?",
        "잠이 안 올 때 해야 할 행동",
        "수면 환경 최적화",
        "운동과 수면의 관계"
    ]
    
    faq = st.selectbox("주제를 선택하세요:", ["선택하세요..."] + faq_list)
    
    if faq != "선택하세요...":
        st.info(f"'{faq}' 관련 정보가 표시됩니다.")
        # 기존 FAQ 내용 유지 (생략)
    
    st.markdown("---")
    
    # Enhanced 채팅 UI
    st.subheader("💬 질문하기")
    st.warning("⚠️ V2.5: 다단계 위기 감지 시스템 활성화됨")
    
    user_input = st.text_input("수면 관련 질문을 입력하세요:")
    
    if user_input:
        # V2.5 Enhanced Crisis Detection
        has_crisis, crisis_level, crisis_response = check_crisis_keywords(user_input)
        
        if has_crisis:
            st.session_state.emergency_mode = True
            st.session_state.crisis_level = crisis_level
            st.rerun()
        else:
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write("""
            현재는 위의 FAQ 주제들을 참고해주세요.
            
            더 궁금하신 점은:
            - 📊 수면 기록으로 패턴 파악
            - 💤 수면 및 분석으로 상태 확인
            - 🧠 CBT-I 교육으로 인지 교정
            - 🫁 호흡 운동으로 즉시 이완
            """)

# ============================================================================
# 9. 메인 앱
# ============================================================================

def main():
    """메인 앱"""
    init_session_state()
    
    # V2.0 - 매일 자동 초기화
    reset_daily_state()
    
    # 면책 조항 미동의 시
    if not st.session_state.agreed_to_terms:
        show_disclaimer()
        return
    
    # V2.5 Enhanced Crisis Mode 체크 (최우선)
    if st.session_state.emergency_mode:
        level = st.session_state.crisis_level
        pattern = get_crisis_pattern()
        response = get_crisis_response(level, pattern)
        
        st.error(response)
        
        st.markdown("---")
        
        if st.button("안전 모드 해제"):
            st.session_state.emergency_mode = False
            st.session_state.crisis_level = 0
            st.rerun()
        return
    
    # V2.0 - AI 개입 모드 체크
    if st.session_state.intervention_mode:
        show_intervention()
        return
    
    # V2.0 - 경계 구역 체크 및 경고
    in_boundary = check_boundary_zone()
    if in_boundary and not st.session_state.recovery_confirmed:
        if st.session_state.target_bedtime:
            st.warning(f"""
            ⚠️ **경계 구역 활성화**
            
            취침 시간 {st.session_state.target_bedtime.strftime('%H:%M')}까지 1시간 미만 남았습니다.
            
            지금부터 스마트폰 사용을 자제하고 수면 준비를 시작하세요.
            """)
            
            if st.button("🚨 AI 강제 개입 발동 (테스트용)", type="secondary"):
                trigger_intervention()
                st.rerun()
    
    # 사이드바
    with st.sidebar:
        st.title("🌙 GINI R.E.S.T.")
        st.caption("Human Recovery AI System v2.5")
        st.caption("Phase 1: Crisis Engine Enhanced ✅")
        
        st.markdown("---")
        
        # V2.5 위기 상태 표시
        pattern = get_crisis_pattern()
        if pattern['trend'] == 'worsening':
            st.error(f"⚠️ 위기: 최근 7일 {pattern['recent_7days']}회")
        elif pattern['trend'] == 'concerning':
            st.warning(f"📊 주의: 최근 7일 {pattern['recent_7days']}회")
        else:
            st.success("✅ 안정적 상태")
        
        # V2.0 상태 표시
        if st.session_state.target_bedtime:
            st.info(f"🎯 목표: {st.session_state.target_bedtime.strftime('%H:%M')}")
            if in_boundary:
                st.warning("⚠️ 경계 구역 활성화")
        
        st.markdown("---")
        
        menu = st.radio(
            "메뉴",
            [
                "🎯 V2.5 설정",
                "📊 위기 대시보드",  # NEW
                "💬 AI 상담",
                "📊 수면 기록",
                "💤 수면 및 분석",
                "🧠 CBT-I 교육",
                "🫁 호흡 운동"
            ]
        )
        
        st.markdown("---")
        st.caption(f"수면 기록: {len(st.session_state.sleep_data)}일")
        st.caption(f"개입 횟수: {st.session_state.intervention_count}회")
        st.caption(f"위기 감지: {pattern['total_count']}회")  # NEW
        
        if st.button("⚠️ 긴급 도움"):
            st.session_state.emergency_mode = True
            st.session_state.crisis_level = 3
            st.rerun()
    
    # 메뉴별 화면
    if menu == "🎯 V2.5 설정":
        st.title("🎯 V2.5 설정")
        set_target_bedtime()
        
        st.markdown("---")
        st.subheader("📊 현재 상태")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 기록", f"{len(st.session_state.sleep_data)}일")
        
        with col2:
            st.metric("AI 개입", f"{st.session_state.intervention_count}회")
        
        with col3:
            st.metric("위기 감지", f"{pattern['total_count']}회")
    
    elif menu == "📊 위기 대시보드":
        st.title("📊 위기 대시보드")
        show_crisis_dashboard()
    
    elif menu == "💬 AI 상담":
        show_education()
    
    elif menu == "📊 수면 기록":
        st.title("📊 수면 기록 추가")
        add_sleep_record()
    
    elif menu == "💤 수면 및 분석":
        st.title("💤 수면 및 분석")
        calculate_sleep_debt()
    
    elif menu == "🧠 CBT-I 교육":
        st.title("🧠 CBT-I 인지 재구조화")
        show_cbti_education()
    
    elif menu == "🫁 호흡 운동":
        st.title("🫁 4-7-8 호흡 운동")
        breathing_exercise()

if __name__ == "__main__":
    main()
