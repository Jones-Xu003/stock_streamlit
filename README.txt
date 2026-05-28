# 股票数据可视化工具

一个使用 Python + Streamlit 开发的股票数据分析小工具。

## 项目功能

* 获取股票历史数据
* 显示收盘价走势
* 计算 MA5 / MA10 / MA20 均线
* 显示成交量
* 计算平均每日波动率
* 导出 CSV 文件

## 技术栈

* Python
* Streamlit
* Pandas
* Matplotlib
* Requests

## 如何运行

### 1. 安装依赖

```bash
pip install streamlit pandas matplotlib requests
```

### 2. 运行项目

```bash
streamlit run app.py
```
方法2：双击“启动.bat”启动程序，关闭时直接关闭网页和cmd（黑框）

## 项目结构

```text
project/
│
├── app.py
├── README.md
└── requirements.txt
```

## 数据来源

数据来源：同花顺

## 项目特点

HTTP 请求
数据抓取
数据清洗
数据分析
数据可视化
Web 界面开发