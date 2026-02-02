"""Setup script for PAT Scheme Analysis Toolkit."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pat-scheme",
    version="1.0.0",
    author="Bosco Chiramel",
    author_email="bosco8b4824@gmail.com",
    description="Python toolkit for analyzing India's PAT scheme for refinery energy efficiency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pat-scheme-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={
        "streamlit": [
            "streamlit>=1.31.0",
            "plotly>=5.18.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
)
