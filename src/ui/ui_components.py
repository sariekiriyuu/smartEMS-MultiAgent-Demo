"""UI components for the Smart Energy Management System demo.

This module contains reusable UI components for rendering charts, status cards,
logs, and metrics in the Streamlit application.
"""

from typing import Dict, List, Optional, Tuple
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Status indicators
STATUS_ICONS = {
    "ok": "✅",
    "active": "🟢",
    "info": "🟡",
    "alert": "⚠️",
    "error": "❌",
}

STATUS_COLORS = {
    "ok": "#1b9e77",
    "active": "#377eb8",
    "info": "#ffcc00",
    "alert": "#d95f02",
    "error": "#d73027",
}

STATUS_BG_COLORS = {
    "ok": "rgba(27, 158, 119, 0.12)",
    "active": "rgba(55, 126, 184, 0.12)",
    "info": "rgba(255, 204, 0, 0.12)",
    "alert": "rgba(217, 95, 2, 0.15)",
    "error": "rgba(215, 48, 39, 0.18)",
}

AGENT_LABELS = {
    "forecaster": "Forecaster",
    "optimizer": "Optimizer",
    "scheduler": "Scheduler",
    "fault": "Fault Detection",
    "orchestrator": "Orchestrator",
    "hils_coach": "HILS Coach",
    "explain": "LLM Analyst",
}


def render_energy_chart(ess_data: List[float], pv_data: List[float], load_data: List[float]) -> None:
    """Render the real-time energy states chart.
    
    Args:
        ess_data: List of ESS SOC values
        pv_data: List of PV output values
        load_data: List of load values
    """
    if not ess_data:
        return
    
    steps = list(range(len(ess_data)))
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=ess_data,
            name="ESS SOC",
            mode="lines",
            line=dict(color="#2ca02c", width=3),
            line_shape="spline",
            fill="tozeroy",
            fillcolor="rgba(44, 160, 44, 0.15)",
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=pv_data,
            name="PV Output",
            mode="lines",
            line=dict(color="#1f77b4", width=2),
            line_shape="spline",
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=load_data,
            name="Load",
            mode="lines",
            line=dict(color="#ff7f0e", width=2, dash="dash"),
            line_shape="spline",
        )
    )
    
    fig.update_layout(
        title="Real-time HILS Energy States",
        xaxis_title="Step",
        yaxis_title="Value",
        margin=dict(l=40, r=20, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def render_agent_status_cards(agent_status: Dict[str, Dict]) -> None:
    """Render agent status cards in a 2-column layout.
    
    Args:
        agent_status: Dictionary mapping agent names to their status info
    """
    if not agent_status:
        return
    
    items = list(agent_status.items())
    cols = st.columns(2)
    
    for idx, (name, info) in enumerate(items):
        status = info.get('status', 'info') if isinstance(info, dict) else 'info'
        message = info.get('message', info) if isinstance(info, dict) else str(info)
        icon = STATUS_ICONS.get(status, STATUS_ICONS['info'])
        border_color = STATUS_COLORS.get(status, STATUS_COLORS['info'])
        bg_color = STATUS_BG_COLORS.get(status, "rgba(0,0,0,0.05)")
        
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div style="background-color:{bg_color};border-left:6px solid {border_color};padding:0.75rem;border-radius:0.6rem;margin-bottom:0.6rem;">
                    <div style="font-weight:600;font-size:1rem;margin-bottom:0.25rem;">{icon} {name}</div>
                    <div style="font-size:0.85rem;color:#1f1f1f;">{message}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_live_logs(logs: List[str], log_records: List[Dict]) -> None:
    """Render live logs with download capability.
    
    Args:
        logs: List of formatted log strings
        log_records: List of log record dictionaries
    """
    if not logs:
        return
    
    st.text_area(
        "Logs",
        "\n".join(logs[-14:]),
        height=240,
        key="log_view",
        disabled=True,
        label_visibility="collapsed",
    )
    
    if log_records:
        log_df = pd.DataFrame(log_records)
        csv_bytes = log_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download CSV",
            data=csv_bytes,
            file_name="simulation_logs.csv",
            mime="text/csv",
            use_container_width=True,
        )


def render_metrics(ess: Optional[float], pv: Optional[float], 
                  load: Optional[float], price: Optional[float]) -> None:
    """Render metric cards in a 4-column layout.
    
    Args:
        ess: ESS SOC value
        pv: PV output value
        load: Load value
        price: Price value
    """
    cols = st.columns(4)
    cols[0].metric("ESS SOC", f"{ess:.1f}%" if ess is not None else "—")
    cols[1].metric("PV Output", f"{pv:.1f}" if pv is not None else "—")
    cols[2].metric("Load", f"{load:.1f}" if load is not None else "—")
    cols[3].metric("Price", f"{price:.0f}" if price is not None else "—")


def render_final_results(ess: float, pv: float, load: float) -> None:
    """Render final simulation results.
    
    Args:
        ess: Final ESS SOC value
        pv: Final PV output value
        load: Final load value
    """
    st.success("Simulation complete")
    metrics_cols = st.columns(3)
    metrics_cols[0].metric("Final ESS SOC", f"{ess:.1f}%")
    metrics_cols[1].metric("Final PV Output", f"{pv:.1f}")
    metrics_cols[2].metric("Final Load", f"{load:.1f}")


def render_agent_status_table(agent_status: Dict[str, Dict]) -> None:
    """Render agent status as a table.
    
    Args:
        agent_status: Dictionary mapping agent names to their status info
    """
    if not agent_status:
        st.info("Agent status will be displayed once simulation starts.")
        return
    
    rows = []
    for name, info in agent_status.items():
        rows.append({
            "Agent": name,
            "Status": info.get("status", "info") if isinstance(info, dict) else "info",
            "Message": info.get("message", info) if isinstance(info, dict) else str(info),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_alert_table(log_records: List[Dict]) -> None:
    """Render security alerts as a table.
    
    Args:
        log_records: List of log record dictionaries
    """
    alerts = [
        r for r in log_records
        if r.get("alerts") or (isinstance(r.get("event"), str) and "alert" in r.get("event", "").lower())
    ]
    
    if alerts:
        st.table([{
            "t": a.get("step"),
            "alerts": a.get("alerts"),
            "details": a.get("details", ""),
        } for a in alerts[-6:]])
    else:
        st.info("No alerts currently. Start the simulation and trigger anomaly events.")
