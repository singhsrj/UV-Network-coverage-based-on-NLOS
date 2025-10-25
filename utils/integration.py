"""
utils/integration.py

Numerical integration utilities for UV network calculations.
Used for connectivity analysis (Section III-C) and coverage integrals.
"""

import numpy as np
from scipy import integrate
from typing import Callable, Tuple, Optional

class IntegrationUtils:
    """Numerical integration utilities"""
    
    @staticmethod
    def integrate_1d(func: Callable, a: float, b: float, method: str = 'quad', **kwargs) -> Tuple[float, float]:
        """
        Numerical integration in 1D
        
        Args:
            func: Function to integrate
            a, b: Integration bounds
            method: Integration method ('quad', 'trapz', 'simps')
            **kwargs: Additional arguments for integration method
            
        Returns:
            (result, error): Integration result and error estimate
        """
        if method == 'dblquad':
            # Double integration using scipy
            x_min, x_max = x_bounds
            y_min, y_max = y_bounds
            result, error = integrate.dblquad(func, x_min, x_max, 
                                            lambda x: y_min, lambda x: y_max,
                                            **kwargs)
            return result, error
        
        elif method == 'grid':
            # Grid-based integration (for complex boundaries)
            nx = kwargs.get('nx', 100)
            ny = kwargs.get('ny', 100)
            x = np.linspace(x_bounds[0], x_bounds[1], nx)
            y = np.linspace(y_bounds[0], y_bounds[1], ny)
            X, Y = np.meshgrid(x, y)
            
            # Evaluate function on grid
            Z = np.zeros_like(X)
            for i in range(ny):
                for j in range(nx):
                    Z[i, j] = func(Y[i, j], X[i, j])
            
            # Trapezoidal integration
            dx = (x_bounds[1] - x_bounds[0]) / (nx - 1)
            dy = (y_bounds[1] - y_bounds[0]) / (ny - 1)
            result = np.sum(Z) * dx * dy
            
            return result, 0.0
        
        else:
            raise ValueError(f"Unknown integration method: {method}")
    
    @staticmethod
    def integrate_polar(func: Callable,
                       r_bounds: Tuple[float, float],
                       phi_bounds: Tuple[float, float],
                       **kwargs) -> Tuple[float, float]:
        """
        Numerical integration in polar coordinates
        Used for connectivity analysis (Equations 20-25)
        
        Args:
            func: Function to integrate f(r, phi)
            r_bounds: (r_min, r_max) radial bounds
            phi_bounds: (phi_min, phi_max) angular bounds (radians)
            **kwargs: Additional arguments
            
        Returns:
            (result, error): Integration result and error estimate
        """
        def integrand_cartesian(phi, r):
            # Convert to Cartesian with Jacobian r
            return func(r, phi) * r
        
        r_min, r_max = r_bounds
        phi_min, phi_max = phi_bounds
        
        result, error = integrate.dblquad(
            integrand_cartesian,
            r_min, r_max,
            lambda r: phi_min,
            lambda r: phi_max,
            **kwargs
        )
        
        return result, error
    
    @staticmethod
    def integrate_circular_segment(func: Callable,
                                   center: Tuple[float, float],
                                   radius: float,
                                   **kwargs) -> Tuple[float, float]:
        """
        Integrate over circular region
        
        Args:
            func: Function to integrate f(x, y)
            center: (cx, cy) circle center
            radius: Circle radius
            **kwargs: Additional arguments
            
        Returns:
            (result, error): Integration result and error estimate
        """
        cx, cy = center
        
        def func_polar(phi, r):
            x = cx + r * np.cos(phi)
            y = cy + r * np.sin(phi)
            return func(x, y) * r  # Include Jacobian
        
        result, error = integrate.dblquad(
            func_polar,
            0, radius,
            lambda r: 0,
            lambda r: 2 * np.pi,
            **kwargs
        )
        
        return result, error
    
    @staticmethod
    def integrate_elliptical_region(func: Callable,
                                   center: Tuple[float, float],
                                   semi_major: float,
                                   semi_minor: float,
                                   rotation: float = 0,
                                   **kwargs) -> Tuple[float, float]:
        """
        Integrate over elliptical region
        Used for single-side coverage (Section III-B-1)
        
        Args:
            func: Function to integrate f(x, y)
            center: (cx, cy) ellipse center
            semi_major: Semi-major axis length
            semi_minor: Semi-minor axis length
            rotation: Rotation angle in radians
            **kwargs: Additional arguments
            
        Returns:
            (result, error): Integration result and error estimate
        """
        cx, cy = center
        
        def func_parametric(theta, r):
            # Parametric ellipse: x = a*r*cos(θ), y = b*r*sin(θ)
            x_local = semi_major * r * np.cos(theta)
            y_local = semi_minor * r * np.sin(theta)
            
            # Apply rotation
            x_rot = x_local * np.cos(rotation) - y_local * np.sin(rotation)
            y_rot = x_local * np.sin(rotation) + y_local * np.cos(rotation)
            
            # Translate to center
            x = cx + x_rot
            y = cy + y_rot
            
            # Jacobian for elliptical coordinates
            jacobian = semi_major * semi_minor * r
            
            return func(x, y) * jacobian
        
        result, error = integrate.dblquad(
            func_parametric,
            0, 1,  # r from 0 to 1 (normalized)
            lambda r: 0,
            lambda r: 2 * np.pi,
            **kwargs
        )
        
        return result, error


class ConnectivityIntegrator:
    """
    Specialized integrator for connectivity calculations (Section III-C)
    Implements Equations 20-25
    """
    
    @staticmethod
    def integrate_adjacent_probability(
        pdf: Callable,
        node_position: Tuple[float, float],
        communication_distance: float,
        **kwargs
    ) -> float:
        """
        Calculate probability that a node has adjacent nodes
        Implements Equation 22
        
        Args:
            pdf: Probability density function U(t*cos(φ), t*sin(φ))
            node_position: (tx, φx) position in polar coordinates
            communication_distance: l (communication distance)
            **kwargs: Integration parameters
            
        Returns:
            P(tx, φx, l): Probability of having adjacent nodes
        """
        tx, phi_x = node_position
        l = communication_distance
        
        # Determine integration bounds based on distance from origin
        if tx >= l:
            # Case 1: d >= l (Equation 20)
            # Partial coverage overlap
            def phi1_bound(tx_val, phi_x_val, l_val):
                sin_term = (tx_val * np.sin(phi_x_val)) / tx_val
                arcsin_term = l_val / tx_val
                if abs(arcsin_term) > 1:
                    return 0
                return np.arcsin(sin_term) - np.arcsin(arcsin_term)
            
            def phi2_bound(tx_val, phi_x_val, l_val):
                sin_term = (tx_val * np.sin(phi_x_val)) / tx_val
                arcsin_term = l_val / tx_val
                if abs(arcsin_term) > 1:
                    return 2 * np.pi
                return np.arcsin(sin_term) + np.arcsin(arcsin_term)
            
            phi_1 = phi1_bound(tx, phi_x, l)
            phi_2 = phi2_bound(tx, phi_x, l)
            
            def integrand(phi, t):
                x = t * np.cos(phi)
                y = t * np.sin(phi)
                return pdf(x, y) * t
            
            # Integration bounds for t
            def t1_bound(phi):
                cos_term = tx * np.cos(phi_x) * np.cos(phi) + tx * np.sin(phi_x) * np.sin(phi)
                sqrt_term = cos_term**2 - (tx**2 - l**2)
                if sqrt_term < 0:
                    return 0
                return cos_term - np.sqrt(sqrt_term)
            
            def t2_bound(phi):
                cos_term = tx * np.cos(phi_x) * np.cos(phi) + tx * np.sin(phi_x) * np.sin(phi)
                sqrt_term = cos_term**2 - (tx**2 - l**2)
                if sqrt_term < 0:
                    return 0
                return cos_term + np.sqrt(sqrt_term)
            
        else:
            # Case 2: d < l (Equation 21)
            # Full coverage overlap
            phi_1 = 0
            phi_2 = 2 * np.pi
            
            def integrand(phi, t):
                x = t * np.cos(phi)
                y = t * np.sin(phi)
                return pdf(x, y) * t
            
            def t1_bound(phi):
                return 0
            
            def t2_bound(phi):
                cos_term = tx * np.cos(phi_x) * np.cos(phi) + tx * np.sin(phi_x) * np.sin(phi)
                sqrt_term = cos_term**2 - (tx**2 - l**2)
                if sqrt_term < 0:
                    return 0
                return cos_term + np.sqrt(sqrt_term)
        
        # Perform integration
        try:
            result, _ = integrate.dblquad(
                integrand,
                phi_1, phi_2,
                t1_bound, t2_bound,
                epsabs=kwargs.get('epsabs', 1e-6),
                epsrel=kwargs.get('epsrel', 1e-6)
            )
            return result
        except:
            return 0.0


if __name__ == "__main__":
    # Test integration utilities
    print("Integration Utilities Test")
    print("=" * 50)
    
    # Test 1D integration
    def f1(x):
        return x**2
    
    result, error = IntegrationUtils.integrate_1d(f1, 0, 1)
    print(f"∫₀¹ x² dx = {result:.6f} (expected: 0.333333)")
    print(f"Error estimate: {error:.2e}")
    
    # Test 2D integration
    def f2(y, x):
        return x + y
    
    result, error = IntegrationUtils.integrate_2d(f2, (0, 1), (0, 1))
    print(f"\n∫∫ (x+y) dxdy = {result:.6f} (expected: 1.0)")
    
    # Test polar integration
    def f_polar(r, phi):
        return 1  # Constant function
    
    result, error = IntegrationUtils.integrate_polar(
        f_polar, (0, 1), (0, 2*np.pi)
    )
    print(f"\n∫∫ r dr dφ (circle) = {result:.6f} (expected: {np.pi:.6f})")
    
    # Test circular integration
    def f_circle(x, y):
        return 1
    
    result, error = IntegrationUtils.integrate_circular_segment(
        f_circle, (0, 0), 1
    )
    print(f"\nCircular area integration = {result:.6f} (expected: {np.pi:.6f})")

    if method == 'quad':
            # Adaptive quadrature (default scipy method)
            result, error = integrate.quad(func, a, b, **kwargs)
            return result, error
        
    elif method == 'trapz':
            # Trapezoidal rule
            n_points = kwargs.get('n_points', 1000)
            x = np.linspace(a, b, n_points)
            y = np.array([func(xi) for xi in x])
            result = np.trapz(y, x)
            return result, 0.0  # No error estimate
        
    elif method == 'simps':
            # Simpson's rule
            n_points = kwargs.get('n_points', 1001)  # Must be odd
            if n_points % 2 == 0:
                n_points += 1
            x = np.linspace(a, b, n_points)
            y = np.array([func(xi) for xi in x])
            result = integrate.simps(y, x)
            return result, 0.0  # No error estimate
        
    else:
            raise ValueError(f"Unknown integration method: {method}")
    
    @staticmethod
    def integrate_2d(func: Callable, 
                    x_bounds: Tuple[float, float],
                    y_bounds: Tuple[float, float],
                    method: str = 'dblquad',
                    **kwargs) -> Tuple[float, float]:
        """
        Numerical integration in 2D
        
        Args:
            func: Function to integrate f(y, x) - note order!
            x_bounds: (x_min, x_max) integration bounds
            y_bounds: (y_min, y_max) integration bounds
            method: Integration method ('dblquad', 'grid')
            **kwargs: Additional arguments
            
        Returns:
            (result, error): Integration result and error estimate
        """