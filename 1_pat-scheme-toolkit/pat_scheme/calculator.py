"""
PAT Scheme Calculator Module
SEC and ESCert calculations.
"""
from dataclasses import dataclass
from typing import Optional
from .data import CO2_FACTOR, MMBTU_TO_TOE

@dataclass
class SECResult:
    """Result of SEC calculation."""
    current_sec: float
    baseline_sec: float
    target_sec: float
    reduction_pct: float
    is_compliant: bool
    energy_savings_mmbtu: float
    co2_avoided_tonnes: float
    
def calculate_sec(
    total_energy_mmbtu: float,
    crude_throughput_mt: float,
    baseline_sec: float = 8.33,
    target_reduction_pct: float = 5.0,
    capacity_utilization: float = 0.85
) -> SECResult:
    """
    Calculate Specific Energy Consumption and related metrics.
    
    Args:
        total_energy_mmbtu: Total energy consumed in MMBTU
        crude_throughput_mt: Crude processed in metric tonnes
        baseline_sec: Baseline SEC in MMBTU/MT
        target_reduction_pct: Target reduction percentage
        capacity_utilization: Capacity utilization factor
    
    Returns:
        SECResult with all calculated metrics
    """
    current_sec = total_energy_mmbtu / crude_throughput_mt
    target_sec = baseline_sec * (1 - target_reduction_pct / 100)
    reduction_pct = ((baseline_sec - current_sec) / baseline_sec) * 100
    
    energy_savings = (baseline_sec - current_sec) * crude_throughput_mt
    co2_avoided = energy_savings * CO2_FACTOR
    
    return SECResult(
        current_sec=round(current_sec, 3),
        baseline_sec=baseline_sec,
        target_sec=round(target_sec, 3),
        reduction_pct=round(reduction_pct, 2),
        is_compliant=current_sec < target_sec,
        energy_savings_mmbtu=round(energy_savings, 0),
        co2_avoided_tonnes=round(co2_avoided, 0)
    )

@dataclass 
class ESCertResult:
    """Result of ESCert calculation."""
    is_generator: bool
    escerts_toe: float
    value_inr: float
    value_usd: float
    breakeven_sec: Optional[float] = None

def calculate_escerts(
    current_sec: float,
    target_sec: float,
    capacity_mmtpa: float,
    escert_price_inr: float = 4000,
    usd_inr_rate: float = 83.0,
    utilization: float = 0.85
) -> ESCertResult:
    """
    Calculate ESCert generation or requirement.
    
    Args:
        current_sec: Current SEC in MMBTU/MT
        target_sec: Target SEC in MMBTU/MT
        capacity_mmtpa: Refinery capacity in MMTPA
        escert_price_inr: ESCert price in INR/TOE
        usd_inr_rate: USD/INR exchange rate
        utilization: Capacity utilization factor
    
    Returns:
        ESCertResult with trading economics
    """
    overachievement = target_sec - current_sec
    annual_throughput = capacity_mmtpa * 1e6 * utilization
    escerts_toe = overachievement * annual_throughput / MMBTU_TO_TOE
    
    value_inr = escerts_toe * escert_price_inr
    value_usd = value_inr / usd_inr_rate
    
    return ESCertResult(
        is_generator=overachievement > 0,
        escerts_toe=round(escerts_toe, 0),
        value_inr=round(value_inr, 0),
        value_usd=round(value_usd, 0),
        breakeven_sec=target_sec if overachievement < 0 else None
    )

def calculate_portfolio_escerts(refineries_df, escert_price_inr: float = 4000) -> dict:
    """
    Calculate industry-wide ESCert balance.
    
    Args:
        refineries_df: DataFrame with refinery data
        escert_price_inr: ESCert price in INR/TOE
    
    Returns:
        Dict with portfolio metrics
    """
    total_generated = 0
    total_required = 0
    refinery_positions = []
    
    for _, row in refineries_df.iterrows():
        result = calculate_escerts(
            row['current_sec'], row['target_sec'], 
            row['capacity_mmtpa'], escert_price_inr
        )
        
        if result.is_generator:
            total_generated += result.escerts_toe
        else:
            total_required += abs(result.escerts_toe)
        
        refinery_positions.append({
            'refinery': row['refinery'],
            'escerts_toe': result.escerts_toe,
            'value_inr_cr': result.value_inr / 1e7
        })
    
    net_balance = total_generated - total_required
    
    return {
        'total_generated_toe': total_generated,
        'total_required_toe': total_required,
        'net_balance_toe': net_balance,
        'market_value_inr_cr': abs(net_balance) * escert_price_inr / 1e7,
        'is_surplus': net_balance > 0,
        'positions': refinery_positions
    }
