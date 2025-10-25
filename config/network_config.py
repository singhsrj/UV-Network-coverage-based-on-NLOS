"""
config/network_config.py

Network configuration parameters for UV NLOS network deployment.
Based on paper's square network analysis.
"""

import numpy as np
from typing import Dict, Tuple

class NetworkConfig:
    """Network deployment configuration"""
    
    # Region of Interest (ROI) - Section IV-B
    SROI_DEFAULT = 1.0e6        # m² (1.0 × 10⁶ m², paper's test case)
    SROI_SIDE_DEFAULT = 1000    # m (square area: 1000m × 1000m)
    
    # Node Count (n) - From Fig. 16 analysis
    N_MIN = 10                  # Minimum nodes for analysis
    N_MAX = 400                 # Maximum analyzed in paper
    N_DEFAULT = 300             # Default for connectivity tests (from Figs 17-18)
    N_STEP = 10                 # Step size for node sweeps
    
    # Four-Node Network (Section III-B-2, Fig. 8)
    FOUR_NODE_NETWORK = {
        'nodes': 4,
        'side_length_factor': 3,  # Network side = 3l
        'description': 'Basic square network for validation'
    }
    
    # Connectivity Levels (Section III-C)
    CONNECTIVITY_LEVELS = {
        1: 'One-connected (minimum)',
        2: 'Two-connected (robust baseline)',
        3: 'Three-connected (high robustness)'
    }
    
    # Connectivity Threshold - Section IV-B-1
    CONNECTIVITY_THRESHOLD = 0.90  # 90% probability (practical standard)
    
    # Coverage Efficiency (Equation 28)
    ETA_EFF = 0.5545  # 55.45% (maximum effective coverage ratio)
    
    # Deployment Pattern
    DEPLOYMENT_PATTERN = 'square'  # Paper uses square network
    
    @classmethod
    def calculate_roi_dimensions(cls, area: float) -> Tuple[float, float]:
        """
        Calculate ROI dimensions for square area
        
        Args:
            area: Area in m²
            
        Returns:
            (width, height): Dimensions in meters
        """
        side = np.sqrt(area)
        return (side, side)
    
    @classmethod
    def calculate_node_density(cls, n: int, area: float) -> float:
        """
        Calculate node density (nodes per m²)
        
        Args:
            n: Number of nodes
            area: Area in m²
            
        Returns:
            Node density (nodes/m²)
        """
        return n / area
    
    @classmethod
    def get_n_range(cls) -> np.ndarray:
        """Get node count range for sweeps"""
        return np.arange(cls.N_MIN, cls.N_MAX + cls.N_STEP, cls.N_STEP)
    
    @classmethod
    def get_default_config(cls) -> Dict:
        """Get default network configuration"""
        side = np.sqrt(cls.SROI_DEFAULT)
        return {
            'S_ROI': cls.SROI_DEFAULT,
            'ROI_width': side,
            'ROI_height': side,
            'n_nodes': cls.N_DEFAULT,
            'deployment': cls.DEPLOYMENT_PATTERN,
            'connectivity_threshold': cls.CONNECTIVITY_THRESHOLD,
            'eta_eff': cls.ETA_EFF
        }
    
    @classmethod
    def validate_network_config(cls, n: int, area: float) -> Tuple[bool, str]:
        """
        Validate network configuration
        
        Args:
            n: Number of nodes
            area: Area in m²
            
        Returns:
            (valid, message): Validation result and message
        """
        if n < cls.N_MIN:
            return False, f"Number of nodes must be >= {cls.N_MIN}"
        
        if area <= 0:
            return False, "Area must be positive"
        
        if n > cls.N_MAX:
            return True, f"Warning: Node count {n} exceeds typical range {cls.N_MAX}"
        
        return True, "Configuration valid"
    
    @classmethod
    def get_four_node_config(cls, communication_distance: float) -> Dict:
        """
        Get four-node network configuration (Fig. 8)
        
        Args:
            communication_distance: Node communication distance (m)
            
        Returns:
            Four-node network configuration
        """
        side_length = cls.FOUR_NODE_NETWORK['side_length_factor'] * communication_distance
        return {
            'nodes': cls.FOUR_NODE_NETWORK['nodes'],
            'side_length': side_length,
            'area': side_length ** 2,
            'node_positions': [
                (0, 0),
                (side_length, 0),
                (0, side_length),
                (side_length, side_length)
            ],
            'communication_distance': communication_distance
        }
    
    @classmethod
    def get_summary(cls) -> Dict:
        """Return summary of network configuration"""
        return {
            'Default ROI Area': f"{cls.SROI_DEFAULT:.2e} m²",
            'Default ROI Side': f"{cls.SROI_SIDE_DEFAULT} m",
            'Node Count Range': f"{cls.N_MIN}-{cls.N_MAX}",
            'Default Nodes': cls.N_DEFAULT,
            'Deployment Pattern': cls.DEPLOYMENT_PATTERN,
            'Connectivity Threshold': f"{cls.CONNECTIVITY_THRESHOLD * 100}%",
            'Coverage Efficiency (η_eff)': f"{cls.ETA_EFF * 100:.2f}%",
            'Four-Node Network': cls.FOUR_NODE_NETWORK
        }


if __name__ == "__main__":
    # Display network configuration
    print("UV Network Configuration")
    print("=" * 50)
    for key, value in NetworkConfig.get_summary().items():
        print(f"{key:30s}: {value}")
    
    print("\nDefault Configuration:")
    for key, value in NetworkConfig.get_default_config().items():
        print(f"{key:30s}: {value}")
    
    print("\nConnectivity Levels:")
    for level, desc in NetworkConfig.CONNECTIVITY_LEVELS.items():
        print(f"  {level}-connected: {desc}")