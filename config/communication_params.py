# UV COMMUNICATION PARAMETERS (TABLE 1) - Communication parameters for UV NLOS network. Configurable ranges and default values based on the paper.

import numpy as np
from typing import Dict, Tuple, List

class CommunicationParams:
    """Communication parameters for UV network"""
    
    # Transmission Power (Pt) - Section V experimental: 0.5W per side
    PT_MIN = 0.1          # W (minimum transmission power)
    PT_MAX = 0.5          # W (maximum for safety)
    PT_DEFAULT = 0.5      # W (paper's experimental value)
    PT_STEP = 0.05        # W (for parameter sweeps)
    
    # Data Rate (Rd) - From Figs 13-14 and Section IV
    RD_MIN = 10e3         # bps (10 kbps)
    RD_MAX = 120e3        # bps (120 kbps)
    RD_DEFAULT = 50e3     # bps (50 kbps, common test value)
    RD_STEP = 10e3        # bps (for parameter sweeps)
    
    # Beam Divergence Angle (Φ₁) - Section IV-A-1
    PHI1_MIN = 5          # degrees (minimum beam divergence)
    PHI1_MAX = 20         # degrees (maximum, paper limit)
    PHI1_DEFAULT = 15     # degrees (common test value)
    PHI1_STEP = 1         # degrees
    
    # Transmission Elevation Angle (θ₁) - Fig. 5 and Section IV
    THETA1_OPTIONS = [30, 40, 50]  # degrees (analyzed in paper)
    THETA1_DEFAULT = 30            # degrees (best performance)
    THETA1_MIN = 30                # degrees (NLOS requirement)
    THETA1_MAX = 50                # degrees (paper's range)
    
    # Reception Elevation Angle (θ₂) - Fig. 5 and Section IV
    THETA2_OPTIONS = [30, 50]      # degrees (analyzed in paper)
    THETA2_DEFAULT = 50            # degrees (common configuration)
    THETA2_MIN = 30                # degrees
    THETA2_MAX = 50                # degrees
    
    # Transceiver Elevation Combinations (analyzed in paper)
    ELEVATION_COMBINATIONS = [
        (30, 30),  # Best coverage
        (30, 50),  # Experimental setup (Section V)
        (50, 30),  # Alternative
        (50, 50)   # Most stringent
    ]
    
    @classmethod
    def get_pt_range(cls) -> np.ndarray:
        """Get transmission power range for sweeps"""
        return np.arange(cls.PT_MIN, cls.PT_MAX + cls.PT_STEP, cls.PT_STEP)
    
    @classmethod
    def get_rd_range(cls) -> np.ndarray:
        """Get data rate range for sweeps"""
        return np.arange(cls.RD_MIN, cls.RD_MAX + cls.RD_STEP, cls.RD_STEP)
    
    @classmethod
    def get_phi1_range(cls) -> np.ndarray:
        """Get beam divergence angle range for sweeps"""
        return np.arange(cls.PHI1_MIN, cls.PHI1_MAX + cls.PHI1_STEP, cls.PHI1_STEP)
    
    @classmethod
    def get_default_params(cls) -> Dict:
        """Get default communication parameters"""
        return {
            'Pt': cls.PT_DEFAULT,
            'Rd': cls.RD_DEFAULT,
            'phi1': cls.PHI1_DEFAULT,
            'theta1': cls.THETA1_DEFAULT,
            'theta2': cls.THETA2_DEFAULT
        }
    
    @classmethod
    def validate_params(cls, Pt: float, Rd: float, phi1: float, 
                       theta1: float, theta2: float) -> Tuple[bool, str]:
        """
        Validate communication parameters
        
        Args:
            Pt: Transmission power (W)
            Rd: Data rate (bps)
            phi1: Beam divergence angle (degrees)
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            
        Returns:
            (valid, message): Validation result and message
        """
        if not cls.PT_MIN <= Pt <= cls.PT_MAX:
            return False, f"Pt must be in [{cls.PT_MIN}, {cls.PT_MAX}] W"
        
        if not cls.RD_MIN <= Rd <= cls.RD_MAX:
            return False, f"Rd must be in [{cls.RD_MIN}, {cls.RD_MAX}] bps"
        
        if not cls.PHI1_MIN <= phi1 <= cls.PHI1_MAX:
            return False, f"phi1 must be in [{cls.PHI1_MIN}, {cls.PHI1_MAX}] degrees"
        
        if not cls.THETA1_MIN <= theta1 <= cls.THETA1_MAX:
            return False, f"theta1 must be in [{cls.THETA1_MIN}, {cls.THETA1_MAX}] degrees"
        
        if not cls.THETA2_MIN <= theta2 <= cls.THETA2_MAX:
            return False, f"theta2 must be in [{cls.THETA2_MIN}, {cls.THETA2_MAX}] degrees"
        
        return True, "Parameters valid"
    
    @classmethod
    def get_summary(cls) -> Dict:
        """Return summary of communication parameters"""
        return {
            'Transmission Power (Pt)': f"{cls.PT_MIN}-{cls.PT_MAX} W",
            'Data Rate (Rd)': f"{cls.RD_MIN/1e3}-{cls.RD_MAX/1e3} kbps",
            'Beam Divergence (Φ₁)': f"{cls.PHI1_MIN}-{cls.PHI1_MAX}°",
            'Tx Elevation (θ₁)': f"{cls.THETA1_MIN}-{cls.THETA1_MAX}°",
            'Rx Elevation (θ₂)': f"{cls.THETA2_MIN}-{cls.THETA2_MAX}°",
            'Elevation Combinations': cls.ELEVATION_COMBINATIONS
        }


if __name__ == "__main__":
    # Display parameters
    print("UV Network Communication Parameters")
    print("=" * 50)
    for key, value in CommunicationParams.get_summary().items():
        print(f"{key:30s}: {value}")
    
    print("\nDefault Parameters:")
    for key, value in CommunicationParams.get_default_params().items():
        print(f"{key:30s}: {value}")