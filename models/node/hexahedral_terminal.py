"""
models/node/hexahedral_terminal.py

Hexahedral (6-sided) UV terminal model.
Based on Figure 4 from the paper.

Simple explanation:
- Device shaped like a cube
- Each of 6 faces has a transmitter and receiver
- Together they provide coverage in all directions
- Like having 6 flashlights pointing in different directions
"""

import numpy as np
import sys
import os
from typing import Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.node.single_side_coverage import SingleSideCoverage
from utils.geometry import GeometryUtils


class HexahedralTerminal:
    """
    6-sided UV communication terminal.
    
    Simple explanation:
    - Top, bottom, and 4 sides (north, south, east, west)
    - Each side has LED array (transmitter) and PMT (receiver)
    - Each side covers a specific direction
    - Together = omnidirectional coverage (all directions)
    """
    
    # Define the 6 faces and their orientations
    FACES = {
        'top': {'direction': 'up', 'azimuth': 0, 'elevation_offset': 90},
        'bottom': {'direction': 'down', 'azimuth': 180, 'elevation_offset': -90},
        'north': {'direction': 'north', 'azimuth': 0, 'elevation_offset': 0},
        'south': {'direction': 'south', 'azimuth': 180, 'elevation_offset': 0},
        'east': {'direction': 'east', 'azimuth': 90, 'elevation_offset': 0},
        'west': {'direction': 'west', 'azimuth': 270, 'elevation_offset': 0}
    }
    
    def __init__(self, 
                 theta1: float = 30,
                 theta2: float = 50,
                 phi1: float = 15,
                 power_per_side: float = 0.5,
                 position: Tuple[float, float] = (0, 0)):
        """
        Initialize hexahedral terminal
        
        Args:
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            phi1: Beam divergence angle (degrees)
            power_per_side: Transmission power per side (Watts)
            position: (x, y) position of terminal (meters)
        """
        self.theta1 = theta1
        self.theta2 = theta2
        self.phi1 = phi1
        self.power_per_side = power_per_side
        self.position = position
        
        # Create coverage model for each side
        self.side_coverage = SingleSideCoverage(theta1, theta2, phi1)
        
        # Terminal specifications (from paper Section V)
        self.specifications = {
            'led_array': '1x5 per side',
            'detector': 'PMT (Photomultiplier Tube) per side',
            'response_time': 'nanosecond level',
            'total_power': power_per_side * 6,  # 6 sides
            'transmission_mode': 'NLOS-c',
            'reception_mode': 'omnidirectional'
        }
    
    def calculate_single_side_coverage(self, l: float) -> float:
        """
        Calculate coverage area for one side
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            Coverage area (square meters)
        """
        return self.side_coverage.calculate_total_coverage(l)
    
    def calculate_omnidirectional_coverage(self, l: float) -> float:
        """
        Calculate total omnidirectional coverage (circular approximation)
        
        Simple explanation:
        - With 6 sides, device can transmit in all directions
        - For network planning, we approximate as a circle
        - Circle radius = communication distance l
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            Total coverage area (square meters)
        """
        # Circular coverage approximation (from paper assumption b)
        coverage_area = np.pi * l ** 2
        return coverage_area
    
    def calculate_directional_coverage(self, l: float, direction: str) -> Dict:
        """
        Calculate coverage for specific direction (one face)
        
        Args:
            l: Communication distance (meters)
            direction: Face direction ('north', 'south', etc.)
            
        Returns:
            Coverage information for that direction
        """
        if direction not in self.FACES:
            raise ValueError(f"Invalid direction. Must be one of: {list(self.FACES.keys())}")
        
        face_info = self.FACES[direction]
        coverage_area = self.calculate_single_side_coverage(l)
        
        return {
            'direction': direction,
            'azimuth': face_info['azimuth'],
            'coverage_area': coverage_area,
            'communication_distance': l
        }
    
    def get_all_faces_coverage(self, l: float) -> Dict:
        """
        Get coverage for all 6 faces
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            Dictionary mapping face name to coverage info
        """
        all_coverage = {}
        
        for face_name in self.FACES.keys():
            all_coverage[face_name] = self.calculate_directional_coverage(l, face_name)
        
        return all_coverage
    
    def calculate_effective_range(self, target_coverage: float) -> float:
        """
        Find required communication distance for target coverage
        
        Simple explanation:
        - "I need to cover X square meters"
        - "How far should my signal reach?"
        
        Args:
            target_coverage: Desired coverage area (square meters)
            
        Returns:
            Required communication distance (meters)
        """
        # From circular approximation: A = πl²
        # Solve for l: l = sqrt(A/π)
        required_distance = np.sqrt(target_coverage / np.pi)
        return required_distance
    
    def get_terminal_summary(self, l: float) -> Dict:
        """
        Get complete terminal summary
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            Complete terminal information
        """
        single_side = self.calculate_single_side_coverage(l)
        omni_coverage = self.calculate_omnidirectional_coverage(l)
        
        return {
            'position': self.position,
            'communication_distance': l,
            'angles': {
                'theta1': self.theta1,
                'theta2': self.theta2,
                'phi1': self.phi1
            },
            'power': {
                'per_side': self.power_per_side,
                'total': self.specifications['total_power']
            },
            'coverage': {
                'single_side_area': single_side,
                'omnidirectional_area': omni_coverage,
                'radius': l
            },
            'specifications': self.specifications,
            'number_of_faces': 6
        }
    
    def estimate_network_nodes(self, area: float, l: float, efficiency: float = 0.5545) -> int:
        """
        Estimate number of terminals needed to cover an area
        Uses Equation 29: n_min = S_ROI / (η_eff × S_node)
        
        Simple explanation:
        - "I need to cover this big area"
        - "How many devices do I need?"
        
        Args:
            area: Area to cover (square meters)
            l: Communication distance per node (meters)
            efficiency: Coverage efficiency (default: 55.45% from paper)
            
        Returns:
            Minimum number of terminals needed
        """
        single_node_coverage = self.calculate_omnidirectional_coverage(l)
        effective_coverage = efficiency * single_node_coverage
        n_min = np.ceil(area / effective_coverage)
        
        return int(n_min)


if __name__ == "__main__":
    print("Hexahedral UV Terminal Model")
    print("=" * 70)
    
    # Create terminal with experimental parameters
    terminal = HexahedralTerminal(
        theta1=30,
        theta2=50,
        phi1=15,
        power_per_side=0.5,
        position=(0, 0)
    )
    
    # Test with different distances
    print("\nTerminal Coverage vs Distance:")
    print("-" * 70)
    print(f"{'Distance (m)':<15} {'Single Side (m²)':<20} {'Omnidirectional (m²)'}")
    print("-" * 70)
    
    for l in [50, 75, 100, 150]:
        single = terminal.calculate_single_side_coverage(l)
        omni = terminal.calculate_omnidirectional_coverage(l)
        print(f"{l:<15} {single:<20.2f} {omni:.2f}")
    
    # Detailed summary for experimental distance (75.1m)
    print("\n\nExperimental Setup (Distance = 75.1m):")
    print("-" * 70)
    summary = terminal.get_terminal_summary(75.1)
    
    print(f"Position: {summary['position']}")
    print(f"Communication Distance: {summary['communication_distance']} m")
    print(f"\nAngles:")
    for key, value in summary['angles'].items():
        print(f"  {key}: {value}°")
    
    print(f"\nPower:")
    print(f"  Per side: {summary['power']['per_side']} W")
    print(f"  Total (6 sides): {summary['power']['total']} W")
    
    print(f"\nCoverage:")
    print(f"  Single side area: {summary['coverage']['single_side_area']:.2f} m²")
    print(f"  Omnidirectional area: {summary['coverage']['omnidirectional_area']:.2f} m²")
    print(f"  Coverage radius: {summary['coverage']['radius']:.2f} m")
    
    print(f"\nSpecifications:")
    for key, value in summary['specifications'].items():
        print(f"  {key}: {value}")
    
    # Calculate nodes needed for different areas
    print("\n\nNetwork Planning (with 30°-50°, distance=95m):")
    print("-" * 70)
    print(f"{'Area (m²)':<20} {'Minimum Nodes':<20} {'Note'}")
    print("-" * 70)
    
    test_areas = [
        (1e4, "Small area (100m × 100m)"),
        (1e5, "Medium area (316m × 316m)"),
        (1e6, "Large area (1km × 1km)"),
    ]
    
    for area, note in test_areas:
        n_nodes = terminal.estimate_network_nodes(area, l=95)
        print(f"{area:<20.0e} {n_nodes:<20} {note}")
    
    # Show all 6 faces coverage
    print("\n\nAll Faces Coverage (Distance = 75m):")
    print("-" * 70)
    all_faces = terminal.get_all_faces_coverage(75)
    
    print(f"{'Face':<10} {'Direction':<10} {'Azimuth':<15} {'Coverage (m²)'}")
    print("-" * 70)
    for face_name, info in all_faces.items():
        print(f"{face_name:<10} {info['direction']:<10} {info['azimuth']}°{'':<10} {info['coverage_area']:.2f}")
    
    print(f"\nTotal directional coverage: {sum(f['coverage_area'] for f in all_faces.values()):.2f} m²")
    print(f"Omnidirectional approximation: {terminal.calculate_omnidirectional_coverage(75):.2f} m²")