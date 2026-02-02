"""Tests for PAT Scheme Analysis Toolkit."""
import pytest
import sys
sys.path.insert(0, '..')

from pat_scheme import (
    get_refinery_data,
    get_cycle_data,
    calculate_sec,
    calculate_escerts,
    predict_sec_reduction,
    monte_carlo_compliance
)

def test_refinery_data():
    """Test refinery data loading."""
    df = get_refinery_data()
    assert len(df) == 23
    assert 'refinery' in df.columns
    assert 'current_sec' in df.columns
    assert df['current_sec'].min() > 0

def test_cycle_data():
    """Test PAT cycle data."""
    df = get_cycle_data()
    assert len(df) == 7
    assert df['cycle'].tolist() == ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']

def test_calculate_sec():
    """Test SEC calculation."""
    result = calculate_sec(
        total_energy_mmbtu=85_000_000,
        crude_throughput_mt=10_000_000,
        baseline_sec=8.33
    )
    assert result.current_sec == 8.5
    assert result.baseline_sec == 8.33
    assert isinstance(result.is_compliant, bool)

def test_calculate_escerts():
    """Test ESCert calculation."""
    result = calculate_escerts(
        current_sec=6.5,
        target_sec=7.5,
        capacity_mmtpa=10.0
    )
    assert result.is_generator == True
    assert result.escerts_toe > 0

def test_predict_sec_reduction():
    """Test diff-in-diff prediction."""
    early = predict_sec_reduction(pat_cycle_entry=1, capacity_mmtpa=10.0)
    late = predict_sec_reduction(pat_cycle_entry=4, capacity_mmtpa=10.0)
    assert early > late  # Early entrants have larger reductions

def test_monte_carlo():
    """Test Monte Carlo simulation."""
    prob, ci_low, ci_high, sims = monte_carlo_compliance(
        baseline_sec=8.33,
        target_sec=7.9,
        predicted_reduction_pct=24.1,
        n_simulations=1000,
        seed=42
    )
    assert 0 <= prob <= 100
    assert ci_low < ci_high
    assert len(sims) == 1000

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
