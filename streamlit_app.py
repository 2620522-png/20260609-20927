import streamlit as st
import psutil
import time
import pandas as pd

# 1. 스트림릿 페이지 설정
st.set_page_config(page_title="실시간 배터리 모니터링", page_icon="🔋", layout="centered")
st.title("🔋 실시간 배터리 모니터링 시스템")
st.write("기기의 배터리 상태를 실시간으로 추적하고 이상 징후를 감지합니다.")

# 현재 배터리 상태 먼저 체크
initial_battery = psutil.sensors_battery()

# 2. 세션 상태(Session State) 초기화 (안전하게 수정)
if "battery_history" not in st.session_state:
    st.session_state.battery_history = []
if "last_battery" not in st.session_state:
    # 배터리가 있으면 해당 퍼센트를, 없으면 임시로 100을 넣어둠
    st.session_state.last_battery = initial_battery.percent if initial_battery else 100

# 실시간 업데이트를 위한 스트림릿 빈 공간(placeholder) 생성
metrics_placeholder = st.empty()
alert_placeholder = st.empty()
chart_placeholder = st.empty()

# 3. 모니터링 루프 시작
while True:
    # 현재 배터리 상태 가져오기
    battery = psutil.sensors_battery()
    
    # [중요] 배터리가 없는 환경이라면 루프를 안전하게 탈출
    if battery is None:
        metrics_placeholder.empty() # 이전 잔상 지우기
        alert_placeholder.error("❌ 현재 기기(데스크톱 PC 또는 클라우드 서버)에서 배터리 정보를 가져올 수 없습니다. 노트북 환경에서 테스트해 주세요.")
        break
        
    current_percent = battery.percent
    is_plugged = battery.power_plugged
    
    # 배터리 잔량 리스트에 추가
    st.session_state.battery_history.append(current_percent)
    
    # --- 조건문 처리 (알림 및 경고) ---
    with alert_placeholder.container():
        drop_threshold = 2 
        if (st.session_state.last_battery - current_percent) >= drop_threshold and not is_plugged:
            st.error(f"⚠️ 경고: 배터리가 급격하게 감소하고 있습니다! (이전: {st.session_state.last_battery}%, 현재: {current_percent}%)")
        
        if current_percent <= 10:
            st.error(f"🚨 위험: 배터리가 {current_percent}% 남았습니다. 즉시 충전기를 연결하세요!")
        elif current_percent <= 20:
            st.warning(f"⚠️ 주의: 배터리 잔량이 {current_percent}%입니다.")
            
        if current_percent == 0:
            st.error("💀 배터리가 0%가 되었습니다. 프로그램을 종료합니다.")
            time.sleep(3)
            st.stop()
            
    st.session_state.last_battery = current_percent

    # --- UI 업데이트 ---
    with metrics_placeholder.container():
        col1, col2 = st.columns(2)
        col1.metric(label="현재 배터리 잔량", value=f"{current_percent}%")
        col2.metric(label="충전 상태", value="⚡ 충전 중" if is_plugged else "🔋 배터리 사용 중")

    with chart_placeholder.container():
        st.subheader("📊 배터리 잔량 변화 기록")
        df = pd.DataFrame(st.session_state.battery_history, columns=["Battery %"])
        st.line_chart(df)
        st.write(st.session_state.battery_history[-10:])

    time.sleep(5)
    st.rerun()