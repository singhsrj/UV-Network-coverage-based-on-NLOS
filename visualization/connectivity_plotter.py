# """
# visualization/connectivity_plotter.py

# Connectivity visualization for UV networks.
# Reproduces Figures 16-18 from the paper.

# Simple explanation:
# - Shows how network connectivity changes
# - With different numbers of nodes, power, data rate
# - Helps design robust networks
# """

# import numpy as np
# import matplotlib.pyplot as plt
# import sys
# import os
# from typing import Dict, List, Tuple, Optional

# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# from config.communication_params import CommunicationParams
# from models.channel.communication_distance import CommunicationDistanceCalculator
# from models.connectivity.m_connectivity import MConnectivityCalculator


# class ConnectivityPlotter:
#     """
#     Visualization tools for connectivity analysis.
#     Reproduces connectivity-related figures from paper (Figures 16-18).
#     """
    
#     def __init__(self, figsize: Tuple[int, int] = (10, 6)):
#         """Initialize plotter"""
#         self.figsize = figsize
#         self.calc = CommunicationDistanceCalculator()
        
#         plt.style.use('seaborn-v0_8-darkgrid')
#         self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
#         self.linestyles = ['-', '--', '-.']
    
#     def plot_connectivity_vs_nodes(self,
#                                   Pt: float = 0.5,
#                                   Rd: float = 50e3,
#                                   theta1: float = 30,
#                                   theta2: float = 50,
#                                   S_ROI: float = 1e6,
#                                   n_range: Optional[np.ndarray] = None,
#                                   m_values: List[int] = [1, 2, 3],
#                                   save_path: Optional[str] = None) -> plt.Figure:
#         """
#         Plot connectivity probability vs number of nodes
#         Reproduces Figure 16 from paper
        
#         Args:
#             Pt, Rd, theta1, theta2: Communication parameters
#             S_ROI: Coverage area (m²)
#             n_range: Range of node counts
#             m_values: Connectivity levels to plot
#             save_path: Path to save figure
            
#         Returns:
#             Figure object
#         """
#         if n_range is None:
#             n_range = np.arange(10, 401, 20)
        
#         # Calculate communication distance
#         l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
        
#         fig, ax = plt.subplots(figsize=self.figsize)
        
#         for i, m in enumerate(m_values):
#             connectivities = []
            
#             for n in n_range:
#                 conn = MConnectivityCalculator.calculate_network_connectivity_probability(
#                     l, n, m, S_ROI, sample_points=10
#                 )
#                 connectivities.append(conn * 100)  # Convert to percentage
            
#             ax.plot(n_range, connectivities, 
#                    linestyle=self.linestyles[i % len(self.linestyles)],
#                    linewidth=2, marker='o', markersize=4,
#                    color=self.colors[i % len(self.colors)],
#                    label=f'{m}-connected')
        
#         # Mark 90% threshold
#         ax.axhline(y=90, color='red', linestyle=':', linewidth=2, 
#                   alpha=0.7, label='90% threshold')
        
#         ax.set_xlabel('Number of Nodes n', fontsize=12)
#         ax.set_ylabel('Network Connectivity Probability (%)', fontsize=12)
#         ax.set_title(f'Connectivity vs Number of Nodes\n'
#                     f'(Pt={Pt}W, Rd={Rd/1e3:.0f}kbps, {theta1}°-{theta2}°, l={l:.1f}m)',
#                     fontsize=14, fontweight='bold')
#         ax.set_ylim([0, 105])
#         ax.grid(True, alpha=0.3)
#         ax.legend()
        
#         plt.tight_layout()
        
#         if save_path:
#             plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
#         return fig
    
#     def plot_connectivity_vs_rate(self,
#                                  Pt: float = 0.5,
#                                  n: int = 300,
#                                  theta1: float = 30,
#                                  theta2: float = 50,
#                                  S_ROI: float = 1e6,
#                                  Rd_range: Optional[np.ndarray] = None,
#                                  m_values: List[int] = [1, 2, 3],
#                                  save_path: Optional[str] = None) -> plt.Figure:
#         """
#         Plot connectivity probability vs data rate
#         Reproduces Figure 17 from paper
        
#         Args:
#             Pt: Transmission power (W)
#             n: Number of nodes
#             theta1, theta2: Elevation angles
#             S_ROI: Coverage area (m²)
#             Rd_range: Range of data rates
#             m_values: Connectivity levels
#             save_path: Path to save figure
            
#         Returns:
#             Figure object
#         """
#         if Rd_range is None:
#             Rd_range = np.linspace(10e3, 120e3, 20)
        
#         fig, ax = plt.subplots(figsize=self.figsize)
        
#         for i, m in enumerate(m_values):
#             connectivities = []
            
#             for Rd in Rd_range:
#                 l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
#                 conn = MConnectivityCalculator.calculate_network_connectivity_probability(
#                     l, n, m, S_ROI, sample_points=10
#                 )
#                 connectivities.append(conn * 100)
            
#             ax.plot(Rd_range/1e3, connectivities,
#                    linestyle=self.linestyles[i % len(self.linestyles)],
#                    linewidth=2, marker='o', markersize=4,
#                    color=self.colors[i % len(self.colors)],
#                    label=f'{m}-connected')
        
#         # Mark 90% threshold
#         ax.axhline(y=90, color='red', linestyle=':', linewidth=2,
#                   alpha=0.7, label='90% threshold')
        
#         ax.set_xlabel('Data Rate Rd (kbps)', fontsize=12)
#         ax.set_ylabel('Network Connectivity Probability (%)', fontsize=12)
#         ax.set_title(f'Connectivity vs Data Rate\n'
#                     f'(Pt={Pt}W, n={n}, {theta1}°-{theta2}°)',
#                     fontsize=14, fontweight='bold')
#         ax.set_ylim([0, 105])
#         ax.grid(True, alpha=0.3)
#         ax.legend()
        
#         plt.tight_layout()
        
#         if save_path:
#             plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
#         return fig
    
#     def plot_connectivity_vs_power(self,
#                                   Rd: float = 50e3,
#                                   n: int = 300,
#                                   theta1: float = 30,
#                                   theta2: float = 50,
#                                   S_ROI: float = 1e6,
#                                   Pt_range: Optional[np.ndarray] = None,
#                                   m_values: List[int] = [1, 2, 3],
#                                   save_path: Optional[str] = None) -> plt.Figure:
#         """
#         Plot connectivity probability vs transmission power
#         Reproduces Figure 18 from paper
        
#         Args:
#             Rd: Data rate (bps)
#             n: Number of nodes
#             theta1, theta2: Elevation angles
#             S_ROI: Coverage area (m²)
#             Pt_range: Range of transmission powers
#             m_values: Connectivity levels
#             save_path: Path to save figure
            
#         Returns:
#             Figure object
#         """
#         if Pt_range is None:
#             Pt_range = np.linspace(0.1, 0.5, 20)
        
#         fig, ax = plt.subplots(figsize=self.figsize)
        
#         for i, m in enumerate(m_values):
#             connectivities = []
            
#             for Pt in Pt_range:
#                 l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
#                 conn = MConnectivityCalculator.calculate_network_connectivity_probability(
#                     l, n, m, S_ROI, sample_points=10
#                 )
#                 connectivities.append(conn * 100)
            
#             ax.plot(Pt_range, connectivities,
#                    linestyle=self.linestyles[i % len(self.linestyles)],
#                    linewidth=2, marker='o', markersize=4,
#                    color=self.colors[i % len(self.colors)],
#                    label=f'{m}-connected')
        
#         # Mark 90% threshold
#         ax.axhline(y=90, color='red', linestyle=':', linewidth=2,
#                   alpha=0.7, label='90% threshold')
        
#         ax.set_xlabel('Transmission Power Pt (W)', fontsize=12)
#         ax.set_ylabel('Network Connectivity Probability (%)', fontsize=12)
#         ax.set_title(f'Connectivity vs Transmission Power\n'
#                     f'(Rd={Rd/1e3:.0f}kbps, n={n}, {theta1}°-{theta2}°)',
#                     fontsize=14, fontweight='bold')
#         ax.set_ylim([0, 105])
#         ax.grid(True, alpha=0.3)
#         ax.legend()
        
#         plt.tight_layout()
        
#         if save_path:
#             plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
#         return fig
    
#     def create_connectivity_dashboard(self,
#                                      Pt_default: float = 0.5,
#                                      Rd_default: float = 50e3,
#                                      n_default: int = 300,
#                                      theta1: float = 30,
#                                      theta2: float = 50,
#                                      S_ROI: float = 1e6,
#                                      save_path: Optional[str] = None) -> plt.Figure:
#         """
#         Create comprehensive connectivity dashboard
#         Combines Figures 16-18 in one view
        
#         Args:
#             Pt_default, Rd_default, n_default: Default parameters
#             theta1, theta2: Elevation angles
#             S_ROI: Coverage area
#             save_path: Path to save figure
            
#         Returns:
#             Figure object
#         """
#         fig = plt.figure(figsize=(16, 5))
#         gs = fig.add_gridspec(1, 3, hspace=0.3, wspace=0.3)
        
#         m_values = [1, 2, 3]
        
#         # Plot 1: Connectivity vs Nodes (Figure 16)
#         ax1 = fig.add_subplot(gs[0, 0])
#         n_range = np.arange(50, 351, 30)
#         l = self.calc.calculate_ook_distance(Pt_default, Rd_default, theta1, theta2)
        
#         for i, m in enumerate(m_values):
#             connectivities = []
#             for n in n_range:
#                 conn = MConnectivityCalculator.calculate_network_connectivity_probability(
#                     l, n, m, S_ROI, sample_points=10
#                 )
#                 connectivities.append(conn * 100)
            
#             ax1.plot(n_range, connectivities,
#                     linestyle=self.linestyles[i % len(self.linestyles)],
#                     linewidth=2, marker='o', markersize=4,
#                     color=self.colors[i % len(self.colors)],
#                     label=f'{m}-connected')
        
#         ax1.axhline(y=90, color='red', linestyle=':', linewidth=2, alpha=0.7)
#         ax1.set_xlabel('Number of Nodes n')
#         ax1.set_ylabel('Connectivity (%)')
#         ax1.set_title('Connectivity vs Nodes')
#         ax1.set_ylim([0, 105])
#         ax1.grid(True, alpha=0.3)
#         ax1.legend()
        
#         # Plot 2: Connectivity vs Rate (Figure 17)
#         ax2 = fig.add_subplot(gs[0, 1])
#         Rd_range = np.linspace(20e3, 120e3, 15)
        
#         for i, m in enumerate(m_values):
#             connectivities = []
#             for Rd in Rd_range:
#                 l = self.calc.calculate_ook_distance(Pt_default, Rd, theta1, theta2)
#                 conn = MConnectivityCalculator.calculate_network_connectivity_probability(
#                     l, n_default, m, S_ROI, sample_points=10
#                 )
#                 connectivities.append(conn * 100)
            
#             ax2.plot(Rd_range/1e3, connectivities,
#                     linestyle=self.linestyles[i % len(self.linestyles)],
#                     linewidth=2, marker='o', markersize=4,
#                     color=self.colors[i % len(self.colors)],
#                     label=f'{m}-connected')
        
#         ax2.axhline(y=90, color='red', linestyle=':', linewidth=2, alpha=0.7)
#         ax2.set_xlabel('Data Rate (kbps)')
#         ax2.set_ylabel('Connectivity (%)')
#         ax2.set_title('Connectivity vs Data Rate')
#         ax2.set_ylim([0, 105])
#         ax2.grid(True, alpha=0.3)
#         ax2.legend()
        
#         # Plot 3: Connectivity vs Power (Figure 18)
#         ax3 = fig.add_subplot(gs[0, 2])
#         Pt_range = np.linspace(0.15, 0.5, 15)
        
#         for i, m in enumerate(m_values):
#             connectivities = []
#             for Pt in Pt_range:
#                 l = self.calc.calculate_ook_distance(Pt, Rd_default, theta1, theta2)
#                 conn = MConnectivityCalculator.calculate_network_connectivity_probability(
#                     l, n_default, m, S_ROI, sample_points=10
#                 )
#                 connectivities.append(conn * 100)
            
#             ax3.plot(Pt_range, connectivities,
#                     linestyle=self.linestyles[i % len(self.linestyles)],
#                     linewidth=2, marker='o', markersize=4,
#                     color=self.colors[i % len(self.colors)],
#                     label=f'{m}-connected')
        
#         ax3.axhline(y=90, color='red', linestyle=':', linewidth=2, alpha=0.7)
#         ax3.set_xlabel('Transmission Power (W)')
#         ax3.set_ylabel('Connectivity (%)')
#         ax3.set_title('Connectivity vs Power')
#         ax3.set_ylim([0, 105])
#         ax3.grid(True, alpha=0.3)
#         ax3.legend()
        
#         fig.suptitle(f'UV Network Connectivity Analysis ({theta1}°-{theta2}°, S_ROI={S_ROI:.0e}m²)',
#                     fontsize=16, fontweight='bold', y=1.02)
        
#         if save_path:
#             plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
#         return fig


# if __name__ == "__main__":
#     print("Connectivity Plotter Test")
#     print("=" * 70)
    
#     plotter = ConnectivityPlotter()
    
#     # Test 1: Connectivity vs nodes (Figure 16)
#     print("\n1. Generating connectivity vs nodes plot (Fig. 16)...")
#     fig1 = plotter.plot_connectivity_vs_nodes()
#     print("   ✓ Figure created")
    
#     # Test 2: Connectivity vs rate (Figure 17)
#     print("\n2. Generating connectivity vs rate plot (Fig. 17)...")
#     fig2 = plotter.plot_connectivity_vs_rate()
#     print("   ✓ Figure created")
    
#     # Test 3: Connectivity vs power (Figure 18)
#     print("\n3. Generating connectivity vs power plot (Fig. 18)...")
#     fig3 = plotter.plot_connectivity_vs_power()
#     print("   ✓ Figure created")
    
#     # Test 4: Dashboard (Figures 16-18 combined)
#     print("\n4. Generating connectivity dashboard...")
#     fig4 = plotter.create_connectivity_dashboard()
#     print("   ✓ Dashboard created")
    
#     print("\n✅ All connectivity visualizations completed!")
#     print("💡 Reproduces Figures 16-18 from paper")
    
#     plt.show()




"""
visualization/connectivity_plotter.py
Connectivity visualization for UV networks.
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
from models.connectivity.m_connectivity import MConnectivityCalculator

class ConnectivityPlotter:
    def __init__(self, figsize: Tuple[int, int] = (10, 6)):
        self.figsize = figsize
        self.calc = CommunicationDistanceCalculator()
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        self.linestyles = ['-', '--', '-.']
    
    def plot_connectivity_vs_nodes(self, Pt=0.5, Rd=50e3, theta1=30, theta2=50, S_ROI=1e6, 
                                  n_range=None, m_values=[1, 2, 3], save_path=None):
        if n_range is None: n_range = np.arange(10, 250, 10)
        
        l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
        fig, ax = plt.subplots(figsize=self.figsize)
        
        for i, m in enumerate(m_values):
            connectivities = []
            for n in n_range:
                # Assuming MConnectivityCalculator exists and works
                conn = MConnectivityCalculator.calculate_network_connectivity_probability(
                    l, n, m, S_ROI, sample_points=10
                )
                connectivities.append(conn * 100)
            ax.plot(n_range, connectivities, marker='o', label=f'{m}-connected')
        
        # 90% Threshold
        ax.axhline(y=90, color='red', linestyle=':', label='90% threshold')
        ax.set_title(f'Connectivity vs Nodes (l={l:.1f}m)')
        ax.set_ylabel('Connectivity (%)')
        ax.set_xlabel('Number of Nodes')
        ax.set_ylim(0, 105)
        ax.legend()
        if save_path: plt.savefig(save_path)
        return fig

    def plot_connectivity_vs_rate(self, Pt=0.5, n=300, theta1=30, theta2=50, S_ROI=1e6, 
                                 Rd_range=None, m_values=[1, 2, 3], save_path=None):
        if Rd_range is None: Rd_range = np.linspace(10e3, 200e3, 20)
        
        fig, ax = plt.subplots(figsize=self.figsize)
        for i, m in enumerate(m_values):
            connectivities = []
            for Rd in Rd_range:
                l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
                conn = MConnectivityCalculator.calculate_network_connectivity_probability(
                    l, n, m, S_ROI, sample_points=10
                )
                connectivities.append(conn * 100)
            ax.plot(Rd_range/1e3, connectivities, marker='o', label=f'{m}-connected')
            
        ax.axhline(y=90, color='red', linestyle=':', label='90% threshold')
        ax.set_title(f'Connectivity vs Data Rate')
        ax.set_ylabel('Connectivity (%)')
        ax.set_xlabel('Data Rate (kbps)')
        ax.set_ylim(0, 105)
        ax.legend()
        if save_path: plt.savefig(save_path)
        return fig

    def plot_connectivity_vs_power(self, Rd=50e3, n=300, theta1=30, theta2=50, S_ROI=1e6, 
                                  Pt_range=None, m_values=[1, 2, 3], save_path=None):
        if Pt_range is None: Pt_range = np.linspace(0.01, 1.0, 20)
        
        fig, ax = plt.subplots(figsize=self.figsize)
        for i, m in enumerate(m_values):
            connectivities = []
            for Pt in Pt_range:
                l = self.calc.calculate_ook_distance(Pt, Rd, theta1, theta2)
                conn = MConnectivityCalculator.calculate_network_connectivity_probability(
                    l, n, m, S_ROI, sample_points=10
                )
                connectivities.append(conn * 100)
            ax.plot(Pt_range, connectivities, marker='o', label=f'{m}-connected')
            
        ax.axhline(y=90, color='red', linestyle=':', label='90% threshold')
        ax.set_title(f'Connectivity vs Power')
        ax.set_ylabel('Connectivity (%)')
        ax.set_xlabel('Power (W)')
        ax.set_ylim(0, 105)
        ax.legend()
        if save_path: plt.savefig(save_path)
        return fig

if __name__ == "__main__":
    cp = ConnectivityPlotter()
    print("Generating connectivity plots...")
    cp.plot_connectivity_vs_nodes(save_path='visualization/conn_nodes_sim.png')
    cp.plot_connectivity_vs_rate(save_path='visualization/conn_rate_sim.png')
    cp.plot_connectivity_vs_power(save_path='visualization/conn_power_sim.png')
    print("Done.")