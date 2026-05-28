import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# 中文字体设置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="股票走势查询", layout="wide")
st.title("📈 股票走势查询工具（价格 + 成交量 + 平均波动）")

stock_code = st.text_input("请输入股票代码（如：600519、000333、300750）", value="600519")

days_options = {"最近30天": 30, "最近60天": 60, "最近100天": 100, "最近180天": 180}
selected_days = st.selectbox("选择显示时间范围", options=list(days_options.keys()))

st.subheader("选择要显示的线条")
col1, col2, col3, col4 = st.columns(4)
with col1:
    show_close = st.checkbox("收盘价", value=True)
with col2:
    show_ma5 = st.checkbox("MA5 (5日均线)", value=True)
with col3:
    show_ma10 = st.checkbox("MA10 (10日均线)", value=True)
with col4:
    show_ma20 = st.checkbox("MA20 (20日均线)", value=False)

if st.button("🔍 查询", type="primary"):
    if not stock_code or len(stock_code) < 6:
        st.error("请输入正确的股票代码！")
        st.stop()

    with st.spinner("正在获取数据并计算平均波动..."):
        try:
            market_prefix = "17" if stock_code.startswith("6") else "33"
            url = f"https://d.10jqka.com.cn/v6/line/{market_prefix}_{stock_code}/01/last1800.js"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": f"https://stockpage.10jqka.com.cn/{stock_code}/"
            }

            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                st.error("❌ 请求失败")
                st.stop()

            text = response.text
            start = text.find('"data":"') + len('"data":"')
            end = text.find('","marketType"')

            if start < 20 or end < 0:
                st.error("❌ 数据提取失败")
                st.stop()

            data_str = text[start:end]
            rows = data_str.split(";")

            result = []
            for row in rows[-days_options[selected_days]:]:
                if not row.strip(): continue
                fields = row.split(",")
                if len(fields) >= 6:
                    result.append({
                        "date": fields[0],
                        "close": float(fields[4]),
                        "volume": float(fields[5])
                    })

            df = pd.DataFrame(result)
            if len(df) < 10:
                st.error("❌ 获取数据过少")
                st.stop()

            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            df = df.sort_values('date').reset_index(drop=True)
            
            df['MA5'] = df['close'].rolling(window=5).mean()
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()

            # ==================== 你想要的波动率计算 ====================
            latest_price = df['close'].iloc[-1]
            latest_date = df['date'].iloc[-1].strftime('%Y-%m-%d')
            
            max_price = df['close'].max()
            max_date = df['date'][df['close'].idxmax()].strftime('%Y-%m-%d')
            
            min_price = df['close'].min()
            min_date = df['date'][df['close'].idxmin()].strftime('%Y-%m-%d')

            # 计算每日价格变化（绝对值）
            df['daily_change'] = df['close'].diff().abs()                    # 绝对价格变化
            avg_daily_change = df['daily_change'].mean()                      # 平均每日波动（元）

            df['daily_pct_change'] = df['close'].pct_change().abs() * 100    # 每日百分比波动
            avg_daily_pct = df['daily_pct_change'].mean()                    # 平均每日百分比波动

            position_pct = (latest_price - min_price) / (max_price - min_price) * 100 if max_price > min_price else 50

            if position_pct >= 85:
                position_text = "📈 **接近最高点**"
            elif position_pct <= 15:
                position_text = "📉 **接近最低点**"
            elif position_pct >= 60:
                position_text = "🔼 处于较高位置"
            elif position_pct <= 40:
                position_text = "🔽 处于较低位置"
            else:
                position_text = "↔️ 处于中间位置"

            # ==================== 显示结果 ====================
            st.success(f"✅ {stock_code}  {selected_days} 数据获取成功")

            st.subheader("📊 当前价格位置分析")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("最新收盘价", f"¥{latest_price:.2f}", latest_date)
            with col2:
                st.metric(f"{selected_days}最高价", f"¥{max_price:.2f}", max_date)
            with col3:
                st.metric(f"{selected_days}最低价", f"¥{min_price:.2f}", min_date)

            st.info(f"**{position_text}**  (最新价格处于{selected_days}内 **{position_pct:.1f}%** 的位置)")

            # ==================== 波动率显示（按你的要求） ====================
            st.subheader("📈 平均每日波动率")
            col4, col5 = st.columns(2)
            with col4:
                st.metric("平均每日价格波动", f"¥{avg_daily_change:.2f}")
            with col5:
                st.metric("平均每日涨跌幅度", f"{avg_daily_pct:.2f}%")

            st.caption(f"计算方式：每日价格绝对变化的总和 ÷ {len(df)-1} 天")

            # 数据表格和下载
            col_a, col_b = st.columns([3, 2])
            with col_a:
                display_cols = ['date', 'close', 'volume']
                if show_ma5: display_cols.append('MA5')
                if show_ma10: display_cols.append('MA10')
                if show_ma20: display_cols.append('MA20')
                st.dataframe(df[display_cols].round(2), use_container_width=True)

            with col_b:
                st.download_button("📥 下载 CSV 文件", 
                                 data=df.to_csv(index=False).encode('utf-8'),
                                 file_name=f"{stock_code}_{selected_days}.csv",
                                 mime="text/csv")

            # 绘图（保持不变）
            fig = plt.figure(figsize=(12, 9))
            ax1 = plt.subplot(2, 1, 1)
            if show_close:
                ax1.plot(df["date"], df["close"], linewidth=2.8, color='#1f77b4', label='收盘价')
            if show_ma5: ax1.plot(df["date"], df["MA5"], linewidth=1.8, color='#ff7f0e', label='MA5')
            if show_ma10: ax1.plot(df["date"], df["MA10"], linewidth=1.8, color='#2ca02c', label='MA10')
            if show_ma20: ax1.plot(df["date"], df["MA20"], linewidth=1.8, color='#d62728', label='MA20')

            ax1.set_title(f"{stock_code} {selected_days} 价格走势 + 成交量", fontsize=16, pad=20)
            ax1.set_ylabel("价格 (元)")
            ax1.grid(True, linestyle='--', alpha=0.5)
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            if any([show_close, show_ma5, show_ma10, show_ma20]):
                ax1.legend(fontsize=11, loc='upper left')

            ax2 = plt.subplot(2, 1, 2)
            ax2.bar(df["date"], df["volume"], color='#4a90e2', alpha=0.8)
            ax2.set_ylabel("成交量")
            ax2.grid(True, linestyle='--', alpha=0.5)
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)

            plt.xticks(rotation=45)
            fig.tight_layout()
            st.pyplot(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ 发生错误: {str(e)}")

st.caption("数据来源：同花顺")