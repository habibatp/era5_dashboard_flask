from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def build_timeseries_figure(df: pd.DataFrame, title: str, y_label: str):
    if "value" in df.columns:
        fig = px.line(
            df,
            x="time",
            y="value",
            title=title,
        )
    else:
        fig = go.Figure()
        
        # Zone hachurée / ombrée entre min et max
        fig.add_trace(go.Scatter(
            x=df["time"].tolist() + df["time"].tolist()[::-1],
            y=df["max"].tolist() + df["min"].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0, 176, 246, 0.2)',
            line=dict(color='rgba(255, 255, 255, 0)'),
            name='Min-Max Range',
            hoverinfo="skip"
        ))
        
        # Courbe du Minimum
        fig.add_trace(go.Scatter(
            x=df["time"],
            y=df["min"],
            mode='lines',
            name='Min',
            line=dict(color='rgba(0, 176, 246, 0.5)', width=1, dash='dot')
        ))
        
        # Courbe du Maximum
        fig.add_trace(go.Scatter(
            x=df["time"],
            y=df["max"],
            mode='lines',
            name='Max',
            line=dict(color='rgba(0, 176, 246, 0.5)', width=1, dash='dot')
        ))
        
        # Courbe de la Moyenne
        fig.add_trace(go.Scatter(
            x=df["time"],
            y=df["mean"],
            mode='lines',
            name='Mean',
            line=dict(color='rgb(0, 176, 246)', width=2)
        ))

        fig.update_layout(title=title)

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title=y_label,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig