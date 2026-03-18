import streamlit as st
import pandas as pd


st.title("📈 現金流投資遊戲（買賣版）")

# 股票資料
stocks = {
    "A":("白狗宅急便",[500,700,700,700,700]),
    "B":("大排長龍海運",[650,830,1000,1000,1000]),
    "C":("健健康康藥廠",[1200,1200,1700,1700,1700]),
    "D":("生命醫療",[840,840,900,900,900]),
    "E":("簡單便宜旅遊",[600,600,600,410,410]),
    "F":("訂下去公司",[650,650,650,400,400]),
    "G":("基體科技",[770,770,770,770,600]),
    "H":("耀星科技",[700,700,700,700,650]),
    "I":("鴻泰金控",[1000,1000,1000,1000,1500]),
    "J":("重錫金控",[950,950,950,950,1400]),
    "K":("綠爆能源",[600,450,450,380,380]),
    "L":("油油典典鳴",[700,700,540,710,710])
}

teams = [f"隊伍{i}" for i in range(1,9)]

# 初始化 session_state
if "month" not in st.session_state:
    st.session_state.month = 0
    st.session_state.cash = {t: 0 for t in teams}
    st.session_state.shares = {t: {s: 0 for s in stocks} for t in teams}
    st.session_state.salary = {t: 0 for t in teams}
    st.session_state.events = {t: 0 for t in teams}

# 設定各隊薪水（只有第一個月可修改）
if st.session_state.month == 0:
    for t in teams:
        st.session_state.salary[t] = st.selectbox(
            f"{t} 月薪",
            [40000,70000,100000],
            key=f"salary_{t}"
        )

# 開始遊戲按鈕（第一次設置初始現金）
if st.session_state.month == 0:
    if st.button("開始遊戲", key="start_game"):
        for t in teams:
            st.session_state.cash[t] = st.session_state.salary[t]
        st.session_state.month = 1

# 遊戲進行
if st.session_state.month > 0:
    st.header(f"📅 第 {st.session_state.month} 月")

    month_valid = True
    error_messages = []

    # 暫存交易
    temp_cash = st.session_state.cash.copy()
    temp_shares = {t: st.session_state.shares[t].copy() for t in teams}

    for t in teams:
        st.subheader(t)

        # 股票買賣交易輸入（正數買入，負數賣出）
        trade_input = st.text_input(
            f"{t} 本月股票買賣 (例: A2 B-1 C3)",
            key=f"trade_{t}_{st.session_state.month}"
        )

        # 突發事件金額
        event_input = st.number_input(
            f"{t} 突發事件金額 (+/-)",
            value=st.session_state.events[t],
            key=f"event_{t}_{st.session_state.month}"
        )
        st.session_state.events[t] = event_input

        total_cost = 0
        orders = []

        if trade_input.strip():
            for o in trade_input.split():
                if len(o) < 2:
                    continue
                code = o[0].upper()
                try:
                    num = int(o[1:])
                    if code not in stocks:
                        error_messages.append(f"{t} 股票代號不存在: {code}")
                        month_valid = False
                        continue
                    price = stocks[code][1][st.session_state.month-1]

                    if num >= 0:
                        # 買入
                        total_cost += price * num
                        orders.append((code, num))
                    else:
                        # 賣出
                        num_sell = -num
                        if temp_shares[t][code] < num_sell:
                            error_messages.append(f"{t} 持股不足: {code}")
                            month_valid = False
                        else:
                            total_cost -= price * num_sell  # 買入為正，賣出增加現金
                            orders.append((code, num))
                except:
                    error_messages.append(f"{t} 輸入格式錯誤: {o}")
                    month_valid = False

        # 檢查現金是否足夠
        if total_cost > temp_cash[t]:
            error_messages.append(f"{t} 現金不足")
            month_valid = False

        # 暫存交易結果
        if month_valid:
            temp_cash[t] -= sum(stocks[code][1][st.session_state.month-1]*num for code,num in orders if num>0)
            temp_cash[t] += sum(stocks[code][1][st.session_state.month-1]*(-num) for code,num in orders if num<0)
            for code,num in orders:
                temp_shares[t][code] += num

            temp_cash[t] += st.session_state.events[t]

        st.write("暫存剩餘現金（不含加薪）:", temp_cash[t])

    # 顯示錯誤訊息
    for msg in error_messages:
        st.error(msg)

    # 下一月按鈕
    if month_valid:
        next_key = f"next_month_{st.session_state.month}"
        if st.button("✅ 所有隊合法，進入下一個月", key=next_key):
            # 更新 session_state
            st.session_state.cash = temp_cash
            st.session_state.shares = temp_shares

            # 從第二月開始加薪
            if st.session_state.month >= 2:
                for t in teams:
                    st.session_state.cash[t] += st.session_state.salary[t]

            # 更新月份
            if st.session_state.month < 5:
                st.session_state.month += 1
            else:
                st.success("遊戲結束")
                # 計算總資產
                results = {}
                for t in teams:
                    total = st.session_state.cash[t]
                    for code in stocks:
                        price = stocks[code][1][4]  # 五月股價
                        total += price * st.session_state.shares[t][code]
                    results[t] = total
                df = pd.DataFrame(results.items(), columns=["隊伍","總資產"])
                df = df.sort_values("總資產", ascending=False).reset_index(drop=True)
                st.table(df)
    else:
        st.info("請修正所有錯誤後，再進入下一個月")


#要記得打 streamlit run stock_game.py