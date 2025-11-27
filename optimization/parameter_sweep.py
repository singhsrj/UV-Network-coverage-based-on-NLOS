"""
Multi-dimensional parameter sweep for UV network optimization.
Based on paper's analysis in Section IV.

Simple explanation:
- Try many different combinations of parameters
- Find which combination gives best results
"""

import numpy as np
import sys
import os
from typing import Dict, List, Tuple, Optional
from itertools import product

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.communication_params import CommunicationParams
from models.channel.communication_distance import CommunicationDistanceCalculator
from models.network.effective_coverage import EffectiveCoverageCalculator
from models.connectivity.m_connectivity import MConnectivityCalculator


class ParameterSweep:
    """
    Multi-dimensional parameter sweep for optimization.
    
    Based on paper's parameter ranges:
    - Transmission power: 0.1-0.5W (from Table I and experiments)
    - Data rate: 10-120 kbps (from Figures 13-14, 17)
    - Elevation angles: 30°, 40°, 50° (from Figure 5 and Section IV)
    - Node count: Variable based on coverage requirements
    """
    
    def __init__(self, S_ROI: float = 1e6, target_connectivity: float = 0.9):
        """
        Initialize parameter sweep
        
        Args:
            S_ROI: Region of interest area (default: 1km² from paper)
            target_connectivity: Target connectivity probability (default: 90% from paper)
        """
        self.S_ROI = S_ROI
        self.target_connectivity = target_connectivity
        self.calc = CommunicationDistanceCalculator()
        
        # Define parameter ranges from paper
        self.param_ranges = {
            'Pt': np.array([0.1, 0.2, 0.3, 0.4, 0.5]),  # Transmission power (W)
            'Rd': np.array([10e3, 30e3, 50e3, 70e3, 100e3, 120e3]),  # Data rate (bps)
            'theta1': np.array([30, 40, 50]),  # Transmission elevation (degrees)
            'theta2': np.array([30, 50]),  # Reception elevation (degrees)
        }
    
    def sweep_1d(self, param_name: str, param_values: np.ndarray,
                 fixed_params: Dict) -> Dict:
        """
        Sweep single parameter while keeping others fixed
        
        Simple explanation:
        - Change ONE parameter at a time
        - See how it affects distance, coverage, connectivity
        - Like testing different oven temperatures with same recipe
        
        Args:
            param_name: Name of parameter to sweep ('Pt', 'Rd', 'theta1', 'theta2')
            param_values: Values to test
            fixed_params: Fixed values for other parameters
            
        Returns:
            Dictionary with sweep results
        """
        results = {
            'param_name': param_name,
            'param_values': param_values,
            'distances': [],
            'coverages': [],
            'min_nodes': [],
            'connectivity_1': [],
            'connectivity_2': [],
            'connectivity_3': []
        }
        
        for value in param_values:
            # Set current parameter value
            current_params = fixed_params.copy()
            current_params[param_name] = value
            
            # Calculate distance (Phase 1)
            l = self.calc.calculate_ook_distance(
                current_params['Pt'],
                current_params['Rd'],
                current_params['theta1'],
                current_params['theta2']
            )
            
            # Skip if distance is invalid
            if l <= 0 or not np.isfinite(l):
                results['distances'].append(0)
                results['coverages'].append(0)
                results['min_nodes'].append(0)
                results['connectivity_1'].append(0)
                results['connectivity_2'].append(0)
                results['connectivity_3'].append(0)
                continue
            
            # Calculate coverage requirements (Phase 2)
            n_min = EffectiveCoverageCalculator.calculate_minimum_nodes(self.S_ROI, l)
            coverage = n_min * EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l)
            
            # Calculate connectivity (Phase 3)
            conn_1 = MConnectivityCalculator.calculate_network_connectivity_probability(
                l, n_min, 1, self.S_ROI, sample_points=10
            )
            conn_2 = MConnectivityCalculator.calculate_network_connectivity_probability(
                l, n_min, 2, self.S_ROI, sample_points=10
            )
            conn_3 = MConnectivityCalculator.calculate_network_connectivity_probability(
                l, n_min, 3, self.S_ROI, sample_points=10
            )
            
            results['distances'].append(l)
            results['coverages'].append(coverage)
            results['min_nodes'].append(n_min)
            results['connectivity_1'].append(conn_1)
            results['connectivity_2'].append(conn_2)
            results['connectivity_3'].append(conn_3)
        
        return results
    
    def sweep_2d(self, param1_name: str, param1_values: np.ndarray,
                 param2_name: str, param2_values: np.ndarray,
                 fixed_params: Dict) -> Dict:
        """
        Sweep two parameters simultaneously
        
        Simple explanation:
        - Change TWO parameters together
        - Creates a grid of combinations
        - Like testing temperature AND time combinations
        
        Args:
            param1_name: First parameter name
            param1_values: Values for first parameter
            param2_name: Second parameter name
            param2_values: Values for second parameter
            fixed_params: Fixed values for other parameters
            
        Returns:
            Dictionary with 2D sweep results
        """
        results = {
            'param1_name': param1_name,
            'param1_values': param1_values,
            'param2_name': param2_name,
            'param2_values': param2_values,
            'distances': np.zeros((len(param1_values), len(param2_values))),
            'min_nodes': np.zeros((len(param1_values), len(param2_values))),
            'connectivity_2': np.zeros((len(param1_values), len(param2_values)))
        }
        
        for i, val1 in enumerate(param1_values):
            for j, val2 in enumerate(param2_values):
                current_params = fixed_params.copy()
                current_params[param1_name] = val1
                current_params[param2_name] = val2
                
                # Calculate distance
                l = self.calc.calculate_ook_distance(
                    current_params['Pt'],
                    current_params['Rd'],
                    current_params['theta1'],
                    current_params['theta2']
                )
                
                if l <= 0 or not np.isfinite(l):
                    continue
                
                # Calculate metrics
                n_min = EffectiveCoverageCalculator.calculate_minimum_nodes(self.S_ROI, l)
                conn_2 = MConnectivityCalculator.calculate_network_connectivity_probability(
                    l, n_min, 2, self.S_ROI, sample_points=10
                )
                
                results['distances'][i, j] = l
                results['min_nodes'][i, j] = n_min
                results['connectivity_2'][i, j] = conn_2
        
        return results
    
    def find_optimal_configuration(self, objective: str = 'min_nodes',
                                  constraints: Optional[Dict] = None) -> Dict:
        """
        Find optimal parameter configuration
        
        Simple explanation:
        - Test ALL reasonable combinations
        - Find the best one based on your goal
        - Goals: minimize nodes, maximize connectivity, etc.
        
        Objectives from paper:
        - 'min_nodes': Minimize number of nodes (cost optimization)
        - 'max_connectivity': Maximize 2-connectivity (reliability)
        - 'balanced': Balance between cost and reliability
        
        Args:
            objective: Optimization objective
            constraints: Constraints (e.g., {'min_connectivity': 0.9})
            
        Returns:
            Optimal configuration and metrics
        """
        if constraints is None:
            constraints = {'min_connectivity_2': self.target_connectivity}
        
        best_config = None
        best_score = float('inf') if objective == 'min_nodes' else float('-inf')
        
        # Generate all combinations
        param_combinations = list(product(
            self.param_ranges['Pt'],
            self.param_ranges['Rd'],
            self.param_ranges['theta1'],
            self.param_ranges['theta2']
        ))
        
        results_list = []
        
        for Pt, Rd, theta1, theta2 in param_combinations:
            # Calculate distance
            l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
            
            '''This ensures that any configuration must produce at least 5 meter of communication distance to even be considered.'''
            if l < 1 or not np.isfinite(l):
                continue
            
            # Calculate requirements
            n_min = EffectiveCoverageCalculator.calculate_minimum_nodes(self.S_ROI, l)
            
            # Calculate connectivity
            conn_2 = MConnectivityCalculator.calculate_network_connectivity_probability(
                l, n_min, 2, self.S_ROI, sample_points=10
            )
            
            # Check constraints
            if 'min_connectivity_2' in constraints:
                if conn_2 < constraints['min_connectivity_2']:
                    continue
            
            if 'max_nodes' in constraints:
                if n_min > constraints['max_nodes']:
                    continue
            
            # Calculate objective score
            if objective == 'min_nodes':
                score = n_min
            elif objective == 'max_connectivity':
                score = -conn_2  # Negative for maximization
            elif objective == 'balanced':
                # Balance: minimize nodes while maintaining high connectivity
                score = n_min * (1.1 - conn_2)  # Penalty for low connectivity
            else:
                score = n_min
            
            # Store result
            result = {
                'Pt': Pt,
                'Rd': Rd,
                'theta1': theta1,
                'theta2': theta2,
                'distance': l,
                'min_nodes': n_min,
                'connectivity_2': conn_2,
                'score': score
            }
            results_list.append(result)
            
            # Update best
            if objective == 'min_nodes' or objective == 'balanced':
                if score < best_score:
                    best_score = score
                    best_config = result
            else:  # maximize
                if score > best_score:
                    best_score = score
                    best_config = result
        
        return {
            'optimal': best_config,
            'all_results': results_list,
            'objective': objective,
            'constraints': constraints
        }


if __name__ == "__main__":
    print("Parameter Sweep Test")
    print("=" * 70)
    
    # Initialize with paper's standard area (1 km²)
    sweep = ParameterSweep(S_ROI=1e6, target_connectivity=0.9)
    
    # Test 1D sweep: Power vs Distance (Figure 11-12 from paper)
    print("\n1D Sweep: Transmission Power (Rd=50kbps, 30°-50°)")
    print("-" * 70)
    
    fixed = {'Rd': 50e3, 'theta1': 30, 'theta2': 50}
    result_power = sweep.sweep_1d('Pt', sweep.param_ranges['Pt'], fixed)
    
    print(f"{'Pt (W)':<10} {'Distance (m)':<15} {'Min Nodes':<15} {'2-Conn %'}")
    print("-" * 70)
    for i, Pt in enumerate(result_power['param_values']):
        dist = result_power['distances'][i]
        nodes = result_power['min_nodes'][i]
        conn2 = result_power['connectivity_2'][i]
        print(f"{Pt:<10.1f} {dist:<15.1f} {nodes:<15} {conn2*100:.2f}%")
    
    # Test 1D sweep: Data Rate (Figure 13-14 from paper)
    print("\n\n1D Sweep: Data Rate (Pt=0.5W, 30°-50°)")
    print("-" * 70)
    
    fixed = {'Pt': 0.5, 'theta1': 30, 'theta2': 50}
    result_rate = sweep.sweep_1d('Rd', sweep.param_ranges['Rd'], fixed)
    
    print(f"{'Rd (kbps)':<10} {'Distance (m)':<15} {'Min Nodes':<15} {'2-Conn %'}")
    print("-" * 70)
    for i, Rd in enumerate(result_rate['param_values']):
        dist = result_rate['distances'][i]
        nodes = result_rate['min_nodes'][i]
        conn2 = result_rate['connectivity_2'][i]
        print(f"{Rd/1e3:<10.0f} {dist:<15.1f} {nodes:<15} {conn2*100:.2f}%")
    
    # Find optimal configuration
    print("\n\nOptimal Configuration Search")
    print("-" * 70)
    print("Objective: Minimize nodes with 90% 2-connectivity\n")
    
    optimal = sweep.find_optimal_configuration(
        objective='min_nodes',
        constraints={'min_connectivity_2': 0.9}
    )
    
    if optimal['optimal']:
        opt = optimal['optimal']
        print(f"✅ Optimal Configuration Found:")
        print(f"   Power: {opt['Pt']} W")
        print(f"   Data Rate: {opt['Rd']/1e3:.0f} kbps")
        print(f"   Angles: {opt['theta1']}°-{opt['theta2']}°")
        print(f"   Distance: {opt['distance']:.1f} m")
        print(f"   Required Nodes: {opt['min_nodes']}")
        print(f"   2-Connectivity: {opt['connectivity_2']*100:.2f}%")
    else:
        print("❌ No configuration meets constraints")
    
    # Show top 5 configurations
    print("\n\nTop 5 Configurations (by node count):")
    print("-" * 70)
    sorted_results = sorted(optimal['all_results'], key=lambda x: x['min_nodes'])[:5]
    
    print(f"{'Rank':<6} {'Pt':<8} {'Rd':<10} {'Angles':<12} {'Nodes':<10} {'2-Conn%'}")
    print("-" * 70)
    for i, res in enumerate(sorted_results, 1):
        print(f"{i:<6} {res['Pt']:<8.1f} {res['Rd']/1e3:<10.0f} "
              f"{res['theta1']}°-{res['theta2']}°{'':<4} {res['min_nodes']:<10} {res['connectivity_2']*100:.1f}%")