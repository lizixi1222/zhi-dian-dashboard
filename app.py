    """
智电未来科技有限公司——公交场站运营数据看板
版本：3.0.0 - GitHub Releases数据版本
深蓝色专业设计 · 全交互式看板
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# 导入数据加载器
from data_loader import ZhiDianDataLoader

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="智电未来 - 场站运营看板",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 初始化数据 ====================
@st.cache_resource
def init_data_loader():
    """初始化数据加载器（只执行一次）"""
    return ZhiDianDataLoader(owner="lizixi1222", repo="zhi-dian-dashboard")

@st.cache_data(ttl=3600)
def load_station_data(_loader):
    """加载场站数据（缓存1小时）"""
    return _loader.run_pipeline()

@st.cache_data(ttl=3600)
def load_hourly_data(_loader):
    """加载小时数据（缓存1小时）"""
    return _loader.get_hourly_profile()

# 初始化
loader = init_data_loader()

# 加载数据（带进度提示）
with st.spinner("正在从GitHub加载数据..."):
    station_data = load_station_data(loader)
    hours, load_data, pv_data = load_hourly_data(loader)


# ==================== 专业CSS样式 ====================
st.markdown("""
<style>
    /* 全局字体 */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-sizing: border-box;
    }
    
    /* 主背景 - 深蓝色渐变 */
    .stApp {
        background: linear-gradient(135deg, #0A1A2F 0%, #1E3A8A 100%);
    }
    
    /* 主内容卡片 */
    .main-card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 32px;
        padding: 28px;
        margin: 16px 0;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 公司标识 */
    .brand-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 24px;
    }
    
    .brand-logo {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        font-weight: 600;
        box-shadow: 0 8px 16px rgba(30, 58, 138, 0.3);
    }
    
    .brand-name {
        font-size: 28px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .brand-sub {
        font-size: 14px;
        color: rgba(255,255,255,0.8);
        margin-top: 4px;
    }
    
    /* 场站信息栏 */
    .station-header {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 24px;
        padding: 16px 24px;
        margin: 20px 0 30px 0;
        border: 1px solid rgba(255,255,255,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: white;
    }
    
    .station-name {
        font-size: 20px;
        font-weight: 600;
    }
    
    .station-badge {
        background: rgba(59, 130, 246, 0.3);
        padding: 6px 16px;
        border-radius: 40px;
        font-size: 13px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* 指标卡片 - 毛玻璃效果 */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(30, 58, 138, 0.1);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 30px rgba(30, 58, 138, 0.15);
        border-color: #1E3A8A;
    }
    
    .metric-label {
        font-size: 13px;
        color: #5F6B7A;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 12px;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #0A1A2F;
        line-height: 1.2;
        margin-bottom: 4px;
    }
    
    .metric-trend {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
    }
    
    .trend-up {
        color: #10B981;
        background: rgba(16, 185, 129, 0.1);
        padding: 4px 8px;
        border-radius: 20px;
    }
    
    .trend-down {
        color: #EF4444;
        background: rgba(239, 68, 68, 0.1);
        padding: 4px 8px;
        border-radius: 20px;
    }
    
    .trend-neutral {
        color: #5F6B7A;
        background: rgba(95, 107, 122, 0.1);
        padding: 4px 8px;
        border-radius: 20px;
    }
    
    /* 模块标题 */
    .section-title {
        font-size: 18px;
        font-weight: 600;
        color: #0A1A2F;
        margin: 30px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid #1E3A8A;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .section-link {
        font-size: 13px;
        color: #1E3A8A;
        font-weight: 500;
        cursor: pointer;
    }
    
    /* 侧边栏 */
    .css-1d391kg {
        background: linear-gradient(180deg, #0A1A2F 0%, #0F2A4A 100%);
    }
    
    .sidebar-brand {
        padding: 24px 16px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }
    
    .sidebar-item {
        padding: 12px 20px;
        margin: 4px 8px;
        border-radius: 16px;
        color: rgba(255,255,255,0.7);
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s;
        cursor: pointer;
    }
    
    .sidebar-item:hover {
        background: rgba(59, 130, 246, 0.2);
        color: white;
    }
    
    .sidebar-item.active {
        background: #1E3A8A;
        color: white;
    }
    
    .sidebar-info {
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 20px;
        margin: 20px 8px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .info-item {
        display: flex;
        justify-content: space-between;
        margin: 12px 0;
        color: rgba(255,255,255,0.9);
        font-size: 14px;
    }
    
    .info-label {
        color: rgba(255,255,255,0.5);
    }
    
    .info-value {
        font-weight: 600;
    }
    
    /* 按钮 */
    .btn-primary {
        background: #1E3A8A;
        color: white;
        border: none;
        border-radius: 40px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 600;
        width: 100%;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .btn-primary:hover {
        background: #2563EB;
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(30, 58, 138, 0.3);
    }
    
    /* 图表容器 */
    .chart-container {
        background: white;
        border-radius: 24px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        margin: 16px 0;
    }
    
    /* 分隔线 */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div style="font-size: 24px; font-weight: 700; color: white; margin-bottom: 4px;">智电未来</div>
        <div style="font-size: 13px; color: rgba(255,255,255,0.6);">ZhiDian Future Tech</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 导航
    pages = ["场站总览", "电量分析", "电池健康", "成本收益", "环保效益", "参数配置"]
    selected_page = "场站总览"
    
    for page in pages:
        active_class = "active" if page == selected_page else ""
        st.markdown(f'<div class="sidebar-item {active_class}">{page}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 场站信息卡片
    st.markdown(f"""
    <div class="sidebar-info">
        <div style="font-size: 16px; font-weight: 600; color: white; margin-bottom: 16px;">{station_data['station_name']}</div>
        <div class="info-item"><span class="info-label">服务车辆</span><span class="info-value">{station_data['total_vehicles']}辆</span></div>
        <div class="info-item"><span class="info-label">同时充电</span><span class="info-value">{station_data['vehicle_count']}辆</span></div>
        <div class="info-item"><span class="info-label">光伏容量</span><span class="info-value">500 kWp</span></div>
        <div class="info-item"><span class="info-label">储能容量</span><span class="info-value">500 kWh</span></div>
        <div class="info-item"><span class="info-label">数据时间</span><span class="info-value">{station_data['date_range']}</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    # 周期选择
    st.markdown('<div style="color: rgba(255,255,255,0.7); font-size: 13px; margin: 16px 8px 8px;">统计周期</div>', unsafe_allow_html=True)
    period = st.selectbox("", ["今日", "本周", "本月", "本季度", "本年"], label_visibility="collapsed", key="period")
    
    # 导出按钮
    st.button("📥 导出数据报表", use_container_width=True, type="primary")


# ==================== 主内容区域 ====================

# 品牌标识和场站信息
col1, col2 = st.columns([1, 3])
with col1:
    st.markdown("""
    <div class="brand-header">
        <div class="brand-logo">⚡</div>
        <div>
            <div class="brand-name">智电未来</div>
            <div class="brand-sub">ZhiDian Future Tech</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="station-header">
        <div>
            <span class="station-name">{station_data['station_name']}</span>
            <span class="station-badge" style="margin-left: 16px;">{station_data['total_records']:,}条数据记录</span>
        </div>
        <div style="color: rgba(255,255,255,0.8); font-size: 14px;">{datetime.now().strftime('%Y年%m月%d日')}</div>
    </div>
    """, unsafe_allow_html=True)


# ==================== 场站总览页面 ====================

if selected_page == "场站总览":
    # 第一行：核心指标
    cols = st.columns(4)
    
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📅 本月电量支出</div>
            <div class="metric-value">¥ {station_data['monthly_energy_cost']:,}</div>
            <div class="metric-trend"><span class="trend-down">↓ {abs(station_data['monthly_change'])}%</span> <span style="color:#5F6B7A;">环比下降</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💰 平台累计节省</div>
            <div class="metric-value">¥ {station_data['cumulative_savings']:,}</div>
            <div class="metric-trend"><span class="trend-neutral">vs 无优化</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">⚡ 百公里平均能耗</div>
            <div class="metric-value">{station_data['avg_energy_consumption']} kWh</div>
            <div class="metric-trend"><span class="trend-up">↓ {station_data['energy_efficiency']}%</span> <span style="color:#5F6B7A;">优于行业</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🔋 电池寿命延长收益</div>
            <div class="metric-value">¥ {station_data['battery_lifetime_value']:,}</div>
            <div class="metric-trend"><span class="trend-neutral">折算TCO价值</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # 第二行：今日运行数据
    st.markdown('<div class="section-title">📊 今日运行数据 <span class="section-link">基于CSV真实数据</span></div>', unsafe_allow_html=True)
    
    cols = st.columns(5)
    daily_metrics = [
        ("充电量", f"{station_data['daily_energy']} kWh", "来自CSV"),
        ("光伏发电", f"{station_data['pv_generation_today']} kWh", ""),
        ("运行成本", f"¥ {abs(station_data['daily_cost'])}", "负成本运营"),
        ("节省电费", f"¥ {station_data['daily_savings']}", ""),
        ("减排CO₂", f"{station_data['daily_co2']} kg", "")
    ]
    
    for i, (label, value, badge) in enumerate(daily_metrics):
        with cols[i]:
            badge_html = f'<span style="background: #1E3A8A; color: white; padding: 4px 8px; border-radius: 20px; font-size: 11px; margin-left: 8px;">{badge}</span>' if badge else ''
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div style="display: flex; align-items: baseline;">
                    <span class="metric-value">{value}</span>
                    {badge_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # 电量支出趋势图
    st.markdown('<div class="section-title">📈 电量支出趋势</div>', unsafe_allow_html=True)
    
    months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    before = [268, 265, 259, 255, 252, 248, 245, 242, 238, 235, 232, 228]
    after = [245, 242, 238, 235, 232, 228, 225, 222, 218, 215, 212, 208]
    
    with st.container():
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months, y=before,
            mode='lines+markers',
            name='优化前',
            line=dict(color='#94A3B8', width=2.5, dash='dot'),
            marker=dict(size=8, color='#94A3B8')
        ))
        fig.add_trace(go.Scatter(
            x=months, y=after,
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
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", size=12)
        )
        
        fig.update_xaxes(gridcolor='#E2E8F0', gridwidth=1, showgrid=True)
        fig.update_yaxes(gridcolor='#E2E8F0', gridwidth=1, showgrid=True)
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # 第三行：小时负荷曲线
    st.markdown('<div class="section-title">⏱️ 典型日负荷曲线</div>', unsafe_allow_html=True)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=load_data,
        mode='lines',
        name='充电负荷',
        line=dict(color='#1E3A8A', width=3),
        fill='tozeroy',
        fillcolor='rgba(30, 58, 138, 0.1)'
    ))
    fig.add_trace(go.Scatter(
        x=hours, y=pv_data,
        mode='lines',
        name='光伏出力',
        line=dict(color='#3B82F6', width=3),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    
    fig.update_layout(
        height=350,
        xaxis_title="小时",
        yaxis_title="功率 (kW)",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(gridcolor='#E2E8F0', tickmode='linear', tick0=0, dtick=2)
    fig.update_yaxes(gridcolor='#E2E8F0')
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # 第四行：成本结构
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-title">💰 TCO成本结构</div>', unsafe_allow_html=True)
        
        cost_cats = ['充电成本', '电池更换', '维护保养', '保险税费', '其他']
        cost_vals = [42, 28, 15, 10, 5]
        colors = ['#1E3A8A', '#3B82F6', '#94A3B8', '#CBD5E1', '#E2E8F0']
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=cost_cats, values=cost_vals, hole=0.45,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='outside',
            textfont=dict(size=13, color='#0A1A2F'),
            showlegend=False
        )])
        
        fig_pie.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=20, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        st.markdown('<div class="section-title">📋 成本节约明细</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: white; border-radius: 24px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.04); height: 320px;">
            <div style="display: flex; flex-direction: column; height: 100%; justify-content: space-between;">
                <div>
                    <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #E2E8F0;">
                        <span style="color: #5F6B7A;">电费节省</span>
                        <span style="font-weight: 600; color: #1E3A8A;">¥ 42,300</span>
                    </div>
                    <div style="display
