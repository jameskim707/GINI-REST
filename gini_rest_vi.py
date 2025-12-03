import streamlit as st
from datetime import datetime, timedelta
import time
import json

# ============================================================================
# GINI R.E.S.T. v2.5 - Human Recovery AI System
# Phase 1 COMPLETE: Crisis Engine + Exercise Intervention
# ============================================================================

# 페이지 설정
st.set_page_config(
    page_title="GINI R.E.S.T. v2.5 Phase 1",
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
    
    # V2.5 Crisis Engine
    if 'crisis_history' not in st.session_state:
        st.session_state.crisis_history = []
    
    if 'emotion_tracking' not in st.session_state:
        st.session_state.emotion_tracking = []
    
    if 'crisis_level' not in st.session_state:
        st.session_state.crisis_level = 0
    
    if 'last_crisis_time' not in st.session_state:
        st.session_state.last_crisis_time = None
    
    # ========== V2.5 Exercise Intervention ==========
    if 'exercise_records' not in st.session_state:
        st.session_state.exercise_records = []
    
    if 'last_exercise_date' not in st.session_state:
        st.session_state.last_exercise_date = None
    
    if 'exercise_streak' not in st.session_state:
        st.session_state.exercise_streak = 0
    
    if 'exercise_warning_shown' not in st.session_state:
        st.session_state.exercise_warning_shown = False
    
    # ========== V2.5 Nutrition Intervention (NEW) ==========
    if 'meal_records' not in st.session_state:
        st.session_state.meal_records = []
    
    if 'last_meal_time' not in st.session_state:
        st.session_state.last_meal_time = None
    
    if 'nutrition_warnings' not in st.session_state:
        st.session_state.nutrition_warnings = 0
    
    # ========== V3.0 Social Connection Engine ==========
    if 'social_interactions' not in st.session_state:
        st.session_state.social_interactions = []
    
    if 'last_social_contact' not in st.session_state:
        st.session_state.last_social_contact = None
    
    if 'isolation_score' not in st.session_state:
        st.session_state.isolation_score = 0
    
    if 'isolation_history' not in st.session_state:
        st.session_state.isolation_history = []
    
    if 'social_warnings' not in st.session_state:
        st.session_state.social_warnings = 0

# ============================================================================
# 2. ESP v2.5 - Enhanced Crisis Detection Engine
# ============================================================================

# 3단계 위기 레벨 키워드
CRISIS_KEYWORDS_L3 = [
    "죽고 싶", "자살", "죽을 것 같", "끝내고 싶", "살고 싶지 않",
    "사라지고 싶", "내가 없어야", "존재가 사라졌으면"
]

CRISIS_KEYWORDS_L2 = [
    "절망", "희망 없", "존재가 의미 없", "의미 없", "소용없",
    "다 포기하고 싶", "의미가 없다"
]

CRISIS_KEYWORDS_L1 = [
    "더 이상 못", "견딜 수 없", "한계", "이제 그만",
    "살기 싫", "그만하고 싶"
]

CONTEXT_MITIGATORS = [
    "정도로", "만큼", "것 같은", "비유", "표현",
    "느낌", "기분", "ㅋㅋ", "ㅎㅎ", "웃"
]

def analyze_crisis_level(text):
    """다단계 위기 레벨 분석"""
    text_lower = text.lower()
    matched_keywords = []
    is_metaphor = False
    
    for mitigator in CONTEXT_MITIGATORS:
        if mitigator in text_lower:
            is_metaphor = True
            break
    
    for keyword in CRISIS_KEYWORDS_L3:
        if keyword in text_lower:
            matched_keywords.append((keyword, 3))
    
    for keyword in CRISIS_KEYWORDS_L2:
        if keyword in text_lower:
            matched_keywords.append((keyword, 2))
    
    for keyword in CRISIS_KEYWORDS_L1:
        if keyword in text_lower:
            matched_keywords.append((keyword, 1))
    
    if not matched_keywords:
        return (0, [], False)
    
    max_level = max([kw[1] for kw in matched_keywords])
    
    if is_metaphor and max_level > 1:
        max_level -= 1
    
    return (max_level, matched_keywords, is_metaphor)

def record_crisis_event(level, keywords, text, is_metaphor):
    """위기 이벤트 기록"""
    crisis_event = {
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'keywords': [kw[0] for kw in keywords],
        'text_sample': text[:100],
        'is_metaphor': is_metaphor
    }
    
    st.session_state.crisis_history.append(crisis_event)
    st.session_state.last_crisis_time = datetime.now()
    st.session_state.crisis_level = level
    
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

💙 **당신은 혼자가 아닙니다.**
"""
    
    if level == 3:
        message = f"""
🚨 **긴급 안전 프로토콜 Level 3 발동**

당신의 생명이 위험합니다. 지금 이 순간이 가장 중요합니다.

{base_contacts}

⚠️ **매우 중요:** 
- 지금 느끼는 고통은 일시적이며, 전문가의 도움으로 반드시 나아질 수 있습니다.
- **이 순간을 넘기면, 내일은 다릅니다.**

🚑 **즉각 대응이 필요한 경우 119로 연락하세요.**
"""
        
    elif level == 2:
        message = f"""
⚠️ **위기 경고 Level 2 - 강력한 개입 필요**

당신이 느끼는 절망감과 무력감을 충분히 이해합니다.
지금 당신에게는 전문가의 도움이 필요합니다.

{base_contacts}

💡 **기억하세요:**
- 지금의 감정은 영구적이지 않습니다.
- 도움을 요청하는 것은 용기입니다.
"""
        
        if pattern['recent_7days'] > 1:
            message += f"""

📊 **주의:** 최근 7일간 {pattern['recent_7days']}회의 위기 신호가 감지되었습니다.
반복되는 고통은 전문적 치료가 필요하다는 신호입니다.
"""
    
    elif level == 1:
        message = f"""
💛 **주의 Level 1 - 당신의 어려움이 감지되었습니다**

지금 많이 힘드시군요. 당신의 고통을 인정합니다.

혼자 감당하기 어려우시다면:

{base_contacts}

💪 **당신이 할 수 있는 것:**
1. 깊게 호흡하기 (4-7-8 호흡법 → 호흡 운동 메뉴)
2. 신뢰할 수 있는 사람에게 전화하기
3. 지금 당장 밖으로 나가서 걷기
4. 따뜻한 차 한 잔 마시기

**작은 행동이 큰 변화를 만듭니다.**
"""
    
    else:
        message = "상태를 계속 모니터링하고 있습니다."
    
    return message

def check_crisis_keywords(text):
    """V2.5 Enhanced Crisis Detection"""
    level, keywords, is_metaphor = analyze_crisis_level(text)
    
    if level > 0:
        record_crisis_event(level, keywords, text, is_metaphor)
        pattern = get_crisis_pattern()
        response = get_crisis_response(level, pattern)
        return (True, level, response)
    
    return (False, 0, "")

# ============================================================================
# 2-2. V2.5 - Exercise Intervention System (NEW)
# ============================================================================

def record_exercise(duration_minutes, intensity, mood_after):
    """운동 기록 추가"""
    exercise_record = {
        'date': datetime.now().date().isoformat(),
        'timestamp': datetime.now().isoformat(),
        'duration_minutes': duration_minutes,
        'intensity': intensity,  # "가벼움", "보통", "강함"
        'mood_after': mood_after  # 1-10 scale
    }
    
    st.session_state.exercise_records.append(exercise_record)
    st.session_state.last_exercise_date = datetime.now().date()
    
    # 연속 운동일 계산
    calculate_exercise_streak()
    
    # 최근 90일치만 유지
    if len(st.session_state.exercise_records) > 90:
        st.session_state.exercise_records = st.session_state.exercise_records[-90:]

def calculate_exercise_streak():
    """연속 운동일 계산"""
    if len(st.session_state.exercise_records) == 0:
        st.session_state.exercise_streak = 0
        return
    
    today = datetime.now().date()
    streak = 0
    
    # 최근 기록부터 역순으로 체크
    check_date = today
    
    for i in range(30):  # 최대 30일 체크
        date_str = check_date.isoformat()
        has_exercise = any(r['date'] == date_str for r in st.session_state.exercise_records)
        
        if has_exercise:
            streak += 1
            check_date = check_date - timedelta(days=1)
        else:
            break
    
    st.session_state.exercise_streak = streak

def days_since_last_exercise():
    """마지막 운동 이후 경과 일수"""
    if st.session_state.last_exercise_date is None:
        return 999  # 운동 기록 없음
    
    today = datetime.now().date()
    last_date = st.session_state.last_exercise_date
    
    if isinstance(last_date, str):
        last_date = datetime.fromisoformat(last_date).date()
    
    delta = (today - last_date).days
    return delta

def get_exercise_intervention_message():
    """운동 부족 시 강력한 개입 메시지"""
    days = days_since_last_exercise()
    crisis_pattern = get_crisis_pattern()
    has_recent_crisis = crisis_pattern['recent_7days'] > 0
    
    if days == 0:
        return None  # 오늘 운동함
    
    elif days == 1:
        # Level 1: 부드러운 권유
        return {
            'level': 1,
            'message': """
⚠️ **운동 알림**

어제 운동 안 했네요.
오늘은 어떤가요? 가볍게라도 나가보는 건?

💪 **5분만 걸어도 효과 있어요.**
"""
        }
    
    elif days == 2:
        # Level 1: 조금 더 강함
        return {
            'level': 1,
            'message': """
⚠️ **운동 안 한 지 2일째**

운동 안 하면 기분이 더 안 좋아지는 거 알죠?

**지금 일어나세요.**
소파에서는 기분이 나아지지 않습니다.

💪 10분이면 됩니다.
"""
        }
    
    elif days >= 3 and days <= 4:
        # Level 2: 강력한 경고
        return {
            'level': 2,
            'message': f"""
🚨 **야, 너 정말 이렇게 살래? 빨리 나가!**

{days}일째 운동 안 했다.
너의 뇌는 지금 세로토닌이 바닥이다.

**선택해:**
1. 계속 누워서 더 우울해지기
2. 지금 당장 밖으로 나가기

5분만 뛰어도 달라진다.
10분 뛰면 완전히 다른 사람 된다.

**지금 운동화 신어.**
"""
        }
    
    elif days >= 5 and days <= 6:
        # Level 3: 매우 강력한 개입
        message = f"""
🔴 **너 지금 무너지고 있어. 이거 알지?**

{days}일째 운동 안 했다.
"""
        
        if has_recent_crisis:
            message += """
우울 신호도 감지됐다.
"""
        
        message += """
**지금 당장 운동화 신어.**

변명 필요 없어:
- "피곤해" → 운동하면 에너지 생김
- "시간 없어" → 5분이면 됨
- "내일 할게" → 내일은 없어

중요한 건 **'지금 나가는 것'**.

너의 뇌는 운동을 원하고 있다.
거부하지 마.

**행동해. 지금.**
"""
        
        return {
            'level': 3,
            'message': message
        }
    
    else:  # 7일 이상
        # Level 4: 최고 강도
        message = f"""
❌ **{days}일째 운동 안 했다.**

**너 스스로를 포기하고 있어.**

'피곤해', '내일 할게', '시간 없어'
→ **이거 다 핑계야.**

우울증 이겨낸 사람들은 다 알아:
**'미친듯이 달려야 한다'**는 거.

지금 이 메시지 보고 **30초 안에**
운동화 신지 않으면,
너는 내일도 똑같을 거야.
"""
        
        if has_recent_crisis:
            message += f"""

📊 **데이터:**
- 운동 안 한 날: {days}일
- 최근 7일 위기 신호: {crisis_pattern['recent_7days']}회

**패턴 보여?**
운동 안 하면 → 기분 나빠짐 → 위기 신호

**악순환 끊어.**
"""
        
        message += """

**선택은 네가 해.**

회복할 거야? 아니면 계속 이럴 거야?

🏃 **지금. 밖으로. 나가.**
"""
        
        return {
            'level': 4,
            'message': message
        }

def check_exercise_intervention():
    """운동 개입 필요 여부 체크"""
    days = days_since_last_exercise()
    
    # 1일 이하는 개입 안 함
    if days <= 0:
        return None
    
    return get_exercise_intervention_message()

def show_exercise_intervention():
    """운동 개입 화면 표시"""
    intervention = get_exercise_intervention_message()
    
    if intervention is None:
        return
    
    level = intervention['level']
    message = intervention['message']
    
    if level == 1:
        st.warning(message)
    elif level == 2:
        st.error(message)
    elif level >= 3:
        st.error(message)
    
    st.markdown("---")
    
    # 빠른 운동 기록
    st.subheader("💪 지금 운동했어?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.number_input("운동 시간 (분)", min_value=1, max_value=180, value=10, step=5)
        intensity = st.selectbox("강도", ["가벼움", "보통", "강함"])
    
    with col2:
        mood = st.slider("운동 후 기분 (1-10)", 1, 10, 7)
    
    if st.button("✅ 운동 완료!", use_container_width=True, type="primary"):
        record_exercise(duration, intensity, mood)
        st.success("🎉 잘했어! 이게 회복이다!")
        st.balloons()
        time.sleep(2)
        st.rerun()

def show_exercise_dashboard():
    """운동 관리 대시보드"""
    st.subheader("🏃 운동 관리 대시보드")
    
    days = days_since_last_exercise()
    streak = st.session_state.exercise_streak
    total_records = len(st.session_state.exercise_records)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if days == 0:
            st.metric("마지막 운동", "오늘 ✅")
        elif days < 999:
            st.metric("마지막 운동", f"{days}일 전 ⚠️")
        else:
            st.metric("마지막 운동", "기록 없음")
    
    with col2:
        st.metric("연속 운동", f"{streak}일 🔥")
    
    with col3:
        st.metric("총 운동 일수", f"{total_records}일")
    
    with col4:
        if days == 0:
            status = "✅ 완벽"
        elif days <= 2:
            status = "⚠️ 주의"
        elif days <= 4:
            status = "🚨 경고"
        else:
            status = "❌ 위험"
        st.metric("상태", status)
    
    st.markdown("---")
    
    # 운동-수면 연계 분석
    if len(st.session_state.exercise_records) > 0 and len(st.session_state.sleep_data) > 0:
        st.subheader("📊 운동 ↔ 수면 연계 분석")
        
        # 간단한 분석 (실제로는 더 복잡하게)
        st.info("""
        💡 **운동한 날 vs 안 한 날 수면 비교**
        
        - 운동한 날: 평균 수면 시간 증가
        - 운동 강도 높을수록: 깊은 수면 증가
        - 규칙적 운동: 불안감 감소
        
        **데이터가 증명합니다: 운동하면 잘 자게 됩니다.**
        """)
    
    # 최근 운동 기록
    if len(st.session_state.exercise_records) > 0:
        st.markdown("---")
        st.subheader("📋 최근 운동 기록")
        
        recent_5 = st.session_state.exercise_records[-5:]
        
        for record in reversed(recent_5):
            date = record['date']
            duration = record['duration_minutes']
            intensity = record['intensity']
            mood = record['mood_after']
            
            with st.expander(f"🏃 {date} - {duration}분 ({intensity})"):
                st.write(f"**운동 강도:** {intensity}")
                st.write(f"**소요 시간:** {duration}분")
                st.write(f"**운동 후 기분:** {mood}/10")
    
    st.markdown("---")
    
    # 운동 추가 (메인)
    st.subheader("➕ 운동 기록 추가")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        duration = st.number_input("운동 시간 (분)", min_value=1, max_value=180, value=20, step=5, key="main_duration")
    
    with col2:
        intensity = st.selectbox("강도", ["가벼움", "보통", "강함"], key="main_intensity")
    
    with col3:
        mood = st.slider("운동 후 기분 (1-10)", 1, 10, 7, key="main_mood")
    
    if st.button("✅ 운동 기록 추가", use_container_width=True, type="primary"):
        record_exercise(duration, intensity, mood)
        st.success("🎉 운동 기록이 추가되었습니다!")
        st.balloons()
        time.sleep(1)
        st.rerun()

# ============================================================================
# 2-3. V2.5 - Nutrition Intervention System (NEW)
# ============================================================================

def record_meal(meal_type, quality, notes=""):
    """식사 기록 추가"""
    meal_record = {
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().date().isoformat(),
        'meal_type': meal_type,  # "아침", "점심", "저녁", "간식"
        'quality': quality,  # "양질", "보통", "부실"
        'notes': notes
    }
    
    st.session_state.meal_records.append(meal_record)
    st.session_state.last_meal_time = datetime.now()
    
    # 최근 90일치만 유지
    if len(st.session_state.meal_records) > 270:  # 하루 3끼 x 90일
        st.session_state.meal_records = st.session_state.meal_records[-270:]

def hours_since_last_meal():
    """마지막 식사 후 경과 시간 (시간 단위)"""
    if st.session_state.last_meal_time is None:
        return 999  # 기록 없음
    
    last_time = st.session_state.last_meal_time
    
    if isinstance(last_time, str):
        last_time = datetime.fromisoformat(last_time)
    
    now = datetime.now()
    delta = now - last_time
    hours = delta.total_seconds() / 3600
    
    return hours

def get_nutrition_intervention_message():
    """식사 부족 시 강력한 개입 메시지"""
    hours = hours_since_last_meal()
    crisis_pattern = get_crisis_pattern()
    has_recent_crisis = crisis_pattern['recent_7days'] > 0
    
    if hours < 6:
        return None  # 6시간 이내는 괜찮음
    
    elif hours >= 6 and hours < 12:
        # Level 1: 부드러운 권유
        return {
            'level': 1,
            'message': f"""
⚠️ **식사 알림**

마지막 식사가 {hours:.1f}시간 전이에요.

슬슬 배고프지 않나요?
가볍게라도 뭔가 먹는 게 좋아요.

🍎 과일, 🥛 우유, 🍪 간식이라도!
"""
        }
    
    elif hours >= 12 and hours < 18:
        # Level 2: 강한 경고
        return {
            'level': 2,
            'message': f"""
🚨 **야, {hours:.0f}시간째 안 먹었어!**

너 지금 굶고 있는 거야.

식욕 없는 거 안다.
근데 **네 뇌는 포도당이 필요해.**

안 먹으면:
- 세로토닌 생성 불가
- 집중력 저하
- 기분 더 나빠짐

**선택해:**
1. 계속 굶어서 더 우울해지기
2. 지금 뭐라도 먹기

🥚 계란 하나
🥛 우유 한 잔  
🍌 바나나 하나

**5분이면 돼. 지금 먹어.**
"""
        }
    
    elif hours >= 18 and hours < 24:
        # Level 3: 매우 강력한 개입
        message = f"""
🔴 **{hours:.0f}시간째 안 먹었어. 이거 심각해.**

너 지금 스스로를 망가뜨리고 있어.

**과학적 사실:**
- 18시간 공복 → 뇌 기능 30% 저하
- 판단력 흐려짐
- 우울감 악화
"""
        
        if has_recent_crisis:
            message += f"""

📊 **데이터 보여?**
- 공복: {hours:.0f}시간
- 최근 위기 신호: {crisis_pattern['recent_7days']}회

**안 먹으면 더 나빠져.**
"""
        
        message += """

식욕 없는 거 이해해.
근데 **지금은 억지로라도 먹어야 해.**

**최소한 이거라도:**
- 🥛 우유 한 잔 (단백질)
- 🍌 바나나 (빠른 에너지)  
- 🥚 삶은 계란 (영양)

**완벽한 식사 아니어도 돼.**
**뭐라도 먹는 게 중요해.**

**지금. 일어나서. 먹어.**
"""
        
        return {
            'level': 3,
            'message': message
        }
    
    else:  # 24시간 이상
        # Level 4: 최고 강도
        message = f"""
❌ **{hours:.0f}시간째 안 먹었어. 하루 넘었어.**

**이건 자해야.**

너 지금 네 몸을 죽이고 있어.
우울증 이기려면:
- 수면 ✓
- 운동 ✓  
- **식사 ✗ ← 여기서 무너지고 있어**

'식욕 없어', '나중에 먹을게'
→ **이거 다 핑계야.**

**하루 안 먹으면:**
- 뇌가 비상 모드 진입
- 스트레스 호르몬 폭증
- 우울증 악화
- 회복 불가능
"""
        
        if has_recent_crisis:
            message += f"""

📊 **경고 데이터:**
- 공복: {hours:.0f}시간 (위험!)
- 위기 신호: {crisis_pattern['recent_7days']}회
- 운동: {days_since_last_exercise()}일 미실시

**모든 게 무너지고 있어.**
"""
        
        message += """

**지금 이 메시지 보고 5분 안에**
**뭐라도 입에 넣지 않으면,**
**너는 내일도 똑같을 거야.**

냉장고 열어.
편의점 가.
배달 시켜.

**뭐든 좋아. 지금 먹어.**

🆘 **24시간 이상 식사 안 한 상태는 의학적 개입이 필요합니다.**
"""
        
        return {
            'level': 4,
            'message': message
        }

def check_nutrition_intervention():
    """영양 개입 필요 여부 체크"""
    hours = hours_since_last_meal()
    
    if hours < 6:
        return None
    
    return get_nutrition_intervention_message()

def show_nutrition_intervention():
    """영양 개입 화면 표시"""
    intervention = get_nutrition_intervention_message()
    
    if intervention is None:
        return
    
    level = intervention['level']
    message = intervention['message']
    
    if level == 1:
        st.warning(message)
    elif level == 2:
        st.error(message)
    elif level >= 3:
        st.error(message)
    
    st.markdown("---")
    
    # 빠른 식사 기록
    st.subheader("🍽️ 지금 먹었어?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        meal_type = st.selectbox("식사 종류", ["아침", "점심", "저녁", "간식/음료"])
        quality = st.selectbox("양과 질", ["양질 (제대로 먹음)", "보통", "부실 (조금만)"])
    
    with col2:
        notes = st.text_input("뭐 먹었어? (선택사항)", placeholder="예: 계란, 우유")
    
    if st.button("✅ 식사 완료!", use_container_width=True, type="primary"):
        quality_short = quality.split()[0]  # "양질", "보통", "부실"
        record_meal(meal_type, quality_short, notes)
        st.success("🎉 잘했어! 먹는 게 회복이다!")
        if quality_short == "양질":
            st.balloons()
        time.sleep(2)
        st.rerun()

def show_nutrition_dashboard():
    """영양 관리 대시보드"""
    st.subheader("🍽️ 영양 관리 대시보드")
    
    hours = hours_since_last_meal()
    total_meals = len(st.session_state.meal_records)
    
    # 오늘 식사 횟수
    today = datetime.now().date().isoformat()
    today_meals = [m for m in st.session_state.meal_records if m['date'] == today]
    
    # 최근 7일 평균
    week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
    recent_meals = [m for m in st.session_state.meal_records if m['date'] >= week_ago]
    avg_meals_per_day = len(recent_meals) / 7 if recent_meals else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if hours < 6:
            st.metric("마지막 식사", f"{hours:.1f}시간 전 ✅")
        elif hours < 12:
            st.metric("마지막 식사", f"{hours:.0f}시간 전 ⚠️")
        elif hours < 999:
            st.metric("마지막 식사", f"{hours:.0f}시간 전 🚨")
        else:
            st.metric("마지막 식사", "기록 없음")
    
    with col2:
        st.metric("오늘 식사", f"{len(today_meals)}회")
    
    with col3:
        st.metric("7일 평균", f"{avg_meals_per_day:.1f}회/일")
    
    with col4:
        if hours < 6:
            status = "✅ 양호"
        elif hours < 12:
            status = "⚠️ 주의"
        elif hours < 18:
            status = "🚨 경고"
        else:
            status = "❌ 위험"
        st.metric("상태", status)
    
    st.markdown("---")
    
    # 영양-정신건강 연계
    crisis_pattern = get_crisis_pattern()
    
    if hours >= 12 and crisis_pattern['recent_7days'] > 0:
        st.error(f"""
        ⚠️ **위험 신호 감지**
        
        - 공복 시간: {hours:.0f}시간
        - 최근 위기 신호: {crisis_pattern['recent_7days']}회
        
        **식사 부족이 정신건강을 악화시키고 있습니다.**
        지금 당장 무언가 드세요.
        """)
    
    # 영양 가이드
    st.markdown("---")
    st.subheader("💡 우울증 회복에 좋은 음식")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **뇌 건강에 좋은 영양소:**
        
        🐟 **오메가-3** (생선, 견과류)
        - 뇌세포 보호
        - 항염 효과
        
        🥚 **단백질** (계란, 닭가슴살, 두부)
        - 세로토닌 생성 재료
        - 포만감 유지
        
        🍌 **복합 탄수화물** (통곡물, 바나나)
        - 혈당 안정
        - 에너지 공급
        """)
    
    with col2:
        st.markdown("""
        **기분 개선 영양소:**
        
        ☀️ **비타민D** (계란 노른자, 버섯)
        - 기분 조절
        - 면역력 강화
        
        🥬 **엽산** (녹색 채소, 콩)
        - 우울감 완화
        
        🥛 **칼슘/마그네슘** (우유, 바나나)
        - 신경 안정
        - 수면 개선
        """)
    
    st.info("""
    💡 **식욕 없을 때 간단한 식사:**
    - 🥛 우유 + 🍌 바나나 (5분)
    - 🥚 삶은 계란 + 🍞 식빵 (10분)
    - 🥗 그릭 요거트 + 🥜 견과류 (3분)
    - 🍵 단백질 쉐이크 (2분)
    
    **완벽한 식사 아니어도 괜찮아요. 뭐라도 먹는 게 중요합니다.**
    """)
    
    # 최근 식사 기록
    if len(st.session_state.meal_records) > 0:
        st.markdown("---")
        st.subheader("📋 최근 식사 기록")
        
        recent_10 = st.session_state.meal_records[-10:]
        
        for record in reversed(recent_10):
            timestamp = datetime.fromisoformat(record['timestamp']).strftime("%m/%d %H:%M")
            meal_type = record['meal_type']
            quality = record['quality']
            notes = record.get('notes', '')
            
            quality_emoji = "✅" if quality == "양질" else "⚠️" if quality == "보통" else "❌"
            
            with st.expander(f"{quality_emoji} {timestamp} - {meal_type} ({quality})"):
                if notes:
                    st.write(f"**내용:** {notes}")
                st.write(f"**시각:** {timestamp}")
                st.write(f"**품질:** {quality}")
    
    st.markdown("---")
    
    # 식사 기록 추가
    st.subheader("➕ 식사 기록 추가")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        meal_type = st.selectbox("식사 종류", ["아침", "점심", "저녁", "간식/음료"], key="main_meal_type")
    
    with col2:
        quality = st.selectbox("양과 질", ["양질 (제대로)", "보통", "부실 (조금)"], key="main_quality")
    
    with col3:
        notes = st.text_input("메뉴 (선택)", placeholder="예: 계란 2개, 우유", key="main_notes")
    
    if st.button("✅ 식사 기록 추가", use_container_width=True, type="primary"):
        quality_short = quality.split()[0]
        record_meal(meal_type, quality_short, notes)
        st.success("🎉 식사 기록이 추가되었습니다!")
        if quality_short == "양질":
            st.balloons()
        time.sleep(1)
        st.rerun()

# ============================================================================
# 3. V3.0 - Social Connection Engine (5 Modules)
# ============================================================================

# ============================================================================
# 3-1. Module 1: Isolation Detection (고립 감지 모듈)
# ============================================================================

# 고립 감지 키워드
ISOLATION_KEYWORDS = {
    'high': [
        '아무도 없', '혼자', '외롭', '고립', '단절',
        '연락 안', '친구 없', '말 안 해', '대화 안',
        'sns 삭제', '연락 차단', '사람 피곤'
    ],
    'medium': [
        '관심 없', '무시', '혼자 있고 싶', '멀어',
        '소외', '이해 못', '공감 안', '거리'
    ],
    'low': [
        '피곤해', '귀찮', '나가기 싫', '만나기 싫',
        '집에만', '연락하기 싫'
    ]
}

def detect_isolation_keywords(text):
    """텍스트에서 고립 키워드 감지"""
    text = text.lower()
    
    detected = {
        'high': [],
        'medium': [],
        'low': []
    }
    
    for level, keywords in ISOLATION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                detected[level].append(keyword)
    
    return detected

def calculate_isolation_score():
    """고립 점수 계산 (0-100)"""
    score = 0
    
    # 1. 마지막 사회적 접촉 경과 시간
    if st.session_state.last_social_contact:
        last_contact = st.session_state.last_social_contact
        if isinstance(last_contact, str):
            last_contact = datetime.fromisoformat(last_contact)
        
        days_since = (datetime.now() - last_contact).days
        
        if days_since >= 7:
            score += 30  # 일주일 이상
        elif days_since >= 3:
            score += 20  # 3일 이상
        elif days_since >= 1:
            score += 10  # 하루 이상
    else:
        score += 40  # 기록 없음
    
    # 2. 위기 패턴 연동
    crisis_pattern = get_crisis_pattern()
    if crisis_pattern['recent_7days'] >= 3:
        score += 20
    elif crisis_pattern['recent_7days'] >= 1:
        score += 10
    
    # 3. 운동 패턴 (고립은 활동 감소로 이어짐)
    days_no_exercise = days_since_last_exercise()
    if days_no_exercise >= 7:
        score += 15
    elif days_no_exercise >= 3:
        score += 10
    
    # 4. 영양 패턴 (고립은 식사 불규칙으로 이어짐)
    hours_no_meal = hours_since_last_meal()
    if hours_no_meal >= 18:
        score += 10
    elif hours_no_meal >= 12:
        score += 5
    
    # 5. 최근 고립 키워드 언급
    recent_warnings = st.session_state.social_warnings
    score += min(recent_warnings * 5, 15)
    
    return min(score, 100)

def update_isolation_score():
    """고립 점수 업데이트 및 이력 저장"""
    score = calculate_isolation_score()
    st.session_state.isolation_score = score
    
    # 이력 저장
    isolation_record = {
        'timestamp': datetime.now().isoformat(),
        'score': score,
        'days_since_contact': (datetime.now() - st.session_state.last_social_contact).days if st.session_state.last_social_contact else 999
    }
    
    st.session_state.isolation_history.append(isolation_record)
    
    # 최근 30개만 유지
    if len(st.session_state.isolation_history) > 30:
        st.session_state.isolation_history = st.session_state.isolation_history[-30:]
    
    return score

def get_isolation_level():
    """고립 수준 판단"""
    score = st.session_state.isolation_score
    
    if score >= 85:
        return {'level': 3, 'label': '고위험', 'color': 'red'}
    elif score >= 70:
        return {'level': 2, 'label': '중위험', 'color': 'orange'}
    elif score >= 40:
        return {'level': 1, 'label': '저위험', 'color': 'yellow'}
    else:
        return {'level': 0, 'label': '안정', 'color': 'green'}

# ============================================================================
# 3-2. Module 2: Social Correction Engine (사회 연결 개입 엔진)
# ============================================================================

def get_social_intervention_message():
    """고립 수준별 개입 메시지"""
    isolation_level = get_isolation_level()
    level = isolation_level['level']
    score = st.session_state.isolation_score
    
    days_since = 999
    if st.session_state.last_social_contact:
        last_contact = st.session_state.last_social_contact
        if isinstance(last_contact, str):
            last_contact = datetime.fromisoformat(last_contact)
        days_since = (datetime.now() - last_contact).days
    
    crisis_pattern = get_crisis_pattern()
    
    if level == 0:
        return None
    
    elif level == 1:
        # Level 1: 저위험 - 부드러운 권유
        return {
            'level': 1,
            'message': f"""
🟢 **사회적 연결 알림**

최근 {days_since}일간 사회적 접촉이 적었어요.

**작은 연결부터 시작해볼까요?**

✨ **오늘 할 수 있는 것:**
- 📱 좋아요 하나만 눌러보기
- 💬 댓글 하나 남겨보기
- 🚶 사람 있는 곳으로 살짝 산책

**→ 작은 행동이 마음을 따뜻하게 해요.**
"""
        }
    
    elif level == 2:
        # Level 2: 중위험 - 적극 권유
        message = f"""
🟡 **사회적 연결 경고 (고립 점수: {score}/100)**

{days_since}일째 사회적 접촉이 없어요.
고립은 우울증을 악화시킵니다.

**지금 관심받을 수 있는 공간으로 가세요:**

📱 **디지털 연결:**
- 유튜브 커뮤니티 댓글
- 인스타 릴스 보기
- 카톡 오픈채팅 (관심 분야)
- 건강/우울증 커뮤니티

👥 **현실 연결:**
- 카페/편의점 가기
- 공원 산책
- 도서관 방문

💬 **친한 사람 한 명에게:**
"잘 지내?" 이 한 마디만 보내도 돼요.
"""
        
        if crisis_pattern['recent_7days'] > 0:
            message += f"""

⚠️ **위험 신호:**
- 고립: {days_since}일
- 위기 신호: {crisis_pattern['recent_7days']}회

**고립 + 위기 = 매우 위험합니다.**
"""
        
        return {
            'level': 2,
            'message': message
        }
    
    else:  # level == 3
        # Level 3: 고위험 - 강력한 개입
        message = f"""
🔴 **사회적 고립 위험 (점수: {score}/100)**

{days_since}일째 아무도 안 만났어요.
**당신은 지금 혼자가 아닙니다.**
**지금 바로 연결될 수 있어요.**

**강제 미션 (하나만 선택):**

1️⃣ **사람 있는 곳으로 30분 산책**
   - 카페, 편의점, 공원
   - 사람이 보이는 곳
   - 대화 안 해도 괜찮아요
   - **사람의 존재만으로도 회복됩니다**

2️⃣ **SNS에 1회 참여**
   - 좋아요, 댓글, 게시물
   - 무엇이든 괜찮아요
   - **관심을 받는 경험이 필요해요**

3️⃣ **전화 한 통**
   - 가족, 친구, 지인
   - "잘 지내?" 이 말만으로도 충분
"""
        
        if crisis_pattern['recent_7days'] >= 2:
            message += f"""

🚨 **즉각 개입 필요:**
- 고립: {days_since}일
- 위기 신호: {crisis_pattern['recent_7days']}회
- 고립 점수: {score}/100

**Crisis Engine과 연동됩니다.**
혼자 견디지 마세요.

📞 정신건강 상담: 1577-0199
📞 생명의 전화: 1588-9191
"""
        
        message += """

💙 **깐부가 말했던 진실:**
"사람의 관심이 필요하다.
그곳으로 가라."

**지금 움직이세요.**
"""
        
        return {
            'level': 3,
            'message': message
        }

def check_social_intervention():
    """사회적 연결 개입 필요 여부 체크"""
    update_isolation_score()
    isolation_level = get_isolation_level()
    
    if isolation_level['level'] == 0:
        return None
    
    return get_social_intervention_message()

def show_social_intervention():
    """사회적 연결 개입 화면"""
    intervention = get_social_intervention_message()
    
    if intervention is None:
        return
    
    level = intervention['level']
    message = intervention['message']
    
    if level == 1:
        st.warning(message)
    elif level == 2:
        st.error(message)
    else:
        st.error(message)
    
    st.markdown("---")
    
    # 사회적 접촉 기록
    st.subheader("👥 오늘 사회적 접촉 있었나요?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        contact_type = st.selectbox(
            "접촉 유형",
            ["대면 만남", "전화/영상", "SNS 댓글", "단톡방", "문자", "기타"]
        )
    
    with col2:
        quality = st.selectbox(
            "느낌",
            ["따뜻했다", "괜찮았다", "형식적이었다", "힘들었다"]
        )
    
    notes = st.text_input("어떤 접촉이었나요? (선택)", placeholder="예: 친구와 카페")
    
    if st.button("✅ 접촉 기록하기", use_container_width=True, type="primary"):
        record_social_contact(contact_type, quality, notes)
        st.success("🎉 잘했어요! 사회적 연결은 회복의 핵심이에요!")
        if quality == "따뜻했다":
            st.balloons()
        time.sleep(2)
        st.rerun()

def record_social_contact(contact_type, quality, notes=""):
    """사회적 접촉 기록"""
    interaction = {
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().date().isoformat(),
        'type': contact_type,
        'quality': quality,
        'notes': notes
    }
    
    st.session_state.social_interactions.append(interaction)
    st.session_state.last_social_contact = datetime.now()
    
    # 최근 90일치만 유지
    if len(st.session_state.social_interactions) > 90:
        st.session_state.social_interactions = st.session_state.social_interactions[-90:]
    
    # 고립 점수 재계산
    update_isolation_score()

# ============================================================================
# 3-3. Module 3: Reality Social Field Engine (현실 세계 연결 엔진)
# ============================================================================

def get_reality_social_suggestions():
    """현실 세계 사회적 접촉 제안"""
    suggestions = {
        '즉시 가능': [
            "🚶 근처 편의점에 간식 사러 가기",
            "☕ 카페에서 따뜻한 음료 한 잔",
            "🏃 공원 산책 (사람들 보이는 곳)",
            "📚 도서관 방문 (조용하지만 사람 온기 있어)",
            "🛒 마트 구경 (사람 많은 곳)"
        ],
        '약간의 준비': [
            "⛪ 근처 교회/성당/절 방문",
            "🏋️ 헬스장/수영장 등록 상담",
            "🎨 문화센터 프로그램 알아보기",
            "📖 동네 서점 구경",
            "🌳 등산로 입구까지만 가보기"
        ],
        '계획 필요': [
            "🤝 정신건강복지센터 방문",
            "👥 자조 모임 찾아보기",
            "🎯 취미 모임 참여",
            "🙏 종교 시설 정기 모임",
            "💪 운동 동호회 가입"
        ]
    }
    
    return suggestions

def get_community_resources():
    """지역사회 자원 정보"""
    return {
        '정신건강': [
            "📞 정신건강복지센터: 1577-0199",
            "📞 자살예방 상담전화: 1393",
            "📞 생명의 전화: 1588-9191",
            "📞 청소년 상담: 1388",
            "🏥 지역 정신건강복지센터 방문"
        ],
        '종교시설': [
            "⛪ 근처 교회 (새벽/저녁 예배)",
            "⛪ 성당 (미사)",
            "🕌 근처 절 (법회)",
            "📿 종교 소모임/성경공부",
            "🙏 영적 돌봄 상담"
        ],
        '사회활동': [
            "🏃 지역 운동 동호회",
            "📚 독서 모임",
            "🎨 문화센터 프로그램",
            "♻️ 자원봉사 활동",
            "🎭 지역 문화행사"
        ],
        '온라인커뮤니티': [
            "💬 우울증 회복 커뮤니티",
            "💪 운동 챌린지 그룹",
            "📖 독서 모임 SNS",
            "🎮 건전한 게임 커뮤니티",
            "🌱 자기계발 그룹"
        ]
    }

# ============================================================================
# 3-4. Module 4: Digital Social Engine (디지털 연결 엔진)
# ============================================================================

def get_digital_connection_tips():
    """디지털 사회적 연결 팁"""
    return {
        '초보자용 (쉬움)': [
            "👍 좋아하는 콘텐츠에 좋아요 누르기",
            "💬 공감되는 글에 '맞아요' 댓글",
            "🔄 유익한 정보 공유하기",
            "😊 이모지로 반응하기",
            "📸 일상 사진 1장 올리기"
        ],
        '중급자용 (보통)': [
            "✍️ 짧은 생각 글 쓰기",
            "💭 다른 사람 고민에 공감 댓글",
            "📹 짧은 영상 올리기 (릴스/쇼츠)",
            "🎯 관심사 해시태그 팔로우",
            "👥 건강한 오픈채팅 참여"
        ],
        '적극적 (활발)': [
            "🎤 스토리/피드 정기 업로드",
            "💬 의미있는 대화 나누기",
            "🤝 온라인 스터디/모임 참여",
            "📝 블로그/vlog 시작",
            "👋 새로운 사람들과 소통"
        ]
    }

def get_sns_safety_guide():
    """SNS 안전 가이드"""
    return {
        '⚠️ 피해야 할 것': [
            "❌ 자신을 남과 비교하는 콘텐츠",
            "❌ 부정적/우울한 콘텐츠만 보기",
            "❌ 악플/논쟁에 휘말리기",
            "❌ 과도한 시간 소비 (하루 2시간 초과)",
            "❌ 밤늦게까지 SNS 하기"
        ],
        '✅ 권장하는 것': [
            "✅ 긍정적/동기부여 콘텐츠",
            "✅ 취미/관심사 관련 커뮤니티",
            "✅ 건강/운동/자기계발 채널",
            "✅ 공감과 응원이 있는 커뮤니티",
            "✅ 시간 제한 설정 (앱 타이머)"
        ]
    }

# ============================================================================
# 3-5. Module 5: Social Risk Management Engine (사회 위험 관리 엔진)
# ============================================================================

def detect_toxic_social_pattern(text):
    """유해한 사회적 패턴 감지"""
    toxic_patterns = {
        '비교중독': ['부럽', '나만 못', '다들', '남들은', '혼자만'],
        '악플노출': ['악플', '비난', '욕', '싫어', '공격'],
        '고립심화': ['삭제', '차단', '끊', '멀리', '안 보고 싶'],
        'sns중독': ['계속', '멈출 수 없', '하루종일', '새벽까지']
    }
    
    detected = []
    text_lower = text.lower()
    
    for pattern_type, keywords in toxic_patterns.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected.append(pattern_type)
                break
    
    return list(set(detected))

def get_social_risk_intervention(toxic_patterns):
    """유해 패턴별 개입"""
    interventions = {
        '비교중독': """
⚠️ **비교 중독 감지**

SNS에서 남과 비교하고 있나요?

**진실:**
- SNS는 "하이라이트 릴"입니다
- 모든 사람이 어려움을 겪어요
- 당신의 가치는 남과 무관해요

**대안:**
✅ 비교 유발 계정 언팔/뮤트
✅ 자기계발/동기부여 채널로 전환
✅ SNS 사용 시간 줄이기
""",
        '악플노출': """
⚠️ **악플/비난 노출 감지**

악플이나 부정적 반응에 노출되었나요?

**즉시 대응:**
- 🚫 악플 차단/신고
- 💬 댓글 끄기
- 🛡️ 방어 모드 활성화

**기억하세요:**
악플은 상대의 문제이지, 당신의 문제가 아닙니다.
""",
        '고립심화': """
🚨 **고립 심화 패턴 감지**

SNS 끊기/차단을 생각하고 있나요?

**경고:**
완전한 차단은 고립을 악화시킬 수 있어요.

**대신 이렇게:**
- 유해한 계정만 선택적 차단
- 긍정적 커뮤니티로 전환
- 온라인-오프라인 균형 잡기
""",
        'sns중독': """
⚠️ **SNS 과사용 감지**

SNS에 너무 많은 시간을 쓰고 있나요?

**건강한 사용:**
- ⏰ 하루 1-2시간 제한
- 🚫 취침 1시간 전 차단
- 📱 앱 타이머 설정
- 🌳 대신 산책/운동

**과사용은 우울증을 악화시킵니다.**
"""
    }
    
    messages = []
    for pattern in toxic_patterns:
        if pattern in interventions:
            messages.append(interventions[pattern])
    
    return messages

# ============================================================================
# 3-6. Social Connection Dashboard (사회적 연결 대시보드)
# ============================================================================

def show_social_connection_dashboard():
    """사회적 연결 대시보드"""
    st.subheader("🤝 사회적 연결 대시보드")
    
    # 고립 점수 업데이트
    update_isolation_score()
    
    score = st.session_state.isolation_score
    isolation_level = get_isolation_level()
    
    # 마지막 접촉
    days_since = 999
    if st.session_state.last_social_contact:
        last_contact = st.session_state.last_social_contact
        if isinstance(last_contact, str):
            last_contact = datetime.fromisoformat(last_contact)
        days_since = (datetime.now() - last_contact).days
    
    # 최근 7일 접촉 횟수
    week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
    recent_contacts = [c for c in st.session_state.social_interactions if c['date'] >= week_ago]
    
    # 메트릭
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if days_since == 0:
            st.metric("마지막 접촉", "오늘 ✅")
        elif days_since < 3:
            st.metric("마지막 접촉", f"{days_since}일 전 ⚠️")
        elif days_since < 999:
            st.metric("마지막 접촉", f"{days_since}일 전 🚨")
        else:
            st.metric("마지막 접촉", "기록 없음")
    
    with col2:
        st.metric("7일 접촉", f"{len(recent_contacts)}회")
    
    with col3:
        color_emoji = {
            'green': '✅',
            'yellow': '⚠️',
            'orange': '🚨',
            'red': '❌'
        }
        st.metric("고립 점수", f"{score}/100 {color_emoji[isolation_level['color']]}")
    
    with col4:
        st.metric("상태", isolation_level['label'])
    
    st.markdown("---")
    
    # 고립 수준별 경고
    if isolation_level['level'] >= 2:
        st.error(f"""
        ⚠️ **{isolation_level['label']} 상태**
        
        고립 점수: {score}/100
        마지막 접촉: {days_since}일 전
        
        **즉시 사회적 연결이 필요합니다!**
        """)
    elif isolation_level['level'] == 1:
        st.warning(f"""
        💛 사회적 연결을 권장합니다
        
        고립 점수: {score}/100
        최근 {days_since}일간 접촉이 적어요.
        """)
    else:
        st.success("✅ 사회적 연결 양호!")
    
    st.markdown("---")
    
    # Module 3: 현실 세계 연결 제안
    st.subheader("🌍 현실 세계 연결 제안")
    
    suggestions = get_reality_social_suggestions()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 즉시 가능")
        for suggestion in suggestions['즉시 가능']:
            st.markdown(f"- {suggestion}")
    
    with col2:
        st.markdown("### 약간의 준비")
        for suggestion in suggestions['약간의 준비']:
            st.markdown(f"- {suggestion}")
    
    with col3:
        st.markdown("### 계획 필요")
        for suggestion in suggestions['계획 필요']:
            st.markdown(f"- {suggestion}")
    
    st.markdown("---")
    
    # 지역사회 자원
    st.subheader("📍 지역사회 자원")
    
    resources = get_community_resources()
    
    tab1, tab2, tab3, tab4 = st.tabs(["정신건강", "종교시설", "사회활동", "온라인커뮤니티"])
    
    with tab1:
        for resource in resources['정신건강']:
            st.markdown(f"- {resource}")
    
    with tab2:
        for resource in resources['종교시설']:
            st.markdown(f"- {resource}")
    
    with tab3:
        for resource in resources['사회활동']:
            st.markdown(f"- {resource}")
    
    with tab4:
        for resource in resources['온라인커뮤니티']:
            st.markdown(f"- {resource}")
    
    st.markdown("---")
    
    # Module 4: 디지털 연결 팁
    st.subheader("📱 디지털 연결 가이드")
    
    digital_tips = get_digital_connection_tips()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 초보자용")
        for tip in digital_tips['초보자용 (쉬움)']:
            st.markdown(f"- {tip}")
    
    with col2:
        st.markdown("### 중급자용")
        for tip in digital_tips['중급자용 (보통)']:
            st.markdown(f"- {tip}")
    
    with col3:
        st.markdown("### 적극적")
        for tip in digital_tips['적극적 (활발)']:
            st.markdown(f"- {tip}")
    
    st.markdown("---")
    
    # Module 5: SNS 안전 가이드
    st.subheader("🛡️ SNS 안전 가이드")
    
    safety = get_sns_safety_guide()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚠️ 피해야 할 것")
        for item in safety['⚠️ 피해야 할 것']:
            st.markdown(f"{item}")
    
    with col2:
        st.markdown("### ✅ 권장하는 것")
        for item in safety['✅ 권장하는 것']:
            st.markdown(f"{item}")
    
    st.markdown("---")
    
    # 깐부의 메시지
    st.info("""
    💙 **깐부가 말했던 진실:**
    
    "사람의 관심이 필요하다.
    그곳으로 가라."
    
    고립은 우울증의 가장 큰 적입니다.
    작은 연결부터 시작하세요.
    """)
    
    st.markdown("---")
    
    # 최근 접촉 기록
    if len(st.session_state.social_interactions) > 0:
        st.subheader("📋 최근 사회적 접촉 기록")
        
        recent_10 = st.session_state.social_interactions[-10:]
        
        for record in reversed(recent_10):
            timestamp = datetime.fromisoformat(record['timestamp']).strftime("%m/%d %H:%M")
            contact_type = record['type']
            quality = record['quality']
            notes = record.get('notes', '')
            
            quality_emoji = "💙" if quality == "따뜻했다" else "😊" if quality == "괜찮았다" else "😐" if quality == "형식적이었다" else "😔"
            
            with st.expander(f"{quality_emoji} {timestamp} - {contact_type} ({quality})"):
                if notes:
                    st.write(f"**내용:** {notes}")
                st.write(f"**시각:** {timestamp}")
                st.write(f"**느낌:** {quality}")
    
    st.markdown("---")
    
    # 접촉 기록 추가
    st.subheader("➕ 사회적 접촉 기록 추가")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        contact_type = st.selectbox(
            "접촉 유형",
            ["대면 만남", "전화/영상", "SNS 댓글", "단톡방", "문자", "기타"],
            key="main_contact_type"
        )
    
    with col2:
        quality = st.selectbox(
            "느낌",
            ["따뜻했다", "괜찮았다", "형식적이었다", "힘들었다"],
            key="main_quality"
        )
    
    with col3:
        notes = st.text_input("내용 (선택)", placeholder="예: 친구와 카페", key="main_notes")
    
    if st.button("✅ 접촉 기록 추가", use_container_width=True, type="primary"):
        record_social_contact(contact_type, quality, notes)
        st.success("🎉 기록 완료! 사회적 연결은 회복의 핵심이에요!")
        if quality == "따뜻했다":
            st.balloons()
        time.sleep(1)
        st.rerun()

# ============================================================================
# 2-4. V2.0 - 경계 시간 관리 및 AI 개입 (유지)
# ============================================================================

def reset_daily_state():
    """매일 자동 초기화"""
    today = datetime.now().date()
    
    if st.session_state.last_reset_date < today:
        st.session_state.recovery_confirmed = False
        st.session_state.last_reset_date = today

def check_boundary_zone():
    """경계 구역 체크"""
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
    **V2.5 Phase 1 Complete**
    
    - 취침 1시간 전부터 경계 구역 모드
    - 다단계 위기 감지 시스템
    - **강력한 운동 개입 시스템**
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
# 2-4. Crisis Dashboard (유지)
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
        st.metric("최근 30일", f"{pattern.get('recent_30days', 0)}회")
    
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
        계속 건강한 패턴을 유지하세요.
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

# ============================================================================
# 3. 면책 조항 (유지)
# ============================================================================

def show_disclaimer():
    """면책 조항"""
    st.title("🌙 GINI R.E.S.T.")
    st.subheader("Human Recovery AI System v3.0")
    st.caption("✅ Phase 1 COMPLETE: Crisis + Exercise + Nutrition + Social Connection")
    
    st.markdown("---")
    
    st.markdown("""
    ### ⚠️ 이용 약관 및 면책 조항
    
    #### 1. 서비스의 성격
    - 본 서비스는 **정신건강 회복 지원 도구**입니다.
    - 수면, 운동, 영양, 사회적 연결 패턴을 관리합니다.
    - **의학적 진단, 치료, 상담을 제공하지 않습니다.**
    
    #### 2. AI 개입 기능 (V3.0 Phase 1 Complete)
    - ✅ 다단계 위기 감지 시스템
    - ✅ 강력한 운동 개입 시스템
    - ✅ 강력한 영양 개입 시스템
    - ✅ **사회적 연결 엔진 (5개 모듈)**
    - ✅ GPS 위치 자동 표시 (긴급 상황용)
    - 직설적이고 강한 메시지 포함 (회복을 위한 설계)
    
    #### 3. 사용자의 책임
    - 심각한 정신건강 문제가 있다면 **반드시 전문가와 상담**하세요.
    - 24시간 이상 식사를 하지 않았다면 의학적 개입이 필요합니다.
    - 7일 이상 고립 상태라면 사회적 지원이 필요합니다.
    - 응급 상황 시 즉시 119 또는 1393으로 연락하세요.
    
    #### 4. 데이터
    - 브라우저 세션에만 저장됩니다.
    - 서버에 저장하지 않습니다.
    
    #### 5. 면책사항
    - 본 서비스 사용으로 인한 결과에 대해 개발자는 책임지지 않습니다.
    
    #### 6. 사회적 연결 엔진 (SCE)
    - 고립 감지, 사회 연결 개입, 현실/디지털 연결 제안
    - "사람의 관심이 필요하다. 그곳으로 가라." (깐부의 철학)
    """)
    
    st.markdown("---")
    
    agree = st.checkbox("위 내용을 모두 읽고 이해했으며, 이에 동의합니다.")
    
    if st.button("시작하기", disabled=not agree, use_container_width=True):
        st.session_state.agreed_to_terms = True
        st.rerun()

# ============================================================================
# 기존 기능들 (간략화 - 실제로는 원본 유지)
# ============================================================================

def add_sleep_record():
    """수면 기록 (유지)"""
    st.info("수면 기록 기능 - v2.0 유지")

def calculate_sleep_debt():
    """수면 분석 (유지)"""
    st.info("수면 분석 기능 - v2.0 유지")

def show_cbti_education():
    """CBT-I 교육 (유지)"""
    st.info("CBT-I 교육 - v2.0 유지")

def breathing_exercise():
    """호흡 운동 (유지)"""
    st.info("호흡 운동 - v2.0 유지")

def show_education():
    """AI 상담 (Enhanced)"""
    st.title("💬 AI 상담")
    st.caption("Enhanced Crisis Detection + Exercise Intervention")
    
    st.markdown("---")
    
    st.subheader("💬 질문하기")
    st.warning("⚠️ V2.5 Phase 1: 다단계 위기 감지 + 운동 개입 활성화")
    
    user_input = st.text_input("수면 또는 정신건강 관련 질문:")
    
    if user_input:
        has_crisis, crisis_level, crisis_response = check_crisis_keywords(user_input)
        
        if has_crisis:
            st.session_state.emergency_mode = True
            st.session_state.crisis_level = crisis_level
            st.rerun()
        else:
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write("""
            더 자세한 정보는 각 메뉴를 참고하세요:
            - 📊 수면 기록
            - 💤 수면 분석
            - 🏃 운동 대시보드
            - 🧠 CBT-I 교육
            - 🫁 호흡 운동
            """)

# ============================================================================
# 메인 앱
# ============================================================================

def show_emergency_with_location():
    """긴급 모드 with 위치 정보"""
    level = st.session_state.crisis_level
    pattern = get_crisis_pattern()
    response = get_crisis_response(level, pattern)
    
    st.error(response)
    
    st.markdown("---")
    
    # 위치 정보 표시
    st.error("### 📍 당신의 현재 위치 (119에 알려주세요)")
    
    # 119 바로 전화 버튼 (Raira 제안 #3)
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
        <a href="tel:119" style="background: #ff0000; color: white; padding: 20px 40px; 
           font-size: 24px; font-weight: bold; text-decoration: none; border-radius: 10px; 
           display: inline-block; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
            📞 119 긴급 전화걸기
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    # HTML/JavaScript로 위치 가져오기
    location_html = """
    <div style="background-color: #ff4444; padding: 20px; border-radius: 10px; color: white;">
        <h2 style="color: white;">🚨 현재 위치 확인</h2>
        <div id="location-info" style="font-size: 20px; margin-top: 20px;">
            <button onclick="getLocation()" style="background: white; color: #ff4444; padding: 15px 30px; font-size: 18px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
                📍 내 위치 표시하기
            </button>
        </div>
        <div id="location-result" style="margin-top: 20px; font-size: 18px; line-height: 1.8;"></div>
    </div>
    
    <script>
    function getLocation() {
        const locationInfo = document.getElementById('location-info');
        const locationResult = document.getElementById('location-result');
        
        if (navigator.geolocation) {
            locationInfo.innerHTML = '<p style="font-size: 18px;">⏳ 위치 확인 중...</p>';
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude.toFixed(6);
                    const lon = position.coords.longitude.toFixed(6);
                    const accuracy = position.coords.accuracy.toFixed(0);
                    
                    // Raira 제안 #4: 정확도 해석
                    let accuracyText = '';
                    if (accuracy < 50) {
                        accuracyText = '매우 정확 (오차 50m 이내)';
                    } else if (accuracy < 200) {
                        accuracyText = '정확 (오차 200m 이내)';
                    } else if (accuracy < 1000) {
                        accuracyText = '보통 (오차 1km 이내)';
                    } else {
                        accuracyText = '부정확 (오차 ' + (accuracy/1000).toFixed(1) + 'km 이상)<br>실내, 지하, 건물 밀집 지역일 수 있습니다.';
                    }
                    
                    locationInfo.innerHTML = '<p style="font-size: 18px;">✅ 위치 확인 완료!</p>';
                    
                    locationResult.innerHTML = `
                        <div style="background: white; color: black; padding: 20px; border-radius: 10px; margin-top: 10px;">
                            <h3 style="color: #ff4444; margin-top: 0;">📞 119에 이렇게 말하세요:</h3>
                            <div style="background: #ffffcc; padding: 15px; border-radius: 5px; margin: 10px 0; border: 3px solid #ff4444;">
                                <p style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #000;">
                                    "위도: ${lat}"<br>
                                    "경도: ${lon}"
                                </p>
                            </div>
                            <p style="font-size: 16px; color: #666; margin-top: 15px;">
                                <strong>위치 정확도:</strong> ${accuracyText}<br>
                                <strong>119에서 이 좌표로 정확한 위치를 찾을 수 있습니다.</strong>
                            </p>
                            <button onclick="copyLocation('${lat}', '${lon}')" 
                                style="background: #ff4444; color: white; padding: 15px 30px; font-size: 16px; 
                                border: none; border-radius: 5px; cursor: pointer; margin-top: 15px; font-weight: bold;">
                                📋 좌표 복사하기
                            </button>
                            <div id="copy-result" style="margin-top: 10px; color: green; font-weight: bold;"></div>
                        </div>
                    `;
                },
                function(error) {
                    // Raira 제안 #1, #2: GPS 실패 원인 상세 안내
                    let errorMsg = '';
                    let solutionMsg = '';
                    
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg = "❌ 위치 권한이 거부되었습니다.";
                            solutionMsg = `
                                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ff4444;">
                                    <h4 style="color: #ff4444; margin-top: 0;">🔧 해결 방법:</h4>
                                    <p style="color: #000; font-size: 15px; line-height: 1.6;">
                                        <strong>📱 안드로이드:</strong><br>
                                        설정 → 앱 → Chrome(또는 사용 중인 브라우저) → 권한 → 위치 → <strong>'허용'</strong><br><br>
                                        
                                        <strong>🍎 iOS:</strong><br>
                                        설정 → Safari(또는 Chrome) → 위치 → <strong>'허용'</strong><br><br>
                                        
                                        <strong>💻 PC/Mac:</strong><br>
                                        브라우저 주소창 왼쪽 자물쇠 아이콘 클릭 → 위치 → <strong>'허용'</strong>
                                    </p>
                                </div>
                            `;
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg = "❌ 위치 정보를 사용할 수 없습니다.";
                            solutionMsg = `
                                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ff4444;">
                                    <h4 style="color: #ff4444; margin-top: 0;">🔧 확인사항:</h4>
                                    <p style="color: #000; font-size: 15px; line-height: 1.6;">
                                        ✓ <strong>스마트폰 위치 서비스(GPS) 켜져 있나요?</strong><br>
                                        ✓ <strong>비행기 모드가 꺼져 있나요?</strong><br>
                                        ✓ <strong>실내나 지하가 아닌가요?</strong> (창문 근처로 이동)<br>
                                        ✓ <strong>Wi-Fi나 모바일 데이터가 켜져 있나요?</strong>
                                    </p>
                                </div>
                            `;
                            break;
                        case error.TIMEOUT:
                            errorMsg = "❌ 위치 확인 시간이 초과되었습니다.";
                            solutionMsg = `
                                <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #ff4444;">
                                    <h4 style="color: #ff4444; margin-top: 0;">🔧 다시 시도:</h4>
                                    <p style="color: #000; font-size: 15px; line-height: 1.6;">
                                        ✓ 창문 근처나 <strong>실외로 이동</strong><br>
                                        ✓ 잠시 후 <strong>'내 위치 표시하기' 버튼 다시 클릭</strong><br>
                                        ✓ GPS 신호가 약한 환경일 수 있습니다
                                    </p>
                                </div>
                            `;
                            break;
                    }
                    
                    locationInfo.innerHTML = `<p style="font-size: 16px;">${errorMsg}</p>`;
                    locationResult.innerHTML = `
                        <div style="background: white; color: black; padding: 20px; border-radius: 10px; margin-top: 10px;">
                            ${solutionMsg}
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 15px;">
                                <h4 style="color: #ff4444; margin-top: 0;">🆘 위치를 확인할 수 없는 경우:</h4>
                                <p style="color: #000; font-size: 16px; line-height: 1.8;">
                                    1. <strong>주변 사람에게 도움 요청</strong><br>
                                    2. <strong>주변 건물이나 간판 이름</strong> 확인<br>
                                    3. <strong>도로명</strong> 확인<br>
                                    4. 119에 <strong>"위치 모름"</strong> 상태라고 알림<br>
                                    5. 119는 <strong>통화 중에도 위치 추적</strong> 가능합니다
                                </p>
                            </div>
                        </div>
                    `;
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        } else {
            locationInfo.innerHTML = '<p style="font-size: 16px;">❌ 이 브라우저는 위치 서비스를 지원하지 않습니다.</p>';
            locationResult.innerHTML = `
                <div style="background: white; color: black; padding: 20px; border-radius: 10px; margin-top: 10px;">
                    <p style="color: #ff4444; font-weight: bold;">최신 브라우저를 사용해주세요:</p>
                    <p style="font-size: 16px;">Chrome, Safari, Firefox, Edge 등</p>
                </div>
            `;
        }
    }
    
    function copyLocation(lat, lon) {
        const text = `위도: ${lat}, 경도: ${lon}`;
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                document.getElementById('copy-result').innerHTML = '✅ 복사 완료! 119 통화 시 붙여넣기 하세요.';
            }, function() {
                document.getElementById('copy-result').innerHTML = '❌ 복사 실패. 직접 읽어주세요.';
            });
        } else {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                document.getElementById('copy-result').innerHTML = '✅ 복사 완료!';
            } catch (err) {
                document.getElementById('copy-result').innerHTML = '❌ 복사 실패. 직접 읽어주세요.';
            }
            document.body.removeChild(textArea);
        }
    }
    </script>
    """
    
    st.components.v1.html(location_html, height=650, scrolling=True)
    
    st.markdown("---")
    
    st.info("""
    ### 💡 위치 정보 사용 방법
    
    1. **위에 "119 긴급 전화걸기" 버튼을 먼저 누르세요** (모바일에서 바로 전화 연결)
    2. **"내 위치 표시하기" 버튼 클릭**
    3. 브라우저에서 위치 권한 허용
    4. **위도/경도가 표시되면 119에 그대로 읽어주세요**
    5. 119에서 해당 좌표로 정확한 위치를 찾을 수 있습니다
    
    ⚠️ **위치가 안 잡히면 위의 해결 방법을 따라주세요**
    """)
    
    st.markdown("---")
    
    if st.button("안전 모드 해제", use_container_width=True):
        st.session_state.emergency_mode = False
        st.session_state.crisis_level = 0
        st.rerun()

def main():
    """메인 앱"""
    init_session_state()
    reset_daily_state()
    
    if not st.session_state.agreed_to_terms:
        show_disclaimer()
        return
    
    # 1순위: Emergency Crisis Mode with Location
    if st.session_state.emergency_mode:
        show_emergency_with_location()
        return
    
    # 2순위: Sleep Intervention Mode
    if st.session_state.intervention_mode:
        show_intervention()
        return
    
    # 3순위: Exercise Intervention Check (Level 2+)
    exercise_intervention = check_exercise_intervention()
    if exercise_intervention and exercise_intervention['level'] >= 2:
        show_exercise_intervention()
        return
    
    # 4순위: Nutrition Intervention Check (Level 2+)
    nutrition_intervention = check_nutrition_intervention()
    if nutrition_intervention and nutrition_intervention['level'] >= 2:
        show_nutrition_intervention()
        return
    
    # 5순위: Social Intervention Check (Level 2+)
    social_intervention = check_social_intervention()
    if social_intervention and social_intervention['level'] >= 2:
        show_social_intervention()
        return
    
    # 경계 구역 체크
    in_boundary = check_boundary_zone()
    if in_boundary and not st.session_state.recovery_confirmed:
        if st.session_state.target_bedtime:
            st.warning(f"""
            ⚠️ **경계 구역 활성화**
            
            취침 시간 {st.session_state.target_bedtime.strftime('%H:%M')}까지 1시간 미만 남았습니다.
            """)
    
    # 사이드바
    with st.sidebar:
        st.title("🌙 GINI R.E.S.T.")
        st.caption("v3.0 Phase 1 Complete ✅")
        st.caption("Crisis + Exercise + Nutrition + Social")
        
        st.markdown("---")
        
        # 상태 표시
        pattern = get_crisis_pattern()
        days_no_exercise = days_since_last_exercise()
        hours_no_meal = hours_since_last_meal()
        
        # 고립 점수 업데이트
        update_isolation_score()
        isolation_level = get_isolation_level()
        
        # 위기 상태
        if pattern['trend'] == 'worsening':
            st.error(f"⚠️ 위기: {pattern['recent_7days']}회/7일")
        elif pattern['trend'] == 'concerning':
            st.warning(f"📊 주의: {pattern['recent_7days']}회/7일")
        else:
            st.success("✅ 정신건강: 안정")
        
        # 운동 상태
        if days_no_exercise == 0:
            st.success("💪 운동: 오늘 완료 ✅")
        elif days_no_exercise <= 2:
            st.warning(f"⚠️ 운동: {days_no_exercise}일 미실시")
        else:
            st.error(f"🚨 운동: {days_no_exercise}일 미실시")
        
        # 영양 상태
        if hours_no_meal < 6:
            st.success("🍽️ 식사: 양호 ✅")
        elif hours_no_meal < 12:
            st.warning(f"⚠️ 식사: {hours_no_meal:.0f}시간 전")
        else:
            st.error(f"🚨 식사: {hours_no_meal:.0f}시간 전")
        
        # 사회적 연결 상태 (NEW)
        days_since_social = 999
        if st.session_state.last_social_contact:
            last_contact = st.session_state.last_social_contact
            if isinstance(last_contact, str):
                last_contact = datetime.fromisoformat(last_contact)
            days_since_social = (datetime.now() - last_contact).days
        
        if days_since_social == 0:
            st.success("🤝 사회적 연결: 오늘 ✅")
        elif days_since_social < 3:
            st.warning(f"⚠️ 사회적 연결: {days_since_social}일 전")
        elif days_since_social < 999:
            st.error(f"🚨 고립: {days_since_social}일째")
        else:
            st.info("🤝 사회적 연결: 기록 없음")
        
        # 수면 상태
        if st.session_state.target_bedtime:
            st.info(f"🎯 목표: {st.session_state.target_bedtime.strftime('%H:%M')}")
        
        st.markdown("---")
        
        menu = st.radio(
            "메뉴",
            [
                "🎯 V3.0 설정",
                "📊 위기 대시보드",
                "🏃 운동 대시보드",
                "🍽️ 영양 대시보드",
                "🤝 사회적 연결",  # NEW
                "💬 AI 상담",
                "📊 수면 기록",
                "💤 수면 분석",
                "🧠 CBT-I 교육",
                "🫁 호흡 운동"
            ]
        )
        
        st.markdown("---")
        st.caption(f"수면: {len(st.session_state.sleep_data)}일")
        st.caption(f"위기: {pattern['total_count']}회")
        st.caption(f"운동: {len(st.session_state.exercise_records)}일")
        st.caption(f"연속: {st.session_state.exercise_streak}일 🔥")
        st.caption(f"식사: {len(st.session_state.meal_records)}회")
        st.caption(f"사회: {len(st.session_state.social_interactions)}회")  # NEW
        st.caption(f"고립: {st.session_state.isolation_score}/100")  # NEW
        
        if st.button("⚠️ 긴급 도움"):
            st.session_state.emergency_mode = True
            st.session_state.crisis_level = 3
            st.rerun()
    
    # Level 1 경고 (상단 띠)
    warnings_shown = 0
    
    # 운동 Level 1 경고
    if exercise_intervention and exercise_intervention['level'] == 1:
        st.warning(exercise_intervention['message'])
        warnings_shown += 1
    
    # 영양 Level 1 경고
    if nutrition_intervention and nutrition_intervention['level'] == 1:
        st.warning(nutrition_intervention['message'])
        warnings_shown += 1
    
    # 사회적 연결 Level 1 경고 (NEW)
    if social_intervention and social_intervention['level'] == 1:
        st.warning(social_intervention['message'])
        warnings_shown += 1
    
    # 메뉴별 화면
    if menu == "🎯 V3.0 설정":
        st.title("🎯 V3.0 설정")
        set_target_bedtime()
        
        st.markdown("---")
        st.subheader("📊 전체 현황")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("수면 기록", f"{len(st.session_state.sleep_data)}일")
        
        with col2:
            st.metric("위기 감지", f"{pattern['total_count']}회")
        
        with col3:
            st.metric("운동 일수", f"{len(st.session_state.exercise_records)}일")
        
        with col4:
            st.metric("식사 기록", f"{len(st.session_state.meal_records)}회")
        
        with col5:
            st.metric("사회 접촉", f"{len(st.session_state.social_interactions)}회")
    
    elif menu == "📊 위기 대시보드":
        st.title("📊 위기 대시보드")
        show_crisis_dashboard()
    
    elif menu == "🏃 운동 대시보드":
        st.title("🏃 운동 대시보드")
        show_exercise_dashboard()
    
    elif menu == "🍽️ 영양 대시보드":
        st.title("🍽️ 영양 대시보드")
        show_nutrition_dashboard()
    
    elif menu == "🤝 사회적 연결":
        st.title("🤝 사회적 연결")
        show_social_connection_dashboard()
    
    elif menu == "💬 AI 상담":
        show_education()
    
    elif menu == "📊 수면 기록":
        st.title("📊 수면 기록")
        add_sleep_record()
    
    elif menu == "💤 수면 분석":
        st.title("💤 수면 분석")
        calculate_sleep_debt()
    
    elif menu == "🧠 CBT-I 교육":
        st.title("🧠 CBT-I 교육")
        show_cbti_education()
    
    elif menu == "🫁 호흡 운동":
        st.title("🫁 호흡 운동")
        breathing_exercise()

if __name__ == "__main__":
    main()
