"""
models/network/square_deployment.py

Square network deployment for UV nodes.
Based on Figures 8 and 15 from the paper.

Simple explanation:
- Arrange nodes in a grid pattern (like a checkerboard)
- Each node placed at regular intervals
- Provides efficient, organized coverage
"""

import numpy as np
import sys
import os
from typing import List, Tuple, Dict

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.network.effective_coverage import EffectiveCoverageCalculator
from utils.geometry import GeometryUtils


class SquareNetworkDeployment:
    def __init__(self, communication_distance: float):
        self.l = communication_distance
        self.calculator = EffectiveCoverageCalculator()
    
    def create_four_node_network(self) -> Dict:
        # Network side length = 3l (from paper)
        side_length = 3 * self.l
        
        # Place nodes at corners
        positions = [
            (0, 0),                          # Bottom-left (Node A)
            (side_length, 0),                # Bottom-right (Node B)
            (0, side_length),                # Top-left (Node C)
            (side_length, side_length)       # Top-right (Node D)
        ]
        
        # Calculate coverage
        effective_coverage = self.calculator.calculate_four_node_effective_coverage(self.l)
        
        return {
            'num_nodes': 4,
            'positions': positions,
            'side_length': side_length,
            'effective_coverage': effective_coverage,
            'communication_distance': self.l,
            'network_type': 'four_node_square',
            'bounds': (0, side_length, 0, side_length)
        }
    
    def create_grid_network(self, area_width: float, area_height: float) -> Dict:
        # Calculate effective spacing between nodes
        S_eff = self.calculator.calculate_single_node_effective_coverage(self.l)
        spacing = np.sqrt(S_eff)  # Approximate spacing
        
        # Calculate number of nodes needed in each dimension
        nx = int(np.ceil(area_width / spacing)) + 1  # Add 1 for coverage overlap
        ny = int(np.ceil(area_height / spacing)) + 1
        
        # Actual spacing to fit area
        x_spacing = area_width / (nx - 1) if nx > 1 else 0
        y_spacing = area_height / (ny - 1) if ny > 1 else 0
        
        # Generate grid positions
        positions = []
        for i in range(nx):
            for j in range(ny):
                x = i * x_spacing
                y = j * y_spacing
                positions.append((x, y))
        
        total_nodes = len(positions)
        total_area = area_width * area_height
        
        return {
            'num_nodes': total_nodes,
            'positions': positions,
            'grid_dimensions': (nx, ny),
            'spacing': (x_spacing, y_spacing),
            'area_covered': total_area,
            'communication_distance': self.l,
            'network_type': 'grid',
            'bounds': (0, area_width, 0, area_height)
        }
    
    def create_square_area_network(self, area: float) -> Dict:
        side_length = np.sqrt(area)
        return self.create_grid_network(side_length, side_length)
    
    def create_minimum_node_network(self, S_ROI: float) -> Dict:
        # Calculate minimum nodes
        n_min = self.calculator.calculate_minimum_nodes(S_ROI, self.l)
        
        # Create square area
        side_length = np.sqrt(S_ROI)
        
        # Calculate grid dimensions (approximately square)
        n_per_side = int(np.ceil(np.sqrt(n_min)))
        
        # Generate positions
        spacing = side_length / n_per_side
        positions = []
        
        for i in range(n_per_side):
            for j in range(n_per_side):
                if len(positions) < n_min:
                    x = i * spacing + spacing / 2  # Center in grid cell
                    y = j * spacing + spacing / 2
                    positions.append((x, y))
        
        return {
            'num_nodes': len(positions),
            'positions': positions,
            'grid_dimensions': (n_per_side, n_per_side),
            'spacing': spacing,
            'area_to_cover': S_ROI,
            'communication_distance': self.l,
            'network_type': 'minimum_nodes',
            'bounds': (0, side_length, 0, side_length)
        }
    
    def calculate_inter_node_distance(self, pos1: Tuple[float, float], 
                                     pos2: Tuple[float, float]) -> float:
        return GeometryUtils.euclidean_distance_2d(
            pos1[0], pos1[1], pos2[0], pos2[1]
        )
    
    def get_neighbor_nodes(self, positions: List[Tuple[float, float]], 
                          node_index: int) -> List[int]:
        node_pos = positions[node_index]
        neighbors = []
        
        for i, other_pos in enumerate(positions):
            if i != node_index:
                distance = self.calculate_inter_node_distance(node_pos, other_pos)
                if distance <= self.l:
                    neighbors.append(i)
        
        return neighbors
    
    def analyze_network_connectivity(self, positions: List[Tuple[float, float]]) -> Dict:
        num_nodes = len(positions)
        neighbor_counts = []
        
        for i in range(num_nodes):
            neighbors = self.get_neighbor_nodes(positions, i)
            neighbor_counts.append(len(neighbors))
        
        return {
            'total_nodes': num_nodes,
            'neighbor_counts': neighbor_counts,
            'min_neighbors': min(neighbor_counts) if neighbor_counts else 0,
            'max_neighbors': max(neighbor_counts) if neighbor_counts else 0,
            'avg_neighbors': np.mean(neighbor_counts) if neighbor_counts else 0,
            'isolated_nodes': [i for i, count in enumerate(neighbor_counts) if count == 0]
        }
    
    def get_deployment_summary(self, network: Dict) -> str:
        summary = []
        summary.append(f"Network Type: {network['network_type']}")
        summary.append(f"Number of Nodes: {network['num_nodes']}")
        summary.append(f"Communication Distance: {network['communication_distance']} m")
        
        if 'side_length' in network:
            summary.append(f"Network Side Length: {network['side_length']} m")
        
        if 'grid_dimensions' in network:
            summary.append(f"Grid Dimensions: {network['grid_dimensions'][0]} × {network['grid_dimensions'][1]}")
        
        if 'spacing' in network:
            if isinstance(network['spacing'], tuple):
                summary.append(f"Node Spacing: {network['spacing'][0]:.1f}m × {network['spacing'][1]:.1f}m")
            else:
                summary.append(f"Node Spacing: {network['spacing']:.1f}m")
        
        if 'effective_coverage' in network:
            summary.append(f"Effective Coverage: {network['effective_coverage']:.2f} m²")
        
        if 'area_covered' in network:
            summary.append(f"Area Covered: {network['area_covered']:.2f} m²")
        
        return "\n".join(summary)


if __name__ == "__main__":
    print("Square Network Deployment Test")
    print("=" * 70)
    
    # Test with experimental distance
    l_exp = 75.1
    deployer = SquareNetworkDeployment(l_exp)
    
    # Test 1: Four-node network
    print("\n1. Four-Node Network (Figure 8):")
    print("-" * 70)
    four_node = deployer.create_four_node_network()
    print(deployer.get_deployment_summary(four_node))
    print("\nNode Positions:")
    for i, pos in enumerate(four_node['positions'], 1):
        print(f"  Node {i}: ({pos[0]:.1f}, {pos[1]:.1f}) m")
    
    # Test 2: Grid network for 1 km²
    print("\n\n2. Grid Network for 1 km² Area:")
    print("-" * 70)
    grid_network = deployer.create_square_area_network(1e6)
    print(deployer.get_deployment_summary(grid_network))
    
    # Analyze connectivity
    connectivity = deployer.analyze_network_connectivity(grid_network['positions'])
    print(f"\nConnectivity Analysis:")
    print(f"  Min neighbors: {connectivity['min_neighbors']}")
    print(f"  Max neighbors: {connectivity['max_neighbors']}")
    print(f"  Avg neighbors: {connectivity['avg_neighbors']:.1f}")
    print(f"  Isolated nodes: {len(connectivity['isolated_nodes'])}")
    
    # Test 3: Minimum node deployment
    print("\n\n3. Minimum Node Deployment (Equation 29):")
    print("-" * 70)
    min_network = deployer.create_minimum_node_network(1e6)
    print(deployer.get_deployment_summary(min_network))
    
    # Test 4: Compare different distances
    print("\n\n4. Deployment Comparison for Different Distances:")
    print("-" * 70)
    print(f"{'Distance (m)':<15} {'Nodes for 1km²':<20} {'Grid Size':<15} {'Spacing (m)'}")
    print("-" * 70)
    
    for l in [50, 75, 100, 150]:
        dep = SquareNetworkDeployment(l)
        network = dep.create_minimum_node_network(1e6)
        grid_dim = network['grid_dimensions']
        spacing = network['spacing']
        print(f"{l:<15} {network['num_nodes']:<20} "
              f"{grid_dim[0]}×{grid_dim[1]}{'':<10} {spacing:.1f}")
    
    # Test 5: Specific area sizes
    print("\n\n5. Deployment for Different Area Sizes (l=95m):")
    print("-" * 70)
    deployer_95 = SquareNetworkDeployment(95)
    
    areas = [
        (1e4, "100m × 100m (small park)"),
        (1e5, "316m × 316m (neighborhood)"),
        (1e6, "1km × 1km (district)"),
    ]
    
    print(f"{'Area':<25} {'Nodes':<15} {'Grid':<15} {'Description'}")
    print("-" * 70)
    
    for area, desc in areas:
        network = deployer_95.create_minimum_node_network(area)
        grid = network['grid_dimensions']
        print(f"{area:<25.0e} {network['num_nodes']:<15} "
              f"{grid[0]}×{grid[1]}{'':<10} {desc}")