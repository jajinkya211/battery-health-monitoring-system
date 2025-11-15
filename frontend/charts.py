"""Plotly chart generation for battery health metrics"""
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict
import pandas as pd


class BatteryCharts:
    """Generate interactive charts for battery health visualization"""
    
    @staticmethod
    def create_soh_chart(metrics: List[Dict]) -> go.Figure:
        """Create State of Health bar chart"""
        df = pd.DataFrame(metrics)
        
        fig = go.Figure()
        
        # Add bars with color based on SoH level
        colors = ['green' if soh >= 90 else 'orange' if soh >= 80 else 'red' 
                 for soh in df['soh_percent']]
        
        fig.add_trace(go.Bar(
            x=[f"Cell {cid}" for cid in df['cell_id']],
            y=df['soh_percent'],
            marker_color=colors,
            text=df['soh_percent'].round(1),
            textposition='auto',
            name='SoH %'
        ))
        
        # Add threshold lines
        fig.add_hline(y=90, line_dash="dash", line_color="green", 
                     annotation_text="Good Threshold")
        fig.add_hline(y=80, line_dash="dash", line_color="orange", 
                     annotation_text="Warning Threshold")
        
        fig.update_layout(
            title="State of Health by Cell",
            xaxis_title="Cell",
            yaxis_title="SoH (%)",
            yaxis_range=[0, 105],
            template="plotly_white",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_resistance_chart(metrics: List[Dict]) -> go.Figure:
        """Create internal resistance chart"""
        df = pd.DataFrame(metrics)
        
        fig = go.Figure()
        
        # Resistance bars
        fig.add_trace(go.Bar(
            x=[f"Cell {cid}" for cid in df['cell_id']],
            y=df['internal_resistance'],
            marker_color='steelblue',
            text=df['internal_resistance'].round(2),
            textposition='auto',
            name='Resistance (mΩ)'
        ))
        
        # Warning threshold
        fig.add_hline(y=100, line_dash="dash", line_color="red", 
                     annotation_text="Critical Threshold (100 mΩ)")
        
        fig.update_layout(
            title="Internal Resistance by Cell",
            xaxis_title="Cell",
            yaxis_title="Resistance (mΩ)",
            template="plotly_white",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_temperature_chart(metrics: List[Dict]) -> go.Figure:
        """Create temperature distribution chart"""
        df = pd.DataFrame(metrics)
        
        fig = go.Figure()
        
        colors = ['blue' if temp < 30 else 'orange' if temp < 40 else 'red' 
                 for temp in df['temperature_c']]
        
        fig.add_trace(go.Bar(
            x=[f"Cell {cid}" for cid in df['cell_id']],
            y=df['temperature_c'],
            marker_color=colors,
            text=df['temperature_c'].round(1),
            textposition='auto',
            name='Temperature (°C)'
        ))
        
        fig.add_hline(y=40, line_dash="dash", line_color="red", 
                     annotation_text="High Temperature Warning")
        
        fig.update_layout(
            title="Cell Temperature Distribution",
            xaxis_title="Cell",
            yaxis_title="Temperature (°C)",
            template="plotly_white",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_soc_chart(metrics: List[Dict]) -> go.Figure:
        """Create State of Charge chart"""
        df = pd.DataFrame(metrics)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=[f"Cell {cid}" for cid in df['cell_id']],
            y=df['soc_percent'],
            mode='lines+markers',
            marker=dict(size=10, color='green'),
            line=dict(width=2, color='green'),
            name='SoC %'
        ))
        
        fig.update_layout(
            title="State of Charge by Cell",
            xaxis_title="Cell",
            yaxis_title="SoC (%)",
            yaxis_range=[0, 105],
            template="plotly_white",
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_metrics_summary_table(metrics: List[Dict]) -> go.Figure:
        """Create summary table of all metrics"""
        df = pd.DataFrame(metrics)
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Cell ID', 'SoC (%)', 'SoH (%)', 'Resistance (mΩ)', 'Temp (°C)', 'Status'],
                fill_color='paleturquoise',
                align='left',
                font=dict(size=12, color='black')
            ),
            cells=dict(
                values=[
                    df['cell_id'],
                    df['soc_percent'].round(1),
                    df['soh_percent'].round(1),
                    df['internal_resistance'].round(2),
                    df['temperature_c'].round(1),
                    ['✓' if p else '✗' for p in df['passes_threshold']]
                ],
                fill_color=[['white', 'lightgray'] * (len(df) // 2 + 1)][:len(df)],
                align='left',
                font=dict(size=11)
            )
        )])
        
        fig.update_layout(
            title="Health Metrics Summary",
            height=300
        )
        
        return fig