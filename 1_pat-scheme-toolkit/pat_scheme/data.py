"""
PAT Scheme Data Module
Refinery data, PAT cycle info, and data loading utilities.
"""
import pandas as pd
import numpy as np

# Constants
CO2_FACTOR = 0.07  # tonnes CO2 per MMBTU
MMBTU_TO_TOE = 41.868  # MMBTU per TOE

def get_refinery_data() -> pd.DataFrame:
    """Load refinery dataset with PAT scheme metrics."""
    refineries = {
        'refinery': [
            'IOCL Panipat', 'IOCL Mathura', 'IOCL Gujarat', 'IOCL Haldia',
            'IOCL Barauni', 'IOCL Guwahati', 'IOCL Digboi', 'IOCL Bongaigaon',
            'BPCL Mumbai', 'BPCL Kochi', 'HPCL Mumbai', 'HPCL Visakh',
            'CPCL Chennai', 'CPCL Nagapattinam', 'MRPL Mangalore', 'NRL Numaligarh',
            'RIL Jamnagar DTA', 'RIL Jamnagar SEZ', 'Nayara Vadinar',
            'ONGC Tatipaka', 'HMEL Bathinda', 'BORL Bina', 'IOCL Paradip'
        ],
        'capacity_mmtpa': [
            15.0, 8.0, 13.7, 8.0, 6.0, 1.0, 0.65, 2.35,
            12.0, 15.5, 7.5, 8.3, 10.5, 1.0, 15.0, 3.0,
            33.0, 35.2, 20.0, 0.07, 11.3, 7.8, 15.0
        ],
        'ownership': [
            'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU',
            'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU',
            'Private', 'Private', 'Private', 'PSU', 'JV', 'JV', 'PSU'
        ],
        'pat_cycle_entry': [1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 3, 1, 2, 1, 1, 1, 4, 2, 3, 3],
        'baseline_sec': [8.2, 8.5, 8.1, 8.7, 8.9, 9.1, 9.0, 8.8, 8.0, 7.8, 8.3, 8.4, 8.2, 8.6, 7.6, 8.5, 6.8, 6.5, 7.2, 8.8, 7.9, 8.1, 7.5],
        'current_sec': [6.4, 6.8, 6.3, 7.0, 7.2, 7.8, 7.9, 7.5, 6.2, 5.9, 6.5, 6.7, 6.4, 7.4, 5.8, 7.0, 5.8, 5.5, 6.1, 8.6, 6.5, 7.0, 6.2],
        'target_sec': [7.8, 8.1, 7.7, 8.3, 8.5, 8.6, 8.5, 8.4, 7.6, 7.4, 7.9, 8.0, 7.8, 8.2, 7.2, 8.1, 6.5, 6.2, 6.8, 8.4, 7.5, 7.7, 7.1],
        'commissioning_year': [1998, 1982, 1999, 1975, 1964, 1962, 1901, 1979, 1955, 1966, 1954, 1957, 1969, 1993, 1996, 2000, 1999, 2008, 2006, 2001, 2012, 2011, 2016]
    }
    
    df = pd.DataFrame(refineries)
    df = _compute_derived_metrics(df)
    return df

def _compute_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add computed columns to refinery dataframe."""
    df['sec_reduction_pct'] = ((df['baseline_sec'] - df['current_sec']) / df['baseline_sec']) * 100
    df['target_reduction_pct'] = ((df['baseline_sec'] - df['target_sec']) / df['baseline_sec']) * 100
    df['overachievement_pct'] = df['sec_reduction_pct'] - df['target_reduction_pct']
    df['energy_savings_mmbtu'] = (df['baseline_sec'] - df['current_sec']) * df['capacity_mmtpa'] * 1e6 * 0.85
    df['co2_avoided_mt'] = df['energy_savings_mmbtu'] * CO2_FACTOR / 1e6
    df['escert_potential_toe'] = df['overachievement_pct'] * df['capacity_mmtpa'] * 1e6 * 0.85 / MMBTU_TO_TOE / 100
    df['refinery_age'] = 2024 - df['commissioning_year']
    df['entry_category'] = df['pat_cycle_entry'].apply(lambda x: 'Early' if x <= 2 else 'Late')
    df['is_compliant'] = df['current_sec'] < df['target_sec']
    return df

def get_cycle_data() -> pd.DataFrame:
    """PAT Cycle timeline and parameters."""
    return pd.DataFrame({
        'cycle': ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'],
        'start_year': [2012, 2016, 2017, 2019, 2021, 2023, 2025],
        'end_year': [2015, 2019, 2020, 2022, 2024, 2026, 2028],
        'refineries_added': [11, 4, 3, 1, 2, 1, 1],
        'avg_target_pct': [4.5, 5.0, 5.5, 6.0, 6.0, 6.5, 7.0],
        'escert_price_inr': [100, 800, 1200, 2000, 3000, 4000, 4500]
    })

def get_industry_stats(df: pd.DataFrame = None) -> dict:
    """Calculate industry-wide statistics."""
    if df is None:
        df = get_refinery_data()
    return {
        'total_refineries': len(df),
        'avg_sec_reduction': df['sec_reduction_pct'].mean(),
        'total_co2_avoided': df['co2_avoided_mt'].sum(),
        'compliance_rate': df['is_compliant'].mean() * 100,
        'avg_baseline_sec': df['baseline_sec'].mean(),
        'avg_current_sec': df['current_sec'].mean(),
        'best_sec': df['current_sec'].min(),
        'worst_sec': df['current_sec'].max()
    }
