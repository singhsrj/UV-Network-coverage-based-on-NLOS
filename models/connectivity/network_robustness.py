"""
Network robustness and reliability analysis.
Combines all connectivity metrics for practical network evaluation.

Simple explanation:
- Robustness = Can the network survive node failures?
- Reliability = What's the chance the network works?
- This module answers: "How good is my network design?"
"""

import numpy as np
import sys
import os
from typing import Dict, List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from models.connectivity.m_connectivity import MConnectivityCalculator
from models.connectivity.probability_density import ProbabilityDensityFunction


class NetworkRobustnessAnalyzer:
    """
    Analyze network robustness and reliability.
    
    Simple explanation:
    - Takes network parameters
    - Calculates how robust/reliable it is
    - Gives recommendations for improvement
    """
    
    @staticmethod
    def evaluate_robustness(l: float, n: int, area: float) -> Dict:
        """
        Evaluate overall network robustness
        
        Simple explanation:
        - Calculates multiple robustness metrics
        - Gives overall "health score"
        - Like a report card for your network
        
        Args:
            l: Communication distance (meters)
            n: Number of nodes
            area: Network area (m²)
            
        Returns:
            Comprehensive robustness report
        """
        # Calculate connectivity probabilities
        conn_1 = MConnectivityCalculator.calculate_network_connectivity_probability(
            l, n, 1, area
        )
        conn_2 = MConnectivityCalculator.calculate_network_connectivity_probability(
            l, n, 2, area
        )
        conn_3 = MConnectivityCalculator.calculate_network_connectivity_probability(
            l, n, 3, area
        )
        
        # Calculate expected neighbors
        expected_neighbors = ProbabilityDensityFunction.calculate_expected_neighbors(
            n, area, l
        )
        
        # Calculate isolation probability
        prob_isolated = ProbabilityDensityFunction.calculate_isolation_probability(
            n, area, l
        )
        
        # Robustness score (0-100)
        # Weighted average of different metrics
        score = (
            conn_1 * 20 +  # Basic connectivity (20%)
            conn_2 * 40 +  # Robust connectivity (40%)
            conn_3 * 20 +  # High redundancy (20%)
            (1 - prob_isolated) * 10 +  # No isolation (10%)
            min(expected_neighbors / 5, 1.0) * 10  # Good neighbor count (10%)
        )
        
        # Robustness level
        if score >= 85:
            level = "Excellent"
            color = ""
        elif score >= 70:
            level = "Good"
            color = ""
        elif score >= 50:
            level = "Fair"
            color = ""
        else:
            level = "Poor"
            color = ""
        
        return {
            'score': score,
            'level': level,
            'color': color,
            'metrics': {
                '1-connectivity': conn_1,
                '2-connectivity': conn_2,
                '3-connectivity': conn_3,
                'expected_neighbors': expected_neighbors,
                'isolation_probability': prob_isolated
            },
            'meets_standards': {
                'basic_connectivity_90': conn_1 >= 0.9,
                'robust_connectivity_90': conn_2 >= 0.9,
                'high_redundancy_90': conn_3 >= 0.9
            }
        }
    
    @staticmethod
    def analyze_failure_tolerance(l: float, n: int, area: float,
                                  failure_rate: float = 0.1) -> Dict:
        """
        Analyze network tolerance to node failures
        
        Simple explanation:
        - "What if some nodes break?"
        - Can the network still work?
        - How many failures can we tolerate?
        
        Args:
            l: Communication distance
            n: Number of nodes
            area: Network area
            failure_rate: Expected failure rate (e.g., 0.1 = 10%)
            
        Returns:
            Failure tolerance analysis
        """
        # Number of expected failures
        expected_failures = int(n * failure_rate)
        
        # Remaining nodes after failure
        n_remaining = n - expected_failures
        
        # Connectivity after failures
        conn_after_failure = {}
        for m in [1, 2, 3]:
            conn_after_failure[m] = MConnectivityCalculator.calculate_network_connectivity_probability(
                l, n_remaining, m, area
            )
        
        # Can network survive?
        survives = conn_after_failure[1] >= 0.8  # 80% connectivity threshold
        
        return {
            'failure_rate': failure_rate,
            'expected_failures': expected_failures,
            'remaining_nodes': n_remaining,
            'connectivity_after_failure': conn_after_failure,
            'network_survives': survives,
            'resilience_rating': 'High' if survives and conn_after_failure[2] >= 0.7 else 'Medium' if survives else 'Low'
        }
    
    @staticmethod
    def recommend_improvements(l: float, n: int, area: float) -> List[str]:
        """
        Generate improvement recommendations
        
        Simple explanation:
        - Analyzes current network
        - Suggests what to improve
        - Practical advice for network planning
        
        Args:
            l: Communication distance
            n: Number of nodes
            area: Network area
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Get current robustness
        robustness = NetworkRobustnessAnalyzer.evaluate_robustness(l, n, area)
        metrics = robustness['metrics']
        
        # Check connectivity levels
        if metrics['1-connectivity'] < 0.9:
            recommendations.append(
                f"⚠️  Basic connectivity is {metrics['1-connectivity']*100:.1f}% (target: 90%). "
                f"Add {int(n * 0.2)} more nodes or increase transmission power."
            )
        
        if metrics['2-connectivity'] < 0.9:
            recommendations.append(
                f"⚠️  2-connectivity is {metrics['2-connectivity']*100:.1f}% (target: 90% for robustness). "
                f"Add {int(n * 0.3)} more nodes for redundancy."
            )
        
        # Check expected neighbors
        if metrics['expected_neighbors'] < 3:
            recommendations.append(
                f"⚠️  Low neighbor count ({metrics['expected_neighbors']:.1f}). "
                f"Network is sparse. Consider: "
                f"(1) Increase power to extend range, "
                f"(2) Add {int(n * 0.5)} more nodes, or "
                f"(3) Reduce coverage area."
            )
        
        # Check isolation risk
        if metrics['isolation_probability'] > 0.05:
            recommendations.append(
                f"⚠️  High isolation risk ({metrics['isolation_probability']*100:.2f}%). "
                f"Some nodes may be unreachable. Add more nodes or increase communication distance."
            )
        
        # If everything is good
        if len(recommendations) == 0:
            recommendations.append(
                f"✅ Network configuration is excellent! "
                f"Robustness score: {robustness['score']:.0f}/100. "
                f"All connectivity requirements met."
            )
        
        # Add optimization suggestion
        if robustness['score'] < 85 and metrics['2-connectivity'] >= 0.8:
            recommendations.append(
                f"💡 Optimization opportunity: Current score {robustness['score']:.0f}/100. "
                f"Small improvements can reach 'Excellent' level."
            )
        
        return recommendations
    
    @staticmethod
    def compare_scenarios(scenarios: List[Dict]) -> Dict:
        """
        Compare multiple network scenarios
        
        Simple explanation:
        - "Option A: 100 nodes with 0.5W power"
        - "Option B: 150 nodes with 0.3W power"
        - Which is better?
        
        Args:
            scenarios: List of dicts with 'name', 'l', 'n', 'area'
            
        Returns:
            Comparison results
        """
        results = {}
        
        for scenario in scenarios:
            name = scenario['name']
            l = scenario['l']
            n = scenario['n']
            area = scenario['area']
            
            robustness = NetworkRobustnessAnalyzer.evaluate_robustness(l, n, area)
            
            results[name] = {
                'parameters': scenario,
                'robustness': robustness,
                'cost_estimate': n  # Simple cost = number of nodes
            }
        
        # Find best scenario
        best_name = max(results.keys(), key=lambda k: results[k]['robustness']['score'])
        
        return {
            'scenarios': results,
            'best_option': best_name,
            'best_score': results[best_name]['robustness']['score']
        }
    
    @staticmethod
    def generate_report(l: float, n: int, area: float) -> str:
        """
        Generate human-readable network robustness report
        
        Args:
            l: Communication distance
            n: Number of nodes
            area: Network area
            
        Returns:
            Formatted report string
        """
        robustness = NetworkRobustnessAnalyzer.evaluate_robustness(l, n, area)
        failure_analysis = NetworkRobustnessAnalyzer.analyze_failure_tolerance(l, n, area)
        recommendations = NetworkRobustnessAnalyzer.recommend_improvements(l, n, area)
        
        report = []
        report.append("=" * 70)
        report.append("UV NETWORK ROBUSTNESS REPORT")
        report.append("=" * 70)
        
        report.append("\n📊 NETWORK CONFIGURATION")
        report.append(f"   Communication Distance: {l} m")
        report.append(f"   Number of Nodes: {n}")
        report.append(f"   Coverage Area: {area:.0e} m² ({np.sqrt(area):.0f}m × {np.sqrt(area):.0f}m)")
        
        report.append(f"\n{robustness['color']} OVERALL ROBUSTNESS: {robustness['level'].upper()}")
        report.append(f"   Score: {robustness['score']:.0f}/100")
        
        report.append("\n📈 CONNECTIVITY METRICS")
        metrics = robustness['metrics']
        report.append(f"   1-Connectivity: {metrics['1-connectivity']*100:.2f}% {'✓' if metrics['1-connectivity'] >= 0.9 else '✗'}")
        report.append(f"   2-Connectivity: {metrics['2-connectivity']*100:.2f}% {'✓' if metrics['2-connectivity'] >= 0.9 else '✗'}")
        report.append(f"   3-Connectivity: {metrics['3-connectivity']*100:.2f}% {'✓' if metrics['3-connectivity'] >= 0.9 else '✗'}")
        report.append(f"   Expected Neighbors: {metrics['expected_neighbors']:.2f}")
        report.append(f"   Isolation Risk: {metrics['isolation_probability']*100:.4f}%")
        
        report.append("\n🛡️  FAILURE TOLERANCE")
        report.append(f"   Expected Failures (10%): {failure_analysis['expected_failures']} nodes")
        report.append(f"   Remaining Nodes: {failure_analysis['remaining_nodes']}")
        report.append(f"   Network Survives: {'YES ✓' if failure_analysis['network_survives'] else 'NO ✗'}")
        report.append(f"   Resilience Rating: {failure_analysis['resilience_rating']}")
        
        report.append("\n💡 RECOMMENDATIONS")
        for rec in recommendations:
            report.append(f"   {rec}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


if __name__ == "__main__":
    print("Network Robustness Analyzer Test")
    print("=" * 70)
    
    # Test with typical configuration
    l = 95
    n = 100
    area = 1e6
    
    # Evaluate robustness
    print("\nRobustness Evaluation:")
    print("-" * 70)
    
    robustness = NetworkRobustnessAnalyzer.evaluate_robustness(l, n, area)
    
    print(f"{robustness['color']} Robustness Level: {robustness['level']}")
    print(f"Score: {robustness['score']:.1f}/100")
    print(f"\nMetrics:")
    for metric, value in robustness['metrics'].items():
        if 'probability' in metric:
            print(f"  {metric}: {value*100:.4f}%")
        else:
            print(f"  {metric}: {value:.2f}")
    
    # Failure tolerance
    print("\n\nFailure Tolerance Analysis:")
    print("-" * 70)
    
    failure = NetworkRobustnessAnalyzer.analyze_failure_tolerance(l, n, area)
    
    print(f"Expected failures (10% rate): {failure['expected_failures']} nodes")
    print(f"Network survives: {'YES ✓' if failure['network_survives'] else 'NO ✗'}")
    print(f"Resilience: {failure['resilience_rating']}")
    
    # Recommendations
    print("\n\nRecommendations:")
    print("-" * 70)
    
    recommendations = NetworkRobustnessAnalyzer.recommend_improvements(l, n, area)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    # Generate full report
    print("\n\nFull Report:")
    print(NetworkRobustnessAnalyzer.generate_report(l, n, area))
    
    # Compare scenarios
    print("\n\nScenario Comparison:")
    print("-" * 70)
    
    scenarios = [
        {'name': 'Budget (50 nodes, 95m)', 'l': 95, 'n': 50, 'area': 1e6},
        {'name': 'Standard (100 nodes, 95m)', 'l': 95, 'n': 100, 'area': 1e6},
        {'name': 'Premium (150 nodes, 95m)', 'l': 95, 'n': 150, 'area': 1e6},
    ]
    
    comparison = NetworkRobustnessAnalyzer.compare_scenarios(scenarios)
    
    print(f"{'Scenario':<30} {'Score':<10} {'2-Conn%':<15} {'Cost'}")
    print("-" * 70)
    
    for name, result in comparison['scenarios'].items():
        score = result['robustness']['score']
        conn2 = result['robustness']['metrics']['2-connectivity'] * 100
        cost = result['cost_estimate']
        marker = "🏆" if name == comparison['best_option'] else "  "
        
        print(f"{marker} {name:<28} {score:<10.1f} {conn2:<15.2f} {cost} nodes")
    
    print(f"\n🏆 Best Option: {comparison['best_option']}")
    print(f"   Score: {comparison['best_score']:.1f}/100")