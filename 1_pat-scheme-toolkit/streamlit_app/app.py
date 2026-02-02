"""
PAT Scheme Dashboard & SEC Calculator
=====================================
Interactive tool for analyzing India's Perform, Achieve and Trade (PAT) scheme
for refinery energy efficiency.

Based on: "The impact of India's PAT scheme on refinery energy efficiency"
Author: Bosco Chiramel
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="PAT Scheme Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .stMetric > div {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ============== DATA ==============
@st.cache_data
def load_refinery_data():
    """Load refinery dataset based on paper's methodology"""
    
    # Refinery data compiled from PPAC and BEE reports
    refineries = {
        'Refinery': [
            'IOCL Panipat', 'IOCL Mathura', 'IOCL Gujarat', 'IOCL Haldia',
            'IOCL Barauni', 'IOCL Guwahati', 'IOCL Digboi', 'IOCL Bongaigaon',
            'BPCL Mumbai', 'BPCL Kochi', 'HPCL Mumbai', 'HPCL Visakh',
            'CPCL Chennai', 'CPCL Nagapattinam', 'MRPL Mangalore', 'NRL Numaligarh',
            'RIL Jamnagar DTA', 'RIL Jamnagar SEZ', 'Nayara Vadinar',
            'ONGC Tatipaka', 'HMEL Bathinda', 'BORL Bina', 'IOCL Paradip'
        ],
        'Capacity_MMTPA': [
            15.0, 8.0, 13.7, 8.0, 6.0, 1.0, 0.65, 2.35,
            12.0, 15.5, 7.5, 8.3, 10.5, 1.0, 15.0, 3.0,
            33.0, 35.2, 20.0, 0.07, 11.3, 7.8, 15.0
        ],
        'Ownership': [
            'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU',
            'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU', 'PSU',
            'Private', 'Private', 'Private', 'PSU', 'JV', 'JV', 'PSU'
        ],
        'PAT_Cycle_Entry': [
            1, 1, 1, 1, 1, 2, 2, 2,
            1, 1, 1, 1, 1, 3, 1, 2,
            1, 1, 1, 4, 2, 3, 3
        ],
        'Baseline_SEC': [
            8.2, 8.5, 8.1, 8.7, 8.9, 9.1, 9.0, 8.8,
            8.0, 7.8, 8.3, 8.4, 8.2, 8.6, 7.6, 8.5,
            6.8, 6.5, 7.2, 8.8, 7.9, 8.1, 7.5
        ],
        'Current_SEC': [
            6.4, 6.8, 6.3, 7.0, 7.2, 7.8, 7.9, 7.5,
            6.2, 5.9, 6.5, 6.7, 6.4, 7.4, 5.8, 7.0,
            5.8, 5.5, 6.1, 8.6, 6.5, 7.0, 6.2
        ],
        'Target_SEC': [
            7.8, 8.1, 7.7, 8.3, 8.5, 8.6, 8.5, 8.4,
            7.6, 7.4, 7.9, 8.0, 7.8, 8.2, 7.2, 8.1,
            6.5, 6.2, 6.8, 8.4, 7.5, 7.7, 7.1
        ],
        'Commissioning_Year': [
            1998, 1982, 1999, 1975, 1964, 1962, 1901, 1979,
            1955, 1966, 1954, 1957, 1969, 1993, 1996, 2000,
            1999, 2008, 2006, 2001, 2012, 2011, 2016
        ]
    }
    
    df = pd.DataFrame(refineries)
    
    # Calculate derived metrics
    df['SEC_Reduction_Pct'] = ((df['Baseline_SEC'] - df['Current_SEC']) / df['Baseline_SEC']) * 100
    df['Target_Reduction_Pct'] = ((df['Baseline_SEC'] - df['Target_SEC']) / df['Baseline_SEC']) * 100
    df['Overachievement_Pct'] = df['SEC_Reduction_Pct'] - df['Target_Reduction_Pct']
    df['Energy_Savings_MMBTU'] = (df['Baseline_SEC'] - df['Current_SEC']) * df['Capacity_MMTPA'] * 1e6 * 0.85
    df['CO2_Avoided_MT'] = df['Energy_Savings_MMBTU'] * 0.07 / 1e6
    df['ESCert_Potential'] = df['Overachievement_Pct'] * df['Capacity_MMTPA'] * 1000  # Simplified
    df['Refinery_Age'] = 2024 - df['Commissioning_Year']
    df['Entry_Category'] = df['PAT_Cycle_Entry'].apply(lambda x: 'Early (Cycle I-II)' if x <= 2 else 'Late (Cycle III+)')
    
    return df

@st.cache_data
def load_cycle_data():
    """PAT Cycle timeline and parameters"""
    cycles = {
        'Cycle': ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'],
        'Start_Year': [2012, 2016, 2017, 2019, 2021, 2023, 2025],
        'End_Year': [2015, 2019, 2020, 2022, 2024, 2026, 2028],
        'Refineries_Added': [11, 4, 3, 1, 2, 1, 1],
        'Avg_Target_Pct': [4.5, 5.0, 5.5, 6.0, 6.0, 6.5, 7.0],
        'ESCert_Price_INR': [100, 800, 1200, 2000, 3000, 4000, 4500]
    }
    return pd.DataFrame(cycles)

# ============== SIDEBAR ==============
st.sidebar.markdown("## 🎯 Navigation")
page = st.sidebar.radio(
    "Select Module",
    ["📊 Dashboard Overview", "🔢 SEC Calculator", "📈 Benchmarking Tool", "💹 ESCert Simulator", "🎯 Target Predictor"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info("""
**PAT Scheme Dashboard**  
Based on diff-in-diff analysis of 23 Indian refineries (2012-2024).

Key Finding: PAT reduces SEC by **24.1%** on average.

*Research: Bosco Chiramel*
""")

# Load data
df = load_refinery_data()
cycle_df = load_cycle_data()

# ============== PAGE: DASHBOARD OVERVIEW ==============
if page == "📊 Dashboard Overview":
    st.markdown('<p class="main-header">⚡ PAT Scheme Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">India\'s Perform, Achieve and Trade Scheme Analysis for Refineries</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📍 Refineries Covered",
            value=f"{len(df)}",
            delta="100% coverage"
        )
    
    with col2:
        avg_reduction = df['SEC_Reduction_Pct'].mean()
        st.metric(
            label="📉 Avg SEC Reduction",
            value=f"{avg_reduction:.1f}%",
            delta=f"{avg_reduction - 4.5:.1f}% vs target"
        )
    
    with col3:
        total_co2 = df['CO2_Avoided_MT'].sum()
        st.metric(
            label="🌱 CO₂ Avoided (Annual)",
            value=f"{total_co2:.1f} MT",
            delta="Million tonnes"
        )
    
    with col4:
        compliance = (df['Current_SEC'] < df['Target_SEC']).sum() / len(df) * 100
        st.metric(
            label="✅ Compliance Rate",
            value=f"{compliance:.0f}%",
            delta="Target achievers"
        )
    
    st.markdown("---")
    
    # Main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("SEC Performance by Refinery")
        fig = go.Figure()
        
        # Sort by current SEC
        df_sorted = df.sort_values('Current_SEC')
        
        fig.add_trace(go.Bar(
            name='Baseline SEC',
            x=df_sorted['Refinery'],
            y=df_sorted['Baseline_SEC'],
            marker_color='#ff7f7f',
            opacity=0.7
        ))
        
        fig.add_trace(go.Bar(
            name='Current SEC',
            x=df_sorted['Refinery'],
            y=df_sorted['Current_SEC'],
            marker_color='#7fb77f'
        ))
        
        fig.add_trace(go.Scatter(
            name='Target SEC',
            x=df_sorted['Refinery'],
            y=df_sorted['Target_SEC'],
            mode='markers',
            marker=dict(color='#1f77b4', size=10, symbol='diamond')
        ))
        
        fig.update_layout(
            barmode='overlay',
            xaxis_tickangle=-45,
            height=500,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            yaxis_title="SEC (MMBTU/MT)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Treatment Effects by Entry Timing")
        
        # Heterogeneity chart
        early = df[df['Entry_Category'] == 'Early (Cycle I-II)']['SEC_Reduction_Pct'].mean()
        late = df[df['Entry_Category'] == 'Late (Cycle III+)']['SEC_Reduction_Pct'].mean()
        
        fig = go.Figure()
        
        categories = ['Early Entrants<br>(Cycle I-II)', 'Late Entrants<br>(Cycle III+)', 'Overall<br>Average']
        values = [early, late, df['SEC_Reduction_Pct'].mean()]
        colors = ['#2ecc71', '#e74c3c', '#3498db']
        
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f'{v:.1f}%' for v in values],
            textposition='outside'
        ))
        
        fig.add_hline(y=4.5, line_dash="dash", line_color="gray",
                      annotation_text="Avg Target (4.5%)")
        
        fig.update_layout(
            height=400,
            yaxis_title="SEC Reduction (%)",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("📊 **Key Finding:** Early entrants show **50 percentage points** higher reductions than late entrants, suggesting strong learning effects.")
    
    # Bottom section: Cycle timeline
    st.subheader("PAT Cycle Timeline & ESCert Prices")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(
            x=cycle_df['Cycle'],
            y=cycle_df['Refineries_Added'],
            name='Refineries Added',
            marker_color='#3498db'
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(
            x=cycle_df['Cycle'],
            y=cycle_df['ESCert_Price_INR'],
            name='ESCert Price (₹/TOE)',
            mode='lines+markers',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=10)
        ),
        secondary_y=True
    )
    
    fig.update_layout(height=350)
    fig.update_yaxes(title_text="Refineries Added", secondary_y=False)
    fig.update_yaxes(title_text="ESCert Price (₹/TOE)", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)

# ============== PAGE: SEC CALCULATOR ==============
elif page == "🔢 SEC Calculator":
    st.markdown("## 🔢 SEC Calculator")
    st.markdown("Calculate Specific Energy Consumption and potential savings for any refinery configuration.")
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Input Parameters")
        
        # Input fields
        crude_throughput = st.number_input(
            "Annual Crude Throughput (MT)",
            min_value=100000,
            max_value=50000000,
            value=10000000,
            step=100000,
            help="Total crude processed per year in metric tonnes"
        )
        
        total_energy = st.number_input(
            "Total Energy Consumed (MMBTU)",
            min_value=1000000,
            max_value=500000000,
            value=85000000,
            step=1000000,
            help="Total energy consumed including fuel, steam, electricity"
        )
        
        capacity_utilization = st.slider(
            "Capacity Utilization (%)",
            min_value=50,
            max_value=100,
            value=85,
            help="Operating capacity utilization"
        )
        
        pat_cycle = st.selectbox(
            "PAT Cycle Entry",
            options=['Cycle I (2012)', 'Cycle II (2016)', 'Cycle III (2017)', 
                     'Cycle IV (2019)', 'Cycle V (2021)', 'Cycle VI (2023)', 'Not Enrolled'],
            index=0
        )
        
        baseline_sec = st.number_input(
            "Baseline SEC (MMBTU/MT)",
            min_value=5.0,
            max_value=12.0,
            value=8.33,
            step=0.1,
            help="SEC at the start of PAT enrollment"
        )
    
    with col2:
        st.subheader("Calculated Results")
        
        # Calculate SEC
        current_sec = total_energy / crude_throughput
        
        # Calculate reductions
        sec_reduction = ((baseline_sec - current_sec) / baseline_sec) * 100
        
        # Determine expected reduction based on cycle
        if 'I' in pat_cycle or 'II' in pat_cycle:
            expected_reduction = 51.8  # Early entrant effect
            entry_category = "Early Entrant"
        elif 'Not' in pat_cycle:
            expected_reduction = 0
            entry_category = "Not Enrolled"
        else:
            expected_reduction = 2.2  # Late entrant effect
            entry_category = "Late Entrant"
        
        # Display metrics
        st.metric(
            label="Current SEC",
            value=f"{current_sec:.2f} MMBTU/MT",
            delta=f"{sec_reduction:.1f}% from baseline" if sec_reduction > 0 else None
        )
        
        # Target SEC (assume 5% reduction target)
        target_sec = baseline_sec * 0.95
        
        st.metric(
            label="Target SEC",
            value=f"{target_sec:.2f} MMBTU/MT",
            delta="5% reduction target"
        )
        
        # Compliance status
        if current_sec <= target_sec:
            st.success(f"✅ **COMPLIANT** - Current SEC is below target")
            overachievement = ((target_sec - current_sec) / target_sec) * 100
            st.info(f"Overachievement: {overachievement:.1f}%")
        else:
            st.error(f"❌ **NON-COMPLIANT** - Gap of {current_sec - target_sec:.2f} MMBTU/MT")
        
        # Energy savings
        energy_savings = (baseline_sec - current_sec) * crude_throughput
        co2_avoided = energy_savings * 0.07 / 1000  # in thousand tonnes
        
        st.metric(
            label="Annual Energy Savings",
            value=f"{energy_savings/1e6:.2f} M MMBTU"
        )
        
        st.metric(
            label="CO₂ Avoided",
            value=f"{co2_avoided:.1f} kT CO₂/year"
        )
    
    st.markdown("---")
    
    # Visualization
    st.subheader("SEC Comparison")
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Baseline SEC', 'Current SEC', 'Target SEC', 'Industry Best'],
        y=[baseline_sec, current_sec, target_sec, 5.75],
        marker_color=['#e74c3c', '#3498db', '#2ecc71', '#9b59b6'],
        text=[f'{baseline_sec:.2f}', f'{current_sec:.2f}', f'{target_sec:.2f}', '5.75'],
        textposition='outside'
    ))
    
    fig.update_layout(
        yaxis_title="SEC (MMBTU/MT)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============== PAGE: BENCHMARKING TOOL ==============
elif page == "📈 Benchmarking Tool":
    st.markdown("## 📈 Refinery SEC Benchmarking")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        ownership_filter = st.multiselect("Ownership", ['PSU', 'Private', 'JV'], ['PSU', 'Private', 'JV'])
    with col2:
        min_cap, max_cap = st.slider("Capacity Range (MMTPA)", 0.0, 36.0, (0.0, 36.0))
    with col3:
        cycle_filter = st.multiselect("PAT Cycle", [1,2,3,4], [1,2,3,4])
    with col4:
        sort_by = st.selectbox("Sort By", ['SEC_Reduction_Pct', 'Current_SEC', 'Capacity_MMTPA'])
    
    filtered_df = df[
        (df['Ownership'].isin(ownership_filter)) &
        (df['Capacity_MMTPA'] >= min_cap) & (df['Capacity_MMTPA'] <= max_cap) &
        (df['PAT_Cycle_Entry'].isin(cycle_filter))
    ].sort_values(sort_by, ascending=(sort_by == 'Current_SEC'))
    
    # Scatter plot
    fig = px.scatter(filtered_df, x='Capacity_MMTPA', y='Current_SEC', size='SEC_Reduction_Pct',
                    color='Ownership', hover_name='Refinery',
                    hover_data=['Baseline_SEC', 'Target_SEC', 'SEC_Reduction_Pct'],
                    color_discrete_map={'PSU': '#3498db', 'Private': '#e74c3c', 'JV': '#2ecc71'})
    fig.add_hline(y=filtered_df['Current_SEC'].mean(), line_dash="dash",
                  annotation_text=f"Avg: {filtered_df['Current_SEC'].mean():.2f}")
    fig.update_layout(xaxis_title="Capacity (MMTPA)", yaxis_title="Current SEC", height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    # Ranking table with export
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Rankings ({len(filtered_df)} refineries)")
    with col2:
        csv = filtered_df[['Refinery','Ownership','Capacity_MMTPA','Current_SEC','SEC_Reduction_Pct']].to_csv(index=False)
        st.download_button("📥 Export", csv, "benchmark.csv", "text/csv")
    
    display_df = filtered_df[['Refinery', 'Ownership', 'Capacity_MMTPA', 'Baseline_SEC', 
                              'Current_SEC', 'Target_SEC', 'SEC_Reduction_Pct']].copy()
    display_df['Rank'] = range(1, len(display_df) + 1)
    display_df['SEC_Reduction_Pct'] = display_df['SEC_Reduction_Pct'].round(1).astype(str) + '%'
    st.dataframe(display_df[['Rank'] + [c for c in display_df.columns if c != 'Rank']], 
                use_container_width=True, hide_index=True)

# ============== PAGE: ESCERT SIMULATOR ==============
elif page == "💹 ESCert Simulator":
    st.markdown("## 💹 ESCert Trading Simulator")
    
    tab1, tab2, tab3 = st.tabs(["🏭 Single Refinery", "📊 Portfolio Analysis", "📈 Price Scenarios"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            selected_refinery = st.selectbox("Select Refinery", df['Refinery'].tolist())
            ref_data = df[df['Refinery'] == selected_refinery].iloc[0]
            
            escert_price = st.slider("ESCert Price (₹/TOE)", 100, 10000, 4000, 100)
            usd_inr = st.number_input("USD/INR Rate", 70.0, 100.0, 83.0)
            utilization = st.slider("Capacity Utilization (%)", 50, 100, 85)
        
        with col2:
            overachievement = ref_data['Target_SEC'] - ref_data['Current_SEC']
            annual_throughput = ref_data['Capacity_MMTPA'] * 1e6 * (utilization/100)
            escerts_toe = overachievement * annual_throughput / 41.868
            
            if overachievement > 0:
                revenue_inr = escerts_toe * escert_price
                st.success(f"✅ **Generator**: {escerts_toe:,.0f} TOE")
                st.metric("Revenue", f"₹{revenue_inr/1e7:.2f} Cr", f"${revenue_inr/usd_inr/1e6:.2f}M")
            else:
                cost_inr = abs(escerts_toe) * escert_price
                st.error(f"❌ **Buyer**: {abs(escerts_toe):,.0f} TOE needed")
                st.metric("Cost", f"₹{cost_inr/1e7:.2f} Cr", f"${cost_inr/usd_inr/1e6:.2f}M")
            
            # Break-even analysis
            if overachievement < 0:
                breakeven_sec = ref_data['Target_SEC']
                gap = ref_data['Current_SEC'] - breakeven_sec
                st.info(f"📉 Reduce SEC by {gap:.2f} MMBTU/MT to break even")
    
    with tab2:
        st.subheader("Industry-Wide ESCert Balance")
        
        # Calculate for all refineries
        portfolio = df.copy()
        portfolio['ESCert_TOE'] = ((portfolio['Target_SEC'] - portfolio['Current_SEC']) * 
                                   portfolio['Capacity_MMTPA'] * 1e6 * 0.85 / 41.868)
        portfolio['Value_Cr'] = portfolio['ESCert_TOE'] * escert_price / 1e7
        
        col1, col2 = st.columns(2)
        with col1:
            total_gen = portfolio[portfolio['ESCert_TOE'] > 0]['ESCert_TOE'].sum()
            total_buy = abs(portfolio[portfolio['ESCert_TOE'] < 0]['ESCert_TOE'].sum())
            st.metric("Total ESCerts Generated", f"{total_gen/1e6:.2f}M TOE")
            st.metric("Total ESCerts Required", f"{total_buy/1e6:.2f}M TOE")
        with col2:
            net_balance = total_gen - total_buy
            st.metric("Net Market Balance", f"{net_balance/1e6:.2f}M TOE", 
                     "Surplus" if net_balance > 0 else "Deficit")
            market_value = abs(net_balance) * escert_price / 1e7
            st.metric("Market Value", f"₹{market_value:.0f} Cr")
        
        # Waterfall chart
        fig = go.Figure(go.Waterfall(
            x=portfolio.sort_values('ESCert_TOE', ascending=False)['Refinery'],
            y=portfolio.sort_values('ESCert_TOE', ascending=False)['ESCert_TOE']/1e3,
            connector={"line":{"color":"rgb(63, 63, 63)"}},
            decreasing={"marker":{"color":"#e74c3c"}},
            increasing={"marker":{"color":"#2ecc71"}}
        ))
        fig.update_layout(title="ESCert Position by Refinery (000 TOE)", height=400, 
                         xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Price Scenario Analysis")
        
        price_scenarios = [1000, 2000, 4000, 6000, 8000, 10000]
        scenario_results = []
        
        for price in price_scenarios:
            for _, row in df.iterrows():
                escerts = ((row['Target_SEC'] - row['Current_SEC']) * 
                          row['Capacity_MMTPA'] * 1e6 * 0.85 / 41.868)
                value = escerts * price / 1e7
                scenario_results.append({
                    'Price': price, 'Refinery': row['Refinery'],
                    'Value_Cr': value, 'Type': 'Revenue' if value > 0 else 'Cost'
                })
        
        scenario_df = pd.DataFrame(scenario_results)
        
        # Aggregate by price
        agg_df = scenario_df.groupby(['Price', 'Type'])['Value_Cr'].sum().reset_index()
        
        fig = px.bar(agg_df, x='Price', y='Value_Cr', color='Type', barmode='group',
                    color_discrete_map={'Revenue': '#2ecc71', 'Cost': '#e74c3c'})
        fig.update_layout(title="Industry ESCert Value by Price Scenario", 
                         xaxis_title="ESCert Price (₹/TOE)", yaxis_title="Value (₹ Cr)")
        st.plotly_chart(fig, use_container_width=True)

# ============== PAGE: TARGET PREDICTOR ==============
elif page == "🎯 Target Predictor":
    st.markdown("## 🎯 PAT Target Achievement Predictor")
    
    tab1, tab2, tab3 = st.tabs(["🎲 Single Prediction", "📊 Batch Analysis", "📥 Export Data"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            pred_baseline_sec = st.number_input("Baseline SEC", 5.0, 12.0, 8.33, key="p1")
            pred_target_pct = st.slider("Target Reduction (%)", 1.0, 10.0, 5.0, 0.5)
            pred_cycle = st.selectbox("Entry Timing", ['Early (Cycle I-II)', 'Late (Cycle III+)'])
            pred_capacity = st.slider("Capacity (MMTPA)", 1.0, 35.0, 10.0)
        
        with col2:
            # Model coefficients from paper
            base_effect = 51.8 if 'Early' in pred_cycle else 2.2
            size_adj = -8.5 if pred_capacity > 10 else 0
            predicted_reduction = base_effect + size_adj
            
            predicted_sec = pred_baseline_sec * (1 - predicted_reduction/100)
            target_sec = pred_baseline_sec * (1 - pred_target_pct/100)
            
            # Monte Carlo
            np.random.seed(42)
            simulated = np.random.normal(predicted_reduction, 17.1, 10000)
            simulated_secs = pred_baseline_sec * (1 - simulated/100)
            compliance_prob = (simulated_secs < target_sec).mean() * 100
            
            st.metric("Predicted Reduction", f"{predicted_reduction:.1f}%")
            st.metric("Predicted SEC", f"{predicted_sec:.2f} MMBTU/MT")
            
            if compliance_prob >= 80:
                st.success(f"✅ Compliance Probability: **{compliance_prob:.0f}%**")
            elif compliance_prob >= 50:
                st.warning(f"⚠️ Compliance Probability: **{compliance_prob:.0f}%**")
            else:
                st.error(f"❌ Compliance Probability: **{compliance_prob:.0f}%**")
            
            ci_low, ci_high = np.percentile(simulated_secs, [2.5, 97.5])
            st.info(f"95% CI: [{ci_low:.2f}, {ci_high:.2f}]")
        
        # Distribution plot
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=simulated_secs, nbinsx=50, marker_color='#3498db', opacity=0.7))
        fig.add_vline(x=target_sec, line_dash="dash", line_color="red", annotation_text="Target")
        fig.add_vline(x=predicted_sec, line_color="green", annotation_text="Predicted")
        fig.update_layout(xaxis_title="SEC (MMBTU/MT)", yaxis_title="Frequency", height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("All Refineries Compliance Forecast")
        
        results = []
        for _, row in df.iterrows():
            base_eff = 51.8 if row['PAT_Cycle_Entry'] <= 2 else 2.2
            size_adj = -8.5 if row['Capacity_MMTPA'] > 10 else 0
            pred_red = base_eff + size_adj
            pred_sec = row['Baseline_SEC'] * (1 - pred_red/100)
            
            np.random.seed(hash(row['Refinery']) % 2**32)
            sims = np.random.normal(pred_red, 17.1, 5000)
            sim_secs = row['Baseline_SEC'] * (1 - sims/100)
            prob = (sim_secs < row['Target_SEC']).mean() * 100
            
            results.append({
                'Refinery': row['Refinery'],
                'Baseline': row['Baseline_SEC'],
                'Target': row['Target_SEC'],
                'Predicted': round(pred_sec, 2),
                'Prob_%': round(prob, 1),
                'Status': '✅' if prob >= 70 else ('⚠️' if prob >= 40 else '❌')
            })
        
        result_df = pd.DataFrame(results).sort_values('Prob_%', ascending=False)
        st.dataframe(result_df, use_container_width=True, hide_index=True)
        
        # Summary stats
        high_prob = len(result_df[result_df['Prob_%'] >= 70])
        med_prob = len(result_df[(result_df['Prob_%'] >= 40) & (result_df['Prob_%'] < 70)])
        low_prob = len(result_df[result_df['Prob_%'] < 40])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("High Probability (≥70%)", high_prob)
        col2.metric("Medium (40-70%)", med_prob)
        col3.metric("At Risk (<40%)", low_prob)
    
    with tab3:
        st.subheader("Export Analysis Data")
        
        # Prepare export data
        export_df = df[['Refinery', 'Ownership', 'Capacity_MMTPA', 'Baseline_SEC', 
                       'Current_SEC', 'Target_SEC', 'SEC_Reduction_Pct', 'CO2_Avoided_MT']].copy()
        export_df.columns = ['Refinery', 'Ownership', 'Capacity_MMTPA', 'Baseline_SEC',
                            'Current_SEC', 'Target_SEC', 'Reduction_%', 'CO2_Avoided_MT']
        
        csv = export_df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "pat_analysis.csv", "text/csv")
        
        # Show preview
        st.dataframe(export_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>PAT Scheme Dashboard v1.0 | Based on research by Bosco Chiramel</p>
    <p>Data sources: BEE PAT Cycle Reports, PPAC, Climate TRACE, IEX</p>
</div>
""", unsafe_allow_html=True)
