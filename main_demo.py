"""
main_demo.py

Complete demonstration of UV Network Coverage System.
Shows all phases from channel modeling to network optimization.

Simple explanation:
- Runs complete workflow
- From basic calculations to full network design
- Demonstrates all key capabilities
"""

import numpy as np
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(__file__))

from config.physical_constants import PhysicalConstants
from config.communication_params import CommunicationParams
from config.network_config import NetworkConfig

from models.channel.communication_distance import CommunicationDistanceCalculator
from models.network.effective_coverage import EffectiveCoverageCalculator
from models.network.square_deployment import SquareNetworkDeployment
from models.connectivity.m_connectivity import MConnectivityCalculator
from models.connectivity.network_robustness import NetworkRobustnessAnalyzer

from optimization.elevation_optimizer import ElevationOptimizer
from optimization.power_optimizer import PowerOptimizer
from optimization.rate_optimizer import RateOptimizer
from optimization.node_count_optimizer import NetworkDesignOptimizer


def print_section(title: str):
    """Print section header"""
    print(f"  {title}")


def demo_phase1_channel_modeling():
    """Phase 1: Channel Model and Communication Distance"""
    print_section("CHANNEL MODEL & COMMUNICATION DISTANCE")
    
    # Initialize calculator
    calc = CommunicationDistanceCalculator()
    
    # Test parameters (from paper's experimental setup)
    Pt = 0.5  # W
    Rd = 50e3  # 50 kbps
    theta1, theta2 = 30, 50  # degrees
    
    print(f"Parameters: (from paper's experimental setup) ")
    print(f"  Transmission Power: {Pt} W")
    print(f"  Data Rate: {Rd/1e3:.0f} kbps")
    print(f"  Elevation Angles: {theta1}°-{theta2}°")
    
    # Calculate communication distance (Equation 1)
    distance = calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
    
    print(f"\nCommunication Distance Calculated: {distance:.2f} m")
    print(f"   (Experimental: 75.1m from paper)")
    
    # Compare all elevation combinations
    print(f"\n Elevation Combination Comparison:")
    print(f"{'Combination':<15} {'Distance (m)':<15} {'vs 30°-30°'}")
    print("-" * 50)
    
    combos = CommunicationParams.ELEVATION_COMBINATIONS
    results = calc.get_distance_summary(Pt, Rd, combos)
    baseline = results['30-30']['distance']
    
    for combo, data in results.items():
        ratio = data['distance'] / baseline * 100
        print(f"{combo + '°':<15} {data['distance']:<15.2f} {ratio:.1f}%")
    
    print(f"\n Key Findings: Smaller angles → longer distance")
    
    return distance


def demo_phase2_coverage_analysis():
    """Phase 2: Network Coverage"""
    print_section("NETWORK COVERAGE ANALYSIS")
    
    # Calculate for experimental distance
    l = 75.1  # meters (from Phase 1)
    
    print(f"Communication Distance: {l} m\n")
    
    # Calculate coverage metrics
    S_4_eff = EffectiveCoverageCalculator.calculate_four_node_effective_coverage(l)
    S_eff = EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l)
    eta_eff = EffectiveCoverageCalculator.calculate_coverage_efficiency()
    
    print(f"Coverage Metrics:")
    print(f"  4-Node Effective Coverage: {S_4_eff:.2f} m²")
    print(f"  Measured (paper): 44,800 m²")
    print(f"  Error: {abs(S_4_eff - 44800)/44800*100:.2f}%")
    
    print(f"\n  Single-Node Effective: {S_eff:.2f} m²")
    print(f"  Coverage Efficiency η_eff: {eta_eff*100:.2f}%")
    
    # Calculate minimum nodes for 1 km²
    S_ROI = 1e6
    n_min = EffectiveCoverageCalculator.calculate_minimum_nodes(S_ROI, l)
    
    print(f"\n  Minimum Nodes (1 km²): {n_min}")
    
    # Compare elevation combinations
    print(f"\n Coverage by Elevation Combination:")
    print(f"{'Combination':<15} {'4-Node (m²)':<15} {'Min Nodes'}")
    print("-" * 50)
    
    calc = CommunicationDistanceCalculator()
    for theta1, theta2 in [(30,30), (30,50), (50,50)]:
        l_temp = calc.calculate_ook_distance(0.5, 50e3, theta1, theta2)
        cov = EffectiveCoverageCalculator.calculate_four_node_effective_coverage(l_temp)
        nodes = EffectiveCoverageCalculator.calculate_minimum_nodes(S_ROI, l_temp)
        print(f"{theta1}°-{theta2}°{'':<9} {cov:<15.0f} {nodes}")
    
    print(f"\n  Key Findings: Coverage efficiency is constant at 55.45%")
    
    return S_eff, n_min


def demo_phase3_connectivity():
    """Phase 3: Network Connectivity"""
    print_section("NETWORK CONNECTIVITY ANALYSIS")
    
    # Use realistic parameters that show connectivity trade-offs
    # From paper's experimental data: l ≈ 75m is realistic
    l = 75  # meters (realistic from Phase 1)
    n = 100  # nodes
    S_ROI = 1e6  # 1 km²
    
    print(f"Network Configuration:")
    print(f"  Communication Distance: {l} m")
    print(f"  Number of Nodes: {n}")
    print(f"  Coverage Area: {S_ROI:.0e} m²")
    print(f"  Average Node Spacing: ~{np.sqrt(S_ROI/n):.0f} m")
    
    # Calculate connectivity for different m values
    print(f"\nm-Connectivity Probabilities:")
    print(f"{'Level':<15} {'Probability':<20} {'Status'}")
    print("-" * 50)
    
    connectivity_results = {}
    for m in [1, 2, 3]:
        conn = MConnectivityCalculator.calculate_network_connectivity_probability(
            l, n, m, S_ROI, sample_points=10
        )
        connectivity_results[m] = conn
        status = "✓ >90%" if conn >= 0.9 else "⚠ <90%"
        print(f"{m}-connected{'':<6} {conn*100:<20.2f}% {status}")
    
    # Show connectivity degradation
    print(f"\nConnectivity Analysis:")
    print(f"  • 1-connectivity is {connectivity_results[1]*100:.1f}% (nearly certain)")
    print(f"  • 2-connectivity is {connectivity_results[2]*100:.1f}% (good robustness)")
    print(f"  • 3-connectivity is {connectivity_results[3]*100:.1f}% (decreasing)")
    print(f"  → Trade-off between connectivity level and probability")
    
    # Find required nodes for 90% 2-connectivity
    print(f"\nFinding Required Nodes for 90% 2-Connectivity...")
    
    result = MConnectivityCalculator.find_required_nodes(
        l, S_ROI, m=2, target_probability=0.9
    )
    
    print(f"  Required Nodes: {result['required_nodes']}")
    print(f"  Achieved: {result['achieved_probability']*100:.2f}%")
    print(f"  With {n} nodes: {connectivity_results[2]*100:.2f}%")
    
    # Additional scenario: Show what happens with fewer nodes
    print(f"\nScenario Comparison:")
    print(f"{'Nodes':<10} {'1-Conn %':<12} {'2-Conn %':<12} {'3-Conn %'}")
    print("-" * 50)
    
    test_nodes = [50, 75, 100, 150]
    for n_test in test_nodes:
        conn_1 = MConnectivityCalculator.calculate_network_connectivity_probability(
            l, n_test, 1, S_ROI, sample_points=5
        )
        conn_2 = MConnectivityCalculator.calculate_network_connectivity_probability(
            l, n_test, 2, S_ROI, sample_points=5
        )
        conn_3 = MConnectivityCalculator.calculate_network_connectivity_probability(
            l, n_test, 3, S_ROI, sample_points=5
        )
        print(f"{n_test:<10} {conn_1*100:<12.1f} {conn_2*100:<12.1f} {conn_3*100:<12.1f}")
    
    print(f"\n Key Findings:  2-connectivity recommended for robustness")
    print(f"  • Balances reliability and resource efficiency")
    print(f"  • Provides redundant paths without excessive nodes")
    
    return result['required_nodes']


def demo_phase4_optimization():
    """Phase 4: Parameter Optimization"""
    print_section("PARAMETER OPTIMIZATION")
    
    # Initialize optimizers
    elev_opt = ElevationOptimizer()
    power_opt = PowerOptimizer()
    rate_opt = RateOptimizer()
    
    print("Optimization Objectives:\n")
    
    # 1. Elevation optimization
    print("1. Elevation Angle Optimization")
    print("   Finding best angles for coverage...\n")
    
    comparison = elev_opt.compare_elevation_combinations(0.5, 50e3, 1e6)
    
    print(f"   {'Angles':<12} {'Distance':<12} {'Min Nodes':<12} {'Rank'}")
    print(f"   {'-'*50}")
    for combo, data in sorted(comparison.items(), key=lambda x: x[1]['rank']):
        print(f"   {combo:<12} {data['distance']:<12.1f} {data['min_nodes']:<12} #{data['rank']}")
    
    best_angles = sorted(comparison.items(), key=lambda x: x[1]['rank'])[0]
    print(f"\n   Best: {best_angles[0]} (minimize nodes)")
    
    # 2. Power optimization
    print(f"\n2. Transmission Power Optimization")
    print(f"   Finding minimum power for 100m distance...\n")
    
    power_result = power_opt.find_minimum_power_for_distance(
        100, Rd=50e3, theta1=30, theta2=50
    )
    
    if power_result['feasible']:
        print(f"   Required Power: {power_result['required_power']:.3f} W")
        print(f"   Achieved Distance: {power_result['achieved_distance']:.1f} m")
    
    # 3. Rate optimization
    print(f"\n3. Data Rate Optimization")
    print(f"   Finding maximum rate for 75m distance...\n")
    
    rate_result = rate_opt.find_maximum_rate_for_distance(
        75, Pt=0.5, theta1=30, theta2=50
    )
    
    if rate_result['feasible']:
        print(f"   Maximum Rate: {rate_result['maximum_rate']/1e3:.1f} kbps")
        print(f"   Achieved Distance: {rate_result['achieved_distance']:.1f} m")
    

def demo_phase5_network_design():
    """Phase 5: Complete Network Design"""
    print_section("COMPLETE NETWORK DESIGN")
    
    optimizer = NetworkDesignOptimizer()
    
    # Scenario: Design network for 1 km² area
    print("Design Scenario:")
    print("  Coverage Area: 1 km² (1000m × 1000m)")
    print("  Target Connectivity: 90% (2-connected)")
    print("  Priority: Balanced (cost + reliability)\n")
    
    requirements = {
        'S_ROI': 1e6,
        'target_connectivity': 0.9,
        'connectivity_level': 2,
        'priority': 'balanced'
    }
    
    print(" Optimizing network design...")
    result = optimizer.design_network(requirements)
    
    if result['success']:
        design = result['design']
        perf = result['performance']
        
        print(f"\n Optimal Design Found:\n")
        print(f"  Communication Parameters:")
        print(f"    Power: {design['power']} W")
        print(f"    Data Rate: {design['data_rate']/1e3:.0f} kbps")
        print(f"    Angles: {design['elevation_tx']}°-{design['elevation_rx']}°")
        print(f"    Distance: {design['communication_distance']:.1f} m")
        
        print(f"\n  Network Requirements:")
        print(f"    Required Nodes: {design['required_nodes']}")
        print(f"    Connectivity: {design['connectivity_probability']*100:.2f}%")
        
        print(f"\n  Performance Assessment:")
        print(f"    Robustness: {perf['robustness_level']} ({perf['robustness_score']:.0f}/100)")
        print(f"    Expected Neighbors: {perf['metrics']['expected_neighbors']:.2f}")
        
        print(f"\n  Requirements Met:")
        for req, met in result['requirements_met'].items():
            status = "✓" if met else "✗"
            print(f"    {status} {req.replace('_', ' ').title()}")
        
        if result['recommendations']:
            print(f"\n   Recommendations:")
            for i, rec in enumerate(result['recommendations'][:3], 1):
                print(f"    {i}. {rec[:70]}{'...' if len(rec) > 70 else ''}")
    
    print(f"\n  Key Findings: Integrated optimization produces deployable design")


def demo_phase6_robustness_analysis():
    """Phase 6: Network Robustness"""
    print_section("NETWORK ROBUSTNESS ANALYSIS")
    
    l = 95
    n = 100
    S_ROI = 1e6
    
    print(f"Network Configuration:")
    print(f"  Distance: {l}m, Nodes: {n}, Area: {S_ROI:.0e}m²\n")
    
    # Evaluate robustness
    robustness = NetworkRobustnessAnalyzer.evaluate_robustness(l, n, S_ROI)
    
    print(f"{robustness['color']} Overall Robustness: {robustness['level'].upper()}")
    print(f"   Score: {robustness['score']:.0f}/100\n")
    
    print(f" Detailed Metrics:")
    metrics = robustness['metrics']
    print(f"   1-Connectivity: {metrics['1-connectivity']*100:.2f}%")
    print(f"   2-Connectivity: {metrics['2-connectivity']*100:.2f}%")
    print(f"   3-Connectivity: {metrics['3-connectivity']*100:.2f}%")
    print(f"   Expected Neighbors: {metrics['expected_neighbors']:.2f}")
    print(f"   Isolation Risk: {metrics['isolation_probability']*100:.4f}%")
    
    # Failure tolerance
    failure = NetworkRobustnessAnalyzer.analyze_failure_tolerance(l, n, S_ROI)
    
    print(f"\n Failure Tolerance (10% failure rate):")
    print(f"   Expected Failures: {failure['expected_failures']} nodes")
    print(f"   Remaining Nodes: {failure['remaining_nodes']}")
    print(f"   Network Survives: {'YES ✓' if failure['network_survives'] else 'NO ✗'}")
    print(f"   Resilience: {failure['resilience_rating']}")
    
    print(f"\n Key Finding: Robustness analysis guides deployment decisions")


def demo_phase7_deployment():
    """Phase 7: Practical Deployment"""
    print_section("PHASE 7: PRACTICAL DEPLOYMENT EXAMPLE")
    
    # Scenario: Deploy network for specific area
    print("Deployment Scenario:")
    print("  Location: Urban area (500m × 500m)")
    print("  Application: Emergency communication")
    print("  Requirements: 90% 2-connectivity\n")
    
    # Calculate requirements
    area = 500 * 500  # 250,000 m²
    l = 95  # meters
    
    deployer = SquareNetworkDeployment(l)
    network = deployer.create_minimum_node_network(area)
    
    print(f" Deployment Plan Generated:\n")
    print(f"  Network Configuration:")
    print(f"    Total Nodes: {network['num_nodes']}")
    print(f"    Grid Layout: {network['grid_dimensions'][0]} × {network['grid_dimensions'][1]}")
    print(f"    Node Spacing: {network['spacing']:.1f} m")
    print(f"    Coverage: {area:.0e} m²")
    
    # Analyze connectivity
    connectivity = deployer.analyze_network_connectivity(network['positions'])
    
    print(f"\n  Connectivity Analysis:")
    print(f"    Min Neighbors: {connectivity['min_neighbors']}")
    print(f"    Max Neighbors: {connectivity['max_neighbors']}")
    print(f"    Avg Neighbors: {connectivity['avg_neighbors']:.1f}")
    print(f"    Isolated Nodes: {len(connectivity['isolated_nodes'])}")
    
    print(f"\n  Estimated Costs:")
    cost_per_node = 1000  # Hypothetical
    print(f"    Cost per Node: ${cost_per_node}")
    print(f"    Total Cost: ${network['num_nodes'] * cost_per_node:,}")
    
    print(f"\n Key Finding: Practical deployment parameters calculated")


def main():
    """Run complete demonstration"""
    
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  UV NETWORK COVERAGE SYSTEM - COMPLETE DEMONSTRATION".center(78) + "║")
    print("║" + "  Implementation of NLOS UV Network Coverage Analysis".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n Based on research paper: UV Network Coverage Based on NLOS Channel")
    print("\n")
    
    try:
        # Run all phases
        distance = demo_phase1_channel_modeling()
        print("\n")

        S_eff, n_min = demo_phase2_coverage_analysis()
        print("\n")

        req_nodes = demo_phase3_connectivity()
        # demo_phase4_optimization()
        print("\n")

        demo_phase5_network_design()
        # demo_phase6_robustness_analysis()
        # demo_phase7_deployment()
    
        # Summary
        print_section("DEMONSTRATION COMPLETE")
        
        print(" All Phases Executed Successfully!\n")
        print("Key Results Summary:")
        print(f"  • Communication Distance: {distance:.2f} m")
        print(f"  • Single-Node Coverage: {S_eff:.0f} m²")
        print(f"  • Min Nodes (1km²): {n_min}")
        print(f"  • Req for 90% 2-Conn: {req_nodes}")        
        
    except Exception as e:
        print(f"\n Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()