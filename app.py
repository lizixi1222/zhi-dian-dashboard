"""
智电未来科技有限公司——公交场站运营数据看板
版本：2.0.0
配色方案：深蓝色 (#1E3A8A) + 白色 · 专业美观
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random

# 页面配置
st.set_page_config(
    page_title="智电未来 - 场站运营看板",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 深蓝色+白色专业CSS ====================
st.markdown("""
<style>
    /* 全局字体 */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 主背景 - 深蓝色 */
    .stApp {
        background-color: #0A1A2F;
    }
    
    /* 主内容区域 */
    .main-content {
        background-color: #F8FAFC;
        border-radius: 24px;
        padding: 24px;
        margin: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    /* 主标题 */
    .main-title {
        font-size: 24px;
        font-weight: 600;
        color: #0A1A2F;
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    
    .sub-title {
        font-size: 14px;
        color: #5F6B7A;
        margin-bottom: 24px;
        padding-bottom: 16px;
        border-bottom: 1px solid #E2E8F0;
    }
    
    /* 指标卡片 - 白色卡片，深蓝色强调 */
    .metric-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #E2E8F0;
        transition: all 0.2s;
    }
    
    .metric-card:hover {
        box-shadow: 0 8px 16px rgba(30, 58, 138, 0.08);
        border-color: #1E3A8A;
    }
    
    .metric-label {
        font-size: 13px;
        color: #5F6B7A;
        font-weight: 500;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }
    
    .metric-value {
        font-size: 30px;
        font-weight: 600;
        color: #0A1A2F;
        line-height: 1.2;
    }
    
    .metric-delta {
        font-size: 13px;
        font-weight: 500;
        margin-left: 8px;
        padding: 2px 8px;
        border-radius: 20px;
        display: inline-block;
    }
    
    .delta-positive {
        background: #DFF0FA;
        color: #1E3A8A;
    }
    
    .delta-neutral {
        background: #F1F5F9;
        color: #5F6B7A;
    }
    
    /* 模块标题 */
    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #0A1A2F;
        margin: 28px 0 20px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #1E3A8A;
    }
    
    /* 卡片标题 */
    .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #0A1A2F;
        margin-bottom: 16px;
    }
    
    /* 表格样式 */
    .dataframe {
        width: 100%;
        border-collapse: collapse;
        background: #FFFFFF;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    
    .dataframe th {
        text-align: left;
        padding: 14px 16px;
        color: #5F6B7A;
        font-weight: 500;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.02em;
        background: #F8FAFC;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .dataframe td {
        padding: 14px 16px;
        color: #0A1A2F;
        font-size: 14px;
        border-bottom: 1px solid #F1F5F9;
    }
    
    /* 标签 */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 500;
        border-radius: 20px;
    }
    
    .badge-primary {
        background: #DFF0FA;
        color: #1E3A8A;
    }
    
    .badge-success {
        background: #E0F2F1;
        color: #0D5E5E;
    }
    
    .badge-warning {
        background: #FFF3E0;
        color: #B85C1A;
    }
    
    /* 侧边栏 - 深蓝色背景 */
    .css-1d391kg {
        background: #0A1A2F;
    }
    
    .sidebar-content {
        padding: 24px 16px;
        color: #FFFFFF;
    }
    
    .sidebar-title {
        font-size: 18px;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 4px;
    }
    
    .sidebar-subtitle {
        font-size: 13px;
        color: #94A3B8;
        margin-bottom: 24px;
    }
    
    .sidebar-item {
        padding: 10px 16px;
        margin: 4px 0;
        font-size: 14px;
        color: #CBD5E1;
        cursor: pointer;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    .sidebar-item:hover {
        background: #1E3A8A;
        color: #FFFFFF;
    }
    
    .sidebar-item.active {
        background: #1E3A8A;
        color: #FFFFFF;
        font-weight: 500;
    }
    
    /* 分隔线 */
    .divider {
        height: 1px;
        background: #253C5C;
        margin: 20px 0;
    }
    
    /* 搜索框 */
    .search-box {
        background: #FFFFFF10;
        border: 1px solid #253C5C;
        border-radius: 8px;
        padding: 10px 16px;
        color: #FFFFFF;
        width: 100%;
        font-size: 14px;
    }
    
    .search-box::placeholder {
        color: #5F6B7A;
    }
    
    /* 按钮 */
    .btn-primary {
        background: #1E3A8A;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 10px 16px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        width: 100%;
        transition: all 0.2s;
    }
    
    .btn-primary:hover {
        background: #2563EB;
    }
    
    .btn-outline {
        background: transparent;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 13px;
        color: #5F6B7A;
        cursor: pointer;
    }
    
    .btn-outline:hover {
        background: #F8FAFC;
        border-color: #1E3A8A;
        color: #1E3A8A;
    }
    
    /* 信息卡片 */
    .info-card {
        background: #F8FAFC;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #E2E8F0;
    }
    
    /* 数值高亮 */
    .highlight-value {
        font-size: 36px;
        font-weight: 600;
        color: #1E3A8A;
    }
    
    .highlight-label {
        font-size: 14px;
        color: #5F6B7A;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 生成场站级数据（基于算法输出）====================

def generate_station_data():
    """
    生成公交场站运营数据
    基于算法输出的真实指标
    """
    # 核心指标（来自算法输出）
    data = {
        "station_name": "长沙格林香山公交场站",
        "vehicle_count": 40,  # 同时充电能力
        "total_vehicles": 150,  # 服务保障能力
        
        # 电量数据
        "monthly_energy_cost": 245800,  # 本月电量支出
        "monthly_energy_cost_change": -8.5,  # 环比变化
        
        "cumulative_savings": 42300,  # 平台累计节省
        "avg_energy_consumption": 0.85,  # 百公里平均能耗
        "energy_efficiency": 12,  # 优于行业标准百分比
        
        "battery_lifetime_value": 120000,  # 电池寿命延长收益
        
        # 光伏数据
        "pv_generation_today": 3809,  # 今日光伏发电
        "pv_self_use_rate": 10.2,  # 光伏自用率
        "pv_total_month": 105700,  # 本月光伏发电
        
        # 储能数据
        "battery_cycles": 809,  # 已循环次数
        "battery_health": 73.9,  # 电池健康度
        "battery_remaining_life": 6.7,  # 剩余寿命(年)
        
        # 成本数据
        "daily_cost": -814,  # 日运行成本
        "daily_savings": 1479,  # 日节省电费
        "annual_savings": 54.0,  # 年节省电费(万元)
        
        # 环保数据
        "daily_co2": 312,  # 日减排CO₂(kg)
        "annual_co2": 86.5,  # 年减排CO₂(吨)
        "carbon_income": 0.52,  # 碳交易收益(万元)
        
        # 投资回报
        "total_investment": 800,  # 总投资(万元)
        "annual_revenue": 76.2,  # 年收益(万元)
        "annual_cost": 52.1,  # 年运营成本(万元)
        "net_profit": 24.1,  # 年净利润(万元)
        "payback_years": 8.3,  # 投资回收期(年)
        "irr": 12.5,  # 内部收益率%
    }
    return data


def generate_energy_trend():
    """生成电量支出趋势"""
    months = ['1月', '2月', '3月', '4月', '5月', '6月']
    before = [268, 265, 259, 255, 252, 248]  # 优化前(千元)
    after = [245, 242, 238, 235, 232, 228]   # 优化后(千元)
    return months, before, after


def generate_cost_structure():
    """生成成本结构数据"""
    categories = ['充电成本', '电池更换', '维护保养', '保险税费', '其他']
    values = [42, 28, 15, 10, 5]  # 百分比
    return categories, values


def generate_savings_details():
    """生成节约明细"""
    details = {
        "电费节省": 42300,
        "电池寿命延长": 120000,
        "维护成本降低": 18500,
        "碳交易收益": 5200,
        "total": 186000
    }
    return details


def generate_roi_projection():
    """生成10年收益预测"""
    years = list(range(1, 11))
    savings = [18.6, 38.5, 59.8, 82.5, 106.8, 132.6, 160.0, 189.0, 219.6, 252.0]
    return years, savings


def generate_battery_trend():
    """生成电池健康度趋势"""
    months = ['1月', '2月', '3月', '4月', '5月', '6月']
    soh = [94.2, 93.8, 93.5, 93.1, 92.8, 92.4]
    return months, soh


# ==================== 生成数据 ====================
station_data = generate_station_data()
months, cost_before, cost_after = generate_energy_trend()
cost_cats, cost_vals = generate_cost_structure()
savings = generate_savings_details()
roi_years, roi_savings = generate_roi_projection()
soh_months, soh_values = generate_battery_trend()


# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">智行电控</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-subtitle">公交场站运营报表</div>', unsafe_allow_html=True)
    st.markdown("长沙格林香山公交场站")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 导航
    pages = [
        "场站总览",
        "电量分析",
        "电池健康",
        "成本收益",
        "环保效益",
        "参数配置"
    ]
    
    # 默认选中第一个
    selected_page = "场站总览"
    
    for page in pages:
        if page == selected_page:
            st.markdown(f'<div class="sidebar-item active">{page}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="sidebar-item">{page}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 场站信息
    st.markdown("##### 场站信息")
    st.markdown(f"服务车辆: {station_data['total_vehicles']}辆")
    st.markdown(f"同时充电: {station_data['vehicle_count']}辆")
    st.markdown(f"光伏容量: 500 kWp")
    st.markdown(f"储能容量: 500 kWh")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 周期选择
    st.markdown("##### 统计周期")
    st.selectbox("", ["今日", "本周", "本月", "本季度", "本年"], label_visibility="collapsed")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown("##### 导出数据")
    st.button("导出报表", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# ==================== 主内容区域 ====================
st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.markdown('<div class="main-title">智行电控 · 公交场站运营看板</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">长沙格林香山公交场站 · TCO全生命周期成本分析</div>', unsafe_allow_html=True)


# ==================== 场站总览页面 ====================

if selected_page == "场站总览":
    # 第一行：核心指标
    cols = st.columns(4)
    
    metrics = [
        ("本月电量支出", f"¥ {station_data['monthly_energy_cost']:,}", f"{station_data['monthly_energy_cost_change']}%", "positive"),
        ("平台累计节省", f"¥ {station_data['cumulative_savings']:,}", "vs 无优化", "neutral"),
        ("百公里平均能耗", f"{station_data['avg_energy_consumption']} kWh", f"-{station_data['energy_efficiency']}% vs 行业", "positive"),
        ("电池寿命延长收益", f"¥ {station_data['battery_lifetime_value']:,}", "折算TCO价值", "neutral")
    ]
    
    for i, (label, value, delta, delta_type) in enumerate(metrics):
        with cols[i]:
            delta_class = "delta-positive" if delta_type == "positive" else "delta-neutral"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div>
                    <span class="metric-value">{value}</span>
                    <span class="metric-delta {delta_class}">{delta}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 第二行：今日运行数据
    st.markdown('<div class="section-title">今日运行数据</div>', unsafe_allow_html=True)
    
    cols = st.columns(5)
    daily_metrics = [
        ("充电量", f"{554} kWh"),
        ("光伏发电", f"{station_data['pv_generation_today']} kWh"),
        ("运行成本", f"¥ {abs(station_data['daily_cost'])}", "负成本" if station_data['daily_cost'] < 0 else ""),
        ("节省电费", f"¥ {station_data['daily_savings']}"),
        ("减排CO₂", f"{station_data['daily_co2']} kg")
    ]
    
    for i, (label, value, *extra) in enumerate(daily_metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div>
                    <span class="metric-value">{value}</span>
                    {f'<span style="font-size:12px; color:#5F6B7A; margin-left:4px;">{extra[0]}</span>' if extra else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 成本效益对比图
    st.markdown('<div class="section-title">电量支出趋势</div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=cost_before,
        mode='lines+markers',
        name='优化前',
        line=dict(color='#94A3B8', width=2.5),
        marker=dict(size=8, color='#94A3B8')
    ))
    fig.add_trace(go.Scatter(
        x=months, y=cost_after,
        mode='lines+markers',
        name='优化后',
        line=dict(color='#1E3A8A', width=3),
        marker=dict(size=10, color='#1E3A8A')
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=40, r=40, t=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="电量支出 (千元)",
        hovermode='x unified',
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto", size=12)
    )
    
    fig.update_xaxes(gridcolor='#F1F5F9', linecolor='#E2E8F0')
    fig.update_yaxes(gridcolor='#F1F5F9', linecolor='#E2E8F0')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 第三行：成本结构和节约明细
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-title">TCO成本结构</div>', unsafe_allow_html=True)
        
        colors = ['#1E3A8A', '#3B82F6', '#94A3B8', '#CBD5E1', '#E2E8F0']
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=cost_cats, values=cost_vals, hole=0.4,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(size=12),
            showlegend=False
        )])
        fig_pie.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-title">成本节约明细</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-card">
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <tr>
                    <td style="padding: 12px 0;">电费节省</td>
                    <td style="text-align: right; font-weight: 600; color: #1E3A8A;">¥ {savings['电费节省']:,}</td>
                </tr>
                <tr>
                    <td style="padding: 12px 0;">电池寿命延长</td>
                    <td style="text-align: right; font-weight: 600; color: #1E3A8A;">¥ {savings['电池寿命延长']:,}</td>
                </tr>
                <tr>
                    <td style="padding: 12px 0;">维护成本降低</td>
                    <td style="text-align: right; font-weight: 600; color: #1E3A8A;">¥ {savings['维护成本降低']:,}</td>
                </tr>
                <tr>
                    <td style="padding: 12px 0; border-bottom: 1px solid #E2E8F0;">碳交易收益</td>
                    <td style="text-align: right; font-weight: 600; color: #1E3A8A; border-bottom: 1px solid #E2E8F0;">¥ {savings['碳交易收益']:,}</td>
                </tr>
                <tr>
                    <td style="padding: 16px 0; font-weight: 600; font-size: 16px;">累计节约</td>
                    <td style="text-align: right; font-weight: 700; color: #1E3A8A; font-size: 20px;">¥ {savings['total']:,}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)


# ==================== 电量分析页面 ====================

elif selected_page == "电量分析":
    st.markdown('<div class="section-title">电量分析</div>', unsafe_allow_html=True)
    
    # 电量指标
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">本月总用电</div>
            <div class="metric-value">158,400 kWh</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">本月光伏发电</div>
            <div class="metric-value">{station_data['pv_total_month']:,} kWh</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">光伏自用率</div>
            <div class="metric-value">{station_data['pv_self_use_rate']}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 小时负荷曲线
    st.markdown('<div class="section-title">典型日负荷曲线</div>', unsafe_allow_html=True)
    
    hours = list(range(24))
    load = [5,3,2,1,1,2,8,25,35,30,25,22,20,25,30,35,40,45,50,48,42,30,20,10]
    pv = [0,0,0,0,0,0,20,80,150,200,220,230,220,200,150,80,20,0,0,0,0,0,0,0]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=load,
        mode='lines',
        name='充电负荷',
        line=dict(color='#1E3A8A', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=hours, y=pv,
        mode='lines',
        name='光伏出力',
        line=dict(color='#3B82F6', width=3)
    ))
    
    fig.update_layout(
        height=350,
        xaxis_title="小时",
        yaxis_title="功率 (kW)",
        hovermode='x unified',
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ==================== 电池健康页面 ====================

elif selected_page == "电池健康":
    st.markdown('<div class="section-title">电池健康分析</div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">电池健康度</div>
            <div class="metric-value">{station_data['battery_health']}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">已循环次数</div>
            <div class="metric-value">{station_data['battery_cycles']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">剩余寿命</div>
            <div class="metric-value">{station_data['battery_remaining_life']} 年</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 健康度趋势
    st.markdown('<div class="section-title">健康度变化趋势</div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=soh_months, y=soh_values,
        mode='lines+markers',
        line=dict(color='#1E3A8A', width=3),
        marker=dict(size=8, color='#1E3A8A')
    ))
    
    fig.update_layout(
        height=300,
        xaxis_title="月份",
        yaxis_title="SOH (%)",
        yaxis_range=[90, 95],
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF'
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ==================== 成本收益页面 ====================

elif selected_page == "成本收益":
    st.markdown('<div class="section-title">投资回报分析</div>', unsafe_allow_html=True)
    
    # 投资回报指标
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">总投资</div>
            <div class="metric-value">{station_data['total_investment']} 万元</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">年净利润</div>
            <div class="metric-value">{station_data['net_profit']} 万元</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">投资回收期</div>
            <div class="metric-value">{station_data['payback_years']} 年</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 收益预测
    st.markdown('<div class="section-title">10年累计收益预测</div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=roi_years, y=roi_savings,
        mode='lines+markers',
        line=dict(color='#1E3A8A', width=3),
        marker=dict(size=8, color='#1E3A8A'),
        fill='tozeroy',
        fillcolor='rgba(30, 58, 138, 0.05)',
        name='累计节约'
    ))
    
    fig.update_layout(
        xaxis_title="年份",
        yaxis_title="节约金额 (万元)",
        height=400,
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF'
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ==================== 环保效益页面 ====================

elif selected_page == "环保效益":
    st.markdown('<div class="section-title">环保效益分析</div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">日减排CO₂</div>
            <div class="metric-value">{station_data['daily_co2']} kg</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">年减排CO₂</div>
            <div class="metric-value">{station_data['annual_co2']} 吨</div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">碳交易收益</div>
            <div class="metric-value">¥ {station_data['carbon_income']*10000:.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 环保等效
    st.markdown('<div class="section-title">环保等效</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="info-card" style="text-align: center;">
            <div style="font-size: 42px; font-weight: 600; color: #1E3A8A;">{int(station_data['annual_co2']*50)}</div>
            <div style="font-size: 14px; color: #5F6B7A;">相当于种树（棵/年）</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-card" style="text-align: center;">
            <div style="font-size: 42px; font-weight: 600; color: #1E3A8A;">{int(station_data['annual_co2']/2.3)}</div>
            <div style="font-size: 14px; color: #5F6B7A;">相当于减少汽车（辆/年）</div>
        </div>
        """, unsafe_allow_html=True)


# ==================== 参数配置页面 ====================

elif selected_page == "参数配置":
    st.markdown('<div class="section-title">算法参数配置</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4 style="margin-top: 0; font-size: 16px; font-weight: 600; color: #1E3A8A;">系统参数</h4>
        """, unsafe_allow_html=True)
        
        st.markdown("**光伏容量**")
        st.slider("", 100, 1000, 500, step=50, label_visibility="collapsed")
        
        st.markdown("**储能容量**")
        st.slider("", 100, 1000, 500, step=50, label_visibility="collapsed")
        
        st.markdown("**储能功率**")
        st.slider("", 50, 500, 200, step=25, label_visibility="collapsed")
        
        st.markdown("**变压器限值**")
        st.slider("", 400, 1200, 800, step=100, label_visibility="collapsed")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4 style="margin-top: 0; font-size: 16px; font-weight: 600; color: #1E3A8A;">电价参数</h4>
        """, unsafe_allow_html=True)
        
        st.markdown("**低谷电价 (元)**")
        st.number_input("", 0.3, 1.0, 0.63, 0.01, label_visibility="collapsed")
        
        st.markdown("**平段电价 (元)**")
        st.number_input("", 0.5, 1.5, 0.95, 0.01, label_visibility="collapsed")
        
        st.markdown("**高峰电价 (元)**")
        st.number_input("", 0.8, 2.0, 1.35, 0.01, label_visibility="collapsed")
        
        st.markdown("**上网电价 (元)**")
        st.number_input("", 0.2, 0.5, 0.30, 0.01, label_visibility="collapsed")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.button("保存配置", use_container_width=True)


# ==================== 关闭主内容区域 ====================
st.markdown('</div>', unsafe_allow_html=True)


# ==================== 页脚 ====================
st.markdown("""
<div style="text-align: center; color: #94A3B8; font-size: 12px; padding: 20px;">
    智电未来科技有限公司 · 让每一度电都聪明 · 版本 2.0.0
</div>
""", unsafe_allow_html=True)