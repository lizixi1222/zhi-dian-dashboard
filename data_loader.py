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
        
    @st.cache_data(ttl=3600)
    def download_csv(self, filename):
        """
        从GitHub Releases下载CSV文件
        """
        url = f"{self.base_url}/{filename}"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            df = pd.read_csv(BytesIO(response.content))
            return df
        except Exception as e:
            st.error(f"下载失败: {e}")
            return self.generate_sample_data()
    
    def generate_sample_data(self):
        """生成示例数据（当下载失败时）"""
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
        
        return df_clean
    
    def generate_load_profile(self, df_clean):
        """生成15分钟负荷曲线"""
        time_15min = pd.date_range(
            start=df_clean['time'].min().floor('15min'),
            end=df_clean['time'].max().ceil('15min'),
            freq='15min'
        )
        
        load_15min = pd.Series(0.0, index=time_15min)
        
        for _, row in df_clean.iterrows():
            if row['is_charging']:
                period = row['time'].floor('15min')
                if period in load_15min.index:
                    load_15min[period] += row['power_kw']
        
        self.load_data = pd.DataFrame({
            'load_kw': load_15min,
            'hour': load_15min.index.hour,
            'date': load_15min.index.date
        })
        
        return self.load_data
    
    def calculate_metrics(self):
        """计算场站运营指标"""
        if self.load_data is None:
            df_clean = self.preprocess_data()
            self.generate_load_profile(df_clean)
        
        # 日充电量
        daily_energy = self.load_data.resample('D')['load_kw'].sum() * 0.25
        avg_daily_energy = daily_energy.mean()
        
        # 今日充电量
        last_date = self.load_data['date'].max()
        today_data = self.load_data[self.load_data['date'] == last_date]
        today_energy = today_data['load_kw'].sum() * 0.25 if not today_data.empty else avg_daily_energy
        
        # 峰值负荷
        peak_load = self.load_data['load_kw'].max()
        
        # 月度数据
        last_30_days = self.load_data.last('30D')
        monthly_energy = last_30_days['load_kw'].sum() * 0.25 if len(last_30_days) > 0 else avg_daily_energy * 30
        
        # 基础指标
        self.station_data = {
            "station_name": "智电未来公交场站",
            "vehicle_count": 40,
            "total_vehicles": 150,
            "daily_energy": round(today_energy, 0),
            "avg_daily_energy": round(avg_daily_energy, 0),
            "peak_load": round(peak_load, 1),
            "monthly_energy": round(monthly_energy, 0),
            "pv_generation_today": 3809,
            "pv_self_use_rate": 10.2,
            "daily_cost": -814,
            "daily_savings": 1479,
            "daily_co2": 312,
            "battery_health": 73.9,
            "battery_cycles": 809,
            "battery_remaining_life": 6.7,
            "monthly_energy_cost": round(monthly_energy * 0.95 * 0.001, 0) * 1000,
            "cumulative_savings": 42300,
            "avg_energy_consumption": 0.85,
            "battery_lifetime_value": 120000,
            "annual_co2": 86.5,
            "carbon_income": 0.52,
            "total_investment": 800,
            "payback_years": 8.3,
        }
        
        return self.station_data
    
    def get_hourly_profile(self):
        """获取小时负荷曲线"""
        if self.load_data is None:
            self.calculate_metrics()
        
        last_date = self.load_data['date'].max()
        day_data = self.load_data[self.load_data['date'] == last_date]
        
        if not day_data.empty:
            hourly = day_data.groupby('hour')['load_kw'].mean()
        else:
            hourly = self.load_data.groupby('hour')['load_kw'].mean()
        
        hours = list(range(24))
        load = [hourly.get(h, 0) for h in hours]
        pv = [0,0,0,0,0,0,20,80,150,200,220,230,220,200,150,80,20,0,0,0,0,0,0,0]
        
        return hours, load, pv
    
    def run_pipeline(self):
        """运行完整数据处理流程"""
        self.load_all_data()
        df_clean = self.preprocess_data()
        self.generate_load_profile(df_clean)
        metrics = self.calculate_metrics()
        return metrics

