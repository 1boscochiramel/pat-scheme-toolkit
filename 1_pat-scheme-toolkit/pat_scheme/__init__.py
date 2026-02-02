"""
PAT Scheme Analysis Toolkit
===========================
Python library for analyzing India's Perform, Achieve and Trade (PAT) scheme.

Based on: "The impact of India's PAT scheme on refinery energy efficiency:
A staggered difference-in-differences analysis" by Bosco Chiramel

Usage:
    from pat_scheme import get_refinery_data, calculate_sec, predict_sec_reduction
    
    # Load data
    df = get_refinery_data()
    
    # Calculate SEC
    result = calculate_sec(total_energy_mmbtu=85000000, crude_throughput_mt=10000000)
    
    # Predict using diff-in-diff model
    reduction = predict_sec_reduction(pat_cycle_entry=1, capacity_mmtpa=15.0)
"""

__version__ = "1.0.0"
__author__ = "Bosco Chiramel"

from .data import (
    get_refinery_data,
    get_cycle_data,
    get_industry_stats,
    CO2_FACTOR,
    MMBTU_TO_TOE
)

from .models import (
    DiffInDiffCoefficients,
    MODEL,
    predict_sec_reduction,
    monte_carlo_compliance,
    batch_compliance_forecast
)

from .calculator import (
    SECResult,
    ESCertResult,
    calculate_sec,
    calculate_escerts,
    calculate_portfolio_escerts
)

__all__ = [
    # Data
    'get_refinery_data', 'get_cycle_data', 'get_industry_stats',
    'CO2_FACTOR', 'MMBTU_TO_TOE',
    # Models
    'DiffInDiffCoefficients', 'MODEL', 'predict_sec_reduction',
    'monte_carlo_compliance', 'batch_compliance_forecast',
    # Calculator
    'SECResult', 'ESCertResult', 'calculate_sec', 
    'calculate_escerts', 'calculate_portfolio_escerts'
]
