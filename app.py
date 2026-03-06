"""
智电未来科技有限公司——公交场站运营数据看板
含CSV数据加载模块 · Python 3.14兼容
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime
import sys
from io import StringIO

# 页面配置
st.set_page_config(
    page_title="智电未来 - 场站运营看板",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== 数据加载模块 ====================
class CSVDataLoader:
    """CSV数据加载器 - 从GitHub Releases读取"""
    
    def __init__(self):
        self.base_url = "https://github.com/lizixi1222/zhi-dian-dashboard/releases/download/v1.0-data"
        self.df = None
        self.stats = {}
        
    @st.cache_data(ttl=3600)
    def download_csv(self, filename):
        """下载CSV文件"""
        url = f"{self.base_url}/{filename}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text))
            return df
        except Exception as e:
            st.warning(f"下载 {filename} 失败: {e}")
            return None
    
    def load_data(self):
        """加载所有CSV数据"""
        st.info("📊 正在加载CSV数据...")
        
        df1 = self.download_csv("2_24_1_4.csv")
        df2 = self.download_csv("3_24_1_4.csv")
        
        valid_dfs = [df for df in [df1, df2] if df is not None]
        
        if valid_dfs:
            self.df = pd.concat(valid_dfs, ignore_index=True)
            st.success(f"✅ 加载 {len(self.df):,} 条充电记录")
            return True
        else:
            st.warning("⚠️ 使用示例数据")
            self.generate_sample_data()
            return False
    
    def generate_sample_data(self):
        """生成示例数据"""
        dates = pd.date_range(start='2022-01-01', end='2023-04-01', freq='15min')
        n = len(dates)
        
        rng = np.random.default_rng(42)
        charge_state = rng.choice([1, 3], size=n, p=[0.2, 0.8])
        soc = rng.uniform(20, 100, n)
        voltage = rng.uniform(400, 600, n)
        current = rng.uniform(0, 200, n)
        
        self.df = pd.DataFrame({
            'DATA_TIME': dates,
            'chargeState': charge_state,
            'SOC': soc,
            'totalVoltage': voltage,
            'totalCurrent': current
        })
    
    def analyze(self):
        """分析数据生成场站指标"""
        if self.df is None:
            self.load_data()
        
        # 数据预处理
        self.df['DATA_TIME'] = pd.to_datetime(self.df['DATA_TIME'])
        self.df['hour'] = self.df['DATA_TIME'].dt.hour
        self.df['date'] = self.df['DATA_TIME'].dt.date
        
        # 计算功率
        self.df['power_kw'] = self.df['totalVoltage'] * self.df['totalCurrent'] / 1000
        self.df['power_kw'] = self.df['power_kw'].clip(lower=0)
        self.df['is_charging'] = (self.df['chargeState'] == 3)
        
        # 充电时段分布
        charging_hours = self.df[self.df['is_charging']].groupby('hour').size()
        
        # 日充电量
        daily_energy = self.df.groupby('date')['power_kw'].sum() * 0.25
        
        # 今日数据
        last_date = self.df['date'].max()
        today_data = self.df[self.df['date'] == last_date]
        today_energy = today_data['power_kw'].sum() * 0.25 if not today_data.empty else daily_energy.mean()
        
        # 统计结果
        self.stats = {
            'station_name': '长沙格林香山公交场站',
            'total_vehicles': 150,
            'vehicle_count': 40,
            'daily_energy': round(today_energy, 0),
            'avg_daily_energy': round(daily_energy.mean(), 0),
            'peak_load': round(self.df['power_kw'].max(), 1),
            'total_records': len(self.df),
            'date_range': f"{self.df['date'].min()} 至 {self.df['date'].max()}",
            'charging_distribution': charging_hours.to_dict(),
            # 算法优化数据
            'pv_generation': 3809,
            'daily_cost': -814,
            'daily_savings': 1479,
            'daily_co2': 312,
            'battery_health': 73.9,
            'battery_cycles': 809,
            'battery_life': 6.7,
            'cumulative_savings': 42300,
            'energy_consumption': 0.85,
        }
        
        return self.stats
    
    def get_hourly_profile(self):
        """获取小时负荷曲线"""
        if not self.stats:
            self.analyze()
        
        hours = list(range(24))
        
        # 从充电分布生成负荷曲线
        if self.stats.get('charging_distribution'):
            load = [self.stats['charging_distribution'].get(h, 0) / 10 for h in hours]
            # 归一化到合理范围
            max_load = max(load) if max(load) > 0 else 1
            load = [min(50, int(l / max_load * 50)) for l in load]
        else:
            # 默认公交充电曲线
            load = [5,3,2,1,1,2,8,25,35,30,25,22,20,25,30,35,40,45,50,48,42,30,20,10]
        
        # 光伏曲线
        pv = [0,0,0,0,0,0,20,80,150,200,220,230,220,200,150,80,20,0,0,0,0,0,0,0]
        
        return hours, load, pv


# ==================== 初始化 ====================
@st.cache_resource
def init_loader():
    return CSVDataLoader()

loader = init_loader()

with st.spinner("正在分析充电数据..."):
    station_data = loader.analyze()
    hours, load_data, pv_data = loader.get_hourly_profile()


# ==================== CSS样式 ====================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0A1A2F 0%, #1E3A8A 100%);
    }
    .metric-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        margin: 10px 0;
        border: 1px solid rgba(30,58,138,0.1);
        transition: all 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 32px rgba(30,58,138,0.15);
    }
    .metric-label {
        font-size: 13px;
        color: #5F6B7A;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #0A1A2F;
        line-height: 1.2;
    }
    .metric-badge {
        font-size: 12px;
        color: #1E3A8A;
        background: rgba(30,58,138,0.1);
        padding: 4px 8px;
        border-radius: 20px;
        display: inline-block;
        margin-top: 8px;
    }
    .section-title {
        font-size: 20px;
        font-weight: 600;
        color: white;
        margin: 30px 0 20px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(255,255,255,0.3);
    }
    .sidebar-info {
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 16px;
        margin: 20px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)


# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("## ⚡ 智电未来")
    st.markdown(f"*Python {sys.version.split()[0]}*")
    st.markdown("---")
    
    # 场站信息
    st.markdown(f"""
    <div class="sidebar-info">
        <div style="color:white; font-size:16px; font-weight:600; margin-bottom:12px;">{station_data['station_name']}</div>
        <div style="color:rgba(255,255,255,0.8); font-size:14px; margin:8px 0;">
            <span style="display:inline-block; width:80px;">服务车辆</span>
            <span style="font-weight:600;">{station_data['total_vehicles']}辆</span>
        </div>
        <div style="color:rgba(255,255,255,0.8); font-size:14px; margin:8px 0;">
            <span style="display:inline-block; width:80px;">同时充电</span>
            <span style="font-weight:600;">{station_data['vehicle_count']}辆</span>
        </div>
        <div style="color:rgba(255,255,255,0.8); font-size:14px; margin:8px 0;">
            <span style="display:inline-block; width:80px;">光伏容量</span>
            <span style="font-weight:600;">500 kWp</span>
        </div>
        <div style="color:rgba(255,255,255,0.8); font-size:14px; margin:8px 0;">
            <span style="display:inline-block; width:80px;">储能容量</span>
            <span style="font-weight:600;">500 kWh</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 数据状态
    st.markdown(f"""
    <div style="color:rgba(255,255,255,0.8); font-size:13px; padding:0 16px;">
        <div>📊 {station_data['total_records']:,} 条充电记录</div>
        <div>📅 {station_data['date_range']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("© 智电未来科技有限公司")


# ==================== 主界面 ====================
st.markdown(f"## {station_data['station_name']}")
st.markdown(f"*{datetime.now().strftime('%Y年%m月%d日')}*")

# 第一行：核心指标
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📊 今日充电量</div>
        <div class="metric-value">{station_data['daily_energy']} kWh</div>
        <div class="metric-badge">来自CSV分析</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">☀️ 今日光伏</div>
        <div class="metric-value">{station_data['pv_generation']} kWh</div>
        <div class="metric-badge">晴天典型值</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">💰 日运行成本</div>
        <div class="metric-value">¥ {abs(station_data['daily_cost'])}</div>
        <div class="metric-badge" style="background:#10B98120; color:#10B981;">负成本运营</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🌿 日减排CO₂</div>
        <div class="metric-value">{station_data['daily_co2']} kg</div>
        <div class="metric-badge">环境效益</div>
    </div>
    """, unsafe_allow_html=True)

# 第二行：负荷曲线
st.markdown('<div class="section-title">📈 典型日负荷曲线</div>', unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=hours, y=load_data,
    mode='lines',
    name='充电负荷',
    line=dict(color='#1E3A8A', width=3),
    fill='tozeroy',
    fillcolor='rgba(30,58,138,0.1)'
))
fig.add_trace(go.Scatter(
    x=hours, y=pv_data,
    mode='lines',
    name='光伏出力',
    line=dict(color='#3B82F6', width=3),
    fill='tozeroy',
    fillcolor='rgba(59,130,246,0.1)'
))

fig.update_layout(
    height=450,
    xaxis_title="小时",
    yaxis_title="功率 (kW)",
    hovermode='x unified',
    plot_bgcolor='white',
    paper_bgcolor='white',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

fig.update_xaxes(gridcolor='#E2E8F0', tickmode='linear', tick0=0, dtick=2)
fig.update_yaxes(gridcolor='#E2E8F0')

st.plotly_chart(fig, use_container_width=True)

# 第三行：电池状态和累计效益
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="section-title">🔋 电池状态</div>', unsafe_allow_html=True)
    sub1, sub2, sub3 = st.columns(3)
    sub1.metric("健康度", f"{station_data['battery_health']}%")
    sub2.metric("循环次数", f"{station_data['battery_cycles']}")
    sub3.metric("剩余寿命", f"{station_data['battery_life']}年")

with col2:
    st.markdown('<div class="section-title">📊 累计效益</div>', unsafe_allow_html=True)
    sub1, sub2 = st.columns(2)
    sub1.metric("累计节省", f"¥ {station_data['cumulative_savings']:,}")
    sub2.metric("百公里能耗", f"{station_data['energy_consumption']} kWh")

# 页脚
st.markdown("---")
st.markdown("智电未来科技有限公司 · 让每一度电都聪明")

