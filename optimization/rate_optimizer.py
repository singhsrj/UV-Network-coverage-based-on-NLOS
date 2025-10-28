"""
Data rate optimization for UV networks.
Based on Figures 13-14 and 17 from the paper.

Simple explanation:
- Higher data rate = shorter distance (need more SNR)
- Lower data rate = longer distance but slower
- Find maximum rate that meets your distance needs
"""

import numpy as np
import sys
import os
from typing import Dict

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.communication_params import CommunicationParams
from models.channel.communication_distance import CommunicationDistanceCalculator
from models.network.effective_coverage import EffectiveCoverageCalculator
from models.connectivity.m_connectivity import MConnectivityCalculator


class RateOptimizer:
    """
    Optimize data rate for UV networks.
    
    Based on paper's analysis:
    - Rate range: 10-120 kbps (from Figures 13-14, 17)
    - Higher rate → shorter distance (SNR requirement)
    - Figure 13-14: Coverage vs rate for 4-node and single-node
    - Figure 17: Connectivity vs rate for different m-connectivity
    """
    
    def __init__(self):
        self.calc = CommunicationDistanceCalculator()
        
        # Rate limits from paper
        self.RD_MIN = CommunicationParams.RD_MIN  # 10 kbps
        self.RD_MAX = CommunicationParams.RD_MAX  # 120 kbps
    
    def find_maximum_rate_for_distance(self, target_distance: float,
                                       Pt: float, theta1: float, theta2: float) -> Dict:
        """
        Find maximum data rate that achieves target distance
        
        Simple explanation:
        - "I need to reach X meters"
        - "What's the fastest data rate I can use?"
        - Binary search to find maximum rate
        
        Args:
            target_distance: Required distance (m)
            Pt: Transmission power (W)
            theta1, theta2: Elevation angles (degrees)
            
        Returns:
            Maximum achievable rate
        """
        # Check if achievable with slowest rate
        min_distance = self.calc.calculate_ook_distance(Pt, self.RD_MAX, theta1, theta2)
        if min_distance < target_distance:
            # Even slowest rate can't reach target
            actual_distance = self.calc.calculate_ook_distance(Pt, self.RD_MIN, theta1, theta2)
            return {
                'feasible': False,
                'maximum_rate': self.RD_MIN,
                'achieved_distance': actual_distance,
                'target_distance': target_distance,
                'message': f'Target {target_distance}m not achievable even with min rate {self.RD_MIN/1e3}kbps'
            }
        
        # Binary search for maximum rate
        Rd_low = self.RD_MIN
        Rd_high = self.RD_MAX
        tolerance = 1e3  # 1 kbps precision
        
        while Rd_high - Rd_low > tolerance:
            Rd_mid = (Rd_low + Rd_high) / 2
            distance = self.calc.calculate_ook_distance(Pt, Rd_mid, theta1, theta2)
            
            if distance < target_distance:
                Rd_high = Rd_mid  # Too fast, reduce rate
            else:
                Rd_low = Rd_mid  # Can go faster
        
        optimal_rate = Rd_low
        achieved_distance = self.calc.calculate_ook_distance(Pt, optimal_rate, theta1, theta2)
        
        return {
            'feasible': True,
            'maximum_rate': optimal_rate,
            'achieved_distance': achieved_distance,
            'target_distance': target_distance,
            'parameters': {'Pt': Pt, 'theta1': theta1, 'theta2': theta2}
        }
    
    def find_rate_for_connectivity(self, S_ROI: float, n: int, m: int,
                                  target_prob: float, Pt: float,
                                  theta1: float, theta2: float) -> Dict:
        """
        Find maximum rate for target connectivity
        
        Simple explanation:
        - "I want 90% 2-connectivity"
        - "What's the fastest rate I can use?"
        
        Based on Figure 17 from paper
        
        Args:
            S_ROI: Coverage area (m²)
            n: Number of nodes
            m: Connectivity level
            target_prob: Target connectivity probability
            Pt, theta1, theta2: Fixed parameters
            
        Returns:
            Maximum rate for connectivity
        """
        Rd_low = self.RD_MIN
        Rd_high = self.RD_MAX
        tolerance = 1e3
        
        while Rd_high - Rd_low > tolerance:
            Rd_mid = (Rd_low + Rd_high) / 2
            
            # Calculate distance and connectivity
            distance = self.calc.calculate_ook_distance(Pt, Rd_mid, theta1, theta2)
            conn_prob = MConnectivityCalculator.calculate_network_connectivity_probability(
                distance, n, m, S_ROI, sample_points=10
            )
            
            if conn_prob < target_prob:
                Rd_high = Rd_mid  # Too fast, reduce rate
            else:
                Rd_low = Rd_mid  # Can go faster
        
        optimal_rate = Rd_low
        final_distance = self.calc.calculate_ook_distance(Pt, optimal_rate, theta1, theta2)
        final_conn = MConnectivityCalculator.calculate_network_connectivity_probability(
            final_distance, n, m, S_ROI, sample_points=10
        )
        
        return {
            'maximum_rate': optimal_rate,
            'achieved_connectivity': final_conn,
            'target_connectivity': target_prob,
            'distance': final_distance,
            'nodes': n,
            'connectivity_level': m,
            'meets_requirement': final_conn >= target_prob
        }
    
    def analyze_rate_impact(self, Rd_range: np.ndarray, Pt: float,
                           theta1: float, theta2: float, S_ROI: float) -> Dict:
        """
        Analyze impact of data rate on network metrics
        Reproduces Figures 13-14 and 17 analysis from paper
        
        Args:
            Rd_range: Range of rates to test (bps)
            Pt, theta1, theta2: Fixed communication parameters
            S_ROI: Coverage area (m²)
            
        Returns:
            Complete rate analysis
        """
        results = {
            'Rd_values': Rd_range,
            'distances': [],
            'min_nodes': [],
            'coverage_4node': [],
            'coverage_single': [],
            'connectivity_1': [],
            'connectivity_2': [],
            'connectivity_3': []
        }
        
        for Rd in Rd_range:
            # Calculate distance
            l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
            
            # Coverage metrics (Phase 2)
            n_min = EffectiveCoverageCalculator.calculate_minimum_nodes(S_ROI, l)
            cov_4node = EffectiveCoverageCalculator.calculate_four_node_effective_coverage(l)
            cov_single = EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l)
            
            # Connectivity metrics (Phase 3) - use n=300 like Figure 17
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
    
    def recommend_rate(self, requirements: Dict) -> Dict:
        """
        Recommend optimal data rate based on requirements
        
        Simple explanation:
        - Tell system your needs
        - Get rate recommendation with reasoning
        
        Requirements can include:
        - 'min_distance': Minimum distance needed
        - 'target_connectivity': Target connectivity
        - 'priority': 'speed' (max rate) or 'range' (max distance)
        
        Args:
            requirements: Dictionary with requirements
            
        Returns:
            Rate recommendation
        """
        Pt = requirements.get('Pt', 0.5)
        theta1 = requirements.get('theta1', 30)
        theta2 = requirements.get('theta2', 50)
        priority = requirements.get('priority', 'balanced')
        
        if priority == 'speed':
            # Maximum rate that meets minimum requirements
            min_distance = requirements.get('min_distance', 50)
            result = self.find_maximum_rate_for_distance(min_distance, Pt, theta1, theta2)
            
            if result['feasible']:
                recommendation = {
                    'recommended_rate': result['maximum_rate'],
                    'achieved_distance': result['achieved_distance'],
                    'reason': f"Maximum rate while reaching {min_distance}m"
                }
            else:
                recommendation = {
                    'recommended_rate': self.RD_MIN,
                    'achieved_distance': result['achieved_distance'],
                    'reason': "Use minimum rate (target not achievable)"
                }
        
        elif priority == 'range':
            # Minimum rate for maximum distance
            recommendation = {
                'recommended_rate': self.RD_MIN,
                'achieved_distance': self.calc.calculate_ook_distance(Pt, self.RD_MIN, theta1, theta2),
                'reason': "Minimum rate for maximum distance"
            }
        
        else:  # balanced
            # Paper's standard: 50 kbps (good balance)
            standard_rate = 50e3
            recommendation = {
                'recommended_rate': standard_rate,
                'achieved_distance': self.calc.calculate_ook_distance(Pt, standard_rate, theta1, theta2),
                'reason': "Balanced rate (paper's standard test value)"
            }
        
        return recommendation


if __name__ == "__main__":
    print("Data Rate Optimizer Test")
    print("=" * 70)
    
    optimizer = RateOptimizer()
    
    # Test 1: Maximum rate for target distance
    print("\nTest 1: Maximum Rate for Target Distance")
    print("-" * 70)
    
    target = 100  # meters
    result = optimizer.find_maximum_rate_for_distance(
        target, Pt=0.5, theta1=30, theta2=50
    )
    
    if result['feasible']:
        print(f"✅ Target distance: {target}m")
        print(f"   Maximum rate: {result['maximum_rate']/1e3:.1f} kbps")
        print(f"   Achieved distance: {result['achieved_distance']:.1f}m")
    else:
        print(f"❌ {result['message']}")
    
    # Test 2: Rate for connectivity (Figure 17 reproduction)
    print("\n\nTest 2: Rate for Target Connectivity (Fig. 17 analysis)")
    print("-" * 70)
    
    result = optimizer.find_rate_for_connectivity(
        S_ROI=1e6, n=300, m=2, target_prob=0.9,
        Pt=0.5, theta1=30, theta2=50
    )
    
    print(f"Target: 90% 2-connectivity with 300 nodes")
    print(f"✅ Maximum rate: {result['maximum_rate']/1e3:.1f} kbps")
    print(f"   Achieved: {result['achieved_connectivity']*100:.2f}%")
    print(f"   Distance: {result['distance']:.1f}m")
    
    # Test 3: Rate impact analysis (Figures 13-14-17)
    print("\n\nTest 3: Rate Impact Analysis")
    print("-" * 70)
    
    Rd_range = np.array([10e3, 30e3, 50e3, 70e3, 100e3, 120e3])
    analysis = optimizer.analyze_rate_impact(
        Rd_range, Pt=0.5, theta1=30, theta2=50, S_ROI=1e6
    )
    
    print(f"{'Rd(kbps)':<10} {'Dist(m)':<12} {'Nodes':<10} {'4-Node(m²)':<15} {'2-Conn%'}")
    print("-" * 70)
    for i, Rd in enumerate(analysis['Rd_values']):
        dist = analysis['distances'][i]
        nodes = analysis['min_nodes'][i]
        cov4 = analysis['coverage_4node'][i]
        conn2 = analysis['connectivity_2'][i]
        print(f"{Rd/1e3:<10.0f} {dist:<12.1f} {nodes:<10} {cov4:<15.0f} {conn2*100:.1f}%")
    
    print(f"\n💡 Observation: Higher rate → shorter distance → more nodes needed")
    
    # Test 4: Rate recommendations
    print("\n\nTest 4: Rate Recommendations")
    print("-" * 70)
    
    priorities = ['speed', 'range', 'balanced']
    
    for priority in priorities:
        req = {
            'Pt': 0.5,
            'theta1': 30,
            'theta2': 50,
            'min_distance': 75,
            'priority': priority
        }
        
        rec = optimizer.recommend_rate(req)
        
        print(f"\nPriority: {priority}")
        print(f"   Recommended: {rec['recommended_rate']/1e3:.1f} kbps")
        print(f"   Distance: {rec['achieved_distance']:.1f}m")
        print(f"   Reason: {rec['reason']}")