"""HILS (Hardware-in-the-Loop Simulation) simulator for energy systems.

This module simulates ESS, PV, and load dynamics for testing and demonstration
of energy management strategies.
"""

import math
import random
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class HILSSimulator:
    """Very simple HILS-like simulator: PV - Load -> affects ESS SOC.
    
    Simulates realistic daily patterns for PV generation and load consumption,
    with stochastic variations to represent real-world uncertainty.
    
    Attributes:
        ess: Current ESS state of charge (0-100 scale)
        time: Current simulation time step
        weather_factor: Random weather multiplier affecting PV output
        load_bias: Random load bias for consumption variations
    """
    
    def __init__(self, initial_ess: float = 58.0):
        """Initialize the HILS simulator.
        
        Args:
            initial_ess: Initial ESS state of charge (default: 58.0)
        """
        self.ess = max(0.0, min(100.0, initial_ess))
        self.time = 0
        self.weather_factor = random.uniform(0.85, 1.15)
        self.load_bias = random.uniform(-4.0, 4.0)
        logger.info(f"HILS Simulator initialized with ESS={self.ess:.1f}%")

    def step(self, t: int) -> Tuple[float, float, float]:
        """Execute one simulation step.
        
        Args:
            t: Current time step (represents hours in a daily cycle)
            
        Returns:
            Tuple of (ess_soc, pv_output, load) values
            
        Raises:
            ValueError: If time step is negative
        """
        if t < 0:
            raise ValueError(f"Time step must be non-negative, got {t}")
        
        try:
            self.time = t
            
            # Emulate a daily PV curve with random weather noise
            day_phase = (t % 24) / 24.0
            solar_profile = max(0.0, math.sin(math.pi * day_phase))
            pv = max(0.0, self.weather_factor * (18 + 35 * solar_profile + random.uniform(-6, 6)))

            # Load varies with time of day plus random shocks
            base_load = 32 + 10 * math.sin(2 * math.pi * day_phase - math.pi / 2)
            load = max(15.0, base_load + self.load_bias + random.uniform(-5, 5))

            # Net energy affects ESS SOC with dampening factor to keep within [0,100]
            net = pv - load
            self.ess = max(0.0, min(100.0, self.ess + net * 0.6))
            
            return self.ess, pv, load
            
        except Exception as e:
            logger.error(f"HILS simulation step error at t={t}: {e}")
            # Return safe fallback values
            return self.ess, 0.0, 0.0
    
    def reset(self, initial_ess: float = 58.0) -> None:
        """Reset the simulator to initial conditions.
        
        Args:
            initial_ess: Initial ESS state of charge (default: 58.0)
        """
        self.ess = max(0.0, min(100.0, initial_ess))
        self.time = 0
        self.weather_factor = random.uniform(0.85, 1.15)
        self.load_bias = random.uniform(-4.0, 4.0)
        logger.info(f"HILS Simulator reset with ESS={self.ess:.1f}%")

