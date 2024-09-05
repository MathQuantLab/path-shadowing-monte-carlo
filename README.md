# Path shadowing Monte carlo simulation
Using [this article](https://github.com/M2QF/path-shadowing-monte-carlo/blob/main/Article.pdf), we will implement the _Path Shadowing_ Monte Carlo method.

## Overview

This repository implements the **Path Shadowing Monte Carlo (PSMC)** method. PSMC is a stochastic model designed for **volatility prediction** and **option pricing** by averaging future quantities over generated price paths whose past history aligns with the actual observed history. The method can be applied to financial models and time-series data analysis.

## Features

- **Prediction and Pricing**: Simulates future volatility and provides insights for pricing options based on historical paths.
- **Shadowing Paths**: Tracks price paths that align with observed historical data.
- **Multi-Processed**: Leverages multi-processing to efficiently scan large datasets for shadowing paths.
- **Time-Series Generation**: Utilizes wavelet scattering spectra to generate synthetic time-series data.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MathQuantLab/path-shadowing-monte-carlo.git
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

Optional: Install the scattering spectra package used for time-series generation:
   ```bash
   pip install git+https://github.com/RudyMorel/scattering_spectra
   ```

## Usage

To use the Path Shadowing Monte Carlo method, you can run the main class `PathShadowing` from the `path_shadowing.py` file.

Example:

```python
from path_shadowing import PathShadowing

# Example usage
shadowing = PathShadowing(data)
shadowing.run_simulation()
```

Additionally, you can explore the notebook `tutorial.ipynb` for a hands-on guide on how to use the method with sample data.

## Dependencies

- Python 3.x
- NumPy
- Scikit-learn
- Pandas
- Matplotlib
- [scattering_spectra](https://github.com/RudyMorel/scattering_spectra)

## Contributing

Contributions are welcome! Feel free to submit issues, feature requests, or pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE.md) file for details.
