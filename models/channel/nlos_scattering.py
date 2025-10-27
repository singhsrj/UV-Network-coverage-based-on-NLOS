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
        """
        Get characteristics of each NLOS mode
        
        Args:
            mode: NLOS mode (a, b, or c)
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            
        Returns:
            Dictionary with mode characteristics
        """
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
        """
        Determine NLOS mode based on elevation angles
        
        Args:
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            
        Returns:
            Appropriate NLOS mode
        """
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
        """
        Calculate scattering efficiency for given angles and mode
        
        Simple explanation:
        - How well the UV light bounces off air particles
        - Better angles = more efficient scattering = longer distance
        
        Args:
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            mode: NLOS mode
            
        Returns:
            Scattering efficiency (0 to 1)
        """
        theta1_rad = np.radians(theta1)
        theta2_rad = np.radians(theta2)
        
        if mode == NLOSMode.NLOS_A:
            # Vertical mode: moderate efficiency
            efficiency = 0.5
        
        elif mode == NLOSMode.NLOS_B:
            # Forward scattering preferred
            efficiency = 0.6 * np.sin(theta1_rad)
        
        elif mode == NLOSMode.NLOS_C:
            # Best efficiency with proper alignment
            # Lower angles give better scattering
            angle_factor = (np.sin(theta1_rad) + np.sin(theta2_rad)) / 2
            efficiency = 0.7 * angle_factor
        
        else:
            efficiency = 0.5
        
        # Ensure efficiency is between 0 and 1
        return np.clip(efficiency, 0.1, 1.0)
    
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
        """
        Compare all three NLOS modes for given angles
        
        Args:
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            
        Returns:
            Comparison dictionary
        """
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