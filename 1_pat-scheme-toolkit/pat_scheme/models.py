"""
PAT Scheme Models Module
Diff-in-diff model coefficients and Monte Carlo simulation.
"""
import numpy as np
from dataclasses import dataclass
from typing import Tuple, List

@dataclass
class DiffInDiffCoefficients:
    """Model coefficients from staggered diff-in-diff analysis."""
    avg_treatment_effect: float = -0.241  # log points
    std_error: float = 0.171
    early_entrant_effect: float = -0.518  # Cycle I-II
    late_entrant_effect: float = -0.022   # Cycle III+
    large_refinery_adj: float = 0.085     # >10 MMTPA
    r_squared: float = 0.843
    n_observations: int = 117

# Global model instance
MODEL = DiffInDiffCoefficients()

def predict_sec_reduction(
    pat_cycle_entry: int,
    capacity_mmtpa: float,
    model: DiffInDiffCoefficients = MODEL
) -> float:
    """
    Predict SEC reduction percentage based on model coefficients.
    
    Args:
        pat_cycle_entry: PAT cycle number (1-7)
        capacity_mmtpa: Refinery capacity in MMTPA
        model: Model coefficients
    
    Returns:
        Predicted SEC reduction as percentage (positive = reduction)
    """
    # Base effect based on entry timing
    if pat_cycle_entry <= 2:
        base_effect = abs(model.early_entrant_effect) * 100  # 51.8%
    else:
        base_effect = abs(model.late_entrant_effect) * 100   # 2.2%
    
    # Size adjustment
    size_adj = -model.large_refinery_adj * 100 if capacity_mmtpa > 10 else 0
    
    return base_effect + size_adj

def monte_carlo_compliance(
    baseline_sec: float,
    target_sec: float,
    predicted_reduction_pct: float,
    n_simulations: int = 10000,
    std_error_pct: float = 17.1,
    seed: int = None
) -> Tuple[float, float, float, np.ndarray]:
    """
    Run Monte Carlo simulation for compliance probability.
    
    Args:
        baseline_sec: Baseline SEC in MMBTU/MT
        target_sec: Target SEC in MMBTU/MT
        predicted_reduction_pct: Predicted reduction percentage
        n_simulations: Number of Monte Carlo draws
        std_error_pct: Standard error as percentage
        seed: Random seed for reproducibility
    
    Returns:
        Tuple of (compliance_probability, ci_lower, ci_upper, simulated_secs)
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Simulate treatment effects
    simulated_effects = np.random.normal(predicted_reduction_pct, std_error_pct, n_simulations)
    simulated_secs = baseline_sec * (1 - simulated_effects / 100)
    
    # Calculate compliance probability
    compliance_prob = (simulated_secs < target_sec).mean() * 100
    
    # 95% confidence interval
    ci_lower = np.percentile(simulated_secs, 2.5)
    ci_upper = np.percentile(simulated_secs, 97.5)
    
    return compliance_prob, ci_lower, ci_upper, simulated_secs

def batch_compliance_forecast(refineries_df) -> List[dict]:
    """
    Run compliance forecast for all refineries.
    
    Args:
        refineries_df: DataFrame with refinery data
    
    Returns:
        List of dicts with compliance forecasts
    """
    results = []
    for _, row in refineries_df.iterrows():
        pred_reduction = predict_sec_reduction(row['pat_cycle_entry'], row['capacity_mmtpa'])
        pred_sec = row['baseline_sec'] * (1 - pred_reduction / 100)
        
        prob, ci_low, ci_high, _ = monte_carlo_compliance(
            row['baseline_sec'], row['target_sec'], pred_reduction,
            n_simulations=5000, seed=hash(row['refinery']) % 2**32
        )
        
        results.append({
            'refinery': row['refinery'],
            'baseline_sec': row['baseline_sec'],
            'target_sec': row['target_sec'],
            'predicted_sec': round(pred_sec, 2),
            'predicted_reduction_pct': round(pred_reduction, 1),
            'compliance_probability': round(prob, 1),
            'ci_lower': round(ci_low, 2),
            'ci_upper': round(ci_high, 2),
            'status': 'High' if prob >= 70 else ('Medium' if prob >= 40 else 'At Risk')
        })
    
    return results
