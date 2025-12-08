"""MCP (Model Context Protocol) Core orchestration module.

This module provides context management and agent orchestration capabilities
for coordinating multiple AI agents in the energy management system.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class MCPCore:
    """MCP Core for context management and agent orchestration.
    
    Maintains shared context state, coordinates agent execution, and tracks
    historical data for decision-making.
    
    Attributes:
        context: Shared context dictionary containing system state and history
    """
    
    def __init__(self):
        """Initialize the MCP Core with empty context."""
        self.context: Dict[str, Any] = {
            "history": {
                "ess_level": [],
                "pv_output": [],
                "load": [],
            }
        }
        logger.info("MCP Core initialized")

    def update_context(self, data: Dict[str, Any]) -> None:
        """Update the shared context with new data.
        
        Args:
            data: Dictionary containing new state values to merge into context
        """
        try:
            self.context.update(data)
            history = self.context.setdefault("history", {
                "ess_level": [],
                "pv_output": [],
                "load": [],
            })
            
            # Update historical data
            for key in ("ess_level", "pv_output", "load"):
                if key in data:
                    history.setdefault(key, []).append(float(data[key]))
                    history[key] = history[key][-50:]  # Keep last 50 values

            # Calculate expected PV from recent history
            pv_hist = history.get("pv_output", [])
            if pv_hist:
                window = pv_hist[-5:]
                self.context["expected_pv"] = sum(window) / len(window)
                
        except Exception as e:
            logger.error(f"Error updating context: {e}")

    def orchestrate(self, task: str, agents: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Orchestrate execution of multiple agents based on task string.
        
        Args:
            task: Semicolon-separated task string (e.g., "Forecast; Optimize; Schedule")
            agents: Dictionary mapping agent names to agent instances
            
        Returns:
            Dictionary mapping agent names to their execution results
            
        Example:
            >>> results = mcp.orchestrate("Forecast; Optimize", {'forecaster': agent1, 'optimizer': agent2})
        """
        tasks = [t.strip() for t in task.split(';') if t.strip()]
        results: Dict[str, Dict[str, Any]] = {}
        
        # Simple mapping by first token (e.g., 'Forecast' -> 'forecaster')
        for t in tasks:
            key = t.lower().split()[0]
            matched = False
            
            for name, agent in agents.items():
                if name.startswith(key):
                    try:
                        output = agent.run(self.context)
                        message = str(output)
                        status = self._infer_status(name, message)
                        matched = True
                    except Exception as e:
                        logger.error(f"Agent {name} execution failed: {e}")
                        message = f"error: {e}"
                        status = "error"
                        matched = True
                    
                    results[name] = {
                        "message": message,
                        "status": status,
                    }
                    self.context[f"{name}_last"] = message
                    break
            
            if not matched:
                logger.warning(f"No agent found for task: {t}")
        
        self.context["last_results"] = results
        return results

    @staticmethod
    def _infer_status(name: str, message: str) -> str:
        """Infer status level from agent name and message content.
        
        Args:
            name: Agent name
            message: Agent output message
            
        Returns:
            Status string: "ok", "active", "alert", "error", or "info"
        """
        lower = message.lower()
        
        if any(flag in lower for flag in ("error", "anomaly", "outage", "deviation", "overshoot")):
            return "alert"
        if "discharge" in lower or "charge" in lower or "hold" in lower:
            return "active"
        if "normal" in lower or "ok" in lower:
            return "ok"
        
        return "info"
    
    def get_context(self) -> Dict[str, Any]:
        """Get the current context state.
        
        Returns:
            Copy of the current context dictionary
        """
        return self.context.copy()
    
    def clear_history(self) -> None:
        """Clear historical data from context."""
        self.context["history"] = {
            "ess_level": [],
            "pv_output": [],
            "load": [],
        }
        logger.info("Context history cleared")

