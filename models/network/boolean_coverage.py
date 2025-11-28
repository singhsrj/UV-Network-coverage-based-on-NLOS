"""
models/network/boolean_coverage.py

Boolean coverage model for UV network.
Implements Equation 2 from the paper.

Simple explanation:
- For any point in space: it's either covered or not covered
- Covered = within range of at least one device
- Not covered = too far from all devices
- Like asking: "Can I get WiFi signal here? Yes or No"
"""

import numpy as np
import sys
import os
from typing import List, Tuple
from utils.geometry import GeometryUtils

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))



class BooleanCoverageModel:
    @staticmethod
    def is_point_covered(point: Tuple[float, float],
                        node_position: Tuple[float, float],
                        coverage_radius: float) -> bool:
        px, py = point
        nx, ny = node_position
        
        # Calculate distance
        distance = GeometryUtils.euclidean_distance_2d(px, py, nx, ny)
        
        # Boolean coverage (Equation 2)
        # p(X) = 1 if d(O, X) < R, else 0
        return distance < coverage_radius
    
    @staticmethod
    def is_point_covered_by_network(point: Tuple[float, float],
                                    node_positions: List[Tuple[float, float]],
                                    coverage_radius: float) -> bool:
        for node_pos in node_positions:
            if BooleanCoverageModel.is_point_covered(point, node_pos, coverage_radius):
                return True
        return False
    
    @staticmethod
    def calculate_coverage_rate(point: Tuple[float, float],
                               node_position: Tuple[float, float],
                               coverage_radius: float) -> float:
        is_covered = BooleanCoverageModel.is_point_covered(
            point, node_position, coverage_radius
        )
        return 1.0 if is_covered else 0.0
    
    @staticmethod
    def count_covering_nodes(point: Tuple[float, float],
                            node_positions: List[Tuple[float, float]],
                            coverage_radius: float) -> int:
        count = 0
        for node_pos in node_positions:
            if BooleanCoverageModel.is_point_covered(point, node_pos, coverage_radius):
                count += 1
        return count
    
    @staticmethod
    def calculate_area_coverage(region_bounds: Tuple[float, float, float, float],
                               node_positions: List[Tuple[float, float]],
                               coverage_radius: float,
                               grid_resolution: int = 100) -> float:
        x_min, x_max, y_min, y_max = region_bounds
        
        # Create grid of test points
        x_points = np.linspace(x_min, x_max, grid_resolution)
        y_points = np.linspace(y_min, y_max, grid_resolution)
        
        covered_count = 0
        total_count = 0
        
        # Check each grid point
        for x in x_points:
            for y in y_points:
                point = (x, y)
                if BooleanCoverageModel.is_point_covered_by_network(
                    point, node_positions, coverage_radius
                ):
                    covered_count += 1
                total_count += 1
        
        coverage_ratio = covered_count / total_count if total_count > 0 else 0.0
        return coverage_ratio
    
    @staticmethod
    def generate_coverage_map(region_bounds: Tuple[float, float, float, float],
                             node_positions: List[Tuple[float, float]],
                             coverage_radius: float,
                             grid_resolution: int = 50) -> np.ndarray:
        x_min, x_max, y_min, y_max = region_bounds
        
        # Create grid
        x_points = np.linspace(x_min, x_max, grid_resolution)
        y_points = np.linspace(y_min, y_max, grid_resolution)
        
        # Initialize coverage map
        coverage_map = np.zeros((grid_resolution, grid_resolution))
        
        # Fill coverage map
        for i, y in enumerate(y_points):
            for j, x in enumerate(x_points):
                point = (x, y)
                if BooleanCoverageModel.is_point_covered_by_network(
                    point, node_positions, coverage_radius
                ):
                    coverage_map[i, j] = 1.0
        
        return coverage_map
    
    @staticmethod
    def generate_redundancy_map(region_bounds: Tuple[float, float, float, float],
                               node_positions: List[Tuple[float, float]],
                               coverage_radius: float,
                               grid_resolution: int = 50) -> np.ndarray:
        x_min, x_max, y_min, y_max = region_bounds
        
        x_points = np.linspace(x_min, x_max, grid_resolution)
        y_points = np.linspace(y_min, y_max, grid_resolution)
        
        redundancy_map = np.zeros((grid_resolution, grid_resolution))
        
        for i, y in enumerate(y_points):
            for j, x in enumerate(x_points):
                point = (x, y)
                count = BooleanCoverageModel.count_covering_nodes(
                    point, node_positions, coverage_radius
                )
                redundancy_map[i, j] = count
        
        return redundancy_map


if __name__ == "__main__":
    print("Boolean Coverage Model Test")
    print("=" * 70)
    
    # Test single point coverage
    print("\nSingle Point Coverage Test:")
    print("-" * 70)
    
    node_pos = (0, 0)
    coverage_radius = 50  # meters
    
    test_points = [
        ((0, 0), "At node"),
        ((25, 0), "Close (25m away)"),
        ((49, 0), "Edge (49m away)"),
        ((50, 0), "Boundary (50m away)"),
        ((51, 0), "Outside (51m away)"),
        ((100, 0), "Far (100m away)")
    ]
    
    print(f"Node at: {node_pos}, Coverage radius: {coverage_radius}m\n")
    print(f"{'Point':<20} {'Distance (m)':<15} {'Covered?'}")
    print("-" * 50)
    
    for point, description in test_points:
        distance = GeometryUtils.euclidean_distance_2d(
            point[0], point[1], node_pos[0], node_pos[1]
        )
        is_covered = BooleanCoverageModel.is_point_covered(
            point, node_pos, coverage_radius
        )
        status = "✓ YES" if is_covered else "✗ NO"
        print(f"{description:<20} {distance:<15.1f} {status}")
    
    # Test network coverage
    print("\n\nNetwork Coverage Test:")
    print("-" * 70)
    
    # Create 4-node square network
    node_positions = [
        (0, 0),
        (150, 0),
        (0, 150),
        (150, 150)
    ]
    
    print(f"4-node square network:")
    for i, pos in enumerate(node_positions, 1):
        print(f"  Node {i}: {pos}")
    print(f"Coverage radius: {coverage_radius}m")
    
    # Test various points
    test_points_network = [
        ((75, 75), "Center of network"),
        ((0, 0), "At Node 1"),
        ((200, 200), "Outside network"),
        ((75, 0), "Between nodes 1-2"),
    ]
    
    print(f"\n{'Point':<25} {'Covering Nodes':<20} {'Status'}")
    print("-" * 70)
    
    for point, description in test_points_network:
        count = BooleanCoverageModel.count_covering_nodes(
            point, node_positions, coverage_radius
        )
        is_covered = BooleanCoverageModel.is_point_covered_by_network(
            point, node_positions, coverage_radius
        )
        status = f"✓ Covered by {count}" if is_covered else "✗ Not covered"
        print(f"{description:<25} {count:<20} {status}")
    
    # Calculate overall coverage
    print("\n\nArea Coverage Analysis:")
    print("-" * 70)
    
    region = (0, 150, 0, 150)  # 150m × 150m area
    coverage_ratio = BooleanCoverageModel.calculate_area_coverage(
        region, node_positions, coverage_radius, grid_resolution=50
    )
    
    total_area = 150 * 150
    covered_area = coverage_ratio * total_area
    
    print(f"Region: 150m × 150m = {total_area:.0f} m²")
    print(f"Coverage ratio: {coverage_ratio * 100:.1f}%")
    print(f"Covered area: {covered_area:.0f} m²")
    print(f"Uncovered area: {total_area - covered_area:.0f} m²")