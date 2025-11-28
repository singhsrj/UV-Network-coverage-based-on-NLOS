"""
m-connectivity probability calculations.
Implements Equations 25-27 from the paper.

Simple explanation:
- m-connectivity: Every node has at least m neighbors
- 1-connected: Basic connectivity (everyone has ≥1 neighbor)
- 2-connected: Robust (everyone has ≥2 neighbors) - if one fails, still connected
- 3-connected: Very robust (everyone has ≥3 neighbors)
"""

import numpy as np
import sys
import os
from typing import Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.statistics import StatisticsUtils
from models.connectivity.adjacent_nodes import AdjacentNodesCalculator


class MConnectivityCalculator:
    @staticmethod
    def calculate_Q_n_m(l: float, n: int, m: int, area: float,
                       sample_points: int = 20) -> float:
        side = np.sqrt(area)
        
        # Sample points throughout the network
        # Use grid sampling for better coverage
        grid_size = int(np.ceil(np.sqrt(sample_points)))
        spacing = side / (grid_size + 1)
        
        probabilities = []
        
        for i in range(1, grid_size + 1):
            for j in range(1, grid_size + 1):
                # Cartesian position
                x = i * spacing
                y = j * spacing
                
                # Convert to polar
                tx = np.sqrt(x**2 + y**2)
                phi_x = np.arctan2(y, x)
                
                # Calculate probability at this position
                prob = AdjacentNodesCalculator.probability_at_least_m_adjacent(
                    tx, phi_x, l, n, m, area
                )
                
                probabilities.append(prob)
        
        # Average probability across all sampled positions
        Q_n_m = np.mean(probabilities)
        
        return Q_n_m
    
    @staticmethod
    def calculate_network_connectivity_probability(l: float, n: int, m: int,
                                                  area: float,
                                                  sample_points: int = 20) -> float:
        # Calculate Q_n,≥m (Equation 25)
        Q_n_m = MConnectivityCalculator.calculate_Q_n_m(l, n, m, area, sample_points)
        
        # Calculate network probability (Equation 27)
        # P(C is m-connected) ≈ (Q_n,≥m)^n
        network_prob = Q_n_m ** n
        
        return network_prob
    
    @staticmethod
    def analyze_connectivity_levels(l: float, n: int, area: float,
                                   max_m: int = 3) -> Dict:
        results = {}
        
        for m in range(1, max_m + 1):
            Q_n_m = MConnectivityCalculator.calculate_Q_n_m(l, n, m, area)
            prob_connected = MConnectivityCalculator.calculate_network_connectivity_probability(
                l, n, m, area
            )
            
            results[m] = {
                'Q_n_m': Q_n_m,
                'network_probability': prob_connected,
                'connectivity_level': f"{m}-connected"
            }
        
        return results
    
    @staticmethod
    def find_required_nodes(l: float, area: float, m: int,
                          target_probability: float = 0.9,
                          n_min: int = 10, n_max: int = 500,
                          tolerance: int = 5) -> Dict:
        # Binary search
        while n_max - n_min > tolerance:
            n_mid = (n_min + n_max) // 2
            
            prob = MConnectivityCalculator.calculate_network_connectivity_probability(
                l, n_mid, m, area
            )
            
            if prob < target_probability:
                n_min = n_mid
            else:
                n_max = n_mid
        
        n_required = n_max
        final_prob = MConnectivityCalculator.calculate_network_connectivity_probability(
            l, n_required, m, area
        )
        
        return {
            'required_nodes': n_required,
            'communication_distance': l,
            'connectivity_level': m,
            'target_probability': target_probability,
            'achieved_probability': final_prob,
            'area': area
        }
    
    @staticmethod
    def compare_connectivity_vs_nodes(l: float, area: float, m: int,
                                     n_range: List[int]) -> Dict:
        results = {}
        
        for n in n_range:
            prob = MConnectivityCalculator.calculate_network_connectivity_probability(
                l, n, m, area
            )
            results[n] = prob
        
        return results
    
    @staticmethod
    def connectivity_summary(l: float, n: int, area: float) -> Dict:
        side = np.sqrt(area)
        
        # Calculate for m=1, 2, 3
        connectivity_levels = MConnectivityCalculator.analyze_connectivity_levels(
            l, n, area, max_m=3
        )
        
        # Expected neighbors
        density = (n - 1) / area
        coverage = np.pi * l**2
        expected_neighbors = density * coverage
        
        return {
            'network_config': {
                'nodes': n,
                'area': area,
                'side_length': side,
                'communication_distance': l
            },
            'expected_neighbors': expected_neighbors,
            'connectivity_levels': connectivity_levels,
            'meets_90_percent': {
                1: connectivity_levels[1]['network_probability'] >= 0.9,
                2: connectivity_levels[2]['network_probability'] >= 0.9,
                3: connectivity_levels[3]['network_probability'] >= 0.9
            }
        }


if __name__ == "__main__":
    print("m-Connectivity Calculator Test")
    print("=" * 70)
    
    # Test parameters
    l = 95  # communication distance
    n = 100  # nodes
    area = 1e6  # 1 km²
    
    print(f"\nNetwork Configuration:")
    print(f"  Communication distance: {l} m")
    print(f"  Number of nodes: {n}")
    print(f"  Area: {area:.0e} m² ({np.sqrt(area):.0f}m × {np.sqrt(area):.0f}m)")
    
    # Test Q_n,≥m calculation
    print("\n\nQ_n,≥m Calculation (Equation 25):")
    print("-" * 70)
    print(f"Q_n,≥m = Probability that arbitrary node has ≥m neighbors\n")
    
    for m in range(1, 4):
        Q_n_m = MConnectivityCalculator.calculate_Q_n_m(l, n, m, area)
        print(f"Q_n,≥{m}(l={l}m): {Q_n_m:.4f} ({Q_n_m*100:.2f}%)")
    
    # Test network connectivity probability
    print("\n\nNetwork m-Connectivity Probability (Equation 27):")
    print("-" * 70)
    print(f"P(network is m-connected) = (Q_n,≥m)^n\n")
    
    for m in range(1, 4):
        prob = MConnectivityCalculator.calculate_network_connectivity_probability(
            l, n, m, area
        )
        status = "✓ Good" if prob >= 0.9 else "⚠ Low"
        print(f"P({m}-connected): {prob:.6f} ({prob*100:.4f}%) {status}")
    
    # Analyze connectivity levels
    print("\n\nConnectivity Analysis:")
    print("-" * 70)
    
    analysis = MConnectivityCalculator.analyze_connectivity_levels(l, n, area)
    
    print(f"{'Level':<15} {'Q_n,≥m':<15} {'Network P':<15} {'Status'}")
    print("-" * 70)
    
    for m, info in analysis.items():
        status = "✓ >90%" if info['network_probability'] >= 0.9 else "✗ <90%"
        print(f"{info['connectivity_level']:<15} "
              f"{info['Q_n_m']:<15.4f} "
              f"{info['network_probability']:<15.6f} "
              f"{status}")
    
    # Find required nodes
    print("\n\nRequired Nodes for 90% Connectivity:")
    print("-" * 70)
    
    for m in range(1, 4):
        result = MConnectivityCalculator.find_required_nodes(
            l, area, m, target_probability=0.9
        )
        
        print(f"\n{m}-connected network:")
        print(f"  Required nodes: {result['required_nodes']}")
        print(f"  Target: {result['target_probability']*100:.0f}%")
        print(f"  Achieved: {result['achieved_probability']*100:.2f}%")
    
    # Compare different node counts
    print("\n\nConnectivity vs Number of Nodes (2-connected):")
    print("-" * 70)
    
    n_range = [50, 75, 100, 150, 200, 300]
    comparison = MConnectivityCalculator.compare_connectivity_vs_nodes(
        l, area, m=2, n_range=n_range
    )
    
    print(f"{'Nodes':<10} {'Probability':<15} {'Percentage':<15} {'Status'}")
    print("-" * 70)
    
    for n_test, prob in comparison.items():
        status = "✓" if prob >= 0.9 else "✗"
        print(f"{n_test:<10} {prob:<15.6f} {prob*100:<15.2f}% {status}")
    
    # Complete summary
    print("\n\nComplete Connectivity Summary:")
    print("-" * 70)
    
    summary = MConnectivityCalculator.connectivity_summary(l, n, area)
    
    print(f"\nNetwork Configuration:")
    print(f"  Nodes: {summary['network_config']['nodes']}")
    print(f"  Area: {summary['network_config']['area']:.0e} m²")
    print(f"  Distance: {summary['network_config']['communication_distance']} m")
    print(f"  Expected neighbors: {summary['expected_neighbors']:.2f}")
    
    print(f"\nConnectivity Probabilities:")
    for m, info in summary['connectivity_levels'].items():
        meets = "✓ YES" if summary['meets_90_percent'][m] else "✗ NO"
        print(f"  {m}-connected: {info['network_probability']*100:.2f}% (Meets 90%: {meets})")
    
    print("\n💡 Key Insight:")
    if summary['meets_90_percent'][2]:
        print("   Network achieves robust 2-connectivity (recommended)!")
    elif summary['meets_90_percent'][1]:
        print("   Network achieves basic 1-connectivity")
        print("   Consider more nodes for 2-connectivity (more robust)")
    else:
        print("   Network connectivity is low - need more nodes!")