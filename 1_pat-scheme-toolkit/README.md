# ⚡ PAT Scheme Analysis Toolkit

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Python library and web dashboard for analyzing India's **Perform, Achieve and Trade (PAT)** scheme for refinery energy efficiency.

## 📊 Research Basis

Based on: *"The impact of India's PAT scheme on refinery energy efficiency: A staggered difference-in-differences analysis"*

**Key Findings:**
| Metric | Value |
|--------|-------|
| Average SEC Reduction | **24.1%** |
| Early Entrants (Cycle I-II) | **-51.8%** |
| Late Entrants (Cycle III+) | **-2.2%** |
| CO₂ Avoided (2012-2024) | **115 MT** |

---

## 🏗️ Project Structure

```
pat_tool/
├── pat_scheme/              # Python Library
│   ├── __init__.py          # Package exports
│   ├── data.py              # Refinery data, PAT cycles
│   ├── models.py            # Diff-in-diff, Monte Carlo
│   └── calculator.py        # SEC & ESCert calculations
├── streamlit_app/           # Web Dashboard
│   └── app.py               # Streamlit application
├── tests/                   # Unit tests
├── data/                    # Data files
├── setup.py                 # Package installation
├── requirements.txt         # Dependencies
└── README.md
```

---

## 🚀 Quick Start

### Install as Python Library

```bash
pip install -e .
```

### Use in Python

```python
from pat_scheme import (
    get_refinery_data, 
    calculate_sec, 
    predict_sec_reduction,
    monte_carlo_compliance
)

# Load refinery data
df = get_refinery_data()
print(df[['refinery', 'current_sec', 'sec_reduction_pct']].head())

# Calculate SEC for a refinery
result = calculate_sec(
    total_energy_mmbtu=85_000_000,
    crude_throughput_mt=10_000_000,
    baseline_sec=8.33,
    target_reduction_pct=5.0
)
print(f"Current SEC: {result.current_sec} MMBTU/MT")
print(f"Compliant: {result.is_compliant}")

# Predict SEC reduction using diff-in-diff model
reduction = predict_sec_reduction(
    pat_cycle_entry=1,  # Cycle I
    capacity_mmtpa=15.0
)
print(f"Predicted reduction: {reduction:.1f}%")

# Monte Carlo compliance probability
prob, ci_low, ci_high, _ = monte_carlo_compliance(
    baseline_sec=8.33,
    target_sec=7.9,
    predicted_reduction_pct=reduction
)
print(f"Compliance probability: {prob:.0f}%")
```

### Run Streamlit Dashboard

```bash
cd streamlit_app
streamlit run app.py
```

---

## 📦 API Reference

### Data Module

| Function | Description |
|----------|-------------|
| `get_refinery_data()` | Load 23 refineries with PAT metrics |
| `get_cycle_data()` | PAT cycle timeline (I-VII) |
| `get_industry_stats()` | Aggregate industry statistics |

### Models Module

| Function | Description |
|----------|-------------|
| `predict_sec_reduction(cycle, capacity)` | Diff-in-diff prediction |
| `monte_carlo_compliance(...)` | Compliance probability with CI |
| `batch_compliance_forecast(df)` | Forecast for all refineries |

### Calculator Module

| Function | Description |
|----------|-------------|
| `calculate_sec(energy, throughput, ...)` | SEC calculation |
| `calculate_escerts(sec, target, ...)` | ESCert economics |
| `calculate_portfolio_escerts(df, price)` | Industry-wide balance |

---

## 🌐 Streamlit Dashboard Features

1. **📊 Dashboard Overview** - Key metrics, SEC performance charts
2. **🔢 SEC Calculator** - Interactive SEC computation
3. **📈 Benchmarking Tool** - Compare refineries with filters
4. **💹 ESCert Simulator** - Trading economics, portfolio analysis
5. **🎯 Target Predictor** - Monte Carlo compliance forecasts

---

## ☁️ Deployment

### Streamlit Cloud (Free)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository → Deploy

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app/app.py"]
```

---

## 📄 Citation

```bibtex
@article{chiramel2024pat,
  title={The impact of India's PAT scheme on refinery energy efficiency: 
         A staggered difference-in-differences analysis},
  author={Chiramel, Bosco},
  year={2024}
}
```

## 👤 Author

**Bosco Chiramel**  
📧 bosco8b4824@gmail.com | ORCID: 0009-0001-8456-5302

## 📝 License

MIT License - see [LICENSE](LICENSE)
