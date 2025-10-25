# Geometric utilities for UV network coverage calculations. Includes coordinate transformations and distance calculations.

import numpy as np
from typing import Tuple, List

class GeometryUtils:
    """Geometric calculation utilities"""
    
    @staticmethod
    def deg_to_rad(degrees: float) -> float:
        """Convert degrees to radians"""
        return np.radians(degrees)
    
    @staticmethod
    def rad_to_deg(radians: float) -> float:
        """Convert radians to degrees"""
        return np.degrees(radians)
    
    @staticmethod
    def euclidean_distance_2d(x1: float, y1: float, x2: float, y2: float) -> float:
        """
        Calculate Euclidean distance between two 2D points
        
        Args:
            x1, y1: Coordinates of first point
            x2, y2: Coordinates of second point
            
        Returns:
            Distance in same units as input
        """
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    @staticmethod
    def euclidean_distance_polar(r1: float, phi1: float, r2: float, phi2: float) -> float:
        """
        Calculate Euclidean distance between two points in polar coordinates
        
        Args:
            r1, phi1: Polar coordinates of first point (radius, angle in radians)
            r2, phi2: Polar coordinates of second point
            
        Returns:
            Euclidean distance
        """
        # Convert to Cartesian
        x1, y1 = r1 * np.cos(phi1), r1 * np.sin(phi1)
        x2, y2 = r2 * np.cos(phi2), r2 * np.sin(phi2)
        return GeometryUtils.euclidean_distance_2d(x1, y1, x2, y2)
    
    @staticmethod
    def cartesian_to_polar(x: float, y: float) -> Tuple[float, float]:
        """
        Convert Cartesian coordinates to polar coordinates
        
        Args:
            x, y: Cartesian coordinates
            
        Returns:
            (r, phi): Polar coordinates (radius, angle in radians)
        """
        r = np.sqrt(x**2 + y**2)
        phi = np.arctan2(y, x)
        return r, phi
    
    @staticmethod
    def polar_to_cartesian(r: float, phi: float) -> Tuple[float, float]:
        """
        Convert polar coordinates to Cartesian coordinates
        
        Args:
            r: Radius
            phi: Angle in radians
            
        Returns:
            (x, y): Cartesian coordinates
        """
        x = r * np.cos(phi)
        y = r * np.sin(phi)
        return x, y
    
    @staticmethod
    def circle_area(radius: float) -> float:
        """Calculate area of circle"""
        return np.pi * radius**2
    
    @staticmethod
    def ellipse_area(semi_major: float, semi_minor: float) -> float:
        """Calculate area of ellipse"""
        return np.pi * semi_major * semi_minor
    
    @staticmethod
    def sector_area(radius: float, angle_rad: float) -> float:
        """
        Calculate area of circular sector
        
        Args:
            radius: Radius of circle
            angle_rad: Central angle in radians
            
        Returns:
            Sector area
        """
        return 0.5 * radius**2 * angle_rad
    
    @staticmethod
    def triangle_area(base: float, height: float) -> float:
        """Calculate area of triangle"""
        return 0.5 * base * height
    
    @staticmethod
    def is_point_in_circle(px: float, py: float, cx: float, cy: float, radius: float) -> bool:
        """
        Check if point (px, py) is inside circle centered at (cx, cy)
        
        Args:
            px, py: Point coordinates
            cx, cy: Circle center coordinates
            radius: Circle radius
            
        Returns:
            True if point is inside circle
        """
        distance = GeometryUtils.euclidean_distance_2d(px, py, cx, cy)
        return distance <= radius
    
    @staticmethod
    def point_to_line_distance(px: float, py: float, x1: float, y1: float, 
                               x2: float, y2: float) -> float:
        """
        Calculate perpendicular distance from point to line
        
        Args:
            px, py: Point coordinates
            x1, y1: First point on line
            x2, y2: Second point on line
            
        Returns:
            Perpendicular distance
        """
        # Line equation: ax + by + c = 0
        a = y2 - y1
        b = x1 - x2
        c = x2 * y1 - x1 * y2
        
        # Distance formula
        numerator = abs(a * px + b * py + c)
        denominator = np.sqrt(a**2 + b**2)
        
        return numerator / denominator if denominator > 0 else 0
    
    @staticmethod
    def rotate_point(x: float, y: float, angle_rad: float, 
                    cx: float = 0, cy: float = 0) -> Tuple[float, float]:
        """
        Rotate point around center by given angle
        
        Args:
            x, y: Point coordinates
            angle_rad: Rotation angle in radians (counter-clockwise)
            cx, cy: Center of rotation (default: origin)
            
        Returns:
            (x_rot, y_rot): Rotated coordinates
        """
        # Translate to origin
        x_trans = x - cx
        y_trans = y - cy
        
        # Rotate
        x_rot = x_trans * np.cos(angle_rad) - y_trans * np.sin(angle_rad)
        y_rot = x_trans * np.sin(angle_rad) + y_trans * np.cos(angle_rad)
        
        # Translate back
        x_rot += cx
        y_rot += cy
        
        return x_rot, y_rot
    
    @staticmethod
    def calculate_angle_between_vectors(x1: float, y1: float, 
                                       x2: float, y2: float) -> float:
        """
        Calculate angle between two vectors from origin
        
        Args:
            x1, y1: First vector
            x2, y2: Second vector
            
        Returns:
            Angle in radians [0, π]
        """
        dot_product = x1 * x2 + y1 * y2
        mag1 = np.sqrt(x1**2 + y1**2)
        mag2 = np.sqrt(x2**2 + y2**2)
        
        if mag1 == 0 or mag2 == 0:
            return 0
        
        cos_angle = dot_product / (mag1 * mag2)
        cos_angle = np.clip(cos_angle, -1, 1)  # Handle numerical errors
        
        return np.arccos(cos_angle)
    
    @staticmethod
    def grid_points(x_min: float, x_max: float, y_min: float, y_max: float,
                   nx: int, ny: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate grid of points in rectangular region
        
        Args:
            x_min, x_max: X-axis bounds
            y_min, y_max: Y-axis bounds
            nx, ny: Number of points in x and y directions
            
        Returns:
            (X, Y): Meshgrid arrays
        """
        x = np.linspace(x_min, x_max, nx)
        y = np.linspace(y_min, y_max, ny)
        X, Y = np.meshgrid(x, y)
        return X, Y
    
    @staticmethod
    def generate_square_network_positions(n: int, side_length: float) -> List[Tuple[float, float]]:
        """
        Generate node positions for square network deployment
        
        Args:
            n: Number of nodes
            side_length: Side length of square area
            
        Returns:
            List of (x, y) positions
        """
        # Calculate grid dimensions
        grid_size = int(np.ceil(np.sqrt(n)))
        spacing = side_length / (grid_size - 1) if grid_size > 1 else 0
        
        positions = []
        for i in range(grid_size):
            for j in range(grid_size):
                if len(positions) < n:
                    x = i * spacing
                    y = j * spacing
                    positions.append((x, y))
        
        return positions[:n]


class CoordinateSystem:
    """Coordinate system handler for UV network"""
    
    def __init__(self, origin: Tuple[float, float] = (0, 0)):
        """
        Initialize coordinate system
        
        Args:
            origin: Origin coordinates (x, y)
        """
        self.origin = origin
    
    def translate_point(self, x: float, y: float) -> Tuple[float, float]:
        """Translate point to this coordinate system"""
        return (x - self.origin[0], y - self.origin[1])
    
    def translate_to_global(self, x: float, y: float) -> Tuple[float, float]:
        """Translate point from this coordinate system to global"""
        return (x + self.origin[0], y + self.origin[1])


if __name__ == "__main__":
    # Test geometry utilities
    print("Geometry Utilities Test")
    print("=" * 50)
    
    # Test conversions
    angle_deg = 45
    angle_rad = GeometryUtils.deg_to_rad(angle_deg)
    print(f"45° = {angle_rad:.4f} rad")
    
    # Test distances
    dist = GeometryUtils.euclidean_distance_2d(0, 0, 3, 4)
    print(f"Distance (0,0) to (3,4): {dist} m")
    
    # Test polar conversion
    r, phi = GeometryUtils.cartesian_to_polar(1, 1)
    print(f"Cartesian (1,1) = Polar (r={r:.4f}, φ={phi:.4f} rad)")
    
    # Test areas
    circle_area = GeometryUtils.circle_area(10)
    print(f"Circle area (r=10): {circle_area:.2f} m²")
    
    # Test network generation
    positions = GeometryUtils.generate_square_network_positions(4, 300)
    print(f"\n4-node square network positions (side=300m):")
    for i, pos in enumerate(positions):
        print(f"  Node {i+1}: {pos}")