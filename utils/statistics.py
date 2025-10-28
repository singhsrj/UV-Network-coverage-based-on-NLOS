#Statistical utilities for UV network analysis. Includes binomial distribution for connectivity (Equation 23).
import numpy as np
from scipy import stats
from scipy.special import comb
from typing import List, Tuple

class StatisticsUtils:
    """Statistical calculation utilities"""
    
    @staticmethod
    def binomial_pmf(n: int, k: int, p: float) -> float:
        """
        Binomial probability mass function
        P(X = k) = C(n,k) * p^k * (1-p)^(n-k)
        
        Used in Equation 23 for m adjacent nodes
        
        Args:
            n: Number of trials
            k: Number of successes
            p: Probability of success
            
        Returns:
            Probability P(X = k)
        """
        if p < 0 or p > 1:
            raise ValueError("Probability must be in [0, 1]")
        if k > n or k < 0:
            return 0.0
        # New fix
        return stats.binom.pmf(k, np.float64(n), p)
        # return stats.binom.pmf(k, np.int_(n), p) # <--- MODIFIED LINE
        # return stats.binom.pmf(k, n, p)
    
    @staticmethod
    def binomial_cdf(n: int, k: int, p: float) -> float:
        """
        Binomial cumulative distribution function
        P(X ≤ k) = Σ(i=0 to k) C(n,i) * p^i * (1-p)^(n-i)
        
        Args:
            n: Number of trials
            k: Upper bound of successes
            p: Probability of success
            
        Returns:
            Probability P(X ≤ k)
        """
        if p < 0 or p > 1:
            raise ValueError("Probability must be in [0, 1]")
        
        return stats.binom.cdf(k, n, p)
    
    @staticmethod
    def binomial_survival(n: int, k: int, p: float) -> float:
        """
        Binomial survival function (complementary CDF)
        P(X > k) = 1 - P(X ≤ k)
        
        Args:
            n: Number of trials
            k: Lower bound of successes
            p: Probability of success
            
        Returns:
            Probability P(X > k)
        """
        return stats.binom.sf(k, n, p)
    
    @staticmethod
    def probability_m_adjacent(n: int, m: int, p: float) -> float:
        """
        Probability that a node has exactly m adjacent nodes
        Implements Equation 23
        
        P_m(tx, φx, l) = C(n-1, m) * P^m * (1-P)^(n-1-m)
        
        Args:
            n: Total number of nodes in network
            m: Number of adjacent nodes
            p: Probability that one node is adjacent P(tx, φx, l)
            
        Returns:
            Probability of having exactly m adjacent nodes
        """
        if m >= n:
            return 0.0
        
        return StatisticsUtils.binomial_pmf(n - 1, m, p)
    
    @staticmethod
    def probability_at_least_m_adjacent(n: int, m: int, p: float) -> float:
        """
        Probability that a node has at least m adjacent nodes
        Implements Equation 24
        
        P_≥m(tx, φx, l) = 1 - Σ(s=0 to m-1) C(n-1, s) * P^s * (1-P)^(n-1-s)
        
        Args:
            n: Total number of nodes in network
            m: Minimum number of adjacent nodes
            p: Probability that one node is adjacent
            
        Returns:
            Probability of having at least m adjacent nodes
        """
        if m >= n:
            return 0.0
        if m <= 0:
            return 1.0
        
        # Calculate sum of probabilities for 0 to m-1 adjacent nodes
        sum_prob = sum(StatisticsUtils.binomial_pmf(n - 1, s, p) 
                      for s in range(m))
        
        return 1.0 - sum_prob
    
    @staticmethod
    def m_connectivity_probability(n: int, m: int, Q_n_m: float) -> float:
        """
        Probability of m-connected network
        Implements Equation 27
        
        P(C is m-connected) ≈ (Q_n,≥m(l))^n
        
        Args:
            n: Number of nodes
            m: Connectivity level
            Q_n_m: Probability that arbitrary node has ≥m adjacent nodes
            
        Returns:
            Probability that network is m-connected
        """
        if Q_n_m < 0 or Q_n_m > 1:
            Q_n_m = np.clip(Q_n_m, 0, 1)
        
        return Q_n_m ** n
    
    @staticmethod
    def uniform_pdf_square(x: float, y: float, n: int, area: float) -> float:
        """
        Uniform probability density function for square network
        Implements Equation 18
        
        U(tx, φx) = n/S_ROI for points in region C
        
        Args:
            x, y: Point coordinates (Cartesian)
            n: Number of nodes
            area: Area of region (S_ROI)
            
        Returns:
            Probability density at point (x, y)
        """
        return n / area if area > 0 else 0
    
    @staticmethod
    def mean_and_std(data: List[float]) -> Tuple[float, float]:
        """Calculate mean and standard deviation"""
        data_array = np.array(data)
        return np.mean(data_array), np.std(data_array)
    
    @staticmethod
    def confidence_interval(data: List[float], confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Calculate confidence interval
        
        Args:
            data: Sample data
            confidence: Confidence level (default: 0.95 for 95% CI)
            
        Returns:
            (mean, lower_bound, upper_bound)
        """
        data_array = np.array(data)
        n = len(data_array)
        mean = np.mean(data_array)
        se = stats.sem(data_array)
        
        # t-distribution for small samples
        h = se * stats.t.ppf((1 + confidence) / 2, n - 1)
        
        return mean, mean - h, mean + h
    
    @staticmethod
    def monte_carlo_estimate(func: callable, n_samples: int, 
                            bounds: List[Tuple[float, float]]) -> Tuple[float, float]:
        """
        Monte Carlo estimation of integral
        
        Args:
            func: Function to integrate
            n_samples: Number of Monte Carlo samples
            bounds: List of (min, max) bounds for each dimension
            
        Returns:
            (estimate, std_error): Integral estimate and standard error
        """
        n_dims = len(bounds)
        
        # Generate random samples
        samples = []
        for low, high in bounds:
            samples.append(np.random.uniform(low, high, n_samples))
        
        # Evaluate function at sample points
        values = []
        for i in range(n_samples):
            point = tuple(samples[j][i] for j in range(n_dims))
            values.append(func(*point))
        
        values = np.array(values)
        
        # Calculate volume
        volume = np.prod([high - low for low, high in bounds])
        
        # Estimate integral
        estimate = volume * np.mean(values)
        std_error = volume * np.std(values) / np.sqrt(n_samples)
        
        return estimate, std_error


class ConnectivityStatistics:
    """
    Statistical analysis for network connectivity
    Implements connectivity probability calculations (Section III-C)
    """
    
    @staticmethod
    def calculate_node_adjacency_distribution(n: int, p: float, max_m: int = None) -> dict:
        """
        Calculate distribution of adjacent nodes
        
        Args:
            n: Total nodes in network
            p: Probability that one node is adjacent
            max_m: Maximum connectivity to calculate (default: n-1)
            
        Returns:
            Dictionary mapping m -> P(exactly m adjacent nodes)
        """
        if max_m is None:
            max_m = n - 1
        
        distribution = {}
        for m in range(max_m + 1):
            distribution[m] = StatisticsUtils.probability_m_adjacent(n, m, p)
        
        return distribution
    
    @staticmethod
    def calculate_connectivity_threshold(n: int, m: int, target_prob: float,
                                        p_min: float = 0, p_max: float = 1,
                                        tolerance: float = 0.01) -> float:
        """
        Find minimum adjacency probability to achieve target m-connectivity
        
        Args:
            n: Number of nodes
            m: Connectivity level
            target_prob: Target connectivity probability (e.g., 0.90)
            p_min, p_max: Search bounds
            tolerance: Search tolerance
            
        Returns:
            Minimum required adjacency probability
        """
        def connectivity_prob(p):
            Q = StatisticsUtils.probability_at_least_m_adjacent(n, m, p)
            return StatisticsUtils.m_connectivity_probability(n, m, Q)
        
        # Binary search
        while (p_max - p_min) > tolerance:
            p_mid = (p_min + p_max) / 2
            prob = connectivity_prob(p_mid)
            
            if prob < target_prob:
                p_min = p_mid
            else:
                p_max = p_mid
        
        return (p_min + p_max) / 2


if __name__ == "__main__":
    # Test statistics utilities
    print("Statistics Utilities Test")
    print("=" * 50)
    
    # Test binomial distribution
    n, k, p = 10, 3, 0.5
    pmf = StatisticsUtils.binomial_pmf(n, k, p)
    print(f"Binomial PMF: P(X={k} | n={n}, p={p}) = {pmf:.6f}")
    
    # Test m-adjacent probability (Equation 23)
    n_nodes = 100
    m_adjacent = 2
    p_adjacent = 0.1
    prob_m = StatisticsUtils.probability_m_adjacent(n_nodes, m_adjacent, p_adjacent)
    print(f"\nP(exactly {m_adjacent} adjacent | n={n_nodes}, p={p_adjacent}) = {prob_m:.6f}")
    
    # Test at least m-adjacent (Equation 24)
    prob_at_least_m = StatisticsUtils.probability_at_least_m_adjacent(
        n_nodes, m_adjacent, p_adjacent
    )
    print(f"P(≥{m_adjacent} adjacent | n={n_nodes}, p={p_adjacent}) = {prob_at_least_m:.6f}")
    
    # Test m-connectivity (Equation 27)
    Q_n_m = prob_at_least_m
    m_conn_prob = StatisticsUtils.m_connectivity_probability(n_nodes, m_adjacent, Q_n_m)
    print(f"\nP(network is {m_adjacent}-connected) = {m_conn_prob:.6f}")
    
    # Test uniform PDF (Equation 18)
    n_nodes = 300
    area = 1e6  # m²
    pdf_value = StatisticsUtils.uniform_pdf_square(0, 0, n_nodes, area)
    print(f"\nUniform PDF: U(0,0) = {pdf_value:.2e} (n={n_nodes}, S_ROI={area:.2e})")
    
    # Test connectivity threshold
    target_connectivity = 0.90
    required_p = ConnectivityStatistics.calculate_connectivity_threshold(
        100, 2, target_connectivity
    )
    print(f"\nRequired p for 90% 2-connectivity (n=100): {required_p:.4f}")