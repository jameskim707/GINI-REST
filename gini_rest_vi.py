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
    """수면 빚 계산 + 패턴 분석 + 감정 태그 분석"""
    if len(st.session_state.sleep_data) == 0:
        st.info("아직 수면 기록이 없습니다. 먼저 기록을 추가해주세요.")
        return
    
    st.subheader("💤 수면 종합 분석")
    
    # 최근 7일 데이터
    recent_data = st.session_state.sleep_data[-7:]
    
    total_hours = sum([record['total_sleep_hours'] for record in recent_data])
    avg_sleep = total_hours / len(recent_data)
    avg_latency = sum([record['sleep_latency'] for record in recent_data]) / len(recent_data)
    avg_awake = sum([record['awake_count'] for record in recent_data]) / len(recent_data)
    
    recommended_sleep = 7.5  # 권장 수면 시간
    daily_deficit = recommended_sleep - avg_sleep
    total_debt = daily_deficit * len(recent_data)
    
    # 기본 지표
    st.markdown("### 📊 기본 수면 지표")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("평균 수면", f"{avg_sleep:.1f}시간")
    
    with col2:
        st.metric("입면 시간", f"{avg_latency:.0f}분")
    
    with col3:
        st.metric("야간 각성", f"{avg_awake:.1f}회")
    
    with col4:
        st.metric("수면 빚", f"{abs(total_debt):.1f}h", 
                 delta=f"{daily_deficit:.1f}h/일", delta_color="inverse")
    
    st.markdown("---")
    
    # 수면 패턴 인사이트
    st.markdown("### 🔍 패턴 인사이트")
    
    # 스마트폰 사용 분석
    screen_days = sum([1 for r in recent_data if r['screen_after_10pm']])
    screen_sleep_avg = sum([r['total_sleep_hours'] for r in recent_data if r['screen_after_10pm']]) / max(screen_days, 1)
    no_screen_sleep_avg = sum([r['total_sleep_hours'] for r in recent_data if not r['screen_after_10pm']]) / max(len(recent_data) - screen_days, 1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📱 스마트폰 사용 영향**")
        if screen_days > 0:
            st.write(f"- 밤 10시 이후 사용: {screen_days}일")
            st.write(f"- 사용일 평균 수면: {screen_sleep_avg:.1f}시간")
            if len(recent_data) - screen_days > 0:
                st.write(f"- 미사용일 평균 수면: {no_screen_sleep_avg:.1f}시간")
                diff = no_screen_sleep_avg - screen_sleep_avg
                if diff > 0.3:
                    st.warning(f"⚠️ 스마트폰 사용 시 수면 {diff:.1f}시간 감소!")
        else:
            st.success("✅ 야간 스마트폰 사용 없음!")
    
    with col2:
        st.markdown("**☕ 카페인 섭취 영향**")
        caffeine_days = sum([1 for r in recent_data if r['caffeine_intake']])
        if caffeine_days > 0:
            caffeine_sleep_avg = sum([r['total_sleep_hours'] for r in recent_data if r['caffeine_intake']]) / caffeine_days
            no_caffeine_sleep_avg = sum([r['total_sleep_hours'] for r in recent_data if not r['caffeine_intake']]) / max(len(recent_data) - caffeine_days, 1)
            
            st.write(f"- 오후 카페인 섭취: {caffeine_days}일")
            st.write(f"- 섭취일 평균 수면: {caffeine_sleep_avg:.1f}시간")
            if len(recent_data) - caffeine_days > 0:
                st.write(f"- 미섭취일 평균 수면: {no_caffeine_sleep_avg:.1f}시간")
                diff = no_caffeine_sleep_avg - caffeine_sleep_avg
                if diff > 0.3:
                    st.warning(f"⚠️ 카페인 섭취 시 수면 {diff:.1f}시간 감소!")
        else:
            st.success("✅ 오후 카페인 섭취 없음!")
    
    st.markdown("---")
    
    # 감정 태그 분석
    st.markdown("### 😊 감정 패턴 분석")
    
    # 모든 감정 태그 수집
    all_moods = []
    for record in recent_data:
        all_moods.extend(record['mood_tags'])
    
    if all_moods:
        from collections import Counter
        mood_counts = Counter(all_moods)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**가장 빈번한 감정 (Top 5)**")
            for mood, count in mood_counts.most_common(5):
                percentage = (count / len(recent_data)) * 100
                st.write(f"- {mood}: {count}회 ({percentage:.0f}%)")
        
        with col2:
            st.markdown("**감정별 수면 영향**")
            
            # 부정적 감정
            negative_moods = ['불안', '스트레스', '우울', '긴장', '걱정', '화남', '무기력', '초조']
            negative_count = sum([1 for mood in all_moods if mood in negative_moods])
            
            if negative_count > len(recent_data) * 0.5:
                st.error(f"⚠️ 부정적 감정 빈도 높음 ({negative_count}회)")
                st.write("부정적 감정은 수면의 질을 저하시킵니다.")
                st.write("💡 호흡 운동과 CBT-I를 활용해보세요.")
            elif negative_count > 0:
                st.info(f"부정적 감정: {negative_count}회")
            else:
                st.success("✅ 안정적인 감정 상태!")
            
            # 긍정적 감정
            positive_moods = ['평온', '만족']
            positive_count = sum([1 for mood in all_moods if mood in positive_moods])
            
            if positive_count > 0:
                st.success(f"긍정적 감정: {positive_count}회")
    else:
        st.info("감정 태그가 기록되지 않았습니다.")
    
    st.markdown("---")
    
    # 종합 조언
    st.markdown("### 💡 맞춤형 조언")
    
    if total_debt > 0:
        recovery_days = int(total_debt / 1.5) + 1
        
        st.warning(f"""
        **⚠️ 수면 빚 누적**
        
        - 지난 {len(recent_data)}일 평균: **{avg_sleep:.1f}시간**
        - 권장량 대비: **매일 {abs(daily_deficit):.1f}시간 부족**
        - 총 누적: **{abs(total_debt):.1f}시간**
        - 회복 예상: **최소 {recovery_days}일**
        
        **우선 실천 사항:**
        """)
        
        # 맞춤형 조언
        if screen_days > len(recent_data) * 0.5:
            st.write("1. 📱 밤 10시 이후 스마트폰 사용 중단")
        
        if caffeine_days > len(recent_data) * 0.5:
            st.write("2. ☕ 오후 2시 이후 카페인 금지")
        
        if avg_latency > 30:
            st.write("3. 🛏️ 20분 규칙 실천 (잠 안 오면 침대 나오기)")
        
        if negative_count > len(recent_data) * 0.5:
            st.write("4. 🫁 매일 취침 전 호흡 운동")
        
    else:
        st.success(f"""
        **✅ 건강한 수면 패턴!**
        
        - 평균 {avg_sleep:.1f}시간 수면
        - 권장량 충족
        - 현재 패턴 유지하세요!
        """)
    
    # 최고/최악의 날
    if len(recent_data) > 1:
        best_day = max(recent_data, key=lambda x: x['total_sleep_hours'])
        worst_day = min(recent_data, key=lambda x: x['total_sleep_hours'])
        
        st.markdown("---")
        st.markdown("### 📅 최고/최저 수면일")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**🏆 최고: {best_day['date']}**")
            st.write(f"- 수면: {best_day['total_sleep_hours']:.1f}시간")
            st.write(f"- 감정: {', '.join(best_day['mood_tags']) if best_day['mood_tags'] else '기록 없음'}")
        
        with col2:
            st.markdown(f"**😴 최저: {worst_day['date']}**")
            st.write(f"- 수면: {worst_day['total_sleep_hours']:.1f}시간")
            st.write(f"- 감정: {', '.join(worst_day['mood_tags']) if worst_day['mood_tags'] else '기록 없음'}")

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
            ["💬 AI 상담", "📊 수면 기록", "💤 수면 및 분석", "🧠 CBT-I 교육", "🫁 호흡 운동"]
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
        st.title("💬 수면 교육 상담")
        
        st.info("""
        **📚 수면에 관한 과학적 정보를 제공합니다.**
        
        궁금한 주제를 선택하거나 질문을 입력하세요.
        """)
        
        # FAQ 섹션
        st.subheader("자주 묻는 질문")
        
        faq = st.selectbox(
            "주제 선택:",
            [
                "카페인이 수면에 미치는 영향",
                "스마트폰 블루라이트와 수면",
                "낮잠을 자도 괜찮을까요?",
                "잠이 안 올 때 해야 할 행동",
                "수면 환경 최적화",
                "운동과 수면의 관계"
            ]
        )
        
        if st.button("답변 보기"):
            if faq == "카페인이 수면에 미치는 영향":
                st.markdown("""
                **☕ 카페인과 수면**
                
                **과학적 사실:**
                - 카페인 반감기: 5-6시간
                - 오후 2시에 마신 커피 → 밤 10시에도 절반이 체내에 남음
                - 수면 잠복기(잠드는 시간) 증가
                - 깊은 수면 단계 감소
                
                **권장사항:**
                - 오후 2시 이후 카페인 섭취 중단
                - 민감한 사람은 정오 이후 금지
                - 카페인 함량: 에스프레소(63mg), 아메리카노(150mg), 에너지드링크(80mg)
                
                💡 **당신의 데이터와 비교해보세요!**
                카페인 섭취한 날과 안 한 날의 수면 기록을 확인해보세요.
                """)
            
            elif faq == "스마트폰 블루라이트와 수면":
                st.markdown("""
                **📱 블루라이트의 영향**
                
                **과학적 메커니즘:**
                - 블루라이트 → 멜라토닌 분비 억제
                - 멜라토닌 = 수면 호르몬
                - 뇌가 "낮"이라고 착각
                
                **연구 결과:**
                - 취침 2시간 전 스마트폰 사용 → 수면 시작 평균 30분 지연
                - 깊은 수면 20% 감소
                
                **실천 방법:**
                - 취침 1시간 전 완전 차단 (최고)
                - 야간 모드 / 블루라이트 필터 (차선)
                - 침실에서 폰 제거 (알람은 시계 사용)
                
                ⚠️ **경고:** 침대에서 폰 보기 = 침대를 각성 공간으로 학습시킴
                """)
            
            elif faq == "낮잠을 자도 괜찮을까요?":
                st.markdown("""
                **😴 낮잠의 과학**
                
                **좋은 낮잠:**
                - 시간: 20-30분 (파워냅)
                - 시각: 오후 1-3시
                - 효과: 집중력↑, 기억력↑, 기분↑
                
                **나쁜 낮잠:**
                - 1시간 이상 → 깊은 수면 진입 → 기상 후 멍함
                - 오후 4시 이후 → 밤 수면 방해
                
                **실천 팁:**
                - 알람 30분 설정
                - 완전히 눕지 말고 소파/의자
                - 커피 낮잠: 자기 직전 커피 한 잔 → 20분 후 카페인 작용 시작
                """)
            
            elif faq == "잠이 안 올 때 해야 할 행동":
                st.markdown("""
                **🛏️ 20분 규칙**
                
                **절대 하지 말아야 할 것:**
                - 침대에서 뒤척이며 시간 보내기
                - 폰으로 시간 확인
                - "잠들어야 해" 압박
                
                **해야 할 것:**
                1. 20분 후에도 잠 안 오면 → 침대에서 나오기
                2. 거실/소파로 이동
                3. 차분한 활동 (독서, 명상, 스트레칭)
                4. 조명 어둡게 유지
                5. 졸림 느껴지면 → 다시 침대
                
                **원리:**
                침대 = 수면 장소로만 학습
                각성 상태에서 침대 = 불면증 강화
                
                💡 호흡 운동 메뉴에서 4-7-8 호흡법을 시도해보세요!
                """)
            
            elif faq == "수면 환경 최적화":
                st.markdown("""
                **🌡️ 최적 수면 환경**
                
                **온도:**
                - 이상적: 18-20°C
                - 너무 더우면 → 깊은 수면 방해
                - 양말 착용 OK (발 혈류↑ → 체온 조절)
                
                **조명:**
                - 완전 암흑 (손 안 보일 정도)
                - 커튼 차단
                - 전자기기 LED 가리기
                
                **소음:**
                - 40dB 이하 (속삭임 수준)
                - 백색소음 OK
                - 귀마개 고려
                
                **침구:**
                - 매트리스: 중간 정도 단단함
                - 베개: 목 정렬 유지
                - 침구 청결 (주 1회 세탁)
                """)
            
            elif faq == "운동과 수면의 관계":
                st.markdown("""
                **🏃 운동 타이밍이 중요**
                
                **좋은 운동 시간:**
                - 아침/오후: 수면의 질 향상
                - 규칙적 운동 → 깊은 수면 증가
                - 체온↑ → 저녁에 체온↓ → 수면 유도
                
                **피해야 할 시간:**
                - 취침 3시간 전 고강도 운동
                - 아드레날린 분비 → 각성
                
                **권장:**
                - 주 150분 중강도 유산소
                - 저녁엔 가벼운 스트레칭/요가
                - 운동 안 한 날 vs 한 날 수면 비교해보세요
                """)
        
        st.markdown("---")
        
        # 간단한 채팅 UI
        st.subheader("💬 질문하기")
        user_input = st.text_input("수면 관련 질문을 입력하세요:")
        
        if user_input:
            # 위기 키워드 감지
            if check_crisis_keywords(user_input):
                st.session_state.emergency_mode = True
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
