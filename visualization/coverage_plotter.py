# """
# visualization/coverage_plotter.py

# Coverage visualization for UV networks.
# Reproduces Figures 10-15 from the paper.

# Simple explanation:
# - Creates graphs showing how coverage changes
# - With different parameters (power, rate, angles)
# - Helps understand trade-offs visually
# """

# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.patches import Circle, Ellipse
# import sys
# import os
# from typing import Dict, List, Tuple, Optional

# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# from config.communication_params import CommunicationParams
# from models.channel.communication_distance import CommunicationDistanceCalculator
# from models.network.effective_coverage import EffectiveCoverageCalculator
# from models.node.single_side_coverage import SingleSideCoverage


# class CoveragePlotter:
#     """
#     Visualization tools for coverage analysis.
#     Reproduces coverage-related figures from paper.
#     """
    
#     def __init__(self, figsize: Tuple[int, int] = (10, 6)):
#         """
#         Initialize plotter
        
#         Args:
#             figsize: Default figure size
#         """
#         self.figsize = figsize
#         self.calc = CommunicationDistanceCalculator()
        
#         # Style settings
#         plt.style.use('seaborn-v0_8-darkgrid')
#         self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
#     def plot_coverage_vs_divergence(self, 
#                                     Pt: float = 0.5,
#                                     Rd: float = 50e3,
#                                     theta1: float = 30,
#                                     theta2: float = 50,
#                                     phi_range: Optional[np.ndarray] = None,
#                                     save_path: Optional[str] = None) -> plt.Figure:
#         """
#         Plot coverage area vs beam divergence angle
#         Reproduces Figure 10 from paper
        
#         Args:
#             Pt, Rd: Fixed parameters
#             theta1, theta2: Fixed elevation angles
#             phi_range: Range of divergence angles to plot
#             save_path: Path to save figure
            
#         Returns:
#             Figure object
#         """
#         if phi_range is None:
#             phi_range = np.arange(5, 21, 1)
        
#         # Calculate coverage for each divergence angle
#         coverages = []
        
#         for phi1 in phi_range:
#             # Calculate distance
#             l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
            
#             # Calculate single-side coverage with this divergence
#             coverage_model = SingleSideCoverage(theta1, theta2, phi1)
#             coverage = coverage_model.calculate_total_coverage(l)
            
#             coverages.append(coverage)
        
#         # Create plot
#         fig, ax = plt.subplots(figsize=self.figsize)
        
#         ax.plot(phi_range, coverages, 'o-', linewidth=2, markersize=6,
#                 color=self.colors[0], label=f'{theta1}°-{theta2}°')
        
#         ax.set_xlabel('Beam Divergence Angle Φ₁ (degrees)', fontsize=12)
#         ax.set_ylabel('Single-Side Coverage Area (m²)', fontsize=12)
#         ax.set_title(f'Coverage vs Beam Divergence\n(Pt={Pt}W, Rd={Rd/1e3:.0f}kbps)', 
#                     fontsize=14, fontweight='bold')
#         ax.grid(True, alpha=0.3)
#         ax.legend()
        
#         plt.tight_layout()
        
#         if save_path:
#             plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
#         return fig
    
#     def plot_coverage_vs_power(self,
#                               Rd: float = 50e3,
#                               elevation_combinations: Optional[List[Tuple[int, int]]] = None,
#                               Pt_range: Optional[np.ndarray] = None,
#                               network_type: str = '4-node',
#                               save_path: Optional[str] = None) -> plt.Figure:
#         """
#         Plot coverage vs transmission power
#         Reproduces Figures 11-12 from paper
        
#         Args:
#             Rd: Data rate (bps)
#             elevation_combinations: List of (theta1, theta2) tuples
#             Pt_range: Power range to plot
#             network_type: '4-node' or 'single-node'
#             save_path: Path to save figure
            
#         Returns:
#             Figure object
#         """
#         if elevation_combinations is None:
#             elevation_combinations = CommunicationParams.ELEVATION_COMBINATIONS
        
#         if Pt_range is None:
#             Pt_range = np.linspace(0.1, 0.5, 20)
        
#         fig, ax = plt.subplots(figsize=self.figsize)
        
#         for i, (theta1, theta2) in enumerate(elevation_combinations):
#             coverages = []
            
#             for Pt in Pt_range:
#                 # Calculate distance
#                 l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
                
#                 # Calculate coverage based on network type
#                 if network_type == '4-node':
#                     coverage = EffectiveCoverageCalculator.calculate_four_node_effective_coverage(l)
#                 else:  # single-node
#                     coverage = EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l)
                
#                 coverages.append(coverage / 1e4)  # Convert to 10⁴ m²
            
#             label = f'{theta1}°-{theta2}°'
#             ax.plot(Pt_range, coverages, 'o-', linewidth=2, markersize=4,
#                    color=self.colors[i % len(self.colors)], label=label)
        
#         title_prefix = '4-Node' if network_type == '4-node' else 'Single-Node'
#         ax.set_xlabel('Transmission Power Pt (W)', fontsize=12)
#         ax.set_ylabel(f'{title_prefix} Coverage (×10⁴ m²)', fontsize=12)
#         ax.set_title(f'{title_prefix} Coverage vs Power\n(Rd={Rd/1e3:.0f}kbps)', 
#                     fontsize=14, fontweight='bold')
#         ax.grid(True, alpha=0.3)
#         ax.legend()
        
#         plt.tight_layout()
        
#         if save_path:
#             plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
#         return fig
    
#     def plot_coverage_vs_rate(self,
#                              Pt: float = 0.5,
#                              elevation_combinations: Optional[List[Tuple[int, int]]] = None,
#                              Rd_range: Optional[np.ndarray] = None,
#                              network_type: str = '4-node',
#                              save_path: Optional[str] = None) -> plt.Figure:
#         """
#         Plot coverage vs data rate
#         Reproduces Figures 13-14 from paper
        
#         Args:
#             Pt: Transmission power (W)
#             elevation_combinations: List of (theta1, theta2) tuples
#             Rd_range: Data rate range to plot
#             network_type: '4-node' or 'single-node'
#             save_path: Path to save figure
            
#         Returns:
#             Figure object
#         """
#         if elevation_combinations is None:
#             elevation_combinations = CommunicationParams.ELEVATION_COMBINATIONS
        
#         if Rd_range is None:
#             Rd_range = np.linspace(10e3, 120e3, 20)
        
#         fig, ax = plt.subplots(figsize=self.figsize)
        
#         for i, (theta1, theta2) in enumerate(elevation_combinations):
#             coverages = []
            
#             for Rd in Rd_range:
#                 # Calculate distance
#                 l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
                
#                 # Calculate coverage based on network type
#                 if network_type == '4-node':
#                     coverage = EffectiveCoverageCalculator.calculate_four_node_effective_coverage(l)
#                 else:  # single-node
#                     coverage = EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l)
                
#                 coverages.append(coverage / 1e4)  # Convert to 10⁴ m²
            
#             label = f'{theta1}°-{theta2}°'
#             ax.plot(Rd_range/1e3, coverages, 'o-', linewidth=2, markersize=4,
#                    color=self.colors[i % len(self.colors)], label=label)
        
#         title_prefix = '4-Node' if network_type == '4-node' else 'Single-Node'
#         ax.set_xlabel('Data Rate Rd (kbps)', fontsize=12)
#         ax.set_ylabel(f'{title_prefix} Coverage (×10⁴ m²)', fontsize=12)
#         ax.set_title(f'{title_prefix} Coverage vs Data Rate\n(Pt={Pt}W)', 
#                     fontsize=14, fontweight='bold')
#         ax.grid(True, alpha=0.3)
#         ax.legend()
        
#         plt.tight_layout()
        
#         if save_path:
#             plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
#         return fig
    
#     def plot_network_coverage_map(self,
#                                   node_positions: List[Tuple[float, float]],
#                                   coverage_radius: float,
#                                   region_bounds: Tuple[float, float, float, float],
#                                   grid_resolution: int = 100,
#                                   save_path: Optional[str] = None) -> plt.Figure:
#         """
#         Plot 2D coverage map of network
        
#         Args:
#             node_positions: List of (x, y) node positions
#             coverage_radius: Coverage radius for each node
#             region_bounds: (x_min, x_max, y_min, y_max)
#             grid_resolution: Grid resolution
#             save_path: Path to save figure
            
#         Returns:
#             Figure object
#         """
#         from models.network.boolean_coverage import BooleanCoverageModel
        
#         # Generate coverage map
#         coverage_map = BooleanCoverageModel.generate_coverage_map(
#             region_bounds, node_positions, coverage_radius, grid_resolution
#         )
        
#         redundancy_map = BooleanCoverageModel.generate_redundancy_map(
#             region_bounds, node_positions, coverage_radius, grid_resolution
#         )
        
#         x_min, x_max, y_min, y_max = region_bounds
        
#         # Create figure with two subplots
#         fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
#         # Plot 1: Boolean coverage
#         im1 = ax1.imshow(coverage_map, extent=[x_min, x_max, y_min, y_max],
#                         origin='lower', cmap='RdYlGn', alpha=0.6, vmin=0, vmax=1)
        
#         # Plot nodes
#         for i, (x, y) in enumerate(node_positions):
#             circle = Circle((x, y), coverage_radius, fill=False, 
#                           edgecolor='blue', linewidth=1, linestyle='--', alpha=0.5)
#             ax1.add_patch(circle)
#             ax1.plot(x, y, 'ko', markersize=8)
#             ax1.text(x, y, f'{i+1}', ha='center', va='center', 
#                     color='white', fontsize=8, fontweight='bold')
        
#         ax1.set_xlabel('X (m)', fontsize=12)
#         ax1.set_ylabel('Y (m)', fontsize=12)
#         ax1.set_title('Network Coverage Map', fontsize=14, fontweight='bold')
#         ax1.grid(True, alpha=0.3)
#         plt.colorbar(im1, ax=ax1, label='Covered')
        
#         # Plot 2: Redundancy map
#         im2 = ax2.imshow(redundancy_map, extent=[x_min, x_max, y_min, y_max],
#                         origin='lower', cmap='YlOrRd', alpha=0.8)
        
#         # Plot nodes
#         for i, (x, y) in enumerate(node_positions):
#             ax2.plot(x, y, 'ko', markersize=8)
#             ax2.text(x, y, f'{i+1}', ha='center', va='center',
#                     color='white', fontsize=8, fontweight='bold')
        
#         ax2.set_xlabel('X (m)', fontsize=12)
#         ax2.set_ylabel('Y (m)', fontsize=12)
#         ax2.set_title('Coverage Redundancy Map', fontsize=14, fontweight='bold')
#         ax2.grid(True, alpha=0.3)
#         plt.colorbar(im2, ax=ax2, label='Number of Covering Nodes')
        
#         plt.tight_layout()
        
#         if save_path:
#             plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
#         return fig
    
#     def create_coverage_comparison_dashboard(self,
#                                             Pt_default: float = 0.5,
#                                             Rd_default: float = 50e3,
#                                             save_path: Optional[str] = None) -> plt.Figure:
#         """
#         Create comprehensive coverage comparison dashboard
#         Combines multiple coverage analyses in one figure
        
#         Args:
#             Pt_default, Rd_default: Default parameters
#             save_path: Path to save figure
            
#         Returns:
#             Figure object
#         """
#         fig = plt.figure(figsize=(16, 10))
#         gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
#         # Get elevation combinations
#         combos = CommunicationParams.ELEVATION_COMBINATIONS
        
#         # Plot 1: Coverage vs Power (4-node)
#         ax1 = fig.add_subplot(gs[0, 0])
#         Pt_range = np.linspace(0.1, 0.5, 15)
#         for i, (theta1, theta2) in enumerate(combos):
#             coverages = []
#             for Pt in Pt_range:
#                 l = self.calc.calculate_ook_distance(Pt, Rd_default, theta1, theta2)
#                 cov = EffectiveCoverageCalculator.calculate_four_node_effective_coverage(l)
#                 coverages.append(cov / 1e4)
#             ax1.plot(Pt_range, coverages, 'o-', label=f'{theta1}°-{theta2}°',
#                     color=self.colors[i % len(self.colors)])
#         ax1.set_xlabel('Power (W)')
#         ax1.set_ylabel('4-Node Coverage (×10⁴ m²)')
#         ax1.set_title('Coverage vs Power')
#         ax1.legend()
#         ax1.grid(True, alpha=0.3)
        
#         # Plot 2: Coverage vs Rate (4-node)
#         ax2 = fig.add_subplot(gs[0, 1])
#         Rd_range = np.linspace(10e3, 120e3, 15)
#         for i, (theta1, theta2) in enumerate(combos):
#             coverages = []
#             for Rd in Rd_range:
#                 l = self.calc.calculate_ook_distance(Pt_default, Rd, theta1, theta2)
#                 cov = EffectiveCoverageCalculator.calculate_four_node_effective_coverage(l)
#                 coverages.append(cov / 1e4)
#             ax2.plot(Rd_range/1e3, coverages, 'o-', label=f'{theta1}°-{theta2}°',
#                     color=self.colors[i % len(self.colors)])
#         ax2.set_xlabel('Data Rate (kbps)')
#         ax2.set_ylabel('4-Node Coverage (×10⁴ m²)')
#         ax2.set_title('Coverage vs Data Rate')
#         ax2.legend()
#         ax2.grid(True, alpha=0.3)
        
#         # Plot 3: Coverage vs Power (single-node)
#         ax3 = fig.add_subplot(gs[1, 0])
#         for i, (theta1, theta2) in enumerate(combos):
#             coverages = []
#             for Pt in Pt_range:
#                 l = self.calc.calculate_ook_distance(Pt, Rd_default, theta1, theta2)
#                 cov = EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l)
#                 coverages.append(cov / 1e3)
#             ax3.plot(Pt_range, coverages, 'o-', label=f'{theta1}°-{theta2}°',
#                     color=self.colors[i % len(self.colors)])
#         ax3.set_xlabel('Power (W)')
#         ax3.set_ylabel('Single-Node Coverage (×10³ m²)')
#         ax3.set_title('Single-Node Coverage vs Power')
#         ax3.legend()
#         ax3.grid(True, alpha=0.3)
        
#         # Plot 4: Coverage vs Rate (single-node)
#         ax4 = fig.add_subplot(gs[1, 1])
#         for i, (theta1, theta2) in enumerate(combos):
#             coverages = []
#             for Rd in Rd_range:
#                 l = self.calc.calculate_ook_distance(Pt_default, Rd, theta1, theta2)
#                 cov = EffectiveCoverageCalculator.calculate_single_node_effective_coverage(l)
#                 coverages.append(cov / 1e3)
#             ax4.plot(Rd_range/1e3, coverages, 'o-', label=f'{theta1}°-{theta2}°',
#                     color=self.colors[i % len(self.colors)])
#         ax4.set_xlabel('Data Rate (kbps)')
#         ax4.set_ylabel('Single-Node Coverage (×10³ m²)')
#         ax4.set_title('Single-Node Coverage vs Data Rate')
#         ax4.legend()
#         ax4.grid(True, alpha=0.3)
        
#         fig.suptitle('UV Network Coverage Analysis Dashboard', 
#                     fontsize=16, fontweight='bold', y=0.995)
        
#         if save_path:
#             plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
#         return fig


# if __name__ == "__main__":
#     print("Coverage Plotter Test")
#     print("=" * 70)
    
#     plotter = CoveragePlotter()
    
#     # Test 1: Coverage vs divergence angle
#     print("\n1. Generating coverage vs divergence plot...")
#     fig1 = plotter.plot_coverage_vs_divergence()
#     print("   ✓ Figure created")
    
#     # Test 2: Coverage vs power (4-node)
#     print("\n2. Generating 4-node coverage vs power plot...")
#     fig2 = plotter.plot_coverage_vs_power(network_type='4-node')
#     print("   ✓ Figure created")
    
#     # Test 3: Coverage vs rate (single-node)
#     print("\n3. Generating single-node coverage vs rate plot...")
#     fig3 = plotter.plot_coverage_vs_rate(network_type='single-node')
#     print("   ✓ Figure created")
    
#     # Test 4: Network coverage map
#     print("\n4. Generating network coverage map...")
#     from models.network.square_deployment import SquareNetworkDeployment
#     deployer = SquareNetworkDeployment(75)
#     network = deployer.create_four_node_network()
#     fig4 = plotter.plot_network_coverage_map(
#         network['positions'],
#         75,
#         (0, 225, 0, 225)
#     )
#     print("   ✓ Figure created")
    
#     # Test 5: Dashboard
#     print("\n5. Generating coverage comparison dashboard...")
#     fig5 = plotter.create_coverage_comparison_dashboard()
#     print("   ✓ Dashboard created")
    
#     print("\n✅ All visualization tests completed!")
#     print("💡 Figures ready for display")
    
#     plt.show()


"""
visualization/coverage_plotter.py

Coverage visualization for UV networks.
Reproduces Figures 10-15 from the paper.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from typing import Dict, List, Tuple, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config.communication_params import CommunicationParams
from models.channel.communication_distance import CommunicationDistanceCalculator

class CoveragePlotter:
    """
    Visualization tools for coverage analysis.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (10, 6)):
        self.figsize = figsize
        self.calc = CommunicationDistanceCalculator()
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def calculate_effective_coverage(self, l: float) -> float:
        """
        Calculate effective coverage area for a 4-node square network.
        Formula derived in paper Equation (10).
        S_4-eff = (1 + sqrt(3) + 5/3 * pi) * l^2
        """
        coeff = 1 + np.sqrt(3) + (5/3 * np.pi)
        return coeff * (l ** 2)

    def plot_coverage_vs_power(self, Rd=50e3, combinations=None, save_path=None):
        """Reproduce Figure 11: Effective coverage vs Power"""
        if combinations is None:
            combinations = [(30, 30), (50, 30), (30, 50), (50, 50)]
            
        Pt_range = np.linspace(0.01, 0.5, 20)
        fig, ax = plt.subplots(figsize=self.figsize)
        
        markers = ['+', 's', 'o', '*']
        
        for i, (theta1, theta2) in enumerate(combinations):
            areas = []
            for Pt in Pt_range:
                l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
                area = self.calculate_effective_coverage(l)
                areas.append(area)
            
            ax.plot(Pt_range, areas, marker=markers[i % len(markers)], 
                   label=f'θ1={theta1}°, θ2={theta2}°')
            
        ax.set_xlabel('Transmission Power (W)')
        ax.set_ylabel('4-node Effective Coverage Area (m²)')
        ax.set_title('Effective Coverage Area vs Transmission Power')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        
        if save_path:
            plt.savefig(save_path, dpi=300)
        return fig

    def plot_coverage_vs_rate(self, Pt=0.5, combinations=None, save_path=None):
        """Reproduce Figure 13: Effective coverage vs Data Rate"""
        if combinations is None:
            combinations = [(30, 30), (50, 30), (30, 50), (50, 50)]
            
        Rd_range = np.linspace(10e3, 120e3, 20)
        fig, ax = plt.subplots(figsize=self.figsize)
        
        markers = ['+', 's', 'o', '*']
        
        for i, (theta1, theta2) in enumerate(combinations):
            areas = []
            for Rd in Rd_range:
                l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
                area = self.calculate_effective_coverage(l)
                areas.append(area)
            
            ax.plot(Rd_range/1e3, areas, marker=markers[i % len(markers)], 
                   label=f'θ1={theta1}°, θ2={theta2}°')
            
        ax.set_yscale('log')
        ax.set_xlabel('Data Rate (kbps)')
        ax.set_ylabel('4-node Effective Coverage Area (m²)')
        ax.set_title('Effective Coverage Area vs Data Rate')
        ax.legend()
        ax.grid(True, which='both', alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300)
        return fig

if __name__ == "__main__":
    cp = CoveragePlotter()
    print("Generating coverage plots...")
    cp.plot_coverage_vs_power(save_path='visualization/coverage_power_sim.png')
    cp.plot_coverage_vs_rate(save_path='visualization/coverage_rate_sim.png')
    print("Done.")