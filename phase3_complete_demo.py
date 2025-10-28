"""
Comprehensive demonstration of Phase 3 functionality.
Shows connectivity analysis and network robustness evaluation.
"""

import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.channel.communication_distance import CommunicationDistanceCalculator
from models.network.effective_coverage import EffectiveCoverageCalculator
from models.connectivity.probability_density import ProbabilityDensityFunction
from models.connectivity.adjacent_nodes import AdjacentNodesCalculator
from models.connectivity.m_connectivity import MConnectivityCalculator
from models.connectivity.network_robustness import NetworkRobustnessAnalyzer


def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def example_1_probability_density():
    """Example 1: Understanding node distribution"""
    print_section("Example 1: Where Are The Nodes? (Probability Density)")
    
    print("\nImagine 100 devices spread across 1 km²:")
    print("  • Question: What's the density?")
    print("  • Answer: 100 devices / 1,000,000 m² = 0.0001 devices/m²")
    print("  • Or: 1 device per 100m × 100m area")
    
    n = 100
    area = 1e6
    
    density = ProbabilityDensityFunction.uniform_square(0, 0, n, area)
    
    print(f"\n📊 Probability Density (Equation 18):")
    print(f"   U(x,y) = n / S_ROI = {n} / {area:.0e} = {density:.2e} nodes/m²")
    print(f"   This means: 0.01 nodes per 100m²")
    
    # Expected neighbors
    l = 95  # communication distance
    exp_neighbors = ProbabilityDensityFunction.calculate_expected_neighbors(n, area, l)
    
    print(f"\n📊 Expected Neighbors:")
    print(f"   Communication range: {l}m")
    print(f"   Coverage per node: π × {l}² = {np.pi * l**2:.0f} m²")
    print(f"   Density: {density:.2e} nodes/m²")
    print(f"   Expected neighbors: {exp_neighbors:.2f}")
    print(f"   Interpretation: Each node can talk to ~{exp_neighbors:.0f} others on average")
    
    # Isolation probability
    prob_iso = ProbabilityDensityFunction.calculate_isolation_probability(n, area, l)
    
    print(f"\n📊 Isolation Risk:")
    print(f"   P(node has NO neighbors) = {prob_iso:.6f}")
    print(f"   That's {prob_iso*100:.4f}% chance")
    
    if prob_iso < 0.01:
        print(f"   ✅ Very low risk - excellent!")
    elif prob_iso < 0.05:
        print(f"   ⚠️  Some risk - consider more nodes")
    else:
        print(f"   ❌ High risk - definitely need more nodes!")


def example_2_adjacent_nodes():
    """Example 2: Neighbor connectivity"""
    print_section("Example 2: How Many Neighbors Does Each Node Have?")
    
    print("\nFor any node, we want to know:")
    print("  • How likely is it to have at least 1 neighbor?")
    print("  • How likely is it to have at least 2 neighbors? (redundancy!)")
    print("  • How likely is it to have at least 3 neighbors? (high redundancy!)")
    
    n = 100
    area = 1e6
    l = 95
    
    # Center node
    tx_center = np.sqrt(2) * 500
    phi_center = np.pi / 4
    
    print(f"\n📊 Node at Center of Network:")
    print(f"   Position: (500m, 500m)")
    
    analysis_center = AdjacentNodesCalculator.analyze_node_position(
        tx_center, phi_center, l, n, area
    )
    
    print(f"   Expected neighbors: {analysis_center['expected_neighbors']:.2f}")
    print(f"\n   Connectivity Probabilities:")
    print(f"   • P(≥1 neighbor): {analysis_center['probabilities']['at_least_1']*100:.2f}% (basic connectivity)")
    print(f"   • P(≥2 neighbors): {analysis_center['probabilities']['at_least_2']*100:.2f}% (robust!)")
    print(f"   • P(≥3 neighbors): {analysis_center['probabilities']['at_least_3']*100:.2f}% (very robust!)")
    
    # Edge node
    tx_edge = 100
    phi_edge = 0
    
    print(f"\n📊 Node at Edge of Network:")
    print(f"   Position: (100m, 0m)")
    
    analysis_edge = AdjacentNodesCalculator.analyze_node_position(
        tx_edge, phi_edge, l, n, area
    )
    
    print(f"   Expected neighbors: {analysis_edge['expected_neighbors']:.2f}")
    print(f"\n   Connectivity Probabilities:")
    print(f"   • P(≥1 neighbor): {analysis_edge['probabilities']['at_least_1']*100:.2f}%")
    print(f"   • P(≥2 neighbors): {analysis_edge['probabilities']['at_least_2']*100:.2f}%")
    print(f"   • P(≥3 neighbors): {analysis_edge['probabilities']['at_least_3']*100:.2f}%")
    
    print(f"\n💡 Key Insight:")
    print(f"   Center nodes: {analysis_center['expected_neighbors']:.1f} neighbors")
    print(f"   Edge nodes: {analysis_edge['expected_neighbors']:.1f} neighbors")
    print(f"   Center nodes are better connected! (As expected)")


def example_3_m_connectivity():
    """Example 3: Network-wide connectivity"""
    print_section("Example 3: Is The WHOLE Network Connected? (m-Connectivity)")
    
    print("\nm-connectivity means EVERY node has at least m neighbors:")
    print("  • 1-connected: Everyone has ≥1 neighbor (basic)")
    print("  • 2-connected: Everyone has ≥2 neighbors (robust - recommended!)")
    print("  • 3-connected: Everyone has ≥3 neighbors (very robust)")
    
    n = 100
    area = 1e6
    l = 95
    
    print(f"\n📊 Network Configuration:")
    print(f"   Nodes: {n}")
    print(f"   Area: 1km × 1km")
    print(f"   Communication distance: {l}m")
    
    # Calculate Q_n,≥m for each m
    print(f"\n📊 Step 1: Q_n,≥m (Equation 25)")
    print(f"   Q_n,≥m = Probability that ANY RANDOM node has ≥m neighbors\n")
    
    Q_values = {}
    for m in range(1, 4):
        Q_values[m] = MConnectivityCalculator.calculate_Q_n_m(l, n, m, area)
        print(f"   Q_n,≥{m} = {Q_values[m]:.4f} ({Q_values[m]*100:.2f}%)")
    
    # Calculate network connectivity
    print(f"\n📊 Step 2: P(network is m-connected) (Equation 27)")
    print(f"   For WHOLE network to be m-connected, EVERY node must have ≥m neighbors")
    print(f"   Formula: P(m-connected) = (Q_n,≥m)^n\n")
    
    for m in range(1, 4):
        prob = MConnectivityCalculator.calculate_network_connectivity_probability(
            l, n, m, area
        )
        status = "✅ Good" if prob >= 0.9 else "⚠️  Low"
        print(f"   P({m}-connected) = ({Q_values[m]:.4f})^{n} = {prob:.6f} ({prob*100:.2f}%) {status}")
    
    print(f"\n💡 Interpretation:")
    print(f"   • If we deploy this network 100 times")
    analysis = MConnectivityCalculator.analyze_connectivity_levels(l, n, area)
    prob_2 = analysis[2]['network_probability']
    print(f"   • About {prob_2*100:.0f} times it will be 2-connected (robust)")
    print(f"   • About {(1-prob_2)*100:.0f} times it won't be (some nodes isolated)")


def example_4_required_nodes():
    """Example 4: How many nodes do I need?"""
    print_section("Example 4: Planning - How Many Nodes Do I Need?")
    
    print("\nGoal: 90% chance of 2-connectivity (robust network)")
    print("Question: How many nodes?")
    
    l = 95
    area = 1e6
    
    print(f"\nNetwork parameters:")
    print(f"   Communication distance: {l}m")
    print(f"   Area: 1km × 1km")
    print(f"   Target: 90% chance of 2-connectivity")
    
    print(f"\n🔍 Searching for minimum nodes...")
    
    result = MConnectivityCalculator.find_required_nodes(
        l, area, m=2, target_probability=0.9
    )
    
    print(f"\n✅ Result:")
    print(f"   Required nodes: {result['required_nodes']}")
    print(f"   Achieved probability: {result['achieved_probability']*100:.2f}%")
    print(f"   Meets target: {'YES ✓' if result['achieved_probability'] >= 0.9 else 'NO ✗'}")
    
    # Compare with Phase 2 minimum
    from models.network.effective_coverage import EffectiveCoverageCalculator
    coverage_min = EffectiveCoverageCalculator.calculate_minimum_nodes(area, l)
    
    print(f"\n📊 Comparison:")
    print(f"   Phase 2 minimum (coverage only): {coverage_min} nodes")
    print(f"   Phase 3 minimum (2-connectivity): {result['required_nodes']} nodes")
    
    if result['required_nodes'] > coverage_min:
        extra = result['required_nodes'] - coverage_min
        print(f"   Extra nodes for connectivity: {extra} ({extra/coverage_min*100:.0f}% more)")
        print(f"   💡 Coverage alone isn't enough - need more for connectivity!")
    else:
        print(f"   💡 Coverage requirement already ensures connectivity!")


def example_5_robustness_analysis():
    """Example 5: Complete network evaluation"""
    print_section("Example 5: Complete Network Robustness Analysis")
    
    print("\nLet's evaluate a complete network design:")
    
    n = 100
    area = 1e6
    l = 95
    
    print(f"   • {n} nodes")
    print(f"   • 1km × 1km area")
    print(f"   • {l}m communication range")
    
    print(f"\n🔍 Running comprehensive analysis...")
    
    robustness = NetworkRobustnessAnalyzer.evaluate_robustness(l, n, area)
    
    print(f"\n{robustness['color']} OVERALL RATING: {robustness['level'].upper()}")
    print(f"   Robustness Score: {robustness['score']:.1f}/100")
    
    print(f"\n📊 Detailed Metrics:")
    metrics = robustness['metrics']
    print(f"   1-Connectivity: {metrics['1-connectivity']*100:.2f}% {'✅' if metrics['1-connectivity'] >= 0.9 else '❌'}")
    print(f"   2-Connectivity: {metrics['2-connectivity']*100:.2f}% {'✅' if metrics['2-connectivity'] >= 0.9 else '❌'}")
    print(f"   3-Connectivity: {metrics['3-connectivity']*100:.2f}%")
    print(f"   Expected Neighbors: {metrics['expected_neighbors']:.2f}")
    print(f"   Isolation Risk: {metrics['isolation_probability']*100:.4f}%")
    
    # Failure tolerance
    print(f"\n🛡️  Failure Tolerance Test:")
    print(f"   Scenario: 10% of nodes fail")
    
    failure = NetworkRobustnessAnalyzer.analyze_failure_tolerance(l, n, area, 0.1)
    
    print(f"   Expected failures: {failure['expected_failures']} nodes")
    print(f"   Remaining: {failure['remaining_nodes']} nodes")
    print(f"   Network survives: {'YES ✅' if failure['network_survives'] else 'NO ❌'}")
    print(f"   Resilience: {failure['resilience_rating']}")


def example_6_recommendations():
    """Example 6: Getting improvement recommendations"""
    print_section("Example 6: What Should I Improve?")
    
    print("\nLet's ask the system for recommendations...")
    
    # Test with suboptimal network
    n = 60  # Too few
    area = 1e6
    l = 95
    
    print(f"\n📊 Testing Network:")
    print(f"   {n} nodes in 1km × 1km")
    print(f"   {l}m range")
    
    recommendations = NetworkRobustnessAnalyzer.recommend_improvements(l, n, area)
    
    print(f"\n💡 System Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec}")
    
    # Test with good network
    print(f"\n\n📊 Testing Better Network:")
    n_better = 150
    print(f"   {n_better} nodes in 1km × 1km")
    print(f"   {l}m range")
    
    recommendations_better = NetworkRobustnessAnalyzer.recommend_improvements(l, n_better, area)
    
    print(f"\n💡 System Recommendations:")
    for i, rec in enumerate(recommendations_better, 1):
        print(f"\n{i}. {rec}")


def example_7_scenario_comparison():
    """Example 7: Comparing different designs"""
    print_section("Example 7: Which Design Is Better?")
    
    print("\nComparing three network designs:")
    
    scenarios = [
        {
            'name': 'Budget (50 nodes)',
            'l': 95,
            'n': 50,
            'area': 1e6
        },
        {
            'name': 'Standard (100 nodes)',
            'l': 95,
            'n': 100,
            'area': 1e6
        },
        {
            'name': 'Premium (150 nodes)',
            'l': 95,
            'n': 150,
            'area': 1e6
        }
    ]
    
    comparison = NetworkRobustnessAnalyzer.compare_scenarios(scenarios)
    
    print(f"\n📊 Comparison Results:")
    print(f"{'Design':<25} {'Score':<10} {'2-Conn %':<12} {'Cost':<12} {'Rating'}")
    print("-" * 70)
    
    for name, result in comparison['scenarios'].items():
        score = result['robustness']['score']
        conn2 = result['robustness']['metrics']['2-connectivity'] * 100
        cost = result['cost_estimate']
        level = result['robustness']['level']
        marker = "🏆" if name == comparison['best_option'] else "  "
        
        print(f"{marker} {name:<23} {score:<10.1f} {conn2:<12.2f} {cost:<12} {level}")
    
    print(f"\n🏆 Best Overall: {comparison['best_option']}")
    print(f"   Score: {comparison['best_score']:.1f}/100")
    
    print(f"\n💡 Trade-offs:")
    print(f"   • Budget: Cheapest but poor connectivity")
    print(f"   • Standard: Balanced cost vs performance")
    print(f"   • Premium: Best reliability but costs more")


def example_8_complete_workflow():
    """Example 8: Complete planning workflow"""
    print_section("Example 8: Complete Network Planning Workflow")
    
    print("\n🎯 Mission: Design UV network for 1km² area")
    print("   Requirements:")
    print("   • Full coverage")
    print("   • 90% chance of 2-connectivity (robust)")
    print("   • Use 0.5W power, 50kbps data rate, 30°-50° angles")
    
    # Step 1: Phase 1 - Calculate distance
    print(f"\n📍 STEP 1: Calculate Communication Distance (Phase 1)")
    calc = CommunicationDistanceCalculator()
    distance = calc.calculate_ook_distance(0.5, 50e3, 30, 50)
    print(f"   Result: {distance:.1f}m")
    
    # Step 2: Phase 2 - Calculate nodes for coverage
    print(f"\n📍 STEP 2: Calculate Nodes for Coverage (Phase 2)")
    area = 1e6
    nodes_coverage = EffectiveCoverageCalculator.calculate_minimum_nodes(area, distance)
    print(f"   Minimum for coverage: {nodes_coverage} nodes")
    
    # Step 3: Phase 3 - Check connectivity
    print(f"\n📍 STEP 3: Check Connectivity (Phase 3)")
    prob_2conn_min = MConnectivityCalculator.calculate_network_connectivity_probability(
        distance, nodes_coverage, 2, area
    )
    print(f"   2-connectivity with {nodes_coverage} nodes: {prob_2conn_min*100:.2f}%")
    
    if prob_2conn_min < 0.9:
        print(f"   ⚠️  Below 90% target!")
        print(f"   Finding required nodes...")
        
        result = MConnectivityCalculator.find_required_nodes(
            distance, area, 2, 0.9
        )
        nodes_final = result['required_nodes']
        prob_final = result['achieved_probability']
        
        print(f"   Need {nodes_final} nodes for 90% 2-connectivity")
        print(f"   Achieved: {prob_final*100:.2f}%")
    else:
        nodes_final = nodes_coverage
        prob_final = prob_2conn_min
        print(f"   ✅ Already meets 90% target!")
    
    # Step 4: Generate report
    print(f"\n📍 STEP 4: Generate Robustness Report")
    print(f"\n" + NetworkRobustnessAnalyzer.generate_report(distance, nodes_final, area))
    
    # Final summary
    print(f"\n📋 FINAL DESIGN:")
    print(f"   • Communication distance: {distance:.1f}m")
    print(f"   • Number of devices: {nodes_final}")
    print(f"   • Area covered: 1km × 1km")
    print(f"   • 2-connectivity probability: {prob_final*100:.2f}%")
    print(f"   • Status: ✅ Ready to deploy!")


def main():
    """Run all Phase 3 examples"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  PHASE 3: CONNECTIVITY ANALYSIS - COMPLETE DEMO".center(68) + "█")
    print("█" + "  Are All Devices Connected?".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    try:
        example_1_probability_density()
        input("\nPress Enter to continue...")
        
        example_2_adjacent_nodes()
        input("\nPress Enter to continue...")
        
        example_3_m_connectivity()
        input("\nPress Enter to continue...")
        
        example_4_required_nodes()
        input("\nPress Enter to continue...")
        
        example_5_robustness_analysis()
        input("\nPress Enter to continue...")
        
        example_6_recommendations()
        input("\nPress Enter to continue...")
        
        example_7_scenario_comparison()
        input("\nPress Enter to continue...")
        
        example_8_complete_workflow()
        
        print_section("PHASE 3 DEMONSTRATION COMPLETE")
        print("\n✅ You now understand:")
        print("  • How to calculate node connectivity probabilities")
        print("  • What m-connectivity means (1, 2, 3-connected)")
        print("  • How to evaluate network robustness")
        print("  • How to get improvement recommendations")
        print("  • Complete workflow: Distance → Coverage → Connectivity")
        
        print("\n🎓 Key Takeaways:")
        print("  • Coverage ≠ Connectivity!")
        print("  • 2-connectivity is the sweet spot (robust but achievable)")
        print("  • Center nodes are better connected than edge nodes")
        print("  • More nodes = better connectivity (but costs more)")
        
        print("\n🎉 You now have a COMPLETE UV network planning system!")
        print("   Phase 1: Calculate distance ✅")
        print("   Phase 2: Plan coverage ✅")
        print("   Phase 3: Verify connectivity ✅")
        
        print("\n🔜 Next: Phase 4 - Parameter Optimization")
        print("     (Automate finding the best power/angle/node combination)")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demonstration interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()