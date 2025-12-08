"""Agent modules for the Smart Energy Management System.

This module contains various AI agents for energy management and system monitoring,
including forecasting, optimization, scheduling, fault detection, and analysis agents.
"""

import random
from textwrap import shorten
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

try:
    from pulp import LpProblem, LpMinimize, LpVariable, value
except Exception:  # pragma: no cover
    LpProblem = LpMinimize = LpVariable = value = None  # graceful degrade
    logger.warning("PuLP not available. Optimizer will use heuristic fallback.")


class BaseAgent:
    """Base class for all agents in the system."""
    
    def run(self, context: Dict[str, Any]) -> str:
        """Execute the agent's logic.
        
        Args:
            context: Dictionary containing current system state
            
        Returns:
            Agent's output message
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError


class ForecasterAgent(BaseAgent):
    """Agent for forecasting future load based on current conditions.
    
    Uses a simple stochastic model to predict near-term load variations.
    """
    
    def run(self, context: Dict[str, Any]) -> str:
        """Forecast the next load value.
        
        Args:
            context: Dictionary containing current system state including 'load'
            
        Returns:
            Formatted forecast message
        """
        try:
            jitter = random.uniform(-5, 5)
            load = float(context.get('load', 0))
            next_load = max(0.0, load + jitter)
            return f"Load ~ {next_load:.1f}"
        except (ValueError, TypeError) as e:
            logger.error(f"ForecasterAgent error: {e}")
            return "Forecast unavailable"


class OptimizerAgent(BaseAgent):
    """Agent for optimizing ESS charge/discharge decisions.
    
    Uses linear programming (MILP) when available, otherwise falls back to
    simple heuristic rules based on price and demand conditions.
    """
    
    def run(self, context: Dict[str, Any]) -> str:
        """Determine optimal ESS charge/discharge action.
        
        Args:
            context: Dictionary containing 'ess_level', 'price', 'load', 'pv_output'
            
        Returns:
            Formatted optimization decision message
        """
        try:
            ess = float(context.get('ess_level', 0))
            price = float(context.get('price', 100))
            cap = max(0.0, 100.0 - ess)
            demand_gap = float(context.get('load', 0)) - float(context.get('pv_output', 0))

            if LpProblem is None:
                # fallback: simple heuristic
                amt = min(20.0, cap) if price < 120 else 0.0
                if demand_gap > 15:
                    return f"Discharge {min(15.0, ess):.1f}"
                return f"Charge {amt:.1f}"

            # LP: minimize cost of charge minus benefit of reducing net demand
            prob = LpProblem("ESSDispatch", LpMinimize)
            charge = LpVariable("charge", lowBound=0, upBound=40)
            discharge = LpVariable("discharge", lowBound=0, upBound=40)

            # objective prefers charging when cheap and discharging when expensive/high demand
            prob += price * charge - (price - 40) * discharge

            # keep SOC within bounds
            prob += charge <= cap
            prob += discharge <= ess
            # satisfy net demand request directionally
            prob += discharge - charge >= min(0, demand_gap)

            prob.solve()
            charge_amt = float(value(charge))
            discharge_amt = float(value(discharge))

            if discharge_amt > charge_amt:
                return f"Discharge {discharge_amt - charge_amt:.1f}"
            return f"Charge {charge_amt - discharge_amt:.1f}"
            
        except Exception as e:
            logger.error(f"OptimizerAgent error: {e}")
            return "Optimization failed"



class SchedulerAgent(BaseAgent):
    """Agent for scheduling ESS charge/discharge based on SOC and market conditions.
    
    Makes high-level decisions about when to charge, discharge, or hold based on
    current state of charge, PV generation, and electricity prices.
    """
    
    def run(self, context: Dict[str, Any]) -> str:
        """Determine scheduling action for ESS.
        
        Args:
            context: Dictionary containing 'ess_level', 'pv_output', 'price', 'load'
            
        Returns:
            Scheduling decision (CHARGE/DISCHARGE/HOLD)
        """
        try:
            ess = float(context.get('ess_level', 0))
            pv = float(context.get('pv_output', 0))
            price = float(context.get('price', 0))
            load = float(context.get('load', 0))
            
            if ess < 30 and pv > 20:
                return "CHARGE"
            if ess > 75 and price >= 150:
                return "DISCHARGE"
            if 35 <= ess <= 70:
                return "HOLD"
            
            trend = "CHARGE" if pv > load else "DISCHARGE"
            return f"{trend} (balancing)"
        except (ValueError, TypeError) as e:
            logger.error(f"SchedulerAgent error: {e}")
            return "HOLD (error)"


class FaultDetectionAgent(BaseAgent):
    """Agent for detecting anomalies and faults in the system.
    
    Monitors PV output and other parameters to detect outages, deviations,
    and unusual operating conditions.
    """
    
    def run(self, context: Dict[str, Any]) -> str:
        """Detect faults in the system.
        
        Args:
            context: Dictionary containing 'pv_output', 'time', 'expected_pv'
            
        Returns:
            Fault status message
        """
        try:
            pv = float(context.get('pv_output', 0))
            t = int(context.get('time', 0))
            expected = context.get('expected_pv', pv)
            
            if pv < 3 and t > 2:
                return "PV_OUTAGE"
            if expected and abs(pv - expected) > max(12.0, 0.4 * expected):
                return "PV_DEVIATION"
            if pv > 70:
                return "PV_OVERSHOOT"
            return "NORMAL"
        except (ValueError, TypeError) as e:
            logger.error(f"FaultDetectionAgent error: {e}")
            return "DETECTION_ERROR"


class OrchestratorAgent(BaseAgent):
    """Agent for coordinating multiple agents and managing system state.
    
    Acts as a high-level coordinator for agent collaboration.
    """
    
    def run(self, context: Dict[str, Any]) -> str:
        """Coordinate agent activities.
        
        Args:
            context: Dictionary containing current system state
            
        Returns:
            Coordination status
        """
        return "OK"  # placeholder for coordination state


class HILSCoachAgent(BaseAgent):
    """Agent for managing HILS simulation parameters and learning rates.
    
    Adjusts simulation mode and learning parameters based on system state.
    """
    
    def run(self, context: Dict[str, Any]) -> str:
        """Determine HILS coaching strategy.
        
        Args:
            context: Dictionary containing 'ess_level', 'price'
            
        Returns:
            Coaching recommendation message
        """
        try:
            ess = float(context.get('ess_level', 0))
            price = float(context.get('price', 0))
            mode = "Aggressive" if price < 120 else "Conservative"
            lr = '0.02' if ess < 30 else '0.01'
            return f"Mode={mode}, LR={lr}"
        except (ValueError, TypeError) as e:
            logger.error(f"HILSCoachAgent error: {e}")
            return "Mode=Default, LR=0.01"


class MockLLMAgent(BaseAgent):
    """Agent simulating LLM-based analysis and recommendations.
    
    Provides high-level strategic analysis of the current system state.
    """
    
    def run(self, context: Dict[str, Any]) -> str:
        """Generate LLM-style analysis summary.
        
        Args:
            context: Dictionary containing 'ess_level', 'pv_output', 'load', 'price'
            
        Returns:
            Analysis summary message
        """
        try:
            ess = float(context.get('ess_level', 0))
            pv = float(context.get('pv_output', 0))
            load = float(context.get('load', 0))
            price = float(context.get('price', 0))
            
            summary = (
                f"ESS {ess:.1f}% with PV {pv:.1f} vs load {load:.1f}."
                f" Price {price:.0f}."
            )
            return shorten(
                f"LLM: Balancing strategy keeps reserve while monitoring PV variability. {summary}", 
                80
            )
        except (ValueError, TypeError) as e:
            logger.error(f"MockLLMAgent error: {e}")
            return "Analysis unavailable"

