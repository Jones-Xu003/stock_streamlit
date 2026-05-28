import streamlit as st

st.title("🎉 Streamlit 测试")
st.write("如果看到这行文字，说明 Streamlit 正常运行！")

stock_code = st.text_input("请输入股票代码", "600519")

if st.button("测试按钮"):
    st.success(f"你输入了：{stock_code} ✅")