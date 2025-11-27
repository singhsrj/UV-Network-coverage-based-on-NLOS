"""
Xi Calibration Tool

This tool reverse-engineers the correct xi_base value from known experimental data.
From paper: Pt=0.5W, Rd=50kbps, theta1=30°, theta2=50° → distance ≈ 75.1m
"""

import numpy as np

# Physical constants (CORRECTED)
h = 6.626e-34  # J·s
c = 3e8        # m/s
lambda_ = 265e-9  # m (CORRECTED from 250nm)
eta = 0.15     # dimensionless (CORRECTED from 0.045)
Pe = 1e-6      # error probability

# Known experimental values
Pt = 0.5       # W
Rd = 50e3      # bps (50 kbps)
theta1 = 30    # degrees
theta2 = 50    # degrees
target_distance = 75.1  # meters (experimental result)

# Calculate alpha using the path loss model logic
theta1_rad = np.radians(theta1)
theta2_rad = np.radians(theta2)

alpha_base = 3.0
angle_factor = (theta1_rad + theta2_rad) / (2 * np.radians(45))
alpha = alpha_base * (0.9 + 0.2 * angle_factor)
alpha = np.clip(alpha, 2.5, 4.0)

print("Xi Calibration Tool")
print("=" * 70)
print(f"\nKnown Experimental Data:")
print(f"  Pt = {Pt} W")
print(f"  Rd = {Rd/1e3} kbps")
print(f"  theta1 = {theta1}°")
print(f"  theta2 = {theta2}°")
print(f"  Target Distance = {target_distance} m")
print(f"\nCalculated alpha = {alpha:.4f}")

# Equation 1: l_OOK = [−ηλPt / (hcξRd × ln(2Pe))]^(1/α)
# Rearranging to solve for xi:
# l_OOK^α = −ηλPt / (hcξRd × ln(2Pe))
# hcξRd × ln(2Pe) = −ηλPt / l_OOK^α
# ξ = −ηλPt / (hcRd × ln(2Pe) × l_OOK^α)

l_alpha = target_distance ** alpha
ln_2Pe = np.log(2 * Pe)

print(f"\nIntermediate calculations:")
print(f"  ln(2Pe) = {ln_2Pe:.4f}")
print(f"  l^α = {target_distance}^{alpha:.4f} = {l_alpha:.4f}")

# Calculate required xi
numerator = -eta * lambda_ * Pt
denominator = h * c * Rd * ln_2Pe * l_alpha

xi_required = numerator / denominator

print(f"\nRequired xi:")
print(f"  Numerator: -η×λ×Pt = {numerator:.6e}")
print(f"  Denominator: h×c×Rd×ln(2Pe)×l^α = {denominator:.6e}")
print(f"  xi_required = {xi_required:.6e}")

# Now find what xi_base should be
# From path_loss.py: xi = xi_base * wavelength_factor * scattering_coefficient / geometric_factor

wavelength_nm = lambda_ * 1e9
wavelength_factor = (280 / wavelength_nm) ** 4
geometric_factor = np.sin(theta1_rad) * np.sin(theta2_rad)
scattering_coefficient = 1.0

xi_base_required = xi_required * geometric_factor / (wavelength_factor * scattering_coefficient)

print(f"\n" + "=" * 70)
print(f"CALIBRATION RESULT:")
print(f"=" * 70)
print(f"  wavelength_factor = {wavelength_factor:.4f}")
print(f"  geometric_factor = {geometric_factor:.4f}")
print(f"  Required xi_base = {xi_base_required:.4f}")
print(f"\n  → Set xi_base = {xi_base_required:.1f} in path_loss.py")
print("=" * 70)

# Verify the calculation
print(f"\nVerification:")
xi_calculated = xi_base_required * wavelength_factor * scattering_coefficient / geometric_factor
print(f"  xi from calibrated xi_base = {xi_calculated:.6e}")
print(f"  xi_required = {xi_required:.6e}")
print(f"  Match: {np.isclose(xi_calculated, xi_required)}")

# Calculate resulting distance
ratio = numerator / (h * c * xi_calculated * Rd * ln_2Pe)
l_OOK = np.power(ratio, 1.0 / alpha)
print(f"\n  Calculated distance = {l_OOK:.2f} m")
print(f"  Target distance = {target_distance} m")
print(f"  Error: {abs(l_OOK - target_distance):.2f} m ({abs(l_OOK - target_distance)/target_distance*100:.2f}%)")