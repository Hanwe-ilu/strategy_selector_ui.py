import streamlit as st
import json
import os
from datetime import datetime, timedelta
import random
import string

st.set_page_config(page_title="策略申請表單", layout="wide")

if "stage" not in st.session_state:
    st.session_state.stage = "intro"

if "last_submit_time" not in st.session_state:
    st.session_state.last_submit_time = None

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ========== 第一階段：個人資料與風險聲明 ==========
if st.session_state.stage == "intro":
    st.markdown("""
        <h1 style='color:#1E90FF;'>📋 雲端託管交易策略申請</h1>
        <h3>步驟一：使用者資料與同意書</h3>
    """, unsafe_allow_html=True)

    with st.form(key="user_info_form"):
        nickname = st.text_input("您的暱稱")
        contact_method = st.radio("請選擇聯絡方式：", ["LINE 通訊軟體 ID", "手機號碼"])

        contact_placeholder = "請輸入正確資料"
        contact_info = st.text_input(contact_placeholder)

        admin_password = st.text_input("若您為管理者請輸入後台密碼（一般使用者請留空）", type="password")
        if admin_password == "only4admin123":
            st.session_state.is_admin = True

        st.markdown("---")
        agree1 = st.checkbox("✅ 我同意由第三方協助執行我所制定的交易邏輯")
        agree2 = st.checkbox("✅ 我理解第三方無法保證獲利，盈虧由本人自行負責")
        agree3 = st.checkbox("✅ 我已閱讀並同意以下使用須知")

        st.markdown("""
        <div style='font-size: 14px;'>
        - 第三方僅依照您設定的邏輯輔助執行策略，<b>協助您落實紀律操作，避免人為干擾</b>。<br>
        - 本系統目前<b>僅支援 BingX 平台</b>，請確認您的帳號平台為 BingX。<br>
        - 由於雲端監控下單與實際成交有時間差（一分鐘左右），判斷進場時的技術指標值可能與實際成交時略有誤差，此屬正常現象，請自行評估風險。
        </div>
        """, unsafe_allow_html=True)

        submitted = st.form_submit_button("➡️ 確認並進入下一步")
        if submitted:
            if all([nickname, contact_info, agree1, agree2, agree3]):
                st.session_state.nickname = nickname
                st.session_state.contact_method = contact_method
                st.session_state.contact_info = contact_info
                st.session_state.stage = "strategy"
            else:
                st.warning("❗ 請填寫所有欄位並勾選所有同意書後才能繼續。")

# ========== 第二階段：策略設定表單 ==========
elif st.session_state.stage == "strategy":
    now = datetime.now()
    if st.session_state.last_submit_time and (now - st.session_state.last_submit_time < timedelta(minutes=5)):
        remaining = 300 - int((now - st.session_state.last_submit_time).total_seconds())
        st.error(f"⚠️ 您已提交過策略，請等待 {remaining} 秒後再嘗試。")
        st.stop()

    st.markdown("""
        <h1 style='color:#1E90FF;'>📈 雲端託管交易策略申請</h1>
                
<h2 style='font-weight:bold;'>交易邏輯設定申請單</h2>
    """, unsafe_allow_html=True)

    account_type = st.selectbox("交易種類", ["標準合約", "永續合約", "現貨買賣"])
    coin = st.selectbox("交易幣種", ["BTCUSDT", "ETHUSDT"])
    leverage = st.slider("槓桿範圍", 1, 125, 20)
    amount = st.number_input("每筆交易金額 (USDT)", min_value=1, value=10)
    take_profit = st.slider("止盈 %", 1, 100, 5)
    stop_loss = st.slider("止損 %", 1, 100, 10)

    timeframe_choices = st.multiselect("📊 請選擇追蹤的 K 線週期（最多兩個）：", [
        "1分K", "3分K", "5分K", "15分K", "30分K",
        "60分K", "2小時K", "4小時K", "6小時K", "12小時K"
    ], max_selections=2)

    st.markdown("---")
    st.subheader("📚 常用技術指標選擇（中英對照）")

    st.markdown("""
    <div style='font-size: 14px;'>
    <ul>
        <li><b>MACD 指標</b>（Moving Average Convergence Divergence）：黃金交叉買進、死亡交叉賣出</li>
        <li><b>RSI 指標</b>（Relative Strength Index）：RSI &lt; 30 買進，RSI &gt; 70 賣出</li>
        <li><b>布林通道</b>（Bollinger Bands）：上下軌突破或反轉進出</li>
        <li><b>EMA</b>（Exponential Moving Average）：短期均線突破長期均線判斷多空</li>
        <li><b>SMA</b>（Simple Moving Average）：價格突破簡單均線</li>
        <li><b>VOL</b>（Volume）：量增配合價格變動判斷趨勢</li>
        <li><b>KD 指標</b>（Stochastic Oscillator）：K上穿D買進，反之賣出</li>
        <li><b>ATR</b>（Average True Range）：衡量波動風險</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    logic_choices = st.multiselect("🔍 技術指標邏輯選擇（最多兩個）", [
        "MACD 黃金交叉買進 / 死亡交叉賣出",
        "RSI 高檔賣出 / 低檔買進",
        "布林通道突破策略",
        "EMA 均線交叉策略",
        "SMA 簡單均線突破策略",
        "成交量放量策略",
        "KD 隨機指標策略",
        "ATR 波動風控策略"
    ], max_selections=2)

    if "captcha" not in st.session_state:
        st.session_state.captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    st.text(f"請輸入驗證碼：{st.session_state.captcha}")
    captcha_input = st.text_input("請輸入上方驗證碼")

    if captcha_input != st.session_state.captcha:
        st.warning("請正確輸入驗證碼才能提交。")
        st.stop()

    if st.button("📤 提交監控條件"):
        payload = {
            "nickname": st.session_state.nickname,
            "contact_method": st.session_state.contact_method,
            "contact_info": st.session_state.contact_info,
            "account_type": account_type,
            "coin": coin,
            "leverage": leverage,
            "amount": amount,
            "take_profit": take_profit,
            "stop_loss": stop_loss,
            "logic": logic_choices,
            "timeframes": timeframe_choices,
            "timestamp": datetime.now().isoformat()
        }

        if not os.path.exists("submitted_strategies"):
            os.makedirs("submitted_strategies")

        filename = f"submitted_strategies/strategy_{st.session_state.nickname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        st.success("🎉 策略已成功送出，我們將在 1-2 個工作日內審核並回覆您設定結果！")
        st.session_state.last_submit_time = datetime.now()
        st.markdown("""
            <div style='background-color:#f0f2f6; padding: 20px; border-radius: 8px; font-size: 16px;'>
            ✅ 感謝您提交策略！我們已成功收到您的設定內容，會由專人儘快協助處理。
            </div>
        """, unsafe_allow_html=True)

# ========== 📋 管理者後台介面 ==========
if st.session_state.is_admin:
    st.markdown("---")
    st.subheader("📋 所有申請紀錄")

    if os.path.exists("submitted_strategies"):
        files = sorted(os.listdir("submitted_strategies"), reverse=True)
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join("submitted_strategies", file), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    with st.expander(f"📄 {file}"):
                        st.json(data)
    else:
        st.info("尚無任何申請紀錄。")
