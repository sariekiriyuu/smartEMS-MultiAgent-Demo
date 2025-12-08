"""Utility functions for the Smart Energy Management System demo.

This module contains helper functions for logging, session state management,
and simulation control.
"""

from typing import Optional, Tuple, Dict, Any
from datetime import datetime
import streamlit as st


def format_log_record(record: Dict[str, Any]) -> str:
    """Format a log record into a human-readable string.
    
    Args:
        record: Dictionary containing log information
        
    Returns:
        Formatted log string
    """
    step = record.get("step")
    prefix = f"[t={step}] " if step is not None else ""
    
    metrics = []
    for key, label in (("ess", "ESS"), ("pv", "PV"), ("load", "Load"), ("price", "Price")):
        value = record.get(key)
        if value is not None:
            if key == "price":
                metrics.append(f"{label}={value:.0f}")
            else:
                metrics.append(f"{label}={value:.1f}")
    
    metrics_part = ", ".join(metrics)
    details = record.get("details") or ""
    alerts = record.get("alerts") or ""
    pieces = [part for part in (metrics_part, details, alerts) if part]
    suffix = " | ".join(pieces)
    
    if suffix:
        return f"{prefix}{suffix}"
    return prefix + (record.get("event", "").capitalize() or "log")


def append_log_record(record: Dict[str, Any]) -> None:
    """Append a log record to the session state.
    
    Args:
        record: Dictionary containing log information
    """
    if "timestamp" not in record:
        record["timestamp"] = datetime.utcnow().isoformat()
    
    st.session_state.log_records.append(record)
    st.session_state.log_records = st.session_state.log_records[-250:]
    st.session_state.logs.append(format_log_record(record))
    st.session_state.logs = st.session_state.logs[-250:]


def latest_metrics() -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """Get the latest metrics from the session state.
    
    Returns:
        Tuple of (ess, pv, load, price) values, or None if not available
    """
    if st.session_state.log_records:
        latest = st.session_state.log_records[-1]
        return (
            latest.get("ess"),
            latest.get("pv"),
            latest.get("load"),
            latest.get("price"),
        )
    
    if st.session_state.ess_data:
        return (
            st.session_state.ess_data[-1],
            st.session_state.pv_data[-1] if st.session_state.pv_data else None,
            st.session_state.load_data[-1] if st.session_state.load_data else None,
            None,
        )
    
    return (None, None, None, None)


def init_session_state() -> None:
    """Initialize session state variables if they don't exist."""
    if 'running' not in st.session_state:
        st.session_state.running = False
        st.session_state.logs = []
        st.session_state.log_records = []
        st.session_state.ess_data = []
        st.session_state.pv_data = []
        st.session_state.load_data = []
        st.session_state.agent_status = {}
        st.session_state.thread_started = False
        st.session_state.celebrated = False
        st.session_state.scenario_config = {}


def get_scenario_config(scenario_name: str, scenarios: Dict) -> Dict[str, Any]:
    """Get scenario configuration by name.
    
    Args:
        scenario_name: Name of the scenario
        scenarios: Dictionary of available scenarios
        
    Returns:
        Scenario configuration dictionary
    """
    return scenarios.get(scenario_name, {
        "price_low": 100,
        "price_high": 160,
        "high_start_ratio": 0.55,
    })


def clear_simulation_data() -> None:
    """Clear all simulation data from session state."""
    st.session_state.logs.clear()
    st.session_state.log_records.clear()
    st.session_state.ess_data.clear()
    st.session_state.pv_data.clear()
    st.session_state.load_data.clear()
    st.session_state.agent_status = {}
    st.session_state.thread_started = False
    st.session_state.celebrated = False
