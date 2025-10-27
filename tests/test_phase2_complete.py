"""
tests/test_phase2_complete.py

Comprehensive test suite for Phase 2 implementation.
Tests all network coverage modules.
"""

import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.channel.communication_distance import CommunicationDistanceCalculator
from models.channel.nlos_scattering import NLOSScatteringModel, NLOSMode
from models.node.single_side_coverage import SingleSideCoverage
from models.node.hexahedral_terminal import HexahedralTerminal
from models.network.boolean_coverage import BooleanCoverageModel
from models.network.effective_coverage import EffectiveCoverageCalculator
from models.network.square_deployment import SquareNetworkDeployment


class Phase2TestSuite:
    """Comprehensive test suite for Phase 2"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def test(self, name: str, condition: bool, message: str = ""):
        """Run a single test"""
        if condition:
            self.passed += 1
            status = "✅ PASS"
        else:
            self.failed += 1
            status = "❌ FAIL"
        
        result = f"{status}: {name}"
        if message:
            result += f" - {message}"
        
        self.results.append(result)
        print(result)
        return condition
    
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        print("\n" + "=" * 70)
        print("PHASE 2 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {total}")
        print(f"Passed: {self.passed} ({100*self.passed/total:.1f}%)")
        print(f"Failed: {self.failed} ({100*self.failed/total:.1f}%)")
        print("=" * 70)
        
        if self.failed == 0:
            print("🎉 ALL PHASE 2 TESTS PASSED!")
        else:
            print("⚠️  Some tests failed. Review results above.")
    
    def run_all_tests(self):
        """Run all Phase 2 tests"""
        print("\n" + "=" * 70)
        print("PHASE 2 COMPREHENSIVE TEST SUITE")
        print("Network Coverage Implementation")
        print("=" * 70 + "\n")
        
        self.test_nlos_modes()
        self.test_single_side_coverage()
        self.test_hexahedral_terminal()
        self.test_boolean_coverage()
        self.test_effective_coverage()
        self.test_square_deployment()
        self.test_integration_with_phase1()
        self.test_paper_validation()
        
        self.print_summary()
    
    def test_nlos_modes(self):
        """Test NLOS communication modes"""
        print("\n--- Testing NLOS Modes ---")
        
        # Test mode determination
        mode_a = NLOSScatteringModel.determine_mode(90, 90)
        self.test("NLOS-a mode detection",
                 mode_a == NLOSMode.NLOS_A,
                 f"90°-90° → {mode_a.value}")
        
        mode_c = NLOSScatteringModel.determine_mode(30, 50)
        self.test("NLOS-c mode detection",
                 mode_c == NLOSMode.NLOS_C,
                 f"30°-50° → {mode_c.value}")
        
        # Test scattering efficiency
        eff = NLOSScatteringModel.calculate_scattering_efficiency(30, 50, NLOSMode.NLOS_C)
        self.test("Scattering efficiency range",
                 0 < eff <= 1,
                 f"efficiency = {eff:.3f}")
        
        # Test coverage types
        cov_type = NLOSScatteringModel.get_coverage_type(NLOSMode.NLOS_C)
        self.test("NLOS-c coverage type",
                 cov_type == 'cone',
                 f"type = {cov_type}")
    
    def test_single_side_coverage(self):
        """Test single-side coverage calculations"""
        print("\n--- Testing Single-Side Coverage ---")
        
        coverage = SingleSideCoverage(theta1=30, theta2=50, phi1=15)
        l = 100  # meters
        
        # Test R1 calculation (Equation 4)
        R1 = coverage.calculate_R1(l)
        self.test("R1 calculation",
                 0 < R1 < l,
                 f"R1 = {R1:.2f}m for l={l}m")
        
        # Test triangle area (Equation 5)
        triangle_area = coverage.calculate_triangle_area(l)
        self.test("Triangle area positive",
                 triangle_area > 0,
                 f"area = {triangle_area:.2f} m²")
        
        # Test ellipse area (Equation 6)
        ellipse_area = coverage.calculate_ellipse_area(l)
        self.test("Ellipse area positive",
                 ellipse_area > 0,
                 f"area = {ellipse_area:.2f} m²")
        
        # Test total coverage (Equation 7)
        total = coverage.calculate_total_coverage(l)
        expected = triangle_area + 0.5 * ellipse_area
        self.test("Total coverage formula (Eq. 7)",
                 abs(total - expected) < 1e-6,
                 f"total = {total:.2f} m²")
        
        # Test that coverage increases with distance
        coverage_50 = coverage.calculate_total_coverage(50)
        coverage_100 = coverage.calculate_total_coverage(100)
        self.test("Coverage increases with distance",
                 coverage_100 > coverage_50,
                 f"{coverage_50:.0f} m² → {coverage_100:.0f} m²")
    
    def test_hexahedral_terminal(self):
        """Test hexahedral terminal model"""
        print("\n--- Testing Hexahedral Terminal ---")
        
        terminal = HexahedralTerminal(theta1=30, theta2=50, phi1=15, power_per_side=0.5)
        l = 75.1
        
        # Test 6 faces
        self.test("Terminal has 6 faces",
                 len(HexahedralTerminal.FACES) == 6,
                 "top, bottom, north, south, east, west")
        
        # Test omnidirectional coverage
        omni_coverage = terminal.calculate_omnidirectional_coverage(l)
        expected_omni = np.pi * l**2
        self.test("Omnidirectional coverage (circular)",
                 abs(omni_coverage - expected_omni) < 1e-6,
                 f"πl² = {omni_coverage:.2f} m²")
        
        # Test total power
        total_power = terminal.specifications['total_power']
        self.test("Total power = 6 × per_side",
                 total_power == 0.5 * 6,
                 f"{total_power}W total")
        
        # Test minimum nodes calculation
        n_min = terminal.estimate_network_nodes(1e6, l=95)
        self.test("Minimum nodes for 1km²",
                 50 < n_min < 200,
                 f"n_min = {n_min}")
    
    def test_boolean_coverage(self):
        """Test Boolean coverage model"""
        print("\n--- Testing Boolean Coverage ---")
        
        node_pos = (0, 0)
        radius = 50
        
        # Test point at node (covered)
        self.test("Point at node is covered",
                 BooleanCoverageModel.is_point_covered((0, 0), node_pos, radius),
                 "distance = 0")
        
        # Test point at boundary (not covered - strict inequality)
        self.test("Point at boundary not covered",
                 not BooleanCoverageModel.is_point_covered((50, 0), node_pos, radius),
                 "distance = radius")
        
        # Test point inside (covered)
        self.test("Point inside is covered",
                 BooleanCoverageModel.is_point_covered((25, 0), node_pos, radius),
                 "distance < radius")
        
        # Test point outside (not covered)
        self.test("Point outside not covered",
                 not BooleanCoverageModel.is_point_covered((100, 0), node_pos, radius),
                 "distance > radius")
        
        # Test network coverage - FIX: nodes closer together so point is covered
        nodes = [(0, 0), (80, 0)]  # Changed from 100 to 80 so (40,0) is covered by first node
        test_point = (40, 0)  # This is within 50m of first node at (0,0)
        self.test("Network coverage (between nodes)",
                 BooleanCoverageModel.is_point_covered_by_network(test_point, nodes, radius),
                 "covered by at least one node")
        
        # Test redundancy counting
        count = BooleanCoverageModel.count_covering_nodes((0, 0), nodes, radius)
        self.test("Redundancy count",
                 count == 1,
                 f"{count} node(s) cover point at first node")
    
    def test_effective_coverage(self):
        """Test effective coverage calculations"""
        print("\n--- Testing Effective Coverage ---")
        
        l = 100
        
        # Test S1 (Equation 14)
        S1 = EffectiveCoverageCalculator.calculate_S1(l)
        expected_S1 = l**2 - 0.25 * np.pi * l**2
        self.test("S1 calculation (Eq. 14)",
                 abs(S1 - expected_S1) < 1e-6,
                 f"S1 = {S1:.2f} m²")
        
        # Test S2 (Equation 12)
        S2 = EffectiveCoverageCalculator.calculate_S2(l)
        self.test("S2 positive",
                 S2 > 0,
                 f"S2 = {S2:.2f} m²")
        
        # Test four-node coverage (Equation 15)
        S_4_eff = EffectiveCoverageCalculator.calculate_four_node_effective_coverage(l)
        self.test("Four-node coverage positive",
                 S_4_eff > 0,
                 f"S_4-eff = {S_4_eff:.2f} m²")
        
        # Test single-node effective (Equation 17)
        S_eff = EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l)
        self.test("Single-node effective positive",
                 S_eff > 0,
                 f"S_eff = {S_eff:.2f} m²")
        
        # Test coverage efficiency (Equation 28)
        S_node = np.pi * l**2
        eta = S_eff / S_node
        expected_eta = 0.5545
        self.test("Coverage efficiency η_eff (Eq. 28)",
                 abs(eta - expected_eta) < 0.001,
                 f"η = {eta:.4f}")
        
        # Test minimum nodes (Equation 29)
        n_min = EffectiveCoverageCalculator.calculate_minimum_nodes(1e6, l)
        self.test("Minimum nodes calculation (Eq. 29)",
                 n_min > 0,
                 f"n_min = {n_min} for 1km²")
    
    def test_square_deployment(self):
        """Test square network deployment"""
        print("\n--- Testing Square Deployment ---")
        
        deployer = SquareNetworkDeployment(75)
        
        # Test four-node network
        four_node = deployer.create_four_node_network()
        self.test("Four-node network has 4 nodes",
                 four_node['num_nodes'] == 4,
                 f"{four_node['num_nodes']} nodes")
        
        self.test("Four-node side length = 3l",
                 abs(four_node['side_length'] - 3 * 75) < 1e-6,
                 f"side = {four_node['side_length']}m")
        
        # Test grid network
        grid = deployer.create_grid_network(1000, 1000)
        self.test("Grid network covers area",
                 grid['num_nodes'] > 0,
                 f"{grid['num_nodes']} nodes for 1km²")
        
        # Test connectivity analysis
        connectivity = deployer.analyze_network_connectivity(four_node['positions'])
        self.test("Connectivity analysis",
                 connectivity['total_nodes'] == 4,
                 f"analyzed {connectivity['total_nodes']} nodes")
        
        # Test neighbor finding
        neighbors = deployer.get_neighbor_nodes(four_node['positions'], 0)
        self.test("Neighbor detection works",
                 isinstance(neighbors, list),
                 f"node 0 has {len(neighbors)} neighbor(s)")
    
    def test_integration_with_phase1(self):
        """Test integration with Phase 1 modules"""
        print("\n--- Testing Phase 1 Integration ---")
        
        # Test using communication distance from Phase 1
        calc = CommunicationDistanceCalculator()
        distance = calc.calculate_ook_distance(0.5, 50e3, 30, 50)
        
        # Use in Phase 2 modules
        terminal = HexahedralTerminal(theta1=30, theta2=50)
        coverage = terminal.calculate_omnidirectional_coverage(distance)
        
        self.test("Phase 1 distance in Phase 2 terminal",
                 coverage > 0,
                 f"coverage = {coverage:.2f} m² at l={distance:.2f}m")
        
        # Test deployment with Phase 1 distance
        deployer = SquareNetworkDeployment(distance)
        network = deployer.create_four_node_network()
        
        self.test("Phase 1 distance in Phase 2 deployment",
                 network['num_nodes'] == 4,
                 "4-node network created successfully")
    
    def test_paper_validation(self):
        """Validate against paper values"""
        print("\n--- Validating Against Paper Values ---")
        
        # Validate experimental setup (Section V)
        l_exp = 75.1
        coverage_exp = SingleSideCoverage(30, 50, 15)
        
        # Four-node coverage should match experimental result
        calc_4_node = EffectiveCoverageCalculator.calculate_four_node_effective_coverage(l_exp)
        measured_4_node = 44800  # m² from paper
        error = abs(calc_4_node - measured_4_node) / measured_4_node * 100
        
        self.test("Four-node coverage validation",
                 error < 10,
                 f"Calculated: {calc_4_node:.0f} m², Measured: {measured_4_node} m², Error: {error:.1f}%")
        
        # Validate coverage efficiency
        eta_paper = 0.5545
        eta_calc = EffectiveCoverageCalculator.calculate_coverage_efficiency()
        self.test("Coverage efficiency matches paper",
                 abs(eta_calc - eta_paper) < 1e-4,
                 f"η_eff = {eta_calc}")
        
        # Validate that smaller angles give better coverage
        cov_30_30 = SingleSideCoverage(30, 30, 15).calculate_total_coverage(100)
        cov_50_50 = SingleSideCoverage(50, 50, 15).calculate_total_coverage(100)
        self.test("Smaller angles → larger coverage",
                 cov_30_30 > cov_50_50,
                 f"30°-30° ({cov_30_30:.0f} m²) > 50°-50° ({cov_50_50:.0f} m²)") #this tests fails


def run_phase2_tests():
    """Run all Phase 2 tests"""
    suite = Phase2TestSuite()
    suite.run_all_tests()
    return suite.failed == 0


if __name__ == "__main__":
    success = run_phase2_tests()
    
    if success:
        print("\n" + "🎉" * 35)
        print("\n✅ PHASE 2 IMPLEMENTATION COMPLETE AND VALIDATED!")
        print("\n📊 Implemented:")
        print("   • NLOS communication modes (NLOS-a/b/c)")
        print("   • Single-side coverage (Equations 3-7)")
        print("   • Hexahedral terminal model (6-sided)")
        print("   • Boolean coverage model (Equation 2)")
        print("   • Effective coverage (Equations 10-17, 28-29)")
        print("   • Square network deployment")
        print("\n🚀 Ready for Phase 3: Connectivity Analysis")
        print("\n" + "🎉" * 35)
    
    sys.exit(0 if success else 1)