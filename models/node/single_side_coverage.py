"""
models/node/single_side_coverage.py

Single-side coverage model for UV node.
Implements Equations 3-7 from the paper (Figure 7).

Simple explanation:
- One side of the device emits UV light in a cone shape
- When projected on the ground, it makes a specific shape
- We calculate the area of this shape

"""
from typing import Dict
import numpy as np
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.geometry import GeometryUtils


class SingleSideCoverage:
    """
    Calculate coverage area for single side of UV node.
    Based on Figure 7 and Equations 3-7 from the paper.
    
    Simple explanation:
    Imagine a flashlight pointing down at an angle:
    - Light spreads out in a cone
    - On the ground, it makes a shape (like an oval)
    - We calculate how big that shape is
    """
    
    def __init__(self, theta1: float, theta2: float, phi1: float):
        """
        Initialize single-side coverage model
        
        Args:
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            phi1: Beam divergence angle (degrees) - how wide the light spreads
        """
        self.theta1 = theta1
        self.theta2 = theta2
        self.phi1 = phi1
        
        # Convert to radians for calculations
        self.theta1_rad = np.radians(theta1)
        self.theta2_rad = np.radians(theta2)
        self.phi1_rad = np.radians(phi1)
    
    def calculate_R1(self, l: float) -> float:
        """
        Calculate communication radius R1 (Equation 4)
        
        Simple explanation:
        - l is how far the signal reaches
        - R1 is the radius of coverage on the ground
        - Depends on the angle you're transmitting at
        
        IMPORTANT NOTE ON ANGLES:
        At the SAME communication distance l, different angles give different R1:
        - Smaller angles (30°) → larger R1 → larger coverage area
        - Larger angles (50°) → smaller R1 → smaller coverage area
        
        However, in practice, smaller angles also give LONGER communication distance
        (from Phase 1), so they're doubly beneficial!
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            R1: Communication radius (meters)
        """
        # Equation 4: R1 = sin(θ2) / sin(θ1 + θ2) × l
        numerator = np.sin(self.theta2_rad)
        denominator = np.sin(self.theta1_rad + self.theta2_rad)
        
        if denominator == 0:
            return l  # Edge case
            
        R1 = (numerator / denominator) * l
        return R1
    
    def calculate_geometric_parameters(self, l: float) -> Dict:
        """
        Calculate all geometric parameters from Equation 3
        
        Simple explanation:
        These are measurements of the coverage shape:
        - How far down the center
        - How wide at different points
        - Heights of different parts
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            Dictionary with all geometric parameters
        """
        R1 = self.calculate_R1(l)
        
        # From Equation 3
        params = {}
        
        # TO' - distance to center point
        params['TO_prime'] = R1 * np.cos(self.theta1_rad)
        
        # TA' - distance to edge point
        params['TA_prime'] = R1 * np.cos(self.theta1_rad + self.phi1_rad / 2)
        
        # OD = O'D' - radius of the beam at center
        params['OD'] = R1 * np.tan(self.phi1_rad / 2)
        params['O_prime_D_prime'] = params['OD']
        
        # O'A' - semi-minor axis of ellipse
        params['O_prime_A_prime'] = R1 * (
            np.cos(self.theta1_rad) - 
            np.cos(self.theta1_rad + self.phi1_rad / 2)
        )
        
        # B'D' - width at widest point
        params['B_prime_D_prime'] = 2 * R1 * np.tan(self.phi1_rad / 2)
        
        params['R1'] = R1
        
        return params
    
    def calculate_triangle_area(self, l: float) -> float:
        """
        Calculate triangular area S_B'TD' (Equation 5)
        
        Simple explanation:
        - Part of the coverage is a triangle shape
        - This calculates that triangle's area
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            Triangle area (square meters)
        """
        R1 = self.calculate_R1(l)
        
        # Equation 5: S_B'TD' = (1/2) × B'D' × TO'
        # = R1² × cos(θ1) × tan(φ1/2)
        
        area = (R1 ** 2) * np.cos(self.theta1_rad) * np.tan(self.phi1_rad / 2)
        
        return area
    
    def calculate_ellipse_area(self, l: float) -> float:
        """
        Calculate elliptical area S_⊙B'C'D'A' (Equation 6)
        
        Simple explanation:
        - Another part of the coverage is ellipse-shaped (oval)
        - This calculates that oval's area
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            Ellipse area (square meters)
        """
        R1 = self.calculate_R1(l)
        
        # Equation 6: S_⊙B'C'D'A' = π × O'D' × O'A'
        # = π × R1² × tan(φ1/2) × (cos(θ1) - cos(θ1 + φ1/2))
        
        area = np.pi * (R1 ** 2) * np.tan(self.phi1_rad / 2) * (
            np.cos(self.theta1_rad) - 
            np.cos(self.theta1_rad + self.phi1_rad / 2)
        )
        
        return area
    
    def calculate_total_coverage(self, l: float) -> float:
        """
        Calculate total single-side coverage S_TB'C'D' (Equation 7)
        
        Simple explanation:
        - Add triangle area + half of ellipse area
        - This is the total ground area covered by one side
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            Total coverage area (square meters)
        """
        # Equation 7: S_TB'C'D' = S_B'TD' + (1/2) × S_⊙B'C'D'A'
        
        triangle_area = self.calculate_triangle_area(l)
        ellipse_area = self.calculate_ellipse_area(l)
        
        total_area = triangle_area + 0.5 * ellipse_area
        
        return total_area
    
    def get_coverage_summary(self, l: float) -> Dict:
        """
        Get complete coverage summary for this side
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            Dictionary with all coverage information
        """
        params = self.calculate_geometric_parameters(l)
        
        return {
            'communication_distance': l,
            'R1': params['R1'],
            'geometric_parameters': params,
            'triangle_area': self.calculate_triangle_area(l),
            'ellipse_area': self.calculate_ellipse_area(l),
            'total_coverage': self.calculate_total_coverage(l),
            'angles': {
                'theta1': self.theta1,
                'theta2': self.theta2,
                'phi1': self.phi1
            }
        }


if __name__ == "__main__":
    print("Single-Side Coverage Model Test")
    print("=" * 70)
    
    # Test with experimental parameters (30°-50°, 15° divergence)
    coverage = SingleSideCoverage(theta1=30, theta2=50, phi1=15)
    
    # Test distances
    distances = [50, 75, 100]
    
    print(f"\nConfiguration: θ1={coverage.theta1}°, θ2={coverage.theta2}°, φ1={coverage.phi1}°\n")
    print(f"{'Distance (m)':<15} {'R1 (m)':<15} {'Triangle (m²)':<18} {'Ellipse (m²)':<18} {'Total (m²)'}")
    print("-" * 85)
    
    for l in distances:
        summary = coverage.get_coverage_summary(l)
        print(f"{l:<15} "
              f"{summary['R1']:<15.2f} "
              f"{summary['triangle_area']:<18.2f} "
              f"{summary['ellipse_area']:<18.2f} "
              f"{summary['total_coverage']:.2f}")
    
    # Detailed output for one distance
    print("\n\nDetailed Analysis for 75m distance:")
    print("-" * 70)
    summary = coverage.get_coverage_summary(75)
    
    print(f"Communication Distance: {summary['communication_distance']} m")
    print(f"Coverage Radius R1: {summary['R1']:.2f} m")
    print(f"\nGeometric Parameters:")
    for key, value in summary['geometric_parameters'].items():
        if key != 'R1':
            print(f"  {key}: {value:.2f} m")
    
    print(f"\nArea Components:")
    print(f"  Triangle area: {summary['triangle_area']:.2f} m²")
    print(f"  Ellipse area: {summary['ellipse_area']:.2f} m²")
    print(f"  Total coverage: {summary['total_coverage']:.2f} m²")
    
    # Test different elevation combinations
    print("\n\nComparison of Elevation Combinations (l=100m, φ1=15°):")
    print("-" * 70)
    print(f"{'Combination':<15} {'R1 (m)':<15} {'Coverage (m²)'}")
    print("-" * 70)
    
    combinations = [(30, 30), (30, 50), (50, 30), (50, 50)]
    for theta1, theta2 in combinations:
        cov = SingleSideCoverage(theta1, theta2, 15)
        summary = cov.get_coverage_summary(100)
        print(f"{theta1}°-{theta2}°{'':<9} "
              f"{summary['R1']:<15.2f} "
              f"{summary['total_coverage']:.2f}")