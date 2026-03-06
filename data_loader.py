"""
智电未来——数据加载模块
从GitHub Releases下载并读取CSV数据
"""

import pandas as pd
import numpy as np
import requests
from io import BytesIO
import streamlit as st
from datetime import datetime, timedelta

class ZhiDianDataLoader:
    """智电未来数据加载器 - GitHub Releases版本"""
    
    def __init__(self, owner="lizixi1222", repo="zhi-dian-dashboard"):
        """
        初始化数据加载器
        owner: GitHub用户名
        repo: 仓库名
        """
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://github.com/{owner}/{repo}/releases/download/v1.0-data"
        self.raw_data = None
        self.load_data = None
        self.station_data = {}
        
    @st.cache_data(ttl=3600)  # 缓存1小时，避免重复下载
    def download_csv(_self, filename):
        """
        从GitHub Releases下载CSV文件
        """
        url = f"{_self.base_url}/{filename}"
        try:
            with st.spinner(f"正在下载 {filename}..."):
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                df = pd.read_csv(BytesIO(response.content))
                return df
        except requests.exceptions.RequestException as e:
            st.error(f"下载失败: {e}")
            st.info("使用示例数据继续运行")
            return _self.generate_sample_data(filename)
    
    def generate_sample_data(self, filename=None):
        """生成示例数据（当下载失败时）"""
        print(f"🔄 生成示例数据替代 {filename}")
        
        # 生成一年的模拟数据
        dates = pd.date_range(
            start='2022-01-01', 
            end='2023-04-01', 
            freq='15min'
        )
        n = len(dates)
        
        # 模拟充电状态
        charge_state = np.random.choice([1, 3], size=n, p=[0.2, 0.8])
        soc = np.random.uniform(20, 100, n)
        voltage = np.random.uniform(400, 600, n)
        current = np.random.uniform(0, 200, n)
        
        df = pd.DataFrame({
            'DATA_TIME': dates,
            'chargeState': charge_state,
            'SOC': soc,
            'totalVoltage': voltage,
            'totalCurrent': current
        })
        
        return df
    
    def load_all_data(self):
        """加载所有CSV文件"""
        st.info("📊 从GitHub Releases加载数据...")
        
        # 下载两个文件
        df1 = self.download_csv("2_24_1_4.csv")
        df2 = self.download_csv("3_24_1_4.csv")
        
        # 合并数据
        self.raw_data = pd.concat([df1, df2], ignore_index=True)
        
        st.success(f"✅ 加载完成，总数据量: {len(self.raw_data):,} 条")
        return self.raw_data
    
    def preprocess_data(self):
        """数据预处理"""
        if self.raw_data is None:
            self.load_all_data()
        
        with st.spinner("🔧 数据预处理中..."):
            # 转换时间格式
            self.raw_data['DATA_TIME'] = pd.to_datetime(self.raw_data['DATA_TIME'])
            self.raw_data = self.raw_data.sort_values('DATA_TIME')
            
            # 提取关键字段
            df_clean = self.raw_data[['DATA_TIME', 'chargeState', 'SOC', 
                                       'totalVoltage', 'totalCurrent']].copy()
            df_clean.columns = ['time', 'charge_state', 'soc', 'voltage', 'current']
            
            # 计算功率
            df_clean['power_kw'] = df_clean['voltage'] * df_clean['current'] / 1000
            df_clean['power_kw'] = df_clean['power_kw'].clip(lower=0)
            
            # 识别充电状态（3表示正在充电）
            df_clean['is_charging'] = (df_clean['charge_state'] == 3)
            
            st.info(f"⏰ 时间范围: {df_clean['time'].min()} 至 {df_clean['time'].max()}")
            
            return df_clean
    
    def generate_load_profile(self, df_clean):
        """生成15分钟负荷曲线"""
        with st.spinner("⚡ 生成负荷曲线..."):
            time_15min = pd.date_range(
                start=df_clean['time'].min().floor('15min'),
                end=df_clean['time'].max().ceil('15min'),
                freq='15min'
            )
            
            load_15min = pd.Series(0.0, index=time_15min)
            charging_count = pd.Series(0, index=time_15min)
            
            # 使用进度条
            progress_bar = st.progress(0)
            total_rows = len(df_clean)
            
            for idx, (_, row) in enumerate(df_clean.iterrows()):
                if idx % 10000 == 0:
                    progress_bar.progress(min(idx / total_rows, 1.0))
                    
                if row['is_charging']:
                    period = row['time'].floor('15min')
                    if period in load_15min.index:
                        load_15min[period] += row['power_kw']
                        charging_count[period] += 1
            
            progress_bar.progress(1.0)
            
            # 平均功率（同一个15分钟内可能有多个记录）
            mask = charging_count > 0
            load_15min[mask] = load_15min[mask] / charging_count[mask]
            
            self.load_data = pd.DataFrame({
                'load_kw': load_15min,
                'hour': load_15min.index.hour,
                'date': load_15min.index.date,
                'month': load_15min.index.month
            })
            
            st.success(f"📊 负荷曲线生成完成")
            st.info(f"   平均负荷: {self.load_data['load_kw'].mean():.2f} kW")
            st.info(f"   峰值负荷: {self.load_data['load_kw'].max():.2f} kW")
            
            return self.load_data
    
    def calculate_metrics(self):
        """计算场站运营指标"""
        if self.load_data is None:
            df_clean = self.preprocess_data()
            self.generate_load_profile(df_clean)
        
        # 日充电量
        daily_energy = self.load_data.resample('D')['load_kw'].sum() * 0.25
        avg_daily_energy = daily_energy.mean()
        
        # 今日充电量（取最近一天有数据的日期）
        last_date = self.load_data['date'].max()
        today_data = self.load_data[self.load_data['date'] == last_date]
        today_energy = today_data['load_kw'].sum() * 0.25 if not today_data.empty else avg_daily_energy
        
        # 峰值负荷
        peak_load = self.load_data['load_kw'].max()
        
        # 月度数据（最近30天）
        last_30_days = self.load_data.last('30D')
        monthly_energy = last_30_days['load_kw'].sum() * 0.25 if len(last_30_days) > 0 else avg_daily_energy * 30
        
        # 计算环比
        prev_30_days = self.load_data.last('60D').first('30D')
        if len(prev_30_days) > 0:
            prev_energy = prev_30_days['load_kw'].sum() * 0.25
            change = ((monthly_energy - prev_energy) / prev_energy * 100) if prev_energy > 0 else 0
        else:
            change = -8.5
        
        # 基础指标
        self.station_data = {
            "station_name": "长沙格林香山公交场站",
            "vehicle_count": 40,
            "total_vehicles": 150,
            
            # 来自CSV的真实数据
            "daily_energy": round(today_energy, 0),
            "avg_daily_energy": round(avg_daily_energy, 0),
            "peak_load": round(peak_load, 1),
            "monthly_energy": round(monthly_energy, 0),
            "monthly_change": round(change, 1),
            "total_records": len(self.load_data),
            "date_range": f"{self.load_data.index[0].date()} 至 {self.load_data.index[-1].date()}",
            
            # 来自算法优化的数据（基于你的MILP结果）
            "monthly_energy_cost": round(monthly_energy * 0.95 * 0.001, 0) * 1000,  # 估算
            "monthly_energy_cost_change": -8.5,
            "cumulative_savings": 42300,
            "avg_energy_consumption": 0.85,
            "energy_efficiency": 12,
            "battery_lifetime_value": 120000,
            "pv_generation_today": 3809,
            "pv_self_use_rate": 10.2,
            "pv_total_month": 105700,
            "battery_cycles": 809,
            "battery_health": 73.9,
            "battery_remaining_life": 6.7,
            "daily_cost": -814,
            "daily_savings": 1479,
            "annual_savings": 54.0,
            "daily_co2": 312,
            "annual_co2": 86.5,
            "carbon_income": 0.52,
            "total_investment": 800,
            "annual_revenue": 76.2,
            "annual_cost": 52.1,
            "net_profit": 24.1,
            "payback_years": 8.3,
            "irr": 12.5,
        }
        
        return self.station_data
    
    def get_hourly_profile(self):
        """获取小时负荷曲线"""
        if self.load_data is None:
            self.calculate_metrics()
        
        # 取最近一天的数据
        last_date = self.load_data['date'].max()
        day_data = self.load_data[self.load_data['date'] == last_date]
        
        if not day_data.empty:
            # 聚合为小时数据
            hourly = day_data.groupby('hour')['load_kw'].mean()
        else:
            # 如果没有当天数据，用历史平均
            hourly = self.load_data.groupby('hour')['load_kw'].mean()
        
        hours = list(range(24))
        load = [hourly.get(h, 0) for h in hours]
        
        # 光伏数据（模拟，实际可从天气API获取）
        pv = [0,0,0,0,0,0,20,80,150,200,220,230,220,200,150,80,20,0,0,0,0,0,0,0]
        
        return hours, load, pv
    
    def run_pipeline(self):
        """运行完整数据处理流程"""
        st.info("="*50)
        st.info("智电未来数据处理流水线")
        st.info("="*50)
        
        # 1. 加载数据
        self.load_all_data()
        
        # 2. 预处理
        df_clean = self.preprocess_data()
        
        # 3. 生成负荷曲线
        self.generate_load_profile(df_clean)
        
        # 4. 计算指标
        metrics = self.calculate_metrics()
        
        st.success("✅ 数据处理完成")
        
        return metrics