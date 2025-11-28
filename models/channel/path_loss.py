"""
models/channel/path_loss.py

Path loss model for UV NLOS communication.
Calculates loss exponent α and loss factor ξ based on transceiver elevation angles.
"""

import numpy as np
from typing import Tuple, Dict

class PathLossModel:
    
    @staticmethod
    def calculate_loss_exponent(theta1: float, theta2: float) -> float:
        # Convert to radians
        theta1_rad = np.radians(theta1)
        theta2_rad = np.radians(theta2)
        
        # Base loss exponent (Increased from 2.0 to 3.0 to match NLOS characteristics)
        # UV NLOS typically ranges from 2.5 to 4.0 depending on geometry
        alpha_base = 3.0
        
        # Correction factors
        # Higher elevation angles increase path loss
        # We normalize against 45 degrees to scale the impact of angles
        angle_factor = (theta1_rad + theta2_rad) / (2 * np.radians(45))
        
        # Calculate loss exponent
        alpha = alpha_base * (0.9 + 0.2 * angle_factor)
        
        # Typical range for UV NLOS is 2.5 to 4.0
        alpha = np.clip(alpha, 2.5, 4.0)
        
        return alpha
    
    @staticmethod
    def calculate_loss_factor(theta1: float, theta2: float, 
                             wavelength: float = 265e-9,
                             scattering_coefficient: float = 1.0) -> float:
        # Convert to radians
        theta1_rad = np.radians(theta1)
        theta2_rad = np.radians(theta2)
        
        # Scattering cross-section dependency
        # Based on Rayleigh scattering: ~1/λ⁴
        wavelength_nm = wavelength * 1e9
        wavelength_factor = (280 / wavelength_nm) ** 4  # Normalized to 280nm
        
        # Geometric factor based on elevation angles
        # Better alignment of transmitter and receiver reduces loss
        geometric_factor = np.sin(theta1_rad) * np.sin(theta2_rad)
        geometric_factor = max(geometric_factor, 0.1)  # Avoid division by zero
        
        # Base loss factor
        xi_base = 57.3
        
        # Calculate total loss factor
        xi = xi_base * wavelength_factor * scattering_coefficient / geometric_factor
        
        return xi
    
    @staticmethod
    def get_path_loss_parameters(theta1: float, theta2: float) -> Dict[str, float]:
        alpha = PathLossModel.calculate_loss_exponent(theta1, theta2)
        xi = PathLossModel.calculate_loss_factor(theta1, theta2)
        
        return {
            'alpha': alpha,
            'xi': xi,
            'theta1': theta1,
            'theta2': theta2
        }
    
    @staticmethod
    def compare_elevation_combinations(combinations: list) -> Dict:
        results = {}
        
        for theta1, theta2 in combinations:
            key = f"{theta1}-{theta2}"
            results[key] = PathLossModel.get_path_loss_parameters(theta1, theta2)
        
        return results


class ScatteringModel:
    """
    UV scattering model for NLOS communication
    Based on single scattering approximation
    """
    
    @staticmethod
    def calculate_scattering_angle(theta1: float, theta2: float) -> float:
        # For NLOS communication, scattering angle relates to elevation angles
        theta_scatter = 180 - (theta1 + theta2)
        return theta_scatter
    
    @staticmethod
    def calculate_effective_scatterer_volume(theta1: float, theta2: float,
                                            beam_divergence: float,
                                            distance: float) -> float:
        # Convert to radians
        theta1_rad = np.radians(theta1)
        theta2_rad = np.radians(theta2)
        phi_rad = np.radians(beam_divergence)
        
        # Geometric calculation of scattering volume
        # This is simplified; actual volume depends on beam geometry
        
        # Height of scatterer region
        h_scatter = distance * np.sin(theta1_rad)
        
        # Cross-sectional area from beam divergence
        r_beam = distance * np.tan(phi_rad / 2)
        a_scatter = np.pi * r_beam**2
        
        # Volume estimate
        volume = a_scatter * h_scatter
        
        return volume
    
    @staticmethod
    def get_scattering_summary(theta1: float, theta2: float, 
                              beam_divergence: float, distance: float) -> Dict:
        scattering_angle = ScatteringModel.calculate_scattering_angle(theta1, theta2)
        volume = ScatteringModel.calculate_effective_scatterer_volume(
            theta1, theta2, beam_divergence, distance
        )
        
        return {
            'theta1': theta1,
            'theta2': theta2,
            'beam_divergence': beam_divergence,
            'distance': distance,
            'scattering_angle': scattering_angle,
            'effective_volume': volume
        }


if __name__ == "__main__":
    # Test path loss model
    print("UV Path Loss Model Test (Calibrated)")
    print("=" * 50)
    
    # Test single elevation combination
    theta1, theta2 = 30, 50
    alpha = PathLossModel.calculate_loss_exponent(theta1, theta2)
    xi = PathLossModel.calculate_loss_factor(theta1, theta2)
    
    print(f"\nElevation Combination: {theta1}°-{theta2}°")
    print(f"Loss Exponent (α): {alpha:.4f}")
    print(f"Loss Factor (ξ): {xi:.4f}")
    
    # Test all elevation combinations from paper
    print("\n\nComparison of Elevation Combinations:")
    print("-" * 70)
    print(f"{'Combination':<15} {'α':<10} {'ξ':<15} {'Performance'}")
    print("-" * 70)
    
    combinations = [(30, 30), (30, 50), (50, 30), (50, 50)]
    results = PathLossModel.compare_elevation_combinations(combinations)
    
    for combo_str, params in results.items():
        alpha_val = params['alpha']
        xi_val = params['xi']
        
        # Estimate relative performance
        # Lower alpha generally implies better range, though xi also matters
        if alpha_val < 3.0:
            performance = "Excellent"
        elif alpha_val < 3.5:
            performance = "Good"
        elif alpha_val < 3.8:
            performance = "Fair"
        else:
            performance = "Poor"
        
        print(f"{combo_str + '°':<15} {alpha_val:<10.4f} {xi_val:<15.4f} {performance}")