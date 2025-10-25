"""
models/channel/communication_distance.py

Communication distance calculator for UV NLOS OOK modulation.
Implements Equation 1 from the paper.
"""

import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.physical_constants import PhysicalConstants
from config.communication_params import CommunicationParams
from models.channel.path_loss import PathLossModel


class CommunicationDistanceCalculator:
    """
    Calculate maximum communication distance for UV NLOS OOK modulation
    Based on Equation 1: l_OOK = α / √[−ηλPt / (hcξRd) × ln(2Pe)]
    """
    
    def __init__(self):
        """Initialize with physical constants"""
        self.h = PhysicalConstants.PLANCK_CONSTANT
        self.c = PhysicalConstants.SPEED_OF_LIGHT
        self.lambda_ = PhysicalConstants.WAVELENGTH
        self.eta = PhysicalConstants.QUANTUM_EFFICIENCY
        self.Pe = PhysicalConstants.ERROR_PROBABILITY
    
    def calculate_ook_distance(self, 
                              Pt: float,
                              Rd: float,
                              theta1: float,
                              theta2: float) -> float:
        """
        Calculate OOK communication distance (Equation 1)
        
        l_OOK = α / √[−ηλPt / (hcξRd) × ln(2Pe)]
        
        Args:
            Pt: Transmission power (W)
            Rd: Data rate (bps)
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            
        Returns:
            Communication distance l_OOK (m)
        """
        # Get path loss parameters for this elevation combination
        alpha = PathLossModel.calculate_loss_exponent(theta1, theta2)
        xi = PathLossModel.calculate_loss_factor(theta1, theta2)
        
        # Calculate denominator terms
        # Numerator: -ηλPt
        numerator = -self.eta * self.lambda_ * Pt
        
        # Denominator: hcξRd × ln(2Pe)
        denominator = self.h * self.c * xi * Rd * np.log(2 * self.Pe)
        
        # Calculate ratio
        ratio = numerator / denominator
        
        # Take square root
        sqrt_term = np.sqrt(ratio)
        
        # Calculate distance
        l_OOK = alpha / sqrt_term
        
        return l_OOK
    
    def calculate_distance_vs_power(self,
                                   Pt_range: np.ndarray,
                                   Rd: float,
                                   theta1: float,
                                   theta2: float) -> np.ndarray:
        """
        Calculate distance for range of transmission powers
        
        Args:
            Pt_range: Array of transmission powers (W)
            Rd: Data rate (bps)
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            
        Returns:
            Array of communication distances (m)
        """
        distances = np.array([
            self.calculate_ook_distance(Pt, Rd, theta1, theta2)
            for Pt in Pt_range
        ])
        return distances
    
    def calculate_distance_vs_rate(self,
                                  Pt: float,
                                  Rd_range: np.ndarray,
                                  theta1: float,
                                  theta2: float) -> np.ndarray:
        """
        Calculate distance for range of data rates
        
        Args:
            Pt: Transmission power (W)
            Rd_range: Array of data rates (bps)
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            
        Returns:
            Array of communication distances (m)
        """
        distances = np.array([
            self.calculate_ook_distance(Pt, Rd, theta1, theta2)
            for Rd in Rd_range
        ])
        return distances
    
    def calculate_distance_vs_elevation(self,
                                       Pt: float,
                                       Rd: float,
                                       theta1_range: np.ndarray,
                                       theta2: float) -> np.ndarray:
        """
        Calculate distance for range of transmission elevation angles
        Used to reproduce Fig. 5
        
        Args:
            Pt: Transmission power (W)
            Rd: Data rate (bps)
            theta1_range: Array of transmission elevation angles (degrees)
            theta2: Reception elevation angle (degrees)
            
        Returns:
            Array of communication distances (m)
        """
        distances = np.array([
            self.calculate_ook_distance(Pt, Rd, theta1, theta2)
            for theta1 in theta1_range
        ])
        return distances
    
    def calculate_distance_matrix(self,
                                 Pt: float,
                                 Rd: float,
                                 theta1_range: np.ndarray,
                                 theta2_range: np.ndarray) -> np.ndarray:
        """
        Calculate distance matrix for elevation angle combinations
        
        Args:
            Pt: Transmission power (W)
            Rd: Data rate (bps)
            theta1_range: Array of transmission elevation angles (degrees)
            theta2_range: Array of reception elevation angles (degrees)
            
        Returns:
            2D array of communication distances (m)
        """
        distances = np.zeros((len(theta1_range), len(theta2_range)))
        
        for i, theta1 in enumerate(theta1_range):
            for j, theta2 in enumerate(theta2_range):
                distances[i, j] = self.calculate_ook_distance(Pt, Rd, theta1, theta2)
        
        return distances
    
    def get_distance_summary(self,
                           Pt: float,
                           Rd: float,
                           elevation_combinations: list) -> dict:
        """
        Get distance summary for multiple elevation combinations
        
        Args:
            Pt: Transmission power (W)
            Rd: Data rate (bps)
            elevation_combinations: List of (theta1, theta2) tuples
            
        Returns:
            Dictionary mapping combinations to distances
        """
        results = {}
        
        for theta1, theta2 in elevation_combinations:
            key = f"{theta1}-{theta2}"
            distance = self.calculate_ook_distance(Pt, Rd, theta1, theta2)
            
            # Get path loss parameters
            alpha = PathLossModel.calculate_loss_exponent(theta1, theta2)
            xi = PathLossModel.calculate_loss_factor(theta1, theta2)
            
            results[key] = {
                'distance': distance,
                'alpha': alpha,
                'xi': xi,
                'Pt': Pt,
                'Rd': Rd
            }
        
        return results
    
    def find_required_power(self,
                          target_distance: float,
                          Rd: float,
                          theta1: float,
                          theta2: float,
                          Pt_min: float = 0.01,
                          Pt_max: float = 1.0,
                          tolerance: float = 0.001) -> float:
        """
        Find required transmission power for target distance
        
        Args:
            target_distance: Desired communication distance (m)
            Rd: Data rate (bps)
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            Pt_min: Minimum power to search (W)
            Pt_max: Maximum power to search (W)
            tolerance: Search tolerance (m)
            
        Returns:
            Required transmission power (W)
        """
        # Binary search
        while (Pt_max - Pt_min) > 0.001:
            Pt_mid = (Pt_min + Pt_max) / 2
            distance = self.calculate_ook_distance(Pt_mid, Rd, theta1, theta2)
            
            if distance < target_distance:
                Pt_min = Pt_mid
            else:
                Pt_max = Pt_mid
        
        return (Pt_min + Pt_max) / 2
    
    def find_supported_rate(self,
                          distance: float,
                          Pt: float,
                          theta1: float,
                          theta2: float,
                          Rd_min: float = 1e3,
                          Rd_max: float = 200e3) -> float:
        """
        Find maximum supported data rate for given distance
        
        Args:
            distance: Communication distance (m)
            Pt: Transmission power (W)
            theta1: Transmission elevation angle (degrees)
            theta2: Reception elevation angle (degrees)
            Rd_min: Minimum rate to search (bps)
            Rd_max: Maximum rate to search (bps)
            
        Returns:
            Maximum supported data rate (bps)
        """
        # Binary search
        while (Rd_max - Rd_min) > 1000:
            Rd_mid = (Rd_min + Rd_max) / 2
            calc_distance = self.calculate_ook_distance(Pt, Rd_mid, theta1, theta2)
            
            if calc_distance < distance:
                Rd_max = Rd_mid
            else:
                Rd_min = Rd_mid
        
        return (Rd_min + Rd_max) / 2


if __name__ == "__main__":
    # Test communication distance calculator
    print("UV Communication Distance Calculator Test")
    print("=" * 70)
    
    # Initialize calculator
    calc = CommunicationDistanceCalculator()
    
    # Default parameters from paper
    Pt_default = CommunicationParams.PT_DEFAULT
    Rd_default = CommunicationParams.RD_DEFAULT
    
    print(f"\nDefault Parameters:")
    print(f"  Transmission Power: {Pt_default} W")
    print(f"  Data Rate: {Rd_default/1e3} kbps")
    print(f"  Error Probability: {PhysicalConstants.ERROR_PROBABILITY}")
    
    # Calculate distance for all elevation combinations
    print("\n\nCommunication Distance vs Elevation Combination:")
    print("-" * 70)
    print(f"{'Combination':<15} {'Distance (m)':<15} {'α':<10} {'ξ'}")
    print("-" * 70)
    
    combinations = CommunicationParams.ELEVATION_COMBINATIONS
    results = calc.get_distance_summary(Pt_default, Rd_default, combinations)
    
    for combo_str, params in results.items():
        print(f"{combo_str + '°':<15} {params['distance']:<15.2f} "
              f"{params['alpha']:<10.4f} {params['xi']:.6e}")
    
    # Test distance vs transmission angle (reproduce Fig. 5 data)
    print("\n\nDistance vs Transmission Elevation Angle (θ₂=50°):")
    print("-" * 50)
    
    theta1_range = np.arange(30, 51, 5)
    theta2_fixed = 50
    distances = calc.calculate_distance_vs_elevation(
        Pt_default, Rd_default, theta1_range, theta2_fixed
    )
    
    for theta1, dist in zip(theta1_range, distances):
        print(f"  θ₁ = {theta1}°: {dist:.2f} m")
    
    # Test power requirement for target distance
    print("\n\nRequired Power for Target Distance:")
    print("-" * 50)
    
    target_dist = 100  # meters
    theta1, theta2 = 30, 50
    required_Pt = calc.find_required_power(target_dist, Rd_default, theta1, theta2)
    
    print(f"Target Distance: {target_dist} m")
    print(f"Elevation: {theta1}°-{theta2}°")
    print(f"Required Power: {required_Pt:.4f} W")
    
    # Verify
    verify_dist = calc.calculate_ook_distance(required_Pt, Rd_default, theta1, theta2)
    print(f"Verification: {verify_dist:.2f} m")
    
    # Test supported data rate for given distance
    print("\n\nSupported Data Rate:")
    print("-" * 50)
    
    test_distance = 75.1  # Experimental distance from paper
    supported_rate = calc.find_supported_rate(test_distance, Pt_default, theta1, theta2)
    
    print(f"Distance: {test_distance} m")
    print(f"Power: {Pt_default} W")
    print(f"Elevation: {theta1}°-{theta2}°")
    print(f"Supported Rate: {supported_rate/1e3:.2f} kbps")