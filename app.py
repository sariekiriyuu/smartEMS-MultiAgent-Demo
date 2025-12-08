"""Simulation-Integrated Multi-AI Agent Energy Platform (Demo)

HILS + Multi-Agent + Hybrid AI + MCP Runtime 기반 에너지 관리 시각화 데모

시스템 동작 흐름:
    [HILS Simulator] → ESS/PV/Load 계산
    [MCP Runtime] → context 업데이트
    [Multi-AI Agents] → 협업 실행 (Forecaster, Optimizer, Scheduler, Fault, Orchestrator, HILS Coach)
    [UI] → 실시간 그래프 + 에이전트 상태 + 로그
"""

import time
import random
import threading
import streamlit as st

from src.core.simulator import HILSSimulator
from src.core.mcp_core import MCPCore
from src.agents.agents import (
    ForecasterAgent,
    OptimizerAgent,
    SchedulerAgent,
    FaultDetectionAgent,
    OrchestratorAgent,
    HILSCoachAgent,
    MockLLMAgent,
)
from src.ui.ui_components import (
    render_energy_chart,
    render_agent_status_cards,
    render_live_logs,
    render_metrics,
    render_final_results,
)
from src.ui.hybrid_ai_ui import (
    render_hybrid_ai_architecture,
    render_agent_collaboration_graph,
    render_mcp_context_flow,
    render_decision_comparison_table,
    render_collaboration_metrics,
    render_hybrid_ai_insights,
)
from src.ui.utils import (
    append_log_record,
    latest_metrics,
    init_session_state,
    clear_simulation_data,
)

try:
    from streamlit.runtime.scriptrunner import add_script_run_ctx
except Exception:
    add_script_run_ctx = None

# ====================================================================================
# Page Configuration
# ====================================================================================
st.set_page_config(page_title="Smart EMS AI Demo", layout="wide")
st.title("🔋 Simulation-Integrated Multi-AI Agent Energy Platform")
st.markdown("**HILS + Hybrid AI + Multi-Agent Collaboration + MCP Runtime** · Demo Version")

# ====================================================================================
# Initialization
# ====================================================================================
init_session_state()

# Scenario Configuration
SCENARIOS = {
    "Baseline (Mild Solar)": {"price_low": 100, "price_high": 160, "high_start_ratio": 0.55},
    "High Price Late Peak": {"price_low": 80, "price_high": 180, "high_start_ratio": 0.4},
    "Volatile Market": {"price_low": 110, "price_high": 200, "high_start_ratio": 0.5},
}

# ====================================================================================
# Simulation Loop (Background Thread)
# ====================================================================================
def run_simulation_loop() -> None:
    """Run HILS simulation loop (Core Patent Technology)"""
    if st.session_state.get("fix_seed"):
        random.seed(42)
    
    # 1. Initialize HILS Simulator
    hils = HILSSimulator()
    
    # 2. Initialize MCP Runtime
    mcp = MCPCore()
    
    # 3. Initialize Multi-AI Agents (6 Core Agents)
    agents = {
        'orchestrator': OrchestratorAgent(),    # Agent coordination
        'forecaster': ForecasterAgent(),        # Forecasting
        'optimizer': OptimizerAgent(),          # MILP optimization
        'scheduler': SchedulerAgent(),          # Scheduling
        'fault': FaultDetectionAgent(),         # Fault detection
        'hils_coach': HILSCoachAgent(),         # HILS tuning
        'explain': MockLLMAgent(),              # LLM-style analysis
    }

    # Simulation Parameters
    duration = st.session_state.get('duration', 20)
    speed = st.session_state.get('speed', 0.8)
    scenario_cfg = st.session_state.get("scenario_config", {
        "price_low": 100,
        "price_high": 160,
        "high_start_ratio": 0.55,
    })
    high_start_step = int(duration * scenario_cfg.get("high_start_ratio", 0.55))

    append_log_record({
        "step": None,
        "event": "loop_init",
        "details": f"HILS simulation started: duration={duration}, speed={speed:.2f}s",
    })

    # Main Simulation Loop
    for t in range(duration):
        if not st.session_state.running:
            break

        # ========== STEP 1: HILS Simulation ==========
        try:
            ess, pv, load = hils.step(t)
        except Exception as e:
            append_log_record({
                "step": t,
                "event": "error",
                "details": f"HILS error: {e}",
            })
            break
        
        st.session_state.ess_data.append(ess)
        st.session_state.pv_data.append(pv)
        st.session_state.load_data.append(load)

        # Calculate Price (Scenario-based)
        price = (scenario_cfg.get("price_low", 100) if t < high_start_step 
                else scenario_cfg.get("price_high", 160))
        
        # ========== STEP 2: Update MCP Context ==========
        mcp.update_context({
            'time': t,
            'ess_level': ess,
            'pv_output': pv,
            'load': load,
            'price': price
        })

        # ========== STEP 3: Execute Multi-AI Agent Collaboration ==========
        task_sequence = "Orchestrator; Forecast; Optimize; Schedule; Fault; HILS; Explain"
        results = mcp.orchestrate(task_sequence, agents)
        
        # Collect Alerts
        alerts = []
        for key, info in results.items():
            if info.get('status') in ("alert", "error"):
                alerts.append(key.replace('_', ' ').title())

        st.session_state.agent_status = results
        
        # Track Agent Decisions (for Hybrid AI + Collaboration Visualization)
        if 'agent_decisions' not in st.session_state:
            st.session_state.agent_decisions = {}
        if 'agent_calls' not in st.session_state:
            st.session_state.agent_calls = {}
        if 'mcp_history' not in st.session_state:
            st.session_state.mcp_history = []
        
        for key, info in results.items():
            agent_name = key.replace('_', ' ').title()
            decision = info.get('message', '')
            
            # Add Decision History
            if agent_name not in st.session_state.agent_decisions:
                st.session_state.agent_decisions[agent_name] = []
            st.session_state.agent_decisions[agent_name].append(decision)
            
            # Increment Call Count
            st.session_state.agent_calls[agent_name] = st.session_state.agent_calls.get(agent_name, 0) + 1
        
        # Add MCP History
        st.session_state.mcp_history.append({
            'step': t,
            'ess_level': ess,
            'pv_output': pv,
            'load': load,
            'price': price,
        })

        # Record Logs
        details = "; ".join(
            f"{key}: {info.get('message', '')}" for key, info in results.items()
        )
        if len(details) > 220:
            details = details[:217] + "..."

        append_log_record({
            'step': t,
            'event': 'tick',
            'ess': ess,
            'pv': pv,
            'load': load,
            'price': price,
            'details': details,
            'alerts': ", ".join(alerts) if alerts else None,
        })

        # Speed Control
        speed = st.session_state.get('speed', speed)
        time.sleep(speed)

    # Simulation Complete
    st.session_state.running = False
    st.session_state.thread_started = False
    append_log_record({
        'step': None,
        'event': 'complete',
        'details': 'HILS simulation completed',
    })


# ====================================================================================
# Sidebar (Simulation Control)
# ====================================================================================
with st.sidebar:
    st.header("⚙️ Simulation Control")
    st.caption("HILS Simulator Settings and Multi-Agent Collaboration Control")
    
    # Scenario Selection
    scenario_name = st.selectbox(
        "Select Scenario", 
        list(SCENARIOS.keys()), 
        index=0,
        help="Choose energy market scenario to simulate"
    )
    
    # Price Flip Point
    price_flip = st.slider(
        "Price Flip Point (Ratio)", 
        0.2, 0.8, 
        float(SCENARIOS[scenario_name]["high_start_ratio"]),
        help="Point where price switches from low to high"
    )
    
    # Duration
    duration = st.slider(
        "Duration (Steps)", 
        5, 60, 
        st.session_state.get('duration', 20),
        help="Total simulation time steps"
    )
    
    # Update Speed
    speed = st.slider(
        "Update Interval (Seconds)", 
        0.2, 2.0, 
        st.session_state.get('speed', 0.8),
        help="Delay between each step"
    )
    
    # Reproducibility Option
    fix_seed = st.checkbox(
        "Fix Seed (Reproducibility)",
        value=False,
        help="Reproduce identical simulation results"
    )
    
    # Update Session State
    st.session_state.scenario_config = {
        **SCENARIOS[scenario_name],
        "high_start_ratio": price_flip,
    }
    st.session_state.duration = duration
    st.session_state.speed = speed
    st.session_state.fix_seed = fix_seed
    
    st.divider()
    
    # Control Buttons
    col1, col2 = st.columns(2)
    with col1:
        start_clicked = st.button("▶️ Start", use_container_width=True, type="primary")
    with col2:
        stop_clicked = st.button("⏹️ Stop", use_container_width=True)
    
    if start_clicked and not st.session_state.running:
        st.session_state.running = True
        clear_simulation_data()
        append_log_record({
            "step": None,
            "event": "start",
            "details": f"Simulation started: {scenario_name}",
        })
        st.rerun()
    
    if stop_clicked:
        st.session_state.running = False
        append_log_record({
            "step": None,
            "event": "stop",
            "details": "Simulation stopped by user",
        })
    
    # System Information
    st.divider()
    st.markdown("### 📊 System Info")
    st.caption(f"**Agents**: 6 (Hybrid AI)")
    st.caption(f"**HILS**: Closed-loop simulation")
    st.caption(f"**MCP**: Context-based orchestration")


# ====================================================================================
# Main Screen (2-Column Layout)
# ====================================================================================
left_col, right_col = st.columns([1.6, 1])

# -------------------- Left: HILS Simulation Graph --------------------
with left_col:
    st.subheader("📈 HILS Energy Simulation")
    
    # Current Metrics
    ess_val, pv_val, load_val, price_val = latest_metrics()
    render_metrics(ess_val, pv_val, load_val, price_val)
    
    st.caption(f"**Selected Scenario**: {scenario_name}")
    
    # Simulation Chart
    chart_placeholder = st.empty()
    
    # Final Results
    result_placeholder = st.container()

# -------------------- Right Top: Agent Status --------------------
with right_col:
    st.subheader("🤖 Multi-AI Agent Status")
    status_placeholder = st.container()
    
    st.divider()
    
    # Right Bottom: Real-time Logs
    st.subheader("📋 Real-time Logs")
    log_placeholder = st.container()


# ====================================================================================
# Simulation Execution (Background Thread)
# ====================================================================================
if st.session_state.running and not st.session_state.thread_started:
    worker = threading.Thread(target=run_simulation_loop, daemon=True)
    if add_script_run_ctx:
        add_script_run_ctx(worker)
    worker.start()
    st.session_state.thread_started = True


# ====================================================================================
# UI Update (Chart + Agent Status + Logs)
# ====================================================================================
# Render Chart
if st.session_state.ess_data:
    with chart_placeholder:
        render_energy_chart(
            st.session_state.ess_data,
            st.session_state.pv_data,
            st.session_state.load_data
        )

# Render Agent Status
if st.session_state.agent_status:
    with status_placeholder:
        render_agent_status_cards(st.session_state.agent_status)

# Render Logs
if st.session_state.logs:
    with log_placeholder:
        render_live_logs(st.session_state.logs, st.session_state.log_records)

# Render Final Results
if (not st.session_state.running) and st.session_state.ess_data:
    final_ess = st.session_state.ess_data[-1]
    final_pv = st.session_state.pv_data[-1]
    final_load = st.session_state.load_data[-1]
    
    with result_placeholder:
        render_final_results(final_ess, final_pv, final_load)


# ====================================================================================
# Auto Refresh (During Simulation)
# ====================================================================================
if st.session_state.running:
    delay = min(1.0, max(0.2, st.session_state.get("speed", 0.8)))
    time.sleep(delay)
    st.rerun()


# ====================================================================================
# Bottom: Hybrid AI + Multi-Agent Collaboration Demo
# ====================================================================================
st.divider()
st.markdown("## 🧪 Hybrid AI + Multi-Agent Collaboration Demo")

demo_tab1, demo_tab2, demo_tab3 = st.tabs([
    "🧠 Hybrid AI Architecture", 
    "🔗 Agent Collaboration", 
    "📡 MCP Context Flow"
])

with demo_tab1:
    # Hybrid AI Architecture Visualization
    render_hybrid_ai_architecture()
    
    # Compare AI Types and Recent Decisions by Agent
    if st.session_state.agent_status:
        latest_decisions = {
            k.replace('_', ' ').title(): v.get('message', '') 
            for k, v in st.session_state.agent_status.items()
        }
        render_decision_comparison_table(latest_decisions)
        
        st.divider()
        
        # Hybrid AI Insights Panel
        ctx = {
            'ess_level': st.session_state.ess_data[-1] if st.session_state.ess_data else 0,
            'pv_output': st.session_state.pv_data[-1] if st.session_state.pv_data else 0,
            'load': st.session_state.load_data[-1] if st.session_state.load_data else 0,
        }
        render_hybrid_ai_insights(ctx, latest_decisions)

with demo_tab2:
    # Multi-Agent Collaboration Timeline
    if hasattr(st.session_state, 'agent_decisions'):
        render_agent_collaboration_graph(st.session_state.agent_decisions)
    
    st.divider()
    
    # Agent Activity Distribution
    if hasattr(st.session_state, 'agent_calls'):
        render_collaboration_metrics(st.session_state.agent_calls)

with demo_tab3:
    # MCP Context Server Data Flow
    if hasattr(st.session_state, 'mcp_history'):
        render_mcp_context_flow(st.session_state.mcp_history)
    
    st.divider()
    
    st.markdown("### 💡 MCP Runtime Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Context Server Role**
        - Central data repository shared by all agents
        - Real-time HILS simulation state updates
        - Platform for inter-agent information exchange
        """)
    
    with col2:
        st.markdown("""
        **Orchestration Capabilities**
        - Task-based agent execution order control
        - Context-based decision support
        - Agent result aggregation and delivery
        """)


# ====================================================================================
# Bottom: System Information
# ====================================================================================
st.divider()
with st.expander("ℹ️ System Architecture Information"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**HILS Simulator**")
        st.caption("- ESS/PV/Load modeling")
        st.caption("- Closed-loop feedback")
        st.caption("- Real-time state generation")
    
    with col2:
        st.markdown("**MCP Runtime**")
        st.caption("- Context server")
        st.caption("- Agent orchestration")
        st.caption("- State sharing platform")
    
    with col3:
        st.markdown("**Hybrid AI Agents**")
        st.caption("- ML: MILP optimization")
        st.caption("- Rule: Scheduling/Detection")
        st.caption("- LLM-like: Strategic analysis")
