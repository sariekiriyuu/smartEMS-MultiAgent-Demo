"""Unit tests for the Smart Energy Management System.

Run with: python -m pytest tests/test_system.py -v
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
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


class TestHILSSimulator:
    """Test cases for the HILS simulator."""
    
    def test_initialization(self):
        """Test simulator initialization."""
        sim = HILSSimulator(initial_ess=50.0)
        assert sim.ess == 50.0
        assert sim.time == 0
    
    def test_step_execution(self):
        """Test a single simulation step."""
        sim = HILSSimulator()
        ess, pv, load = sim.step(0)
        assert 0 <= ess <= 100
        assert pv >= 0
        assert load >= 0
    
    def test_step_with_negative_time_raises_error(self):
        """Test that negative time step raises ValueError."""
        sim = HILSSimulator()
        with pytest.raises(ValueError):
            sim.step(-1)
    
    def test_reset(self):
        """Test simulator reset functionality."""
        sim = HILSSimulator(initial_ess=80.0)
        sim.step(5)
        sim.reset(initial_ess=60.0)
        assert sim.ess == 60.0
        assert sim.time == 0


class TestMCPCore:
    """Test cases for the MCP Core."""
    
    def test_initialization(self):
        """Test MCP Core initialization."""
        mcp = MCPCore()
        assert "history" in mcp.context
        assert "ess_level" in mcp.context["history"]
    
    def test_update_context(self):
        """Test context update functionality."""
        mcp = MCPCore()
        mcp.update_context({"ess_level": 50.0, "pv_output": 30.0})
        assert mcp.context["ess_level"] == 50.0
        assert len(mcp.context["history"]["ess_level"]) == 1
    
    def test_orchestrate_agents(self):
        """Test agent orchestration."""
        mcp = MCPCore()
        agents = {
            'forecaster': ForecasterAgent(),
            'scheduler': SchedulerAgent(),
        }
        mcp.update_context({'load': 40.0, 'ess_level': 60.0, 'pv_output': 25.0, 'price': 100})
        results = mcp.orchestrate("Forecast; Schedule", agents)
        assert 'forecaster' in results
        assert 'scheduler' in results
        assert 'message' in results['forecaster']
    
    def test_clear_history(self):
        """Test history clearing."""
        mcp = MCPCore()
        mcp.update_context({"ess_level": 50.0})
        mcp.clear_history()
        assert len(mcp.context["history"]["ess_level"]) == 0


class TestAgents:
    """Test cases for energy management agents."""
    
    def test_forecaster_agent(self):
        """Test ForecasterAgent execution."""
        agent = ForecasterAgent()
        result = agent.run({'load': 40.0})
        assert 'Load' in result
        assert isinstance(result, str)
    
    def test_optimizer_agent(self):
        """Test OptimizerAgent execution."""
        agent = OptimizerAgent()
        context = {'ess_level': 50.0, 'price': 100, 'load': 40.0, 'pv_output': 20.0}
        result = agent.run(context)
        assert isinstance(result, str)
        assert ('Charge' in result or 'Discharge' in result)
    
    def test_scheduler_agent(self):
        """Test SchedulerAgent execution."""
        agent = SchedulerAgent()
        context = {'ess_level': 50.0, 'pv_output': 30.0, 'price': 100, 'load': 40.0}
        result = agent.run(context)
        assert isinstance(result, str)
        assert any(word in result for word in ['CHARGE', 'DISCHARGE', 'HOLD'])
    
    def test_fault_detection_agent_normal(self):
        """Test FaultDetectionAgent with normal conditions."""
        agent = FaultDetectionAgent()
        context = {'pv_output': 30.0, 'time': 5, 'expected_pv': 32.0}
        result = agent.run(context)
        assert isinstance(result, str)
    
    def test_fault_detection_agent_outage(self):
        """Test FaultDetectionAgent detecting outage."""
        agent = FaultDetectionAgent()
        context = {'pv_output': 1.0, 'time': 5, 'expected_pv': 30.0}
        result = agent.run(context)
        assert 'OUTAGE' in result or 'DEVIATION' in result
    
    def test_orchestrator_agent(self):
        """Test OrchestratorAgent execution."""
        agent = OrchestratorAgent()
        result = agent.run({})
        assert result == "OK"
    
    def test_hils_coach_agent(self):
        """Test HILSCoachAgent execution."""
        agent = HILSCoachAgent()
        context = {'ess_level': 25.0, 'price': 110}
        result = agent.run(context)
        assert 'Mode' in result
        assert 'LR' in result
    
    def test_mock_llm_agent(self):
        """Test MockLLMAgent execution."""
        agent = MockLLMAgent()
        context = {'ess_level': 50.0, 'pv_output': 30.0, 'load': 40.0, 'price': 120}
        result = agent.run(context)
        assert isinstance(result, str)
        assert len(result) > 0


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_full_simulation_cycle(self):
        """Test a complete simulation cycle with all components."""
        sim = HILSSimulator()
        mcp = MCPCore()
        agents = {
            'forecaster': ForecasterAgent(),
            'optimizer': OptimizerAgent(),
            'scheduler': SchedulerAgent(),
            'fault': FaultDetectionAgent(),
            'orchestrator': OrchestratorAgent(),
            'hils_coach': HILSCoachAgent(),
            'explain': MockLLMAgent(),
        }
        
        # Run a few simulation steps
        for t in range(3):
            ess, pv, load = sim.step(t)
            mcp.update_context({
                'time': t,
                'ess_level': ess,
                'pv_output': pv,
                'load': load,
                'price': 100 + t * 10
            })
            results = mcp.orchestrate(
                "Orchestrator; Forecast; Optimize; Schedule; Fault; HILS; Explain",
                agents
            )
            
            # Verify all agents executed (7 agents)
            assert len(results) == 7
            for agent_result in results.values():
                assert 'message' in agent_result
                assert 'status' in agent_result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
