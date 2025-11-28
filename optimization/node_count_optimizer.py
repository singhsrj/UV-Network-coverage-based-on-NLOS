"""
Complete network design optimizer.
Combines all optimization modules for end-to-end network design.

Simple explanation:
- Input: Your requirements (area, budget, performance needs)
- Output: Complete network design (power, angles, rate, nodes)
- Like an automated network engineer!
"""

import numpy as np
import sys
import os
from typing import Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from optimization.parameter_sweep import ParameterSweep
from optimization.power_optimizer import PowerOptimizer
from optimization.elevation_optimizer import ElevationOptimizer
from optimization.rate_optimizer import RateOptimizer
from models.connectivity.network_robustness import NetworkRobustnessAnalyzer


class NetworkDesignOptimizer:
    
    def __init__(self):
        self.sweep = None  # Will initialize with specific S_ROI
        self.power_opt = PowerOptimizer()
        self.elevation_opt = ElevationOptimizer()
        self.rate_opt = RateOptimizer()
    
    def design_network(self, requirements: Dict) -> Dict:
        # Extract requirements
        S_ROI = requirements['S_ROI']
        budget_nodes = requirements.get('budget_nodes', None)
        target_conn = requirements.get('target_connectivity', 0.9)
        conn_level = requirements.get('connectivity_level', 2)
        priority = requirements.get('priority', 'balanced')
        
        # Initialize sweep with this area
        self.sweep = ParameterSweep(S_ROI, target_conn)
        
        # Find optimal configuration
        if priority == 'cost':
            # Minimize nodes
            optimal = self.sweep.find_optimal_configuration(
                objective='min_nodes',
                constraints={'min_connectivity_2': target_conn}
            )
        elif priority == 'reliability':
            # Maximize connectivity
            optimal = self.sweep.find_optimal_configuration(
                objective='max_connectivity',
                constraints={'max_nodes': budget_nodes} if budget_nodes else {}
            )
        else:  # balanced
            optimal = self.sweep.find_optimal_configuration(
                objective='balanced',
                constraints={'min_connectivity_2': target_conn}
            )
        
        if not optimal['optimal']:
            return {
                'success': False,
                'message': 'No configuration meets requirements',
                'requirements': requirements
            }
        
        config = optimal['optimal']
        
        # Get robustness analysis
        robustness = NetworkRobustnessAnalyzer.evaluate_robustness(
            config['distance'],
            config['min_nodes'],
            S_ROI
        )
        
        # Get recommendations for improvements
        recommendations = NetworkRobustnessAnalyzer.recommend_improvements(
            config['distance'],
            config['min_nodes'],
            S_ROI
        )
        
        return {
            'success': True,
            'design': {
                'power': config['Pt'],
                'data_rate': config['Rd'],
                'elevation_tx': config['theta1'],
                'elevation_rx': config['theta2'],
                'communication_distance': config['distance'],
                'required_nodes': config['min_nodes'],
                'connectivity_probability': config['connectivity_2']
            },
            'performance': {
                'robustness_score': robustness['score'],
                'robustness_level': robustness['level'],
                'metrics': robustness['metrics']
            },
            'recommendations': recommendations,
            'requirements_met': {
                'area_covered': True,
                'connectivity_target': config['connectivity_2'] >= target_conn,
                'node_budget': config['min_nodes'] <= budget_nodes if budget_nodes else True
            }
        }
    
    def optimize_for_cost(self, S_ROI: float, target_connectivity: float = 0.9) -> Dict:
        requirements = {
            'S_ROI': S_ROI,
            'target_connectivity': target_connectivity,
            'priority': 'cost'
        }
        return self.design_network(requirements)
    
    def optimize_for_reliability(self, S_ROI: float, budget_nodes: int) -> Dict:
        requirements = {
            'S_ROI': S_ROI,
            'budget_nodes': budget_nodes,
            'priority': 'reliability'
        }
        return self.design_network(requirements)
    
    def compare_designs(self, designs: list) -> Dict:
        results = []
        
        for i, design_req in enumerate(designs):
            design_result = self.design_network(design_req)
            if design_result['success']:
                results.append({
                    'name': design_req.get('name', f'Design {i+1}'),
                    'design': design_result['design'],
                    'performance': design_result['performance'],
                    'cost': design_result['design']['required_nodes']
                })
        
        # Find best by different criteria
        best_cost = min(results, key=lambda x: x['cost']) if results else None
        best_reliability = max(results, key=lambda x: x['performance']['robustness_score']) if results else None
        
        return {
            'all_designs': results,
            'best_for_cost': best_cost,
            'best_for_reliability': best_reliability
        }


if __name__ == "__main__":
    print("Complete Network Design Optimizer Test")
    print("=" * 70)
    
    optimizer = NetworkDesignOptimizer()
    
    # Test 1: Cost-optimized design
    print("\nTest 1: Cost-Optimized Design")
    print("-" * 70)
    print("Goal: Minimize nodes while meeting 90% 2-connectivity\n")
    
    result = optimizer.optimize_for_cost(S_ROI=1e6, target_connectivity=0.9)
    
    if result['success']:
        design = result['design']
        perf = result['performance']
        
        print(f"✅ Optimal Design Found:")
        print(f"   Power: {design['power']} W")
        print(f"   Data Rate: {design['data_rate']/1e3:.0f} kbps")
        print(f"   Angles: {design['elevation_tx']}°-{design['elevation_rx']}°")
        print(f"   Distance: {design['communication_distance']:.1f} m")
        print(f"   Required Nodes: {design['required_nodes']}")
        print(f"   Connectivity: {design['connectivity_probability']*100:.2f}%")
        print(f"\n   Robustness: {perf['robustness_level']} ({perf['robustness_score']:.0f}/100)")
    else:
        print(f"❌ {result['message']}")
    
    # Test 2: Reliability-optimized design
    print("\n\nTest 2: Reliability-Optimized Design")
    print("-" * 70)
    print("Goal: Maximum reliability with 100-node budget\n")
    
    result = optimizer.optimize_for_reliability(S_ROI=1e6, budget_nodes=100)
    
    if result['success']:
        design = result['design']
        perf = result['performance']
        
        print(f"✅ Optimal Design Found:")
        print(f"   Power: {design['power']} W")
        print(f"   Data Rate: {design['data_rate']/1e3:.0f} kbps")
        print(f"   Angles: {design['elevation_tx']}°-{design['elevation_rx']}°")
        print(f"   Distance: {design['communication_distance']:.1f} m")
        print(f"   Required Nodes: {design['required_nodes']}")
        print(f"   Connectivity: {design['connectivity_probability']*100:.2f}%")
        print(f"\n   Robustness: {perf['robustness_level']} ({perf['robustness_score']:.0f}/100)")
    
    # Test 3: Custom requirements
    print("\n\nTest 3: Custom Requirements Design")
    print("-" * 70)
    
    custom_req = {
        'S_ROI': 5e5,  # 500m × 500m
        'budget_nodes': 75,
        'target_connectivity': 0.85,
        'priority': 'balanced'
    }
    
    print(f"Requirements:")
    print(f"   Area: {custom_req['S_ROI']:.0e} m² (~700m × 700m)")
    print(f"   Budget: {custom_req['budget_nodes']} nodes")
    print(f"   Target: {custom_req['target_connectivity']*100:.0f}% 2-connectivity\n")
    
    result = optimizer.design_network(custom_req)
    
    if result['success']:
        design = result['design']
        
        print(f"✅ Design Generated:")
        print(f"   Configuration: {design['power']}W, {design['data_rate']/1e3:.0f}kbps, "
              f"{design['elevation_tx']}°-{design['elevation_rx']}°")
        print(f"   Nodes: {design['required_nodes']} (within budget: "
              f"{'✓' if result['requirements_met']['node_budget'] else '✗'})")
        print(f"   Connectivity: {design['connectivity_probability']*100:.2f}% "
              f"(meets target: {'✓' if result['requirements_met']['connectivity_target'] else '✗'})")
        
        if result['recommendations']:
            print(f"\n   Recommendations:")
            for rec in result['recommendations'][:2]:  # Show first 2
                print(f"   • {rec}")
    
    # Test 4: Compare multiple designs
    print("\n\nTest 4: Design Comparison")
    print("-" * 70)
    
    designs_to_compare = [
        {'name': 'Budget', 'S_ROI': 1e6, 'budget_nodes': 50, 'priority': 'cost'},
        {'name': 'Standard', 'S_ROI': 1e6, 'target_connectivity': 0.9, 'priority': 'balanced'},
        {'name': 'Premium', 'S_ROI': 1e6, 'target_connectivity': 0.95, 'priority': 'reliability'}
    ]
    
    comparison = optimizer.compare_designs(designs_to_compare)
    
    print(f"{'Design':<12} {'Nodes':<10} {'Power':<10} {'Rate':<12} {'Robustness'}")
    print("-" * 70)
    for design in comparison['all_designs']:
        print(f"{design['name']:<12} "
              f"{design['cost']:<10} "
              f"{design['design']['power']:<10.1f} "
              f"{design['design']['data_rate']/1e3:<12.0f} "
              f"{design['performance']['robustness_score']:.0f}/100")
    
    if comparison['best_for_cost']:
        print(f"\n🏆 Best for Cost: {comparison['best_for_cost']['name']} "
              f"({comparison['best_for_cost']['cost']} nodes)")
    else:
        print("\n🏆 Best for Cost: No valid design found.")

    if comparison['best_for_reliability']:
        print(f"🏆 Best for Reliability: {comparison['best_for_reliability']['name']} "
              f"(score: {comparison['best_for_reliability']['performance']['robustness_score']:.0f})")
    else:
        print("🏆 Best for Reliability: No valid design found.")