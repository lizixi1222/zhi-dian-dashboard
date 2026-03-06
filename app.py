"""
智电未来科技有限公司——公交场站运营数据看板
版本：3.0.0 - GitHub Releases数据版本
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

from data_loader import ZhiDianDataLoader

# ==================== 页面配置（必须是第一个）====================
st.set_page_config(
    page_title="智电未来 - 场站运营看板",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 初始化数据 ====================
@st.cache_resource
def init_data_loader():
    return ZhiDianDataLoader(owner="lizixi1222", repo="zhi-dian-dashboard")

@st.cache_data(ttl=3600)
def load_station_data(_loader):
    return _loader.run_pipeline()

@st.cache_data(ttl=3600)
def load_hourly_data(_loader):
    return _loader.get_hourly_profile()

# 加载数据
loader = init_data_loader()
station_data = load_station_data(loader)
hours, load_data, pv_data = load_hourly_data(loader)


# ==================== CSS样式 ====================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0A1A2F 0%, #1E3A8A 100%);
    }
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .metric-label {
        font-size: 13px;
        color: #5F6B7A;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 600;
        color: #0A1A2F;
    }
    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: white;
        margin: 20px 0 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("## ⚡ 智电未来")
    st.markdown("---")
    pages = ["场站总览", "电量分析", "电池健康"]
    selected = "场站总览"
    for p in pages:
        st.markdown(f"- {p}")
    st.markdown("---")
    st.markdown(f"**{station_data['station_name']}**")
    st.markdown(f"服务车辆: {station_data['total_vehicles']}辆")
    st.markdown(f"同时充电: {station_data['vehicle_count']}辆")


# ==================== 主界面 ====================
st.markdown(f"## 智电未来 · {station_data['station_name']}")
st.markdown(f"*{datetime.now().strftime('%Y年%m月%d日')}*")

# 指标卡片
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">今日充电量</div>
        <div class="metric-value">{station_data['daily_energy']} kWh</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">今日光伏发电</div>
        <div class="metric-value">{station_data['pv_generation_today']} kWh</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">日运行成本</div>
        <div class="metric-value">¥ {abs(station_data['daily_cost'])}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">日减排CO₂</div>
        <div class="metric-value">{station_data['daily_co2']} kg</div>
    </div>
    """, unsafe_allow_html=True)

# 负荷曲线图
st.markdown('<div class="section-title">📈 典型日负荷曲线</div>', unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=hours, y=load_data,
    mode='lines',
    name='充电负荷',
    line=dict(color='#1E3A8A', width=3)
))
fig.add_trace(go.Scatter(
    x=hours, y=pv_data,
    mode='lines',
    name='光伏出力',
    line=dict(color='#3B82F6', width=3)
))

fig.update_layout(
    height=400,
    xaxis_title="小时",
    yaxis_title="功率 (kW)",
    hovermode='x unified',
    plot_bgcolor='white',
    paper_bgcolor='white'
)

st.plotly_chart(fig, use_container_width=True)

# 电池健康
st.markdown('<div class="section-title">🔋 电池状态</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("电池健康度", f"{station_data['battery_health']}%")
col2.metric("已循环次数", f"{station_data['battery_cycles']}")
col3.metric("剩余寿命", f"{station_data['battery_remaining_life']} 年")

st.markdown("---")
st.markdown("智电未来科技有限公司 · 让每一度电都聪明")
