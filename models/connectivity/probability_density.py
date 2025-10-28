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
    """
    Probability density functions for node distribution.
    
    Simple explanation:
    - Uniform distribution: nodes equally likely anywhere in area
    - Like throwing darts at a board - equal chance everywhere
    - Used for calculating connectivity probabilities
    """
    
    @staticmethod
    def uniform_square(x: float, y: float, n: int, area: float) -> float:
        """
        Uniform probability density for square network (Equation 18)
        
        Simple explanation:
        - n nodes spread evenly over an area
        - Probability = n / area (constant everywhere)
        - Like: "10 people in 100 m² room = 0.1 people per m²"
        
        Equation 18: U(tx, φx) = n / S_ROI for (tx, φx) ∈ C
        
        Args:
            x, y: Point coordinates (meters)
            n: Total number of nodes in network
            area: Total area (S_ROI in square meters)
            
        Returns:
            Probability density (nodes per square meter)
        """
        if area <= 0:
            return 0.0
        
        # Equation 18: uniform density = n / S_ROI
        density = n / area
        return density
    
    @staticmethod
    def uniform_square_polar(t: float, phi: float, n: int, area: float) -> float:
        """
        Uniform probability density in polar coordinates
        
        Simple explanation:
        - Same as uniform_square but uses polar coordinates (r, θ)
        - Useful for calculating connectivity integrals (Equations 20-25)
        
        Args:
            t: Radial coordinate (meters from origin)
            phi: Angular coordinate (radians)
            n: Number of nodes
            area: Total area (square meters)
            
        Returns:
            Probability density
        """
        return ProbabilityDensityFunction.uniform_square(
            t * np.cos(phi), t * np.sin(phi), n, area
        )
    
    @staticmethod
    def is_point_in_square(x: float, y: float, side_length: float) -> bool:
        """
        Check if point is inside square region
        
        Args:
            x, y: Point coordinates
            side_length: Side length of square
            
        Returns:
            True if point is inside square
        """
        return (0 <= x <= side_length) and (0 <= y <= side_length)
    
    @staticmethod
    def create_uniform_pdf(n: int, area: float) -> Callable:
        """
        Create a probability density function for uniform distribution
        
        Simple explanation:
        - Returns a function that you can call with (x, y)
        - Always returns same value (uniform = constant)
        
        Args:
            n: Number of nodes
            area: Coverage area
            
        Returns:
            Function that takes (x, y) and returns probability density
        """
        def pdf(x: float, y: float) -> float:
            return ProbabilityDensityFunction.uniform_square(x, y, n, area)
        
        return pdf
    
    @staticmethod
    def calculate_expected_neighbors(n: int, area: float, 
                                    communication_distance: float) -> float:
        """
        Calculate expected number of neighbors for a node
        
        Simple explanation:
        - On average, how many other nodes are within range?
        - Uses: density × coverage area
        - Like: "0.1 people/m² × 100 m² coverage = 10 neighbors"
        
        Args:
            n: Total nodes in network
            area: Total network area
            communication_distance: How far each node can reach
            
        Returns:
            Expected number of neighbors
        """
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
        """
        Calculate probability that a node has NO neighbors (isolated)
        
        Simple explanation:
        - What's the chance a node is alone (can't talk to anyone)?
        - Uses Poisson distribution approximation
        - Important for network reliability
        
        Args:
            n: Number of nodes
            area: Network area
            communication_distance: Communication range
            
        Returns:
            Probability of isolation (0 to 1)
        """
        # Expected neighbors
        lambda_val = ProbabilityDensityFunction.calculate_expected_neighbors(
            n, area, communication_distance
        )
        
        # Probability of 0 neighbors: P(X=0) = λ^0 × e^(-λ) / 0! = e^(-λ)
        prob_isolated = np.exp(-lambda_val)
        
        return prob_isolated
    
    @staticmethod
    def calculate_network_density(n: int, area: float) -> dict:
        """
        Calculate various network density metrics
        
        Args:
            n: Number of nodes
            area: Network area
            
        Returns:
            Dictionary with density metrics
        """
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
    """
    Node distribution models for different deployment scenarios
    """
    
    @staticmethod
    def uniform_random(n: int, area: float) -> np.ndarray:
        """
        Generate uniform random node positions
        
        Args:
            n: Number of nodes
            area: Square area
            
        Returns:
            Array of (x, y) positions
        """
        side = np.sqrt(area)
        positions = np.random.uniform(0, side, (n, 2))
        return positions
    
    @staticmethod
    def grid_deterministic(n: int, area: float) -> np.ndarray:
        """
        Generate deterministic grid positions
        
        Args:
            n: Number of nodes
            area: Square area
            
        Returns:
            Array of (x, y) positions
        """
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