"""
Probability density functions for connectivity analysis.
Implements Equation 18 from the paper.

Simple explanation:
- In a network, nodes are placed randomly or in a pattern
- We need to know: "What's the probability of finding a node at position X?"
- This is the "probability density" - like a map showing where nodes are likely to be
"""

import numpy as np
import sys
import os
from typing import Tuple, Callable

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


class ProbabilityDensityFunction:
    @staticmethod
    def uniform_square(x: float, y: float, n: int, area: float) -> float:
        if area <= 0:
            return 0.0
        
        # Equation 18: uniform density = n / S_ROI
        density = n / area
        return density
    
    @staticmethod
    def uniform_square_polar(t: float, phi: float, n: int, area: float) -> float:
        return ProbabilityDensityFunction.uniform_square(
            t * np.cos(phi), t * np.sin(phi), n, area
        )
    
    @staticmethod
    def is_point_in_square(x: float, y: float, side_length: float) -> bool:
        return (0 <= x <= side_length) and (0 <= y <= side_length)
    
    @staticmethod
    def create_uniform_pdf(n: int, area: float) -> Callable:
        def pdf(x: float, y: float) -> float:
            return ProbabilityDensityFunction.uniform_square(x, y, n, area)
        
        return pdf
    
    @staticmethod
    def calculate_expected_neighbors(n: int, area: float, 
                                    communication_distance: float) -> float:
        # Density of other nodes (excluding self)
        density = (n - 1) / area
        
        # Coverage area (circular)
        coverage_area = np.pi * communication_distance ** 2
        
        # Expected neighbors = density × coverage
        expected_neighbors = density * coverage_area
        
        return expected_neighbors
    
    @staticmethod
    def calculate_isolation_probability(n: int, area: float,
                                       communication_distance: float) -> float:
        # Expected neighbors
        lambda_val = ProbabilityDensityFunction.calculate_expected_neighbors(
            n, area, communication_distance
        )
        
        # Probability of 0 neighbors: P(X=0) = λ^0 × e^(-λ) / 0! = e^(-λ)
        prob_isolated = np.exp(-lambda_val)
        
        return prob_isolated
    
    @staticmethod
    def calculate_network_density(n: int, area: float) -> dict:
        side_length = np.sqrt(area)
        density = n / area
        
        return {
            'nodes': n,
            'area': area,
            'side_length': side_length,
            'density': density,
            'density_per_100m2': density * 100,
            'average_spacing': np.sqrt(area / n) if n > 0 else 0
        }


class NodeDistribution:
    @staticmethod
    def uniform_random(n: int, area: float) -> np.ndarray:
        side = np.sqrt(area)
        positions = np.random.uniform(0, side, (n, 2))
        return positions
    
    @staticmethod
    def grid_deterministic(n: int, area: float) -> np.ndarray:
        side = np.sqrt(area)
        grid_size = int(np.ceil(np.sqrt(n)))
        spacing = side / grid_size
        
        positions = []
        for i in range(grid_size):
            for j in range(grid_size):
                if len(positions) < n:
                    x = (i + 0.5) * spacing
                    y = (j + 0.5) * spacing
                    positions.append([x, y])
        
        return np.array(positions)


if __name__ == "__main__":
    print("Probability Density Function Test")
    print("=" * 70)
    
    # Test uniform PDF (Equation 18)
    print("\nUniform PDF (Equation 18):")
    print("-" * 70)
    
    n = 100  # nodes
    area = 1e6  # 1 km²
    
    density = ProbabilityDensityFunction.uniform_square(0, 0, n, area)
    print(f"Network: {n} nodes in {area:.0e} m²")
    print(f"Density U(x,y): {density:.2e} nodes/m²")
    print(f"Expected: {n/area:.2e} nodes/m²")
    print(f"Match: {'✓' if abs(density - n/area) < 1e-10 else '✗'}")
    
    # Test expected neighbors
    print("\n\nExpected Neighbors Calculation:")
    print("-" * 70)
    
    l = 95  # communication distance
    expected = ProbabilityDensityFunction.calculate_expected_neighbors(n, area, l)
    
    print(f"Communication distance: {l} m")
    print(f"Coverage per node: {np.pi * l**2:.0f} m²")
    print(f"Expected neighbors: {expected:.2f}")
    print(f"Interpretation: Each node can talk to ~{expected:.0f} others on average")
    
    # Test isolation probability
    print("\n\nIsolation Probability:")
    print("-" * 70)
    
    prob_isolated = ProbabilityDensityFunction.calculate_isolation_probability(n, area, l)
    print(f"P(node is isolated): {prob_isolated:.6f}")
    print(f"P(node is isolated): {prob_isolated * 100:.4f}%")
    
    if prob_isolated < 0.01:
        print(f"✓ Very low isolation risk - good network!")
    elif prob_isolated < 0.1:
        print(f"⚠ Some isolation risk - consider more nodes")
    else:
        print(f"✗ High isolation risk - need more nodes!")
    
    # Test different scenarios
    print("\n\nScenario Comparison:")
    print("-" * 70)
    print(f"{'Nodes':<10} {'Area (m²)':<15} {'Distance (m)':<15} {'Exp. Neighbors':<20} {'Isolation %'}")
    print("-" * 70)
    
    scenarios = [
        (50, 1e6, 95),
        (100, 1e6, 95),
        (200, 1e6, 95),
        (100, 1e6, 70),
    ]
    
    for n_test, area_test, l_test in scenarios:
        exp_neighbors = ProbabilityDensityFunction.calculate_expected_neighbors(
            n_test, area_test, l_test
        )
        prob_iso = ProbabilityDensityFunction.calculate_isolation_probability(
            n_test, area_test, l_test
        )
        
        print(f"{n_test:<10} {area_test:<15.0e} {l_test:<15} "
              f"{exp_neighbors:<20.2f} {prob_iso*100:.4f}%")
    
    # Test network density metrics
    print("\n\nNetwork Density Metrics:")
    print("-" * 70)
    
    metrics = ProbabilityDensityFunction.calculate_network_density(100, 1e6)
    print(f"Nodes: {metrics['nodes']}")
    print(f"Area: {metrics['area']:.0e} m²")
    print(f"Side length: {metrics['side_length']:.0f} m")
    print(f"Density: {metrics['density']:.2e} nodes/m²")
    print(f"Density: {metrics['density_per_100m2']:.4f} nodes per 100m²")
    print(f"Average spacing: {metrics['average_spacing']:.2f} m")