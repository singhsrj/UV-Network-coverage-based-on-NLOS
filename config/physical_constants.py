
#Physical constants for UV NLOS communication system. All values from Table I of the paper.

import numpy as np

class PhysicalConstants:
    """Physical constants for UV communication"""
    
    # Fundamental Physical Constants
    PLANCK_CONSTANT = 6.62607015e-34  # J·s (h)
    SPEED_OF_LIGHT = 2.99792458e8     # m/s (c)
    
    # UV Communication Constants (from Table I)
    WAVELENGTH = 265e-9               # m (λ = 265 nm, solar-blind band)
    QUANTUM_EFFICIENCY = 0.15         # η = 0.15 (dimensionless)
    
    # Communication Parameters (defaults from Table I)
    ERROR_PROBABILITY = 1e-6          # Pe = 10^-6
    
    # Photon Energy
    @classmethod
    def photon_energy(cls):
        """Calculate photon energy: E = hc/λ"""
        return (cls.PLANCK_CONSTANT * cls.SPEED_OF_LIGHT) / cls.WAVELENGTH
    
    # Useful conversions
    NM_TO_M = 1e-9
    M_TO_KM = 1e-3
    W_TO_MW = 1e3
    
    @classmethod
    def get_summary(cls):
        """Return summary of physical constants"""
        return {
            'Planck Constant (h)': f"{cls.PLANCK_CONSTANT} J·s",
            'Speed of Light (c)': f"{cls.SPEED_OF_LIGHT} m/s",
            'Wavelength (λ)': f"{cls.WAVELENGTH * 1e9} nm",
            'Quantum Efficiency (η)': cls.QUANTUM_EFFICIENCY,
            'Error Probability (Pe)': cls.ERROR_PROBABILITY,
            'Photon Energy': f"{cls.photon_energy():.2e} J"
        }


if __name__ == "__main__":
    # Display constants
    print("UV Network Physical Constants")
    print("=" * 50)
    for key, value in PhysicalConstants.get_summary().items():
        print(f"{key:30s}: {value}")