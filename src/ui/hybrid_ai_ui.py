"""Hybrid AI and Multi-Agent Collaboration UI components.

This module provides enhanced visualization for demonstrating:
1. Hybrid AI architecture (ML + Rule-based + LLM)
2. Multi-Agent collaboration and decision-making process
"""

from typing import Dict, List, Any
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def render_hybrid_ai_architecture() -> None:
    """Render Hybrid AI architecture diagram showing ML + LLM components."""
    
    st.markdown("### 🧠 Hybrid AI Architecture")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);color:white;padding:1.5rem;border-radius:1rem;text-align:center;">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">🔢</div>
            <div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;">ML Optimizer</div>
            <div style="font-size:0.85rem;opacity:0.95;">MILP (PuLP)<br/>Mathematical Optimization</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg, #f093fb 0%, #f5576c 100%);color:white;padding:1.5rem;border-radius:1rem;text-align:center;">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">⚙️</div>
            <div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;">Rule-based</div>
            <div style="font-size:0.85rem;opacity:0.95;">Forecaster, Scheduler<br/>Heuristic Rules</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background:linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);color:white;padding:1.5rem;border-radius:1rem;text-align:center;">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">🤖</div>
            <div style="font-weight:700;font-size:1.1rem;margin-bottom:0.5rem;">LLM Analyst</div>
            <div style="font-size:0.85rem;opacity:0.95;">MockLLM<br/>Context Analysis</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")


def render_agent_collaboration_graph(agent_decisions: Dict[str, List[str]]) -> None:
    """Render multi-agent collaboration decision flow graph.
    
    Args:
        agent_decisions: Dictionary mapping agent names to their recent decisions
    """
    
    st.markdown("### 🔗 Multi-Agent Collaboration Flow")
    
    if not agent_decisions:
        st.info("Agent collaboration process will be displayed once simulation starts.")
        return
    
    # Create decision timeline chart
    fig = go.Figure()
    
    agents = list(agent_decisions.keys())
    colors = ['#667eea', '#f093fb', '#4facfe', '#fa709a', '#30cfd0', '#a8edea']
    
    for idx, (agent_name, decisions) in enumerate(agent_decisions.items()):
        if decisions:
            steps = list(range(len(decisions)))
            y_values = [idx] * len(decisions)
            
            fig.add_trace(go.Scatter(
                x=steps,
                y=y_values,
                mode='markers+lines',
                name=agent_name,
                marker=dict(size=12, color=colors[idx % len(colors)]),
                line=dict(width=2, color=colors[idx % len(colors)]),
                hovertemplate=f'<b>{agent_name}</b><br>Step: %{{x}}<br>Decision: %{{text}}<extra></extra>',
                text=[d[:40] + '...' if len(d) > 40 else d for d in decisions],
            ))
    
    fig.update_layout(
        title="Agent Decision Timeline",
        xaxis_title="Simulation Step",
        yaxis=dict(
            tickvals=list(range(len(agents))),
            ticktext=agents,
        ),
        height=400,
        margin=dict(l=150, r=20, t=60, b=40),
        hovermode='closest',
    )
    
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def render_mcp_context_flow(mcp_history: List[Dict[str, Any]]) -> None:
    """Render MCP context server data flow visualization.
    
    Args:
        mcp_history: List of MCP context updates
    """
    
    st.markdown("### 📡 MCP Context Server Flow")
    
    if not mcp_history or len(mcp_history) < 2:
        st.info("MCP context data is being collected...")
        return
    
    # Show recent context updates
    recent = mcp_history[-5:]
    
    cols = st.columns(len(recent))
    for idx, ctx in enumerate(recent):
        with cols[idx]:
            step = ctx.get('step', '?')
            ess = ctx.get('ess_level', 0)
            pv = ctx.get('pv_output', 0)
            
            st.markdown(f"""
            <div style="background:rgba(100, 181, 246, 0.1);border:2px solid #64b5f6;padding:0.8rem;border-radius:0.5rem;text-align:center;">
                <div style="font-weight:700;font-size:0.9rem;color:#1976d2;margin-bottom:0.3rem;">Step {step}</div>
                <div style="font-size:0.75rem;">ESS: {ess:.1f}%</div>
                <div style="font-size:0.75rem;">PV: {pv:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.caption("MCP serves as a Context server shared by all agents.")


def render_decision_comparison_table(decisions: Dict[str, str]) -> None:
    """Render agent decision comparison table showing hybrid AI approaches.
    
    Args:
        decisions: Dictionary mapping agent names to their latest decisions
    """
    
    st.markdown("### 📊 Agent Decision Comparison")
    
    if not decisions:
        st.info("No agent decisions yet.")
        return
    
    # Map agent to AI type
    ai_type_map = {
        "Forecaster": "Rule-based",
        "Optimizer": "ML (MILP)",
        "Scheduler": "Rule-based",
        "Fault Detection": "Rule-based",
        "Orchestrator": "Context-based",
        "HILS Coach": "Feedback-based",
        "LLM Analyst": "LLM (Mock)",
    }
    
    rows = []
    for agent_name, decision in decisions.items():
        ai_type = ai_type_map.get(agent_name, "Unknown")
        rows.append({
            "Agent": agent_name,
            "AI Type": ai_type,
            "Latest Decision": decision[:60] + "..." if len(decision) > 60 else decision,
        })
    
    st.table(rows)
    
    st.caption("💡 Hybrid AI combines ML optimization, rule-based control, and LLM analysis.")


def render_collaboration_metrics(agent_calls: Dict[str, int]) -> None:
    """Render agent collaboration metrics as pie chart.
    
    Args:
        agent_calls: Dictionary mapping agent names to call counts
    """
    
    st.markdown("### 📈 Agent Activity Distribution")
    
    if not agent_calls:
        st.info("Collecting agent activity data.")
        return
    
    fig = go.Figure(data=[go.Pie(
        labels=list(agent_calls.keys()),
        values=list(agent_calls.values()),
        hole=0.4,
        marker=dict(colors=['#667eea', '#f093fb', '#4facfe', '#fa709a', '#30cfd0', '#a8edea']),
    )])
    
    fig.update_layout(
        title="Agent Execution Count",
        height=350,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def render_hybrid_ai_insights(context: Dict[str, Any], decisions: Dict[str, str]) -> None:
    """Render combined hybrid AI insights panel.
    
    Args:
        context: Current system context
        decisions: Recent agent decisions
    """
    
    st.markdown("### 💡 Hybrid AI Insights")
    
    # ML Insight
    optimizer_decision = decisions.get("Optimizer", "No data")
    st.markdown(f"""
    <div style="background:rgba(102, 126, 234, 0.1);border-left:4px solid #667eea;padding:1rem;border-radius:0.5rem;margin-bottom:0.8rem;">
        <div style="font-weight:700;margin-bottom:0.3rem;">🔢 ML Optimizer</div>
        <div style="font-size:0.9rem;">{optimizer_decision}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Rule-based Insight
    forecaster_decision = decisions.get("Forecaster", "No data")
    st.markdown(f"""
    <div style="background:rgba(240, 147, 251, 0.1);border-left:4px solid #f093fb;padding:1rem;border-radius:0.5rem;margin-bottom:0.8rem;">
        <div style="font-weight:700;margin-bottom:0.3rem;">⚙️ Rule-based Forecaster</div>
        <div style="font-size:0.9rem;">{forecaster_decision}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # LLM Insight
    llm_decision = decisions.get("LLM Analyst", "No data")
    st.markdown(f"""
    <div style="background:rgba(79, 172, 254, 0.1);border-left:4px solid #4facfe;padding:1rem;border-radius:0.5rem;margin-bottom:0.8rem;">
        <div style="font-weight:700;margin-bottom:0.3rem;">🤖 LLM Analyst</div>
        <div style="font-size:0.9rem;">{llm_decision}</div>
    </div>
    """, unsafe_allow_html=True)
