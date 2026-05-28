@echo off
title 股票走势查询工具
python -m streamlit run stock_app.py --server.port 8501
pause