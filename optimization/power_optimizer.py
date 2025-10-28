"""
Transmission power optimization.
Based on Figures 11-12 and 18 from the paper.

Simple explanation:
- More power = longer distance = fewer nodes
- But too much power = unsafe and expensive
- Find the minimum power needed to meet requirements
"""

import numpy as np
import sys
import os
from typing import Dict, Tuple

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.communication_params import CommunicationParams
from models.channel.communication_distance import CommunicationDistanceCalculator
from models.network.effective_coverage import EffectiveCoverageCalculator
from models.connectivity.m_connectivity import MConnectivityCalculator


class PowerOptimizer:
    """
    Optimize transmission power for UV networks.
    
    Based on paper's analysis:
    - Power range: 0.1-0.5W (safety limit from experiments)
    - Figure 11-12: Coverage vs power for 4-node and single-node
    - Figure 18: Connectivity vs power for different m-connectivity
    """
    
    def __init__(self):
        self.calc = CommunicationDistanceCalculator()
        
        # Safety limits from paper (Section V)
        self.PT_MIN = CommunicationParams.PT_MIN  # 0.1W
        self.PT_MAX = CommunicationParams.PT_MAX  # 0.5W (eye/skin safety)
    
    def find_minimum_power_for_distance(self, target_distance: float,
                                       Rd: float, theta1: float, theta2: float) -> Dict:
        """
        Find minimum power to achieve target distance
        
        Simple explanation:
        - "I need to reach X meters"
        - "What's the minimum power?"
        - Binary search to find answer
        
        Args:
            target_distance: Desired communication distance (m)
            Rd: Data rate (bps)
            theta1, theta2: Elevation angles (degrees)
            
        Returns:
            Dictionary with optimal power and achieved distance
        """
        # Binary search
        Pt_low = self.PT_MIN
        Pt_high = self.PT_MAX
        tolerance = 0.01  # 0.01W precision
        
        # Check if achievable
        max_distance = self.calc.calculate_ook_distance(Pt_high, Rd, theta1, theta2)
        if max_distance < target_distance:
            return {
                'feasible': False,
                'required_power': Pt_high,
                'achieved_distance': max_distance,
                'target_distance': target_distance,
                'message': f'Target {target_distance}m not achievable with max power {Pt_high}W'
            }
        
        # Binary search
        while Pt_high - Pt_low > tolerance:
            Pt_mid = (Pt_low + Pt_high) / 2
            distance = self.calc.calculate_ook_distance(Pt_mid, Rd, theta1, theta2)
            
            if distance < target_distance:
                Pt_low = Pt_mid
            else:
                Pt_high = Pt_mid
        
        optimal_power = Pt_high
        achieved_distance = self.calc.calculate_ook_distance(optimal_power, Rd, theta1, theta2)
        
        return {
            'feasible': True,
            'required_power': optimal_power,
            'achieved_distance': achieved_distance,
            'target_distance': target_distance,
            'parameters': {'Rd': Rd, 'theta1': theta1, 'theta2': theta2}
        }
    
    def find_minimum_power_for_coverage(self, S_ROI: float, max_nodes: int,
                                       Rd: float, theta1: float, theta2: float) -> Dict:
        """
        Find minimum power to cover area with limited nodes
        
        Simple explanation:
        - "I can only afford N devices"
        - "What power do they need to cover the area?"
        
        Args:
            S_ROI: Area to cover (m²)
            max_nodes: Maximum nodes available
            Rd: Data rate (bps)
            theta1, theta2: Elevation angles (degrees)
            
        Returns:
            Optimal power configuration
        """
        # Calculate required distance per node
        # From n_min = S_ROI / (η_eff × πl²)
        # Solve for l: l = sqrt(S_ROI / (n_min × η_eff × π))
        eta_eff = 0.5545
        required_distance = np.sqrt(S_ROI / (max_nodes * eta_eff * np.pi))
        
        # Find power for this distance
        result = self.find_minimum_power_for_distance(
            required_distance, Rd, theta1, theta2
        )
        
        if result['feasible']:
            # Verify with actual calculation
            actual_nodes = EffectiveCoverageCalculator.calculate_minimum_nodes(
                S_ROI, result['achieved_distance']
            )
            
            result['actual_nodes'] = actual_nodes
            result['max_nodes'] = max_nodes
            result['meets_requirement'] = actual_nodes <= max_nodes
        
        return result
    
    def find_minimum_power_for_connectivity(self, S_ROI: float, n: int, m: int,
                                           target_prob: float, Rd: float,
                                           theta1: float, theta2: float) -> Dict:
        """
        Find minimum power for target m-connectivity
        
        Simple explanation:
        - "I want 90% chance of 2-connectivity"
        - "What power do I need?"
        
        Based on Figure 18 from paper
        
        Args:
            S_ROI: Coverage area (m²)
            n: Number of nodes
            m: Connectivity level
            target_prob: Target connectivity probability
            Rd, theta1, theta2: Communication parameters
            
        Returns:
            Optimal power for connectivity
        """
        # Binary search on power
        Pt_low = self.PT_MIN
        Pt_high = self.PT_MAX
        tolerance = 0.01
        
        while Pt_high - Pt_low > tolerance:
            Pt_mid = (Pt_low + Pt_high) / 2
            
            # Calculate distance and connectivity
            distance = self.calc.calculate_ook_distance(Pt_mid, Rd, theta1, theta2)
            conn_prob = MConnectivityCalculator.calculate_network_connectivity_probability(
                distance, n, m, S_ROI, sample_points=10
            )
            
            if conn_prob < target_prob:
                Pt_low = Pt_mid  # Need more power
            else:
                Pt_high = Pt_mid  # Can use less power
        
        optimal_power = Pt_high
        final_distance = self.calc.calculate_ook_distance(optimal_power, Rd, theta1, theta2)
        final_conn = MConnectivityCalculator.calculate_network_connectivity_probability(
            final_distance, n, m, S_ROI, sample_points=10
        )
        
        return {
            'required_power': optimal_power,
            'achieved_connectivity': final_conn,
            'target_connectivity': target_prob,
            'distance': final_distance,
            'nodes': n,
            'connectivity_level': m,
            'meets_requirement': final_conn >= target_prob
        }
    
    def analyze_power_impact(self, Pt_range: np.ndarray, Rd: float,
                            theta1: float, theta2: float, S_ROI: float) -> Dict:
        """
        Analyze impact of power on network metrics
        Reproduces Figures 11-12 and 18 analysis from paper
        
        Args:
            Pt_range: Range of powers to test (W)
            Rd, theta1, theta2: Fixed communication parameters
            S_ROI: Coverage area (m²)
            
        Returns:
            Complete power analysis
        """
        results = {
            'Pt_values': Pt_range,
            'distances': [],
            'min_nodes': [],
            'coverage_4node': [],
            'coverage_single': [],
            'connectivity_1': [],
            'connectivity_2': [],
            'connectivity_3': []
        }
        
        for Pt in Pt_range:
            # Calculate distance
            l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
            
            if l <= 0 or not np.isfinite(l):
                # Invalid distance, skip
                results['distances'].append(0)
                results['min_nodes'].append(0)
                results['coverage_4node'].append(0)
                results['coverage_single'].append(0)
                results['connectivity_1'].append(0)
                results['connectivity_2'].append(0)
                results['connectivity_3'].append(0)
                continue
            
            # Coverage metrics (Phase 2)
            n_min = EffectiveCoverageCalculator.calculate_minimum_nodes(S_ROI, l)
            cov_4node = EffectiveCoverageCalculator.calculate_four_node_effective_coverage(l)
            cov_single = EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l)
            
            # Connectivity metrics (Phase 3) - use n=300 like Figure 18
            n_test = 300
            conn_1 = MConnectivityCalculator.calculate_network_connectivity_probability(
                l, n_test, 1, S_ROI, sample_points=10
            )
            conn_2 = MConnectivityCalculator.calculate_network_connectivity_probability(
                l, n_test, 2, S_ROI, sample_points=10
            )
            conn_3 = MConnectivityCalculator.calculate_network_connectivity_probability(
                l, n_test, 3, S_ROI, sample_points=10
            )
            
            results['distances'].append(l)
            results['min_nodes'].append(n_min)
            results['coverage_4node'].append(cov_4node)
            results['coverage_single'].append(cov_single)
            results['connectivity_1'].append(conn_1)
            results['connectivity_2'].append(conn_2)
            results['connectivity_3'].append(conn_3)
        
        return results


if __name__ == "__main__":
    print("Power Optimizer Test")
    print("=" * 70)
    
    optimizer = PowerOptimizer()
    
    # Test 1: Find power for target distance
    print("\nTest 1: Minimum Power for Target Distance")
    print("-" * 70)
    
    target = 100  # meters
    result = optimizer.find_minimum_power_for_distance(
        target, Rd=50e3, theta1=30, theta2=50
    )
    
    if result['feasible']:
        print(f"✅ Target distance: {target}m")
        print(f"   Required power: {result['required_power']:.3f}W")
        print(f"   Achieved distance: {result['achieved_distance']:.1f}m")
    else:
        print(f"❌ {result['message']}")
    
    # Test 2: Find power for coverage with limited nodes
    print("\n\nTest 2: Power for Coverage with Node Limit")
    print("-" * 70)
    
    area = 1e6  # 1 km²
    max_nodes = 50
    
    result = optimizer.find_minimum_power_for_coverage(
        area, max_nodes, Rd=50e3, theta1=30, theta2=50
    )
    
    if result['feasible']:
        print(f"Area: {area:.0e}m², Max nodes: {max_nodes}")
        print(f"✅ Required power: {result['required_power']:.3f}W")
        print(f"   Distance: {result['achieved_distance']:.1f}m")
        print(f"   Actual nodes: {result['actual_nodes']}")
        print(f"   Meets requirement: {result['meets_requirement']}")
    
    # Test 3: Power for connectivity (Figure 18 reproduction)
    print("\n\nTest 3: Power for Target Connectivity (Fig. 18 analysis)")
    print("-" * 70)
    
    result = optimizer.find_minimum_power_for_connectivity(
        S_ROI=1e6, n=300, m=2, target_prob=0.9,
        Rd=50e3, theta1=30, theta2=50
    )
    
    print(f"Target: 90% 2-connectivity with 300 nodes")
    print(f"✅ Required power: {result['required_power']:.3f}W")
    print(f"   Achieved: {result['achieved_connectivity']*100:.2f}%")
    print(f"   Distance: {result['distance']:.1f}m")
    
    # Test 4: Power impact analysis (Figures 11-12-18)
    print("\n\nTest 4: Power Impact Analysis")
    print("-" * 70)
    
    Pt_range = np.linspace(0.1, 0.5, 5)
    analysis = optimizer.analyze_power_impact(
        Pt_range, Rd=50e3, theta1=30, theta2=50, S_ROI=1e6
    )
    
    print(f"{'Pt(W)':<8} {'Dist(m)':<12} {'Nodes':<10} {'4-Node(m²)':<15} {'2-Conn%'}")
    print("-" * 70)
    for i, Pt in enumerate(analysis['Pt_values']):
        dist = analysis['distances'][i]
        nodes = analysis['min_nodes'][i]
        cov4 = analysis['coverage_4node'][i]
        conn2 = analysis['connectivity_2'][i]
        print(f"{Pt:<8.2f} {dist:<12.1f} {nodes:<10} {cov4:<15.0f} {conn2*100:.1f}%")