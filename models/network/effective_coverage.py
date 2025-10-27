"""
models/network/effective_coverage.py

Effective coverage calculations for UV network.
Implements Equations 10-17, 28-29 from the paper.

Simple explanation:
- When you place multiple devices, their coverage overlaps
- Effective coverage = total covered area (not counting overlaps twice)
- Like drawing circles on paper - count the total shaded area once
"""

import numpy as np
import sys
import os
from typing import List, Tuple, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.geometry import GeometryUtils


class EffectiveCoverageCalculator:
    """
    Calculate effective coverage for UV networks.
    Handles overlapping coverage from multiple nodes.
    
    Simple explanation:
    - Multiple devices = overlapping circles
    - Effective coverage = union of all circles (total area covered)
    - Don't count overlapping parts multiple times
    """
    
    # Coverage efficiency from Equation 28
    ETA_EFF = 0.5545  # 55.45% - maximum effective coverage ratio
    
    @staticmethod
    def calculate_overlap_area_two_circles(r1: float, r2: float, d: float) -> float:
        """
        Calculate overlap area between two circles
        
        Simple explanation:
        - Two circles overlap like a Venn diagram
        - Calculate the lens-shaped area in the middle
        
        Args:
            r1: Radius of first circle
            r2: Radius of second circle  
            d: Distance between circle centers
            
        Returns:
            Overlap area (square meters)
        """
        # No overlap if circles too far apart
        if d >= r1 + r2:
            return 0.0
        
        # One circle completely inside the other
        if d <= abs(r1 - r2):
            return np.pi * min(r1, r2) ** 2
        
        # Partial overlap - use lens formula
        # Area = r1²*arccos((d²+r1²-r2²)/(2dr1)) + r2²*arccos((d²+r2²-r1²)/(2dr2)) 
        #        - 0.5*sqrt((r1+r2-d)(d+r1-r2)(d-r1+r2)(d+r1+r2))
        
        part1 = r1**2 * np.arccos((d**2 + r1**2 - r2**2) / (2 * d * r1))
        part2 = r2**2 * np.arccos((d**2 + r2**2 - r1**2) / (2 * d * r2))
        part3 = 0.5 * np.sqrt((r1 + r2 - d) * (d + r1 - r2) * 
                              (d - r1 + r2) * (d + r1 + r2))
        
        overlap = part1 + part2 - part3
        return overlap
    
    @staticmethod
    def calculate_S1(l: float) -> float:
        """
        Calculate S1 area (corner region in 4-node network) - Equation 14
        
        Simple explanation:
        - S1 is the uncovered corner area in a square network
        - Square area minus circular coverage at corner
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            S1 area (square meters)
        """
        # Equation 14: S1 = l² - (1/4)πl²
        S1 = l**2 - 0.25 * np.pi * l**2
        return S1
    
    @staticmethod
    def calculate_S2(l: float) -> float:
        """
        Calculate S2 area (edge overlap region) - Equation 12
        
        Simple explanation:
        - S2 is a small overlap region between adjacent nodes
        - Shaped like a lens (intersection of two circles)
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            S2 area (square meters)
        """
        # Equation 12: S2 = (1 - π/6 - √3/4) × l²
        S2 = (1 - np.pi/6 - np.sqrt(3)/4) * l**2
        return S2
    
    @staticmethod
    def calculate_four_node_effective_coverage(l: float) -> float:
        """
        Calculate effective coverage for 4-node square network (Equation 15)
        
        Simple explanation:
        - 4 nodes arranged in a square (like corners of a square)
        - Side length = 3l (from Figure 8)
        - Total coverage = square area - uncovered corners - overlaps
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            Effective coverage area S_4-eff (square meters)
        """
        # Equation 10 & 15: S_4-eff = S_EFGH - 4S1 - 4S2
        
        # Square area with side length 3l (Equation 11)
        S_EFGH = (3 * l) ** 2  # = 9l²
        
        # Corner regions
        S1 = EffectiveCoverageCalculator.calculate_S1(l)
        
        # Edge overlap regions
        S2 = EffectiveCoverageCalculator.calculate_S2(l)
        
        # Total effective coverage
        S_4_eff = S_EFGH - 4 * S1 - 4 * S2
        
        return S_4_eff
    
    @staticmethod
    def calculate_single_node_effective_coverage(l: float) -> float:
        """
        Calculate effective coverage added by single node (Equation 17)
        
        Simple explanation:
        - When you add one more node to a network
        - How much NEW area does it cover?
        - (Not counting areas already covered by other nodes)
        
        Args:
            l: Communication distance (meters)
            
        Returns:
            Single node effective coverage S_eff (square meters)
        """
        # Equation 16: Sector area S_PQCB = (1/2)πl²
        S_PQCB = 0.5 * np.pi * l**2
        
        S1 = EffectiveCoverageCalculator.calculate_S1(l)
        S2 = EffectiveCoverageCalculator.calculate_S2(l)
        
        # Equation 17: S_eff = S_PQCB + (S1 - S2)
        S_eff = S_PQCB + (S1 - S2)
        
        return S_eff
    
    @staticmethod
    def calculate_coverage_efficiency() -> float:
        """
        Calculate coverage efficiency η_eff (Equation 28)
        
        Simple explanation:
        - What fraction of a node's coverage is "useful"?
        - 55.45% is useful, rest is overlap with neighbors
        
        Returns:
            η_eff = 0.5545 (55.45%)
        """
        # Equation 28: η_eff = S_eff / S_node = 55.45%
        return EffectiveCoverageCalculator.ETA_EFF
    
    @staticmethod
    def calculate_minimum_nodes(S_ROI: float, l: float) -> int:
        """
        Calculate minimum nodes for complete coverage (Equation 29)
        
        Simple explanation:
        - "I need to cover this big area"
        - "Each node covers this much useful area"
        - "How many nodes minimum?"
        
        Args:
            S_ROI: Region of interest area (square meters)
            l: Communication distance per node (meters)
            
        Returns:
            Minimum number of nodes needed
        """
        # Single node coverage (circular)
        S_node = np.pi * l**2
        
        # Effective coverage per node
        S_eff = EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l)
        
        # Equation 29: n_min = S_ROI / S_eff = S_ROI / (η_eff × S_node)
        n_min = S_ROI / S_eff
        
        # Round up (can't have partial nodes)
        return int(np.ceil(n_min))
    
    @staticmethod
    def get_coverage_summary(l: float, S_ROI: float = 1e6) -> Dict:
        """
        Get complete coverage summary
        
        Args:
            l: Communication distance (meters)
            S_ROI: Region of interest area (default: 1e6 m² = 1 km²)
            
        Returns:
            Dictionary with all coverage metrics
        """
        # Basic calculations
        S_node = np.pi * l**2
        S1 = EffectiveCoverageCalculator.calculate_S1(l)
        S2 = EffectiveCoverageCalculator.calculate_S2(l)
        S_4_eff = EffectiveCoverageCalculator.calculate_four_node_effective_coverage(l)
        S_eff = EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l)
        n_min = EffectiveCoverageCalculator.calculate_minimum_nodes(S_ROI, l)
        
        return {
            'communication_distance': l,
            'single_node_coverage': S_node,
            'overlap_regions': {
                'S1_corner': S1,
                'S2_edge': S2
            },
            'four_node_network': {
                'effective_coverage': S_4_eff,
                'network_side_length': 3 * l
            },
            'single_node_effective': S_eff,
            'coverage_efficiency': EffectiveCoverageCalculator.ETA_EFF,
            'minimum_nodes': {
                'S_ROI': S_ROI,
                'n_min': n_min,
                'actual_coverage': n_min * S_eff
            }
        }


if __name__ == "__main__":
    print("Effective Coverage Calculator Test")
    print("=" * 70)
    
    # Test with experimental distance (75.1m)
    l_exp = 75.1
    
    print(f"\nExperimental Parameters (l = {l_exp}m):")
    print("-" * 70)
    
    summary = EffectiveCoverageCalculator.get_coverage_summary(l_exp)
    
    print(f"Communication Distance: {summary['communication_distance']} m")
    print(f"\nSingle Node:")
    print(f"  Coverage area: {summary['single_node_coverage']:.2f} m²")
    print(f"  Coverage radius: {l_exp} m")
    
    print(f"\nOverlap Regions:")
    print(f"  S1 (corner): {summary['overlap_regions']['S1_corner']:.2f} m²")
    print(f"  S2 (edge): {summary['overlap_regions']['S2_edge']:.2f} m²")
    
    print(f"\nFour-Node Network:")
    print(f"  Side length: {summary['four_node_network']['network_side_length']:.1f} m")
    print(f"  Effective coverage: {summary['four_node_network']['effective_coverage']:.2f} m²")
    print(f"  Measured (paper): 44,800 m²")
    print(f"  Error: {abs(summary['four_node_network']['effective_coverage'] - 44800) / 44800 * 100:.1f}%")
    
    print(f"\nSingle Node Effective Coverage:")
    print(f"  S_eff: {summary['single_node_effective']: .2f} m²")
    print(f"  Efficiency η_eff: {summary['coverage_efficiency'] * 100:.2f}%")
    
    print(f"\nMinimum Nodes (for 1 km² area):")
    print(f"  ROI area: {summary['minimum_nodes']['S_ROI']:.2e} m²")
    print(f"  Minimum nodes: {summary['minimum_nodes']['n_min']}")
    print(f"  Actual coverage: {summary['minimum_nodes']['actual_coverage']:.2e} m²")
    
    # Test different distances
    print("\n\nCoverage vs Distance:")
    print("-" * 70)
    print(f"{'Distance (m)':<15} {'4-Node (m²)':<20} {'Single Eff (m²)':<20} {'Min Nodes (1km²)'}")
    print("-" * 70)
    
    for l in [50, 75, 100, 150]:
        summary = EffectiveCoverageCalculator.get_coverage_summary(l)
        print(f"{l:<15} "
              f"{summary['four_node_network']['effective_coverage']:<20.0f} "
              f"{summary['single_node_effective']:<20.0f} "
              f"{summary['minimum_nodes']['n_min']}")
    
    # Validate Equation 28
    print("\n\nValidation of Equation 28 (Coverage Efficiency):")
    print("-" * 70)
    
    l_test = 100
    S_node = np.pi * l_test**2
    S_eff = EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l_test)
    eta_calculated = S_eff / S_node
    eta_expected = EffectiveCoverageCalculator.ETA_EFF
    
    print(f"Distance: {l_test} m")
    print(f"S_node (πl²): {S_node:.2f} m²")
    print(f"S_eff: {S_eff:.2f} m²")
    print(f"η_eff calculated: {eta_calculated:.4f} ({eta_calculated * 100:.2f}%)")
    print(f"η_eff expected: {eta_expected:.4f} ({eta_expected * 100:.2f}%)")
    print(f"Match: {'✓ YES' if abs(eta_calculated - eta_expected) < 0.001 else '✗ NO'}")