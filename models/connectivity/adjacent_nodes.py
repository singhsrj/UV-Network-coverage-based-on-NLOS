"""
Adjacent nodes probability calculations.
Implements Equations 20-24 from the paper.

Simple explanation:
- For any node at position X, how likely is it to have neighbors?
- "Neighbors" = other nodes within communication range
- More neighbors = more reliable network
"""

import numpy as np
import sys
import os
from typing import Tuple, Callable, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.statistics import StatisticsUtils
from models.connectivity.probability_density import ProbabilityDensityFunction


class AdjacentNodesCalculator:
    
    @staticmethod
    def calculate_coverage_probability(node_distance: float,
                                      communication_distance: float,
                                      n: int,
                                      area: float) -> float:
        # Density of other nodes (excluding the node itself)
        density = (n - 1) / area
        
        # Coverage area
        coverage_area = np.pi * communication_distance ** 2
        
        # Simple approximation: P = density × area
        # This is valid when node is far from boundaries
        probability = density * coverage_area
        
        # Clip to [0, 1] range
        return min(probability, 1.0)
    
    @staticmethod
    def calculate_adjacent_probability_simple(tx: float, phi_x: float,
                                             l: float, n: int, area: float) -> float:
        # Calculate Cartesian position
        x = tx * np.cos(phi_x)
        y = tx * np.sin(phi_x)
        
        # For square network, check if node is well inside boundaries
        side = np.sqrt(area)
        
        # Distance to nearest boundary
        dist_to_boundary = min(x, y, side - x, side - y)
        
        # If coverage circle completely inside network
        if dist_to_boundary >= l:
            # Full circle coverage - use simple formula
            density = (n - 1) / area
            coverage = np.pi * l ** 2
            probability = density * coverage
        else:
            # Near boundary - coverage circle is truncated
            # Use reduced effective coverage area
            # (Simplified - full calculation needs integration)
            boundary_factor = max(0.5, dist_to_boundary / l)
            density = (n - 1) / area
            coverage = np.pi * l ** 2 * boundary_factor
            probability = density * coverage
        
        return min(probability, 1.0)
    
    @staticmethod
    def probability_m_adjacent_nodes(tx: float, phi_x: float, l: float,
                                    n: int, m: int, area: float) -> float:
        # Get probability that one node is adjacent
        P = AdjacentNodesCalculator.calculate_adjacent_probability_simple(
            tx, phi_x, l, n, area
        )
        
        # Use binomial distribution (Equation 23)
        prob_m = StatisticsUtils.probability_m_adjacent(n, m, P)
        
        return prob_m
    
    @staticmethod
    def probability_at_least_m_adjacent(tx: float, phi_x: float, l: float,
                                       n: int, m: int, area: float) -> float:
        # Get base probability
        P = AdjacentNodesCalculator.calculate_adjacent_probability_simple(
            tx, phi_x, l, n, area
        )
        
        # Use cumulative binomial (Equation 24)
        prob_at_least_m = StatisticsUtils.probability_at_least_m_adjacent(n, m, P)
        
        return prob_at_least_m
    
    @staticmethod
    def analyze_node_position(tx: float, phi_x: float, l: float,
                             n: int, area: float) -> Dict:
        # Convert to Cartesian
        x = tx * np.cos(phi_x)
        y = tx * np.sin(phi_x)
        
        # Base probability
        P = AdjacentNodesCalculator.calculate_adjacent_probability_simple(
            tx, phi_x, l, n, area
        )
        
        # Expected neighbors
        expected_neighbors = P * (n - 1)
        
        # Probabilities for different m values
        probs = {}
        for m in range(1, min(n, 6)):  # Calculate for m=1 to 5
            probs[f'exactly_{m}'] = AdjacentNodesCalculator.probability_m_adjacent_nodes(
                tx, phi_x, l, n, m, area
            )
            probs[f'at_least_{m}'] = AdjacentNodesCalculator.probability_at_least_m_adjacent(
                tx, phi_x, l, n, m, area
            )
        
        return {
            'position_cartesian': (x, y),
            'position_polar': (tx, phi_x),
            'base_probability': P,
            'expected_neighbors': expected_neighbors,
            'probabilities': probs
        }
    
    @staticmethod
    def find_critical_positions(l: float, n: int, area: float,
                               m: int, target_prob: float = 0.9) -> Dict:
        side = np.sqrt(area)
        
        # Test several positions
        positions = {
            'center': (side/2, 0),  # Center of network
            'near_center': (side/3, 0),
            'mid_range': (side/4, 0),
            'edge': (l, 0),  # Near edge
            'corner': (l/2, np.pi/4)  # Near corner
        }
        
        results = {}
        for name, (tx, phi_x) in positions.items():
            prob = AdjacentNodesCalculator.probability_at_least_m_adjacent(
                tx, phi_x, l, n, m, area
            )
            meets_requirement = prob >= target_prob
            results[name] = {
                'position': (tx, phi_x),
                'probability': prob,
                'meets_requirement': meets_requirement
            }
        
        return results


if __name__ == "__main__":
    print("Adjacent Nodes Calculator Test")
    print("=" * 70)
    
    # Test parameters
    n = 100  # nodes
    area = 1e6  # 1 km²
    l = 95  # communication distance
    
    print(f"\nNetwork Configuration:")
    print(f"  Nodes: {n}")
    print(f"  Area: {area:.0e} m² ({np.sqrt(area):.0f}m × {np.sqrt(area):.0f}m)")
    print(f"  Communication distance: {l} m")
    
    # Test center node
    print("\n\nNode at Center (500, 500):")
    print("-" * 70)
    
    tx_center = np.sqrt(2) * 500  # Distance from origin to center
    phi_center = np.pi / 4  # 45 degrees
    
    analysis = AdjacentNodesCalculator.analyze_node_position(
        tx_center, phi_center, l, n, area
    )
    
    print(f"Position (Cartesian): ({analysis['position_cartesian'][0]:.0f}, "
          f"{analysis['position_cartesian'][1]:.0f})")
    print(f"Expected neighbors: {analysis['expected_neighbors']:.2f}")
    print(f"\nConnectivity Probabilities:")
    print(f"  P(≥1 neighbor): {analysis['probabilities']['at_least_1']:.4f} "
          f"({analysis['probabilities']['at_least_1']*100:.2f}%)")
    print(f"  P(≥2 neighbors): {analysis['probabilities']['at_least_2']:.4f} "
          f"({analysis['probabilities']['at_least_2']*100:.2f}%)")
    print(f"  P(≥3 neighbors): {analysis['probabilities']['at_least_3']:.4f} "
          f"({analysis['probabilities']['at_least_3']*100:.2f}%)")
    
    # Test edge node
    print("\n\nNode at Edge (100, 0):")
    print("-" * 70)
    
    tx_edge = 100
    phi_edge = 0
    
    analysis_edge = AdjacentNodesCalculator.analyze_node_position(
        tx_edge, phi_edge, l, n, area
    )
    
    print(f"Position (Cartesian): ({analysis_edge['position_cartesian'][0]:.0f}, "
          f"{analysis_edge['position_cartesian'][1]:.0f})")
    print(f"Expected neighbors: {analysis_edge['expected_neighbors']:.2f}")
    print(f"\nConnectivity Probabilities:")
    print(f"  P(≥1 neighbor): {analysis_edge['probabilities']['at_least_1']:.4f}")
    print(f"  P(≥2 neighbors): {analysis_edge['probabilities']['at_least_2']:.4f}")
    print(f"  P(≥3 neighbors): {analysis_edge['probabilities']['at_least_3']:.4f}")
    
    # Compare different m-connectivity requirements
    print("\n\nm-Connectivity Probability Comparison:")
    print("-" * 70)
    print(f"{'m-connectivity':<20} {'Center Node':<20} {'Edge Node':<20} {'Difference'}")
    print("-" * 70)
    
    for m in range(1, 4):
        prob_center = analysis['probabilities'][f'at_least_{m}']
        prob_edge = analysis_edge['probabilities'][f'at_least_{m}']
        diff = prob_center - prob_edge
        
        print(f"{m}-connected{'':<12} {prob_center:<20.4f} {prob_edge:<20.4f} {diff:+.4f}")
    
    print("\n💡 Observation: Center nodes have better connectivity than edge nodes!")
    
    # Test critical positions
    print("\n\nCritical Position Analysis (2-connectivity, 90% target):")
    print("-" * 70)
    
    critical = AdjacentNodesCalculator.find_critical_positions(l, n, area, m=2, target_prob=0.9)
    
    print(f"{'Position':<15} {'Probability':<20} {'Meets 90%?'}")
    print("-" * 70)
    for name, info in critical.items():
        status = "✓ YES" if info['meets_requirement'] else "✗ NO"
        print(f"{name:<15} {info['probability']:<20.4f} {status}")