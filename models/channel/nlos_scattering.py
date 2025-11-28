"""
models/channel/nlos_scattering.py

NLOS (Non-Line-of-Sight) communication modes for UV networks.
Implements three modes from Figure 2 of the paper:
- NLOS-a: Vertical transmission and vertical reception (circular coverage)
- NLOS-b: Non-vertical transmission and vertical reception
- NLOS-c: Non-vertical transmission and non-vertical reception (best performance)
"""

import numpy as np
from typing import Tuple, Dict
from enum import Enum


class NLOSMode(Enum):
    """Three NLOS communication modes"""
    NLOS_A = "nlos_a"  # Vertical-Vertical (circular coverage)
    NLOS_B = "nlos_b"  # Non-vertical-Vertical
    NLOS_C = "nlos_c"  # Non-vertical-Non-vertical (directional, best performance)


class NLOSScatteringModel:
    """
    NLOS scattering model for UV communication.
    
    Simple explanation:
    - UV light bounces off air particles to reach the receiver
    - Different angles give different coverage shapes
    - NLOS-c mode: directional (like a flashlight cone)
    - NLOS-a mode: omnidirectional (like a light bulb)
    """
    
    @staticmethod
    def get_mode_characteristics(mode: NLOSMode, theta1: float, theta2: float) -> Dict:
        if mode == NLOSMode.NLOS_A:
            # Vertical transmission and reception
            # Coverage is circular (symmetric in all directions)
            return {
                'mode': 'NLOS-a',
                'transmission': 'vertical',
                'reception': 'vertical',
                'coverage_shape': 'circular',
                'directional': False,
                'description': 'Omnidirectional coverage, equal forward/backward scattering',
                'theta1_range': [90],
                'theta2_range': [90],
                'performance': 'Medium bandwidth, medium delay'
            }
        
        elif mode == NLOSMode.NLOS_B:
            # Non-vertical transmission, vertical reception
            # Coverage is somewhat directional
            return {
                'mode': 'NLOS-b',
                'transmission': 'non-vertical',
                'reception': 'vertical',
                'coverage_shape': 'directional',
                'directional': True,
                'description': 'Omnidirectional reception, directional transmission',
                'theta1_range': [30, 50],
                'theta2_range': [90],
                'performance': 'Good bandwidth, lower delay than NLOS-a'
            }
        
        elif mode == NLOSMode.NLOS_C:
            # Non-vertical transmission and reception
            # Most directional, best performance
            return {
                'mode': 'NLOS-c',
                'transmission': 'non-vertical',
                'reception': 'non-vertical',
                'coverage_shape': 'highly_directional',
                'directional': True,
                'description': 'Best performance: large bandwidth, small delay, strong directionality',
                'theta1_range': [30, 50],
                'theta2_range': [30, 50],
                'performance': 'Best: Large bandwidth, smallest delay'
            }
        
        else:
            raise ValueError(f"Unknown NLOS mode: {mode}")
    
    @staticmethod
    def determine_mode(theta1: float, theta2: float) -> NLOSMode:

        # Vertical means 90 degrees
        is_theta1_vertical = abs(theta1 - 90) < 5
        is_theta2_vertical = abs(theta2 - 90) < 5
        
        if is_theta1_vertical and is_theta2_vertical:
            return NLOSMode.NLOS_A
        elif not is_theta1_vertical and is_theta2_vertical:
            return NLOSMode.NLOS_B
        elif not is_theta1_vertical and not is_theta2_vertical:
            return NLOSMode.NLOS_C
        else:
            # Default to NLOS-b
            return NLOSMode.NLOS_B
    
    @staticmethod
    def calculate_scattering_efficiency(theta1: float, theta2: float, mode: NLOSMode) -> float:
        
        theta1_rad = np.radians(theta1)
        theta2_rad = np.radians(theta2)
        
        # Calculate directivity factor based on mode
        if mode == NLOSMode.NLOS_A:
            # Vertical (90°): omnidirectional scattering
            # Energy spreads equally in all directions (4π steradians)
            # Very low directivity
            directivity = 0.25  # 1/(4π) normalized
            
        elif mode == NLOSMode.NLOS_B:
            # Semi-directional: one angle optimized
            # Directivity improves with non-vertical transmission
            # Better forward scattering with lower theta1
            directivity = 0.5 * (1.0 - np.sin(theta1_rad))
            
        elif mode == NLOSMode.NLOS_C:
            # Highly directional: both angles optimized
            # Maximum forward scattering efficiency
            # Both angles contribute to directivity
            directivity = 0.7 * (2.0 - np.sin(theta1_rad) - np.sin(theta2_rad)) / 2.0
            
        else:
            directivity = 0.5
        
        # Calculate angle quality factor
        # Lower angles give better scattering geometry
        # This represents the scattering cross-section optimization
        avg_angle_rad = (theta1_rad + theta2_rad) / 2.0
        
        # Scattering is optimal at lower angles (better path through scattering volume)
        # Use cosine to favor lower angles: cos(0°)=1, cos(90°)=0
        angle_quality = np.cos(avg_angle_rad)
        
        # Geometric efficiency: how well transmitter and receiver are aligned
        # Uses the difference in angles - smaller difference = better alignment
        angle_difference = abs(theta1 - theta2)
        alignment_factor = 1.0 - (angle_difference / 90.0) * 0.3  # 30% penalty for max difference
        
        # Combine all factors
        # Base efficiency from directivity
        # Scaled by angle quality (scattering geometry)
        # Adjusted by alignment
        efficiency = directivity * (0.6 + 0.4 * angle_quality) * alignment_factor
        
        # # Mode-specific adjustments based on paper's performance statements
        # if mode == NLOSMode.NLOS_A:
        #     # Omnidirectional: fundamental limit due to spreading
        #     efficiency *= 0.85  # Additional penalty for omnidirectional loss
            
        # elif mode == NLOSMode.NLOS_B:
        #     # Good middle ground
        #     efficiency *= 1.0  # No additional adjustment
            
        # elif mode == NLOSMode.NLOS_C:
        #     # Best performance (from paper: "evidently better")
        #     efficiency *= 1.15  # Bonus for optimal configuration
        
        # Ensure efficiency is in valid range [0.2, 1.0]
        return np.clip(efficiency, 0.2, 1.0)
    
    @staticmethod
    def get_coverage_type(mode: NLOSMode) -> str:
        """
        Get coverage type description
        
        Returns:
            'circular', 'elliptical', or 'cone'
        """
        if mode == NLOSMode.NLOS_A:
            return 'circular'
        elif mode == NLOSMode.NLOS_B:
            return 'elliptical'
        elif mode == NLOSMode.NLOS_C:
            return 'cone'
        else:
            return 'unknown'
    
    @staticmethod
    def compare_modes(theta1: float, theta2: float) -> Dict:
        results = {}
        
        for mode in NLOSMode:
            char = NLOSScatteringModel.get_mode_characteristics(mode, theta1, theta2)
            efficiency = NLOSScatteringModel.calculate_scattering_efficiency(
                theta1, theta2, mode
            )
            
            results[mode.value] = {
                'characteristics': char,
                'scattering_efficiency': efficiency,
                'recommended': mode == NLOSMode.NLOS_C
            }
        
        return results


if __name__ == "__main__":
    print("NLOS Communication Modes")
    print("=" * 70)
    
    # Test mode determination
    print("\nMode Determination:")
    test_angles = [(90, 90), (30, 90), (30, 50)]
    
    for theta1, theta2 in test_angles:
        mode = NLOSScatteringModel.determine_mode(theta1, theta2)
        char = NLOSScatteringModel.get_mode_characteristics(mode, theta1, theta2)
        eff = NLOSScatteringModel.calculate_scattering_efficiency(theta1, theta2, mode)
        
        print(f"\nAngles {theta1}°-{theta2}°:")
        print(f"  Mode: {char['mode']}")
        print(f"  Coverage: {char['coverage_shape']}")
        print(f"  Efficiency: {eff:.2f}")
        print(f"  Performance: {char['performance']}")
    
    # Compare all modes
    print("\n\nMode Comparison for 30°-50° angles:")
    print("-" * 70)
    comparison = NLOSScatteringModel.compare_modes(30, 50)
    
    for mode_name, info in comparison.items():
        print(f"\n{mode_name.upper()}:")
        print(f"  Efficiency: {info['scattering_efficiency']:.2f}")
        print(f"  Shape: {info['characteristics']['coverage_shape']}")
        print(f"  Recommended: {'✓' if info['recommended'] else '✗'}")